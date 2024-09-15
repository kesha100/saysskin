from django.urls import path
from products import views

urlpatterns = [
    path('get-products/', views.ProductView.as_view({'get':'list'})),
]