from django.db import models
from django.conf import settings
from products.models import Tag, Product, SkinType, Concern

class Answer(models.Model):
    answer_text = models.CharField(max_length=150)
    # tags = models.ManyToManyField(Tag, related_name='answers')  # Link answers to tags

    def __str__(self):
        return self.answer_text


class Question(models.Model):
    question_text = models.CharField(max_length=150)
    question_order = models.PositiveSmallIntegerField(default=0)
    answers = models.ManyToManyField(Answer, related_name='questions')  # Many answers can be linked to one question

    def __str__(self):
        return self.question_text


class Quiz(models.Model):
    quiz_name = models.CharField(max_length=150, db_index=True)
    questions = models.ManyToManyField(Question, blank=True)  # A quiz can have many questions

    def __str__(self):
        return self.quiz_name
    
    class Meta:
        ordering = ['id']


class QuizSession(models.Model):
    session_id = models.CharField(max_length=40, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, db_index=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, db_index=True)
    answers_data = models.JSONField()  # Store all answers in JSON format
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Quiz Session {self.session_id} for {self.quiz.quiz_name}"