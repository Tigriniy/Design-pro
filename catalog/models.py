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


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название категории',
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class Application(models.Model):
    STATUS_CHOICES = [
        ('новая', 'Новая'),
        ('в работе', 'Принято в работу'),
        ('выполнено', 'Выполнено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='описание')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='категория'
    )
    photo = models.ImageField(
        upload_to='applications/',
        blank=True,
        null=True,
        verbose_name='фото/план помещения'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='новая',
        verbose_name='статус'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='временная метка')

    def __str__(self):
        return f'{self.title} ({self.user.username})'

    class Meta:
        verbose_name = 'заявка'
        verbose_name_plural = 'заявки'
        ordering = ['-created_at']