import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()
admin = User.objects.filter(username='admin_user_test_redirect').first()
if not admin:
    admin = User.objects.create_user(
        username='admin_user_test_redirect', 
        email='admintest@test.com', 
        password='pass', 
        role='admin',
        is_staff=True
    )

client = APIClient()
client.force_authenticate(user=admin)

response = client.post('/api/categories/', {
    'name': 'Test Redirect',
    'slug': 'test-redirect',
    'description': 'Test',
    'icon': 'test',
    'display_order': 1,
    'is_active': True,
}, format='json')

print('Status:', response.status_code)
if response.status_code == 301:
    location = response.get('Location', 'No location header')
    print('Location:', location)
if hasattr(response, 'data'):
    print('Response data:', response.data)
else:
    print('Response content:', response.content[:200])
