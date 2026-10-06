"""
Paginación OPCIONAL de la lista de productos.

Paginar = entregar la lista "por partes" (páginas) en vez de todo de una vez.
Es útil cuando la tabla crece: el cliente pide, por ejemplo, de a 5 productos.

Cómo se usa (en GET /api/productos/):
    /api/productos/                       -> TODOS los productos (sin paginar)
    /api/productos/?por_pagina=5          -> primeros 5 (página 1)
    /api/productos/?por_pagina=5&pagina=2 -> productos 6 al 10

La paginación solo se activa si se envía "por_pagina". Así el GET que pide el
enunciado ("devuelve todos los productos") sigue funcionando igual.
Se activa para toda la API en settings.py: REST_FRAMEWORK["DEFAULT_PAGINATION_CLASS"].
"""
from rest_framework.pagination import PageNumberPagination


class PaginacionOpcional(PageNumberPagination):
    # page_size=None: SIN "por_pagina" en la URL no se pagina (se listan todos).
    page_size = None
    # Nombre del parámetro con el número de página (?pagina=2).
    page_query_param = "pagina"
    # Nombre del parámetro con la cantidad por página (?por_pagina=5).
    page_size_query_param = "por_pagina"
    # Tope de seguridad: aunque pidan ?por_pagina=100000, se entregan 100.
    max_page_size = 100
    # Mensaje si piden una página que no existe (?pagina=999) -> 404 en JSON.
    invalid_page_message = "La página solicitada no existe."
