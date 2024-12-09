import os
from django.core.wsgi import get_wsgi_application
from corsheaders.middleware import CorsMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queue_management.settings')

application = get_wsgi_application()
application = CorsMiddleware(application)

