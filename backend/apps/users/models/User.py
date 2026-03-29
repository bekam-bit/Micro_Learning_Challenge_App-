from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_ADMIN = "admin"
    ROLE_LEARNER = "learner"

    ROLE_CHOICES = (
        (ROLE_ADMIN, "Admin"),
        (ROLE_LEARNER, "Learner"),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_LEARNER)
    date_joined = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.ROLE_ADMIN
            self.is_staff = True
        elif self.role == self.ROLE_ADMIN:
            self.is_staff = True
        else:
            self.is_staff = False

        super().save(*args, **kwargs)
   
    def __str__(self) -> str:
        return self.username
