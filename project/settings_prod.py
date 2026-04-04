"""
Production settings for Talant №1
"""
from .settings import *
import os

# ─── SECURITY ──────────────────────────────────────────────
DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'change-me-to-a-random-50-char-string')

ALLOWED_HOSTS = ['talant.inbrain.kz', 'www.talant.inbrain.kz', '89.46.33.230']

# ─── STATIC & MEDIA ──────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ─── CSRF ────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = [
    'https://talant.inbrain.kz',
    'http://talant.inbrain.kz',
]
