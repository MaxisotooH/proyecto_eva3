"""
Respuesta del método HTTP OPTIONS.

OPTIONS es el verbo que un cliente usa para preguntar "¿qué puedo hacer en
esta URL?". DRF responde con el nombre del recurso, los formatos aceptados y
la descripción de los campos de cada acción (POST, PUT).

Problema que resuelve este archivo:
  En este proyecto la URL de la LISTA (/api/productos/) también acepta PUT,
  porque el enunciado pide "PUT Productos/" con el id dentro del JSON.
  Para describir un PUT, DRF por defecto busca el objeto con view.get_object(),
  pero en la lista no hay id en la URL, y eso terminaba en un error 500.
  (El error aparecía al presionar el botón OPTIONS de la vista navegable.)

Solución:
  En la lista solo se describe el POST (crear). El PUT, con el detalle de
  sus campos, se ve en el OPTIONS de un producto: /api/productos/4/
Se activa en views.py con: metadata_class = ProductoMetadata
"""
from rest_framework.metadata import SimpleMetadata


class ProductoMetadata(SimpleMetadata):
    def determine_actions(self, request, view):
        # view.detail es True en /api/productos/4/ y False en /api/productos/
        if view.detail:
            # Detalle: comportamiento normal de DRF (describe el PUT).
            return super().determine_actions(request, view)
        # Lista: solo POST. get_serializer_info() arma la descripción de cada
        # campo (tipo, si es obligatorio, largo máximo, opciones, etc.).
        return {"POST": self.get_serializer_info(view.get_serializer())}
