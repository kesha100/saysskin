from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from products.models import Tag, Product, SkinType, Concern
from user.models import CustomUser
CustomUser = settings.AUTH_USER_MODEL

class Answer(models.Model):
    answer_text = models.CharField(max_length=150)
    tags = models.ManyToManyField(Tag, related_name='answers')  # Link answers to tags

    def __str__(self):
        return self.answer_text


class Question(models.Model):
    question_text = models.CharField(max_length=150)
    question_order = models.PositiveSmallIntegerField(default=0)
    answers = models.ManyToManyField(Answer, related_name='questions')  # Many answers can be linked to one question

    def __str__(self):
        return self.question_text


class Quiz(models.Model):
    quiz_name = models.CharField(max_length=150)
    questions = models.ManyToManyField(Question, blank=True)  # A quiz can have many questions

    def __str__(self):
        return self.quiz_name



class UserQuiz(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=40, null=True, blank=True)
    completed = models.BooleanField(default=False)

    # def recommend_products(self):
    #     profile = self.user.profile
    #     products = Product.objects.all()
    #     recommendations = []

    #     for product in products:
    #         score = 0
    #         # Check compatibility with user's skin types
    #         for skin_type in profile.skin_types.all():
    #             if product.skin_types.filter(skin_type=skin_type).exists():
    #                 score += product.productattribute_set.filter(skin_type=skin_type).first().effectiveness_score

    #         # Check for concerns
    #         for concern in profile.concerns.all():
    #             if product.concerns.filter(concern=concern).exists():
    #                 score += product.productattribute_set.filter(concern=concern).first().effectiveness_score

    #         # Adjust score for lifestyle preferences
    #         score += len(set(profile.lifestyle_preferences.all()) & set(product.tags.all()))

    #         # Penalize or reward based on blacklisted/favored ingredients
    #         score -= len(set(profile.blacklisted_ingredients.all()) & set(product.tags.all()))
    #         score += len(set(profile.favored_ingredients.all()) & set(product.tags.all()))

    #         recommendations.append((product, score))

    #     # Sort products by score
    #     recommendations.sort(key=lambda x: x[1], reverse=True)
    #     return recommendations


class UserAnswer(models.Model):
    user_quiz = models.ForeignKey(UserQuiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True)
    selected_answer = models.ForeignKey(Answer, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Selected '{self.selected_answer.answer_text}' for '{self.question.question_text}' by {self.user_quiz.user.username}"


