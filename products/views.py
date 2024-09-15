from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView

from products.models import Product
from products.serializers import ProductSerializer


# Create your views here.

class ProductView(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
