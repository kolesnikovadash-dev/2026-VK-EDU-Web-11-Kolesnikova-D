from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE,
        verbose_name='пользователь',
    )
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name='аватар',
    )

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'профиль'
        verbose_name_plural = 'профили'