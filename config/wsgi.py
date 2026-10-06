"""
Punto de entrada WSGI: lo usan los servidores web de producción
(Gunicorn, Apache mod_wsgi, etc.) para ejecutar el proyecto.
En el laboratorio no se usa directamente: "python manage.py runserver"
cumple esa función.
"""
import os

from django.core.wsgi import get_wsgi_application

# Le indica a Django qué archivo de configuración usar.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()
