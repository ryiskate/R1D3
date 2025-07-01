"""
Storage backends for the R1D3 system.
Configures Backblaze B2 for media file storage using boto3 and django-storages.
"""
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class BackblazeB2Storage(S3Boto3Storage):
    """
    Storage backend for Backblaze B2.
    Uses the S3 compatible API provided by Backblaze.
    """
    access_key = settings.BACKBLAZE_ACCESS_KEY
    secret_key = settings.BACKBLAZE_SECRET_KEY
    bucket_name = settings.BACKBLAZE_BUCKET_NAME
    endpoint_url = f"https://s3.{settings.BACKBLAZE_REGION}.backblazeb2.com"
    region_name = settings.BACKBLAZE_REGION
    custom_domain = settings.BACKBLAZE_CUSTOM_DOMAIN if hasattr(settings, 'BACKBLAZE_CUSTOM_DOMAIN') else None
    file_overwrite = False
    default_acl = 'public-read'
    querystring_auth = False  # Don't add authentication to URLs


class MediaStorage(BackblazeB2Storage):
    """
    Storage backend for media files (user uploads).
    """
    location = settings.MEDIA_LOCATION
