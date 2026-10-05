from django.contrib import admin
from django.urls import include, path, re_path

from productos.views import cliente_rest, error_404_json

urlpatterns = [
    path("admin/", admin.site.urls),
    # API REST (ViewSet + Router)
    path("api/", include("productos.urls")),
    # Cualquier otra ruta bajo /api/ responde 404 en JSON (también con DEBUG=True)
    re_path(r"^api/", error_404_json),
    # Cliente REST web propio que consume la API con fetch()
    path("", cliente_rest, name="cliente-rest"),
]

# Cualquier URL inexistente responde con JSON (cuando DEBUG=False)
handler404 = error_404_json
