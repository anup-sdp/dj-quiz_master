# users, models.py:
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{3,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.") # min 3 digit
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    bio = models.TextField(null=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.pk:  # only for new users
            self.is_active = False  # set True by activation email.
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
