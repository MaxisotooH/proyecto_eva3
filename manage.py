#!/usr/bin/env python
"""
Utilidad de línea de comandos de Django.

Ejemplos de uso (con el entorno virtual activado):
    python manage.py crear_base_datos   -> crea la base "tienda_api" en MySQL
    python manage.py migrate            -> crea las tablas a partir de los modelos
    python manage.py preparar_demo      -> carga los productos de ejemplo y el admin
    python manage.py runserver          -> levanta el servidor en http://127.0.0.1:8000/
    python manage.py test productos     -> ejecuta las pruebas automáticas
"""
import os
import sys

# Versiones de Python compatibles con Django 4.2 (desde 3.10 hasta 3.12).
# Con Python 3.13 o superior, Django 4.2 falla al dibujar plantillas: el admin
# y la vista navegable de DRF responden con error. Ver DOCUMENTACION.md.
PYTHON_MINIMO = (3, 10)
PYTHON_MAXIMO = (3, 12)


def revisar_version_python():
    """Detiene el programa con un mensaje claro si la versión de Python no sirve."""
    actual = sys.version_info[:2]
    if not PYTHON_MINIMO <= actual <= PYTHON_MAXIMO:
        sys.exit(
            f"ERROR: este proyecto necesita Python 3.10, 3.11 o 3.12 "
            f"(estás usando Python {actual[0]}.{actual[1]}).\n"
            "Crea el entorno virtual con una versión compatible, por ejemplo:\n"
            "    py -3.12 -m venv venv\n"
            "Ver DOCUMENTACION.md, sección 'Instalación paso a paso'."
        )


def main():
    revisar_version_python()
    # Le indica a Django qué archivo de configuración usar.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Activaste el entorno virtual e "
            "instalaste requirements.txt?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
