from django.contrib import admin

from products.models import Product, Price, Currency, Category, Tag

# Register your models here.

admin.site.register(Product)
admin.site.register(Price)
admin.site.register(Currency)
admin.site.register(Category)
admin.site.register(Tag)
