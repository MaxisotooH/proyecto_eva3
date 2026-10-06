"""
Rutas principales del proyecto (el "índice" de URLs).

Django revisa esta lista de ARRIBA hacia ABAJO y usa la primera ruta que
coincide con la URL pedida. Por eso el orden importa:

    /admin/...           -> panel de administración de Django
    /api/...             -> API REST (rutas definidas en productos/urls.py)
    /api/<otra cosa>     -> 404 en JSON (la API nunca responde HTML)
    /                    -> cliente REST web (página que consume la API)
"""
from django.contrib import admin
from django.urls import include, path, re_path

from productos.views import cliente_rest, error_404_json

urlpatterns = [
    # Panel de administración: http://127.0.0.1:8000/admin/
    path("admin/", admin.site.urls),
    # API REST: include() "anexa" las rutas que genera el router del ViewSet
    # (productos/urls.py), todas con el prefijo /api/.
    path("api/", include("productos.urls")),
    # Si la URL empieza con /api/ pero no coincidió con ninguna ruta anterior,
    # se responde un 404 en JSON. Sin esto, con DEBUG=True Django mostraría
    # su página de error en HTML, que un cliente REST no sabe leer.
    re_path(r"^api/", error_404_json),
    # Página principal: cliente REST web hecho con HTML + JavaScript (fetch).
    path("", cliente_rest, name="cliente-rest"),
]

# handler404: vista que Django usa para CUALQUIER URL inexistente, pero solo
# cuando DEBUG=False (con DEBUG=True Django muestra su página de depuración).
handler404 = error_404_json
