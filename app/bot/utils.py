import os

from django.conf import settings


def get_file_path(file_field):
    return os.path.join(settings.BASE_DIR, "media", str(file_field))