from rest_framework import serializers

from apps.modules.models import Module

from .models import Category


class ModuleSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["id", "title", "description"]


class CategoryListSerializer(serializers.ModelSerializer):
    module_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "icon", "module_count"]


class CategoryDetailSerializer(serializers.ModelSerializer):
    modules = ModuleSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "icon", "modules"]


class CategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "icon", "display_order", "is_active"]
