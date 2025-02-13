from django.contrib import admin
from .models import Quiz, QuizSession, Question, Answer
# Register your models here.

admin.site.register(Question)
admin.site.register(Quiz)
admin.site.register(Answer)
admin.site.register(QuizSession)
