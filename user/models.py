from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    # Add custom fields here
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    skin_types = models.ManyToManyField('products.SkinType', blank=True)
    concerns = models.ManyToManyField('products.Concern', blank=True)
    lifestyle_preferences = models.ManyToManyField('products.Tag', blank=True)
    blacklisted_ingredients = models.ManyToManyField('products.Tag', related_name='blacklisted_by_users', blank=True)
    favored_ingredients = models.ManyToManyField('products.Tag', related_name='favored_by_users', blank=True)

@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()