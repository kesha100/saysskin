from django.contrib import admin
from .views import Question, Quiz, Answer, UserAnswer, UserQuiz
# Register your models here.

admin.site.register(Question)
admin.site.register(Quiz)
admin.site.register(Answer)
admin.site.register(UserQuiz)
admin.site.register(UserAnswer)
