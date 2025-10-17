from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import CreateQuizRequestSerializer, QuizSerializer, QuizListSerializer, QuizDetailReadSerializer, QuizPartialUpdateSerializer
from quiz_app.services.service import create_quiz_from_url
from django.db.models import Prefetch
from ..models import Quiz, Question
from .permissions import IsQuizOwner


class CreateQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = CreateQuizRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        url = s.validated_data["url"]
        try:
            quiz = create_quiz_from_url(request.user, url)
            return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"detail": "Failed to create quiz."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuizListSerializer
    pagination_class = None

    def get_queryset(self):
        return (
            Quiz.objects
            .filter(user=self.request.user)
            .prefetch_related(
                Prefetch('questions', queryset=Question.objects.order_by('id'))
            )
            .order_by('-created_at')
        )


class QuizDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsQuizOwner]
    lookup_url_kwarg = 'id'
    lookup_field = 'id'

    def get_queryset(self):
        return (
            Quiz.objects
            .prefetch_related(
                Prefetch('questions', queryset=Question.objects.order_by('id'))
            )
        )

    def get_serializer_class(self):
        return (
            QuizDetailReadSerializer
            if self.request.method == 'GET'
            else QuizPartialUpdateSerializer
        )
