from rest_framework.renderers import BrowsableAPIRenderer


class VistaNavegableRenderer(BrowsableAPIRenderer):
    """Vista navegable de DRF sin el formulario HTML de PUT en la lista.

    En /api/productos/ el PUT necesita el "id" dentro del JSON y ese formulario
    no lo trae, así que en la lista el PUT se hace desde la pestaña "Raw data".
    """

    def get_rendered_html_form(self, data, view, method, request):
        if method == "PUT" and getattr(view, "detail", None) is False:
            return None
        return super().get_rendered_html_form(data, view, method, request)
