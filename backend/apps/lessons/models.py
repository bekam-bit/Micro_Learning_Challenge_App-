
from django.db import models
from django.utils import timezone
from apps.categories.models import Category
from apps.modules.models import Module


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Rich text or HTML content")
    video_url = models.URLField(blank=True, null=True, help_text="URL to video explanation")
    video_file = models.FileField(upload_to='videos/', blank=True, null=True, help_text="Upload a video file")
    order = models.PositiveIntegerField(default=0, help_text="Order of lesson in module")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='lessons')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']
        indexes = [
            models.Index(fields=['module', 'title'], name='lesson_module_title_idx'),
            models.Index(fields=['module', 'updated_at'], name='lesson_module_upd_idx'),
        ]

    def __str__(self):
        return self.title