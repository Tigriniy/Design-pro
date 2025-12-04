from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    full_name = models.CharField(
        max_length=150,
        verbose_name='ФИО',
        blank=False
    )
    agree_to_terms = models.BooleanField(
        default=False,
        verbose_name='Согласие на обработку ПД'
    )

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    UserProfile.objects.get_or_create(user=instance)