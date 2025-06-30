"""
Backblaze B2 settings for the R1D3 system.
Import this file in settings.py to enable Backblaze B2 storage.
"""
import os

# Backblaze B2 Settings
BACKBLAZE_ACCESS_KEY = os.environ.get('BACKBLAZE_ACCESS_KEY', '')
BACKBLAZE_SECRET_KEY = os.environ.get('BACKBLAZE_SECRET_KEY', '')
BACKBLAZE_BUCKET_NAME = os.environ.get('BACKBLAZE_BUCKET_NAME', '')
BACKBLAZE_REGION = os.environ.get('BACKBLAZE_REGION', 'us-west-002')
BACKBLAZE_CUSTOM_DOMAIN = os.environ.get('BACKBLAZE_CUSTOM_DOMAIN', None)

# Media files location within the bucket
MEDIA_LOCATION = 'media'

# Storage settings
DEFAULT_FILE_STORAGE = 'company_system.storage_backends.MediaStorage'

# URL that handles the media served from Backblaze B2
if BACKBLAZE_CUSTOM_DOMAIN:
    MEDIA_URL = f'https://{BACKBLAZE_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/'
else:
    MEDIA_URL = f'https://s3.{BACKBLAZE_REGION}.backblazeb2.com/{BACKBLAZE_BUCKET_NAME}/{MEDIA_LOCATION}/'
