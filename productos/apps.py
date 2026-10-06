"""Configuración de la app "productos" (Django la registra al iniciar)."""
from django.apps import AppConfig


class ProductosConfig(AppConfig):
    name = "productos"
    # Nombre con que aparece la app en el panel de administración.
    verbose_name = "Gestión de Productos"
