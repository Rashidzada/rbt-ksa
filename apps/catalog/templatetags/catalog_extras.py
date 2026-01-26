import re
from django import template

register = template.Library()


@register.filter
def drive_image_url(url):
    """
    Convert Google Drive share URLs to direct image URLs.
    Example: https://drive.google.com/file/d/<id>/view -> https://drive.google.com/uc?export=view&id=<id>
    """
    if not url:
        return url

    if "drive.google.com" not in url:
        return url

    match = re.search(r"/file/d/([a-zA-Z0-9_-]+)", url)
    if not match:
        match = re.search(r"[?&]id=([a-zA-Z0-9_-]+)", url)

    if not match:
        return url

    file_id = match.group(1)
    return f"https://drive.google.com/uc?export=view&id={file_id}"
