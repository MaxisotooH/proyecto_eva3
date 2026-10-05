from rest_framework.routers import DefaultRouter, Route

from .views import ProductoViewSet


class ProductoRouter(DefaultRouter):
    """
    Router de DRF con dos ajustes:
    1. La barra final es opcional: sirven /api/productos/4 y /api/productos/4/
    2. La ruta de lista también acepta PUT y DELETE con el "id" en el JSON
       (el enunciado pide "PUT Productos/" con el id en el cuerpo).
    """

    routes = [
        ruta._replace(
            mapping={
                **ruta.mapping,
                "put": "actualizar_por_json",
                "delete": "eliminar_por_json",
            }
        )
        if isinstance(ruta, Route) and ruta.name == "{basename}-list"
        else ruta
        for ruta in DefaultRouter.routes
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = "/?"


router = ProductoRouter()
router.register(r"productos", ProductoViewSet, basename="producto")

urlpatterns = router.urls
