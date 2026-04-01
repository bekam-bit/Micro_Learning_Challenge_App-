from rest_framework import serializers

from .models import Module

class ModuleSerializer(serializers.ModelSerializer):
	prerequisites = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

	class Meta:
		model = Module
		fields = [
			'id', 'category', 'title', 'description',
			'status', 'level', 'estimated_time',
			'prerequisites',
			'created_at', 'updated_at'
		]
		read_only_fields = ['id', 'created_at', 'updated_at']
