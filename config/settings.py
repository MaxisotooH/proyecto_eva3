"""
Configuración del proyecto "tienda_api" (Evaluación 3 - Programación Backend).

Este archivo es el "panel de control" de Django: aquí se declaran las
aplicaciones instaladas, la base de datos, el idioma, la configuración de
Django REST Framework (DRF), etc.

Los valores sensibles o que cambian de un PC a otro (clave de MySQL, modo
DEBUG, etc.) se leen desde VARIABLES DE ENTORNO con os.environ.get(...).
Si la variable no existe, se usa el valor por defecto (pensado para XAMPP:
usuario root sin clave). Así el mismo código funciona en cualquier PC sin
tener que editarlo. Ver DOCUMENTACION.md, sección "Variables de entorno".
"""
import os
from pathlib import Path

# Carpeta raíz del proyecto (la que contiene manage.py).
# __file__ = config/settings.py -> .parent = config/ -> .parent = proyecto_eva3/
BASE_DIR = Path(__file__).resolve().parent.parent


def _variable_booleana(nombre, por_defecto):
    """
    Lee una variable de entorno y la interpreta como verdadero/falso.

    Las variables de entorno siempre son texto, por eso "0", "false" o "no"
    se convierten a False y "1", "true" o "si" a True.
    """
    valor = os.environ.get(nombre)
    if valor is None:
        return por_defecto
    return valor.strip().lower() in ("1", "true", "si", "sí", "yes", "on")


# ---------------------------------------------------------------------------
# Seguridad
# ---------------------------------------------------------------------------
# SECRET_KEY: clave que Django usa para firmar cookies y tokens.
# En producción DEBE venir de una variable de entorno y ser secreta; el valor
# por defecto solo sirve para desarrollo en el laboratorio.
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-eva3-backend-cambiar-en-produccion",
)

# DEBUG=True muestra páginas de error detalladas y sirve los archivos CSS del
# admin y de la vista navegable de DRF. Es lo que se quiere en el laboratorio,
# por eso el valor por defecto es True. En un servidor real: DJANGO_DEBUG=0.
DEBUG = _variable_booleana("DJANGO_DEBUG", True)

# ALLOWED_HOSTS: nombres de dominio/IP desde los que se acepta el servidor.
# Por defecto solo el propio PC. Para abrir la API desde otro equipo de la red,
# definir por ejemplo:  DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,192.168.1.50
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost,[::1]").split(",")
    if host.strip()
]

# ---------------------------------------------------------------------------
# Aplicaciones
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    # Aplicaciones que trae Django (admin, usuarios, sesiones, etc.)
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Terceros: Django REST Framework, la librería que convierte Django en una API REST
    "rest_framework",
    # Propias: la app con el modelo Producto y la API
    "productos",
]

# Middleware: "capas" por las que pasa cada petición antes de llegar a la vista
# (seguridad, sesiones, CSRF, autenticación del admin, etc.). Son los de fábrica.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Archivo donde están las rutas principales del proyecto.
ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        # APP_DIRS=True: busca plantillas en <app>/templates/ (ej. productos/templates/)
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Base de datos MySQL
# ---------------------------------------------------------------------------
# El conector es PyMySQL (ver config/__init__.py), por eso el ENGINE sigue
# siendo el oficial de Django para MySQL: "django.db.backends.mysql".
# Funciona igual con MySQL 8 y con MariaDB (la que trae XAMPP).
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        # Nombre de la base de datos (se crea con: python manage.py crear_base_datos)
        "NAME": os.environ.get("DB_NAME", "tienda_api"),
        # Usuario y clave de MySQL. XAMPP trae "root" sin clave; si tu MySQL
        # tiene clave, defínela con la variable de entorno DB_PASSWORD.
        "USER": os.environ.get("DB_USER", "root"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        # Se usa 127.0.0.1 y NO "localhost": en Windows "localhost" puede
        # resolverse a IPv6 (::1) y no llegar al servidor MySQL.
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", "3306"),
        "OPTIONS": {
            # utf8mb4: guarda correctamente tildes, ñ y emojis.
            "charset": "utf8mb4",
            # Modo estricto: MySQL rechaza datos inválidos en vez de "arreglarlos"
            # en silencio (por ejemplo, cortar un texto demasiado largo).
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Solo para correr las pruebas o ver el proyecto SIN MySQL:  USE_SQLITE=1
# (la evaluación se presenta siempre con MySQL).
if _variable_booleana("USE_SQLITE", False):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Reglas de las contraseñas de los usuarios del admin (las de fábrica).
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internacionalización
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "es-cl"          # mensajes de Django y DRF en español
TIME_ZONE = "America/Santiago"   # hora de Chile
USE_I18N = True
USE_TZ = True                    # las fechas se guardan en UTC y se muestran en hora local

STATIC_URL = "static/"
# Tipo de la clave primaria automática "id" (entero grande, BIGINT en MySQL).
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    # Renderers: cómo se "dibuja" la respuesta.
    #   - JSONRenderer: JSON puro (Postman, fetch, curl...).
    #   - VistaNavegableRenderer: página HTML de DRF para probar en el navegador.
    # DRF elige uno según la cabecera "Accept" de la petición.
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "productos.renderers.VistaNavegableRenderer",
    ],
    # API abierta (sin login) para la demostración con Postman / Thunder Client.
    # Al no haber autenticación por sesión, DRF tampoco exige token CSRF.
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    # Todos los errores (400, 404, 405, 500...) salen con el mismo formato JSON.
    "EXCEPTION_HANDLER": "productos.exceptions.manejador_excepciones_json",
    # Paginación OPCIONAL: solo se activa si se envía ?por_pagina=N
    # (ver productos/paginacion.py). Sin ese parámetro se listan todos.
    "DEFAULT_PAGINATION_CLASS": "productos.paginacion.PaginacionOpcional",
}
