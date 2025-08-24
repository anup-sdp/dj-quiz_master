# users, models.py:
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from uuid import uuid4  # Universally Unique Identifiers, uuid4 is a common choice as it generates random UUIDs


class CustomUser(AbstractUser):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{3,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.") # min 3 digit
    USER_TYPES = (("admin", "Admin"), ("user", "End User"))
    user_type = models.CharField(max_length=10, choices= USER_TYPES, default="user")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    bio = models.TextField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False) # ---
    email_verification_token = models.UUIDField(default=uuid4, editable=False) # ---
    #profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.user_type = 'admin'
        if not self.pk:  # only for new users
            self.is_active = True # set True by activation email.                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
