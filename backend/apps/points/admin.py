from django.contrib import admin

from .models import PointTransaction


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'points', 'source_type', 'source_id', 'created_at')
    list_filter = ('source_type', 'created_at')
    search_fields = ('user__username', 'user__email', 'reason')
