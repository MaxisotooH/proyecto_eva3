"""
Renderer de la "vista navegable" de DRF.

Un RENDERER decide cómo se dibuja la respuesta. DRF trae, entre otros:
  - JSONRenderer: JSON puro (lo que reciben Postman, fetch, curl...).
  - BrowsableAPIRenderer: una página HTML con la respuesta y formularios para
    probar POST/PUT/DELETE desde el navegador (como la Figura 2 del enunciado).

DRF elige uno según la cabecera "Accept" de la petición: el navegador pide
text/html y Postman pide application/json.
Se activa en settings.py: REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"].
"""
from rest_framework.renderers import BrowsableAPIRenderer


class VistaNavegableRenderer(BrowsableAPIRenderer):
    """
    Vista navegable de DRF, pero SIN el formulario de PUT ni el botón DELETE en la lista.

    Motivo: en /api/productos/ el PUT y el DELETE necesitan el "id" dentro del
    JSON. El formulario HTML de DRF no tiene ese campo (el id es de solo
    lectura) y el botón rojo DELETE envía la petición sin cuerpo, así que
    ambos siempre responderían 400. En la lista, esas dos operaciones se hacen
    desde la pestaña "Raw data" (o desde Postman); en el detalle
    (/api/productos/4/) el formulario PUT y el botón DELETE se ven normales.
    """

    def get_rendered_html_form(self, data, view, method, request):
        # view.detail es False en la lista (/api/productos/).
        if method in ("PUT", "DELETE") and getattr(view, "detail", None) is False:
            return None  # None = no dibujar ese formulario / botón
        # En cualquier otro caso, comportamiento normal de DRF.
        return super().get_rendered_html_form(data, view, method, request)
