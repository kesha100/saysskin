from django.db import models


class Currency(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Price(models.Model):
    price = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class SkinType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Concern(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    benefits = models.TextField(blank=True, null=True)  # Describe the benefits for skincare

    def __str__(self):
        return self.name


class ProductIngredient(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    concentration = models.FloatField(help_text="Concentration of ingredient in percentage")

    def __str__(self):
        return f"{self.ingredient.name} in {self.product.name} at {self.concentration}%"


class ProductAttribute(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    skin_type = models.ForeignKey(SkinType, on_delete=models.CASCADE)
    concern = models.ForeignKey(Concern, on_delete=models.CASCADE, null=True, blank=True)
    effectiveness_score = models.IntegerField(default=0)  # Score for how effective a product is for a skin type/concern
    concentration = models.FloatField(default=0.0)  # Concentration of the active ingredient


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.ForeignKey(Price, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    skin_types = models.ManyToManyField(SkinType, through=ProductAttribute)
    concerns = models.ManyToManyField(Concern, through=ProductAttribute)
    ingredients = models.ManyToManyField(Ingredient, through=ProductIngredient)

    interest_count = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
