from rest_framework import serializers
from .models import Quiz, QuizSession, Question, Answer

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = '__all__'


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = '__all__'


class QuizSessionSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    quiz = QuizSerializer(read_only=True)
    answers_data = serializers.JSONField()

    class Meta:
        model = QuizSession
        fields = ['id', 'quiz', 'answers_data', 'user', 'completed', 'session_id']  # Include session_id

    def get_id(self, obj):
        return obj.id if obj.user else obj.session_id

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.user is None:
            ret['id'] = ret.pop('session_id', None)
        return ret