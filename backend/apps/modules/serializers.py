from rest_framework import serializers

from .models import Module

class ModuleSerializer(serializers.ModelSerializer):
	prerequisites = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
	module_action = serializers.SerializerMethodField()
	module_progress_percent = serializers.SerializerMethodField()
	module_completed_parts = serializers.SerializerMethodField()
	module_total_parts = serializers.SerializerMethodField()

	class Meta:
		model = Module
		fields = [
			'id', 'category', 'title', 'description',
			'status', 'level', 'estimated_time',
			'prerequisites',
			'module_action',
			'module_progress_percent',
			'module_completed_parts',
			'module_total_parts',
			'created_at', 'updated_at'
		]
		read_only_fields = ['id', 'created_at', 'updated_at']

	@staticmethod
	def _read_learning_value(obj, name, default=0):
		return getattr(obj, name, default)

	def get_module_action(self, obj):
		if obj.status == 'coming_soon':
			return 'coming_soon'

		request = self.context.get('request')
		if not request or not request.user.is_authenticated:
			return 'enroll'

		enrolled = bool(self._read_learning_value(obj, 'user_is_enrolled', False))
		progress_percent = int(self._read_learning_value(obj, 'user_progress_percent', 0) or 0)

		if not enrolled and progress_percent <= 0:
			return 'enroll'

		if progress_percent > 0:
			return 'resume'

		return 'start'

	def get_module_progress_percent(self, obj):
		return int(self._read_learning_value(obj, 'user_progress_percent', 0) or 0)

	def get_module_completed_parts(self, obj):
		return int(self._read_learning_value(obj, 'user_completed_parts', 0) or 0)

	def get_module_total_parts(self, obj):
		return int(self._read_learning_value(obj, 'user_total_parts', 0) or 0)
