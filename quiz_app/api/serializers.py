from rest_framework import serializers
from quiz_app.models import Quiz, Question


class CreateQuizRequestSerializer(serializers.Serializer):
    url = serializers.URLField()


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id',
            'question_title',
            'question_options',
            'answer',
            'created_at',
            'updated_at'
        ]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Quiz
        fields = [
            'id',
            'title',
            'description',
            'created_at',
            'updated_at',
            'video_url',
            'questions'
        ]


class QuizListSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = (
            'id',
            'title',
            'description',
            'created_at',
            'updated_at',
            'video_url',
            'questions'
        )


class QuizDetailReadSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = (
            'id',
            'title',
            'description',
            'created_at',
            'updated_at',
            'video_url',
            'questions'
        )


class QuizPartialUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz

        fields = ('title', 'description', 'video_url')

        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'video_url': {'required': False},
        }
