from rest_framework.pagination import PageNumberPagination

class QuestionPagination(PageNumberPagination):
    page_size = 1  # Adjust this based on how many questions should load at once
