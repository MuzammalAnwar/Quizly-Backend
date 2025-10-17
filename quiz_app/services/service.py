import os, re, json, time, tempfile, logging
import whisper, yt_dlp
from yt_dlp.utils import DownloadError
from google import genai
from django.db import transaction
from ..models import Quiz, Question

log = logging.getLogger(__name__)
_WHISPER_MODEL = None
_client = None


# --- YT audio download (full video) ---
def download_audio_file(url: str, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    outtmpl = os.path.join(out_dir, '%(id)s.%(ext)s')

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'noplaylist': True,
        'quiet': True,
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            vid = info.get('id')
            title = info.get('title', 'unknown')
            log.info('YT downloaded: id=%s title="%s"', vid, title)
    except DownloadError as e:
        raise ValueError(f'YouTube download failed: {e}')

    for ext in ('mp3', 'm4a', 'webm', 'opus', 'ogg', 'wav'):
        path = os.path.join(out_dir, f'{vid}.{ext}')
        if os.path.exists(path):
            return path

    raise ValueError('Audio download failed — no audio file found')


# --- Whisper ---
def _get_whisper_model():
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        name = os.getenv('WHISPER_MODEL', 'base')
        log.info('Whisper load start: %s', name)
        _WHISPER_MODEL = whisper.load_model(name)
        log.info('Whisper load done: %s', name)
    return _WHISPER_MODEL


def transcribe_with_whisper(audio_path: str) -> str:
    model = _get_whisper_model()
    log.info('Whisper transcribe call')
    result = model.transcribe(audio_path, fp16=False, without_timestamps=True)
    transcript = result['text']
    snippet = transcript[:240].replace('\n', ' ')
    log.info('Transcript len=%d sample="%s..."', len(transcript), snippet)
    return transcript


# --- Gemini ---
def get_gemini_client():
    global _client
    if _client is None:
        key = os.getenv('GOOGLE_API_KEY')
        if not key:
            raise RuntimeError('GOOGLE_API_KEY not set.')
        _client = genai.Client(api_key=key)
    return _client


def _coerce_json(txt: str) -> dict:
    t = re.sub(r'^```.*?\n|\n```$', '', txt.strip(), flags=re.DOTALL)
    return json.loads(t)


def make_quiz_with_gemini(transcript: str) -> dict:
    client = get_gemini_client()
    prompt = f"""
        You are given a transcript from which you have to create a quiz in STRICT JSON:

        {{
        "title": "<short descriptive quiz title>",
        "description": "<1-2 sentence description>",
        "questions": [
            {{
            "question_title": "<question text>",
            "question_options": ["Option A","Option B","Option C","Option D"],
            "answer": "Option A"
            }}
        ]
        }}

        Rules:
        - Exactly 10 questions.
        - Exactly 4 options per question.
        - The "answer" MUST be one of the provided options (exact text).
        - Output ONLY valid JSON (no prose).
        - If the transcript is mostly music, noise, or not instructional, return:
        {{"error":"insufficient_content"}} only.

        Transcript:
        \"\"\"{transcript}\"\"\"
        """
    resp = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    return _coerce_json(resp.text)


# --- DB save ---
def _save_quiz(data: dict, user, url: str) -> Quiz:
    with transaction.atomic():
        quiz = Quiz.objects.create(
            user=user,
            title=data.get('title', 'Quiz'),
            description=data.get('description', ''),
            video_url=url,
        )
        for q in data.get('questions', []):
            Question.objects.create(
                quiz=quiz,
                question_title=q.get('question_title', ''),
                question_options=q.get('question_options', []),
                answer=q.get('answer', ''),
            )
    return quiz


# --- function which is called in views.py to create quiz ---
def create_quiz_from_url(user, url: str) -> Quiz:
    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix='quiz_') as tmp:
        log.info('Step 1: download start')
        audio_path = download_audio_file(url, tmp)
        log.info('Step 1: download done in %.1fs', time.time() - t0)

        log.info('Step 2: whisper start')
        transcript = transcribe_with_whisper(audio_path)
        if not transcript or len(transcript.strip()) < 150:
            raise ValueError('Transcript too short or low-signal; try another video.')
        log.info('Step 2: whisper done (len=%d)', len(transcript))

        log.info('Step 3: gemini start')
        quiz_json = make_quiz_with_gemini(transcript)
        if quiz_json.get('error') == 'insufficient_content':
            raise ValueError('Video not instructional; cannot create quiz.')
        log.info('Step 3: gemini done in %.1fs', time.time() - t0)

        quiz = _save_quiz(quiz_json, user, url)
        log.info('Step 4: saved quiz in DB. Total %.1fs', time.time() - t0)
        return quiz
