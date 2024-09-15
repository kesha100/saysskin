from rest_framework import serializers
from .models import Quiz, Question, Answer, UserQuiz, UserAnswer
from products.models import Product, Tag


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'answer_text', 'tags']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_order', 'answers']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True, allow_null=True)

    class Meta:
        model = Quiz
        fields = ['id', 'quiz_name', 'questions']


class UserQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuiz
        fields = ['id', 'user', 'quiz', 'completed']


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = ['id', 'user_quiz', 'question', 'selected_answer']
