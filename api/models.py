from django.contrib.auth.models import AbstractUser
from django.db import models


class Player(AbstractUser):
    level = models.PositiveSmallIntegerField(default=1)
    xp = models.PositiveSmallIntegerField(default=0)
    score = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Player'
        verbose_name_plural = 'Players'