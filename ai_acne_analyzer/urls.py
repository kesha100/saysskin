from django.urls import path
from .views import AcneAnalysisView

urlpatterns = [
    path('analyze-acne/', AcneAnalysisView.as_view(), name='analyze-acne'),
]