import os
import pytest

# Configure Django settings before importing anything else
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Set up an in-memory SQLite database for testing BEFORE django.setup()
from django.conf import settings
settings.DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

import django
django.setup()
