"""
Rutas de la API (se incluyen con el prefijo /api/ en config/urls.py).

¿Qué es un ROUTER?
  Con un ViewSet no se escribe cada ruta a mano: el router de DRF las genera.
  Un DefaultRouter normal crea, para router.register("productos", ...):

    URL                     Verbo    Método del ViewSet
    /api/                   GET      (raíz de la API, "Api Root")
    /api/productos/         GET      list()            listar todos
    /api/productos/         POST     create()          crear
    /api/productos/<id>/    GET      retrieve()        ver uno
    /api/productos/<id>/    PUT      update()          actualizar completo
    /api/productos/<id>/    PATCH    partial_update()  actualizar algunos campos
    /api/productos/<id>/    DELETE   destroy()         eliminar

Este proyecto usa un router PERSONALIZADO (ProductoRouter) con dos ajustes:

  1. El enunciado pide "PUT Productos/" con el id DENTRO del JSON. Por eso la
     ruta de la lista también acepta:
        PUT     /api/productos/   -> actualizar_por_json()
        DELETE  /api/productos/   -> eliminar_por_json()

  2. La barra final es opcional: sirven /api/productos/4 y /api/productos/4/
     (el enunciado escribe "Productos/4", sin barra).
"""
from rest_framework.routers import DefaultRouter, Route

from .views import ProductoViewSet


def _rutas_con_put_y_delete_en_lista():
    """
    Copia las rutas del DefaultRouter y agrega PUT y DELETE a la ruta de la lista.

    DefaultRouter.routes es una lista de "plantillas" de rutas. Cada Route tiene:
      - name:    nombre de la ruta ("{basename}-list" es la de la lista)
      - mapping: diccionario verbo HTTP -> método del ViewSet
                 (en la lista: {"get": "list", "post": "create"})
    """
    rutas = []
    for ruta in DefaultRouter.routes:
        es_ruta_de_lista = isinstance(ruta, Route) and ruta.name == "{basename}-list"
        if es_ruta_de_lista:
            nuevo_mapping = dict(ruta.mapping)                 # copia: {"get": "list", "post": "create"}
            nuevo_mapping["put"] = "actualizar_por_json"       # PUT    /api/productos/
            nuevo_mapping["delete"] = "eliminar_por_json"      # DELETE /api/productos/
            # Route es una "namedtuple" (inmutable): _replace() devuelve una
            # copia con el campo cambiado, sin modificar la original de DRF.
            ruta = ruta._replace(mapping=nuevo_mapping)
        rutas.append(ruta)
    return rutas


class ProductoRouter(DefaultRouter):
    """DefaultRouter con PUT/DELETE en la lista y barra final opcional."""

    # Ajuste 1: las rutas modificadas reemplazan a las de fábrica.
    routes = _rutas_con_put_y_delete_en_lista()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajuste 2: el router arma cada ruta como una expresión regular que
        # termina en self.trailing_slash. "/?" significa "una barra, opcional".
        self.trailing_slash = "/?"


router = ProductoRouter()
# register(prefijo, ViewSet, basename):
#   - "productos": la parte de la URL  -> /api/productos/
#   - basename: prefijo de los nombres de las rutas ("producto-list", "producto-detail")
router.register(r"productos", ProductoViewSet, basename="producto")

# Lista final de rutas que config/urls.py incluye con include("productos.urls").
urlpatterns = router.urls
