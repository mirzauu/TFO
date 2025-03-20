from django.http import HttpResponse, Http404
import requests
from django.conf import settings

def serve_image(request, path):
    s3_url =  f"{settings.SITE_URL}/static/assets/{path}"
    response = requests.get(s3_url)

    if response.status_code == 200:
        # Get the content type from the response headers
        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        return HttpResponse(response.content, content_type=content_type)
    else:
        raise Http404("File not found")
