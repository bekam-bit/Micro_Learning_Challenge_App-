from django.db import models

from apps.categories.models import Category


class Module(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("coming_soon", "Coming Soon"),
    ]
    LEVEL_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("expert", "Expert"),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=150)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner")
    estimated_time = models.PositiveIntegerField(default=0, help_text="Estimated time to complete in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='dependent_modules', help_text="Modules that must be completed before this one")

    class Meta:
        ordering = ['title']
        unique_together = ('category', 'title')

    def __str__(self):
        return self.title
