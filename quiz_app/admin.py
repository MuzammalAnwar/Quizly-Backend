# admin.py
from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils.html import format_html
from django.utils.timezone import localtime
from django import forms
import json

from .models import Quiz, Question


# ---------- Forms ----------

class QuestionAdminForm(forms.ModelForm):
    """
    Nicer JSON editing for question_options + basic validation.
    """
    class Meta:
        model = Question
        fields = "__all__"
        widgets = {
            "question_options": forms.Textarea(attrs={
                "rows": 4,
                "style": "font-family: monospace; tab-size: 2; width: 100%;",
                "placeholder": 'e.g. ["A", "B", "C", "D"]'
            })
        }

    def clean_question_options(self):
        value = self.cleaned_data["question_options"]
        # Allow admins to paste a JSON string
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as e:
                raise forms.ValidationError(f"Invalid JSON: {e}")
        if not isinstance(value, (list, tuple)):
            raise forms.ValidationError(
                "question_options must be a JSON list (e.g. [\"A\", \"B\"]).")
        return value


# ---------- Inlines ----------

class QuestionInline(admin.TabularInline):
    model = Question
    form = QuestionAdminForm
    extra = 0
    show_change_link = True
    fields = ("question_title", "question_options",
              "answer", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("id",)


# ---------- Admin Actions ----------

def export_quizzes_as_json(modeladmin, request, queryset):
    """
    Export selected quizzes (with nested questions) as a JSON file.
    """
    payload = []
    for quiz in queryset.select_related("user").prefetch_related("questions"):
        payload.append({
            "id": quiz.id,
            "user_id": quiz.user_id,
            "title": quiz.title,
            "description": quiz.description,
            "video_url": quiz.video_url,
            "created_at": localtime(quiz.created_at).isoformat(),
            "updated_at": localtime(quiz.updated_at).isoformat(),
            "questions": [
                {
                    "id": q.id,
                    "question_title": q.question_title,
                    "question_options": q.question_options,
                    "answer": q.answer,
                    "created_at": localtime(q.created_at).isoformat(),
                    "updated_at": localtime(q.updated_at).isoformat(),
                }
                for q in quiz.questions.all().order_by("id")
            ],
        })
    data = json.dumps(payload, ensure_ascii=False, indent=2)
    resp = HttpResponse(data, content_type="application/json; charset=utf-8")
    resp["Content-Disposition"] = "attachment; filename=quizzes.json"
    return resp


export_quizzes_as_json.short_description = "Export selected quizzes as JSON"


@admin.action(description="Duplicate selected quizzes (including questions)")
def duplicate_quizzes(modeladmin, request, queryset):
    copied = 0
    for quiz in queryset.prefetch_related("questions"):
        original_questions = list(quiz.questions.all().order_by("id"))
        quiz.pk = None
        quiz.title = f"Copy of {quiz.title}"
        quiz.save()
        for q in original_questions:
            Question.objects.create(
                quiz=quiz,
                question_title=q.question_title,
                question_options=q.question_options,
                answer=q.answer,
            )
        copied += 1
    messages.success(request, f"Duplicated {copied} quiz(zes).")


# ---------- ModelAdmins ----------

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    save_on_top = True
    list_display = (
        "id", "title", "user", "question_count", "video_preview", "created_at", "updated_at",
    )
    list_display_links = ("id", "title")
    list_filter = ("user", "created_at", "updated_at")
    search_fields = ("title", "description", "user__username",
                     "questions__question_title")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_select_related = ("user",)
    readonly_fields = ("created_at", "updated_at")
    actions = [duplicate_quizzes, export_quizzes_as_json]
    autocomplete_fields = ("user",)

    fieldsets = (
        ("Quiz Info", {
            "fields": ("user", "title", "description", "video_url"),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    @admin.display(description="Questions", ordering="id")
    def question_count(self, obj: Quiz):
        return obj.questions.count()

    @admin.display(description="Video")
    def video_preview(self, obj: Quiz):
        if not obj.video_url:
            return "-"
        return format_html('<a href="{}" target="_blank" rel="noopener">Open</a>', obj.video_url)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    form = QuestionAdminForm
    save_on_top = True
    list_display = ("id", "short_title", "quiz", "answer", "created_at")
    list_display_links = ("id", "short_title")
    list_filter = ("quiz", "created_at", "updated_at")
    search_fields = ("question_title", "answer", "quiz__title")
    ordering = ("quiz", "id")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("quiz",)
    fields = ("quiz", "question_title", "question_options",
              "answer", "created_at", "updated_at")

    @admin.display(description="Question")
    def short_title(self, obj: Question):
        return (obj.question_title or "")[:70]
