from django.contrib import admin

from .models import Producto

admin.site.site_header = "Tienda API · Administración"
admin.site.site_title = "Tienda API"
admin.site.index_title = "Mantención de datos"


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "categoria", "precio", "stock", "activo", "fecha_actualizacion")
    list_display_links = ("id", "nombre")
    list_editable = ("precio", "stock", "activo")
    list_filter = ("categoria", "activo", "fecha_creacion")
    search_fields = ("nombre", "descripcion")
    ordering = ("id",)
    list_per_page = 20
    readonly_fields = ("fecha_creacion", "fecha_actualizacion")
    fieldsets = (
        ("Datos del producto", {"fields": ("nombre", "descripcion", "categoria")}),
        ("Inventario y precio", {"fields": ("precio", "stock", "activo")}),
        ("Auditoría", {"fields": ("fecha_creacion", "fecha_actualizacion"), "classes": ("collapse",)}),
    )
    actions = ("activar", "desactivar")

    @admin.action(description="Activar productos seleccionados")
    def activar(self, request, queryset):
        actualizados = queryset.update(activo=True)
        self.message_user(request, f"{actualizados} producto(s) activado(s).")

    @admin.action(description="Desactivar productos seleccionados")
    def desactivar(self, request, queryset):
        actualizados = queryset.update(activo=False)
        self.message_user(request, f"{actualizados} producto(s) desactivado(s).")
