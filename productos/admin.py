"""
Configuración del panel de administración de Django (/admin/).

El admin permite mantener los datos (crear, listar, editar y borrar productos)
desde el navegador, sin escribir código. Se ingresa con un superusuario
(python manage.py preparar_demo crea admin / admin123).
"""
from django.contrib import admin

from .models import Producto

# Textos del encabezado y del título del panel.
admin.site.site_header = "Tienda API · Administración"
admin.site.site_title = "Tienda API"
admin.site.index_title = "Mantención de datos"


# @admin.register(Producto) equivale a: admin.site.register(Producto, ProductoAdmin)
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Columnas que se ven en el listado.
    list_display = ("id", "nombre", "categoria", "precio", "stock", "activo", "fecha_actualizacion")
    # Columnas que funcionan como enlace para abrir el producto.
    list_display_links = ("id", "nombre")
    # Columnas que se pueden editar directamente en el listado (botón "Guardar").
    list_editable = ("precio", "stock", "activo")
    # Filtros del panel lateral derecho.
    list_filter = ("categoria", "activo", "fecha_creacion")
    # Campos en los que busca la caja de búsqueda.
    search_fields = ("nombre", "descripcion")
    ordering = ("id",)
    list_per_page = 20
    # Las fechas las pone el sistema: se muestran, pero no se pueden editar.
    readonly_fields = ("fecha_creacion", "fecha_actualizacion")
    # Agrupación de los campos en el formulario de edición.
    fieldsets = (
        ("Datos del producto", {"fields": ("nombre", "descripcion", "categoria")}),
        ("Inventario y precio", {"fields": ("precio", "stock", "activo")}),
        # "collapse": sección plegada por defecto.
        ("Auditoría", {"fields": ("fecha_creacion", "fecha_actualizacion"), "classes": ("collapse",)}),
    )
    # Acciones masivas del menú "Acción" (sobre los productos marcados).
    actions = ("activar", "desactivar")

    @admin.action(description="Activar productos seleccionados")
    def activar(self, request, queryset):
        # queryset = productos marcados; update() modifica todos en una sola consulta.
        actualizados = queryset.update(activo=True)
        self.message_user(request, f"{actualizados} producto(s) activado(s).")

    @admin.action(description="Desactivar productos seleccionados")
    def desactivar(self, request, queryset):
        actualizados = queryset.update(activo=False)
        self.message_user(request, f"{actualizados} producto(s) desactivado(s).")
