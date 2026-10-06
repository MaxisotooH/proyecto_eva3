"""
Vistas de la app "productos".

Una VISTA recibe la petición HTTP (request) y devuelve la respuesta (response).
Aquí está:
  - ProductoViewSet: la API REST (CRUD completo) usando un ViewSet de DRF.
  - cliente_rest:    la página HTML que consume la API con JavaScript.
  - error_404_json:  respuesta JSON para rutas que no existen.

¿Qué es un ViewSet?
  En vez de escribir una vista por cada operación, un ModelViewSet agrupa en
  UNA clase todas las acciones del CRUD: list, retrieve, create, update,
  partial_update y destroy. El router (productos/urls.py) conecta cada verbo
  HTTP + URL con la acción correspondiente.

  En este proyecto se redefinen esas acciones para que TODAS las respuestas
  tengan el mismo formato JSON:  {"ok", "status", "mensaje", "data"}.
"""
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnDict

from .exceptions import respuesta_error
from .metadata import ProductoMetadata
from .models import Producto
from .serializers import ProductoSerializer

# Mayor id posible: el máximo de un BIGINT con signo (2^63 - 1), que es el tipo
# de la columna "id" (BigAutoField). Un id mayor no puede existir, así que se
# responde 404 sin consultar la base de datos. Además evita un error 500 en
# SQLite, que no acepta enteros más grandes que ese.
MAXIMO_ID = 9_223_372_036_854_775_807


def respuesta_ok(mensaje, data=None, http_status=status.HTTP_200_OK, **extra):
    """
    Arma la respuesta JSON estándar de ÉXITO:

        {"ok": true, "status": 200, "mensaje": "...", <extra>, "data": {...}}

    **extra permite agregar campos adicionales, por ejemplo total=8.
    """
    cuerpo = {"ok": True, "status": http_status, "mensaje": mensaje}
    cuerpo.update(extra)
    cuerpo["data"] = data

    # Detalle técnico para la vista navegable de DRF (navegador):
    # serializer.data no es un dict común, sino un "ReturnDict" que recuerda
    # qué serializer lo creó. La vista navegable usa ese dato para rellenar el
    # formulario PUT con los valores actuales del producto. Como aquí "data"
    # queda DENTRO de otro diccionario, se envuelve el cuerpo en un ReturnDict
    # con el mismo serializer para no perder ese comportamiento.
    # Para Postman / JSON no cambia nada: se ve como un diccionario normal.
    serializer = getattr(data, "serializer", None)
    if serializer is not None:
        cuerpo = ReturnDict(cuerpo, serializer=serializer)
    return Response(cuerpo, status=http_status)


def convertir_id(valor):
    """
    Convierte el id recibido (texto o número) a entero.

    Lanza ValueError si no es un entero válido. Casos especiales:
      - True / False: Python permite int(True) == 1, pero no es un id válido.
      - 1.5: int(1.5) daría 1 en silencio; se rechaza. (4.0 sí se acepta.)
    """
    if isinstance(valor, bool) or (isinstance(valor, float) and not valor.is_integer()):
        raise ValueError("id no entero")
    return int(valor)


def id_en_rango(producto_id):
    """True si el id puede existir en la tabla (entre 1 y MAXIMO_ID)."""
    return 1 <= producto_id <= MAXIMO_ID


class ProductoViewSet(viewsets.ModelViewSet):
    """
    API REST de productos (CRUD completo sobre MySQL).

    GET     /api/productos/      -> lista todos los productos
    GET     /api/productos/4     -> devuelve el producto con id 4
    POST    /api/productos/      -> crea un producto (valida nombre único)
    PUT     /api/productos/      -> actualiza el producto cuyo "id" viene en el JSON
    PUT     /api/productos/4     -> actualiza el producto 4
    PATCH   /api/productos/4     -> actualización parcial del producto 4
    DELETE  /api/productos/4     -> elimina el producto 4
    DELETE  /api/productos/      -> elimina el producto cuyo "id" viene en el JSON

    Filtros opcionales en GET lista: ?buscar=texto&categoria=HOGAR&activo=true
    Paginación opcional en GET lista: ?por_pagina=5&pagina=2
    """

    # queryset: registros sobre los que trabaja el ViewSet (todos los productos).
    queryset = Producto.objects.all()
    # serializer_class: cómo se convierten y validan los datos (serializers.py).
    serializer_class = ProductoSerializer
    # metadata_class: respuesta del verbo OPTIONS (ver metadata.py).
    metadata_class = ProductoMetadata

    # ------------------------------------------------------------------
    # Filtros simples por parámetros de la URL (query params)
    # ------------------------------------------------------------------
    def get_queryset(self):
        """
        Productos a listar, aplicando los filtros que vengan en la URL.

        Ej.: /api/productos/?buscar=cafe&categoria=alimentos&activo=true
        """
        qs = super().get_queryset()
        params = self.request.query_params  # diccionario con lo que va tras el "?"
        buscar = params.get("buscar")
        categoria = params.get("categoria")
        activo = params.get("activo")
        if buscar:
            # Q(...) | Q(...) = condición "O": el texto está en el nombre O en la descripción.
            # __icontains = "contiene", sin distinguir mayúsculas.
            qs = qs.filter(Q(nombre__icontains=buscar) | Q(descripcion__icontains=buscar))
        if categoria:
            qs = qs.filter(categoria__iexact=categoria)
        # Solo se filtra si "activo" trae un valor reconocible.
        if activo is not None and activo.lower() in ("true", "1", "false", "0"):
            qs = qs.filter(activo=activo.lower() in ("true", "1"))
        return qs

    # ------------------------------------------------------------------
    # GET /api/productos/   (listar)
    # ------------------------------------------------------------------
    def list(self, request, *args, **kwargs):
        productos = self.filter_queryset(self.get_queryset())

        # paginate_queryset() devuelve None si NO se pidió ?por_pagina=
        # (ver paginacion.py); en ese caso se listan todos.
        pagina = self.paginate_queryset(productos)
        if pagina is not None:
            serializer = self.get_serializer(pagina, many=True)
            pagina_actual = self.paginator.page   # objeto Page de Django
            return respuesta_ok(
                "Listado de productos obtenido correctamente.",
                serializer.data,
                total=pagina_actual.paginator.count,            # total de productos (todas las páginas)
                pagina=pagina_actual.number,                     # número de esta página
                total_paginas=pagina_actual.paginator.num_pages,
                siguiente=self.paginator.get_next_link(),        # URL de la página siguiente (o null)
                anterior=self.paginator.get_previous_link(),     # URL de la página anterior (o null)
            )

        # many=True: se serializa una LISTA de productos, no uno solo.
        serializer = self.get_serializer(productos, many=True)
        return respuesta_ok(
            "Listado de productos obtenido correctamente.",
            serializer.data,
            total=len(serializer.data),
        )

    # ------------------------------------------------------------------
    # GET /api/productos/4   (ver uno)
    # ------------------------------------------------------------------
    def retrieve(self, request, *args, **kwargs):
        producto = self.get_object()  # si no existe -> 404 en JSON (ver get_object)
        return respuesta_ok(
            f"Producto {producto.pk} encontrado.",
            self.get_serializer(producto).data,
        )

    # ------------------------------------------------------------------
    # POST /api/productos/   (crear)
    # ------------------------------------------------------------------
    def create(self, request, *args, **kwargs):
        # request.data: el JSON recibido, ya convertido a diccionario por DRF.
        serializer = self.get_serializer(data=request.data)
        # is_valid(raise_exception=True): si hay errores (incluido el nombre
        # repetido) lanza ValidationError y el manejador responde 400 en JSON.
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)  # serializer.save() -> INSERT en MySQL
        return respuesta_ok(
            "Producto creado correctamente.",
            serializer.data,
            http_status=status.HTTP_201_CREATED,
        )

    # ------------------------------------------------------------------
    # PUT / PATCH /api/productos/4   (actualizar con el id en la URL)
    # ------------------------------------------------------------------
    def update(self, request, *args, **kwargs):
        # DRF llama a update() tanto para PUT como para PATCH.
        # En PATCH (partial_update) llega partial=True: solo se validan y
        # cambian los campos enviados. En PUT se exigen todos los obligatorios.
        parcial = kwargs.pop("partial", False)
        producto = self.get_object()
        return self._actualizar(producto, request.data, parcial)

    # ------------------------------------------------------------------
    # PUT /api/productos/  con el id dentro del JSON (requisito del enunciado)
    # ------------------------------------------------------------------
    def actualizar_por_json(self, request, *args, **kwargs):
        """
        Ejemplo de JSON:  {"id": 4, "precio": 17990, "stock": 35}

        Si el id no existe responde 404 con un JSON de error (requisito).
        """
        producto, error = self._buscar_por_id_en_json(request)
        if error:
            return error
        # Se actualizan solo los campos enviados junto al "id" (parcial),
        # así no es necesario reenviar el producto completo.
        return self._actualizar(producto, request.data, parcial=True)

    def _actualizar(self, producto, datos, parcial):
        """Lógica común de los PUT/PATCH: validar y guardar."""
        # Pasar la instancia (producto) le indica al serializer que es una
        # ACTUALIZACIÓN y no una creación.
        serializer = self.get_serializer(producto, data=datos, partial=parcial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)  # serializer.save() -> UPDATE en MySQL
        return respuesta_ok(
            f"Producto {producto.pk} actualizado correctamente.",
            serializer.data,
        )

    # ------------------------------------------------------------------
    # DELETE /api/productos/4   y   DELETE /api/productos/ {"id": 4}
    # ------------------------------------------------------------------
    def destroy(self, request, *args, **kwargs):
        producto = self.get_object()
        return self._eliminar(producto)

    def eliminar_por_json(self, request, *args, **kwargs):
        producto, error = self._buscar_por_id_en_json(request)
        if error:
            return error
        return self._eliminar(producto)

    def _eliminar(self, producto):
        """Lógica común de los DELETE."""
        # Se guardan los datos ANTES de borrar, para devolverlos en la respuesta.
        datos = self.get_serializer(producto).data
        producto_id = producto.pk
        producto.delete()  # DELETE en MySQL
        # Se responde 200 (y no 204 "sin contenido") para poder devolver un
        # JSON de confirmación, como pide el enunciado.
        return respuesta_ok(f"Producto {producto_id} eliminado correctamente.", datos)

    # ------------------------------------------------------------------
    # OPTIONS (cualquier ruta)
    # ------------------------------------------------------------------
    def options(self, request, *args, **kwargs):
        """
        Respuesta del verbo OPTIONS con el mismo formato que el resto de la API.

        super().options() arma la descripción del recurso usando metadata_class
        (ver metadata.py); aquí solo se envuelve en {"ok", "status", "mensaje", "data"}.
        """
        respuesta = super().options(request, *args, **kwargs)
        return respuesta_ok("Opciones disponibles para esta ruta.", respuesta.data)

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def _buscar_por_id_en_json(self, request):
        """
        Busca el producto usando el campo "id" del JSON recibido.

        Devuelve una tupla (producto, error):
          - si todo va bien:  (producto, None)
          - si hay problema:  (None, respuesta_de_error_en_JSON)
        """
        datos = request.data
        # hasattr(datos, "get"): el JSON debe ser un objeto {...}, no una lista [...].
        if not hasattr(datos, "get") or datos.get("id") in (None, ""):
            return None, respuesta_error(
                'Debe enviar el campo "id" del producto en el JSON.',
                status.HTTP_400_BAD_REQUEST,
                {"id": ["Este campo es obligatorio."]},
                codigo="ID_REQUERIDO",
            )

        try:
            producto_id = convertir_id(datos.get("id"))
        except (TypeError, ValueError):
            return None, respuesta_error(
                'El campo "id" debe ser un número entero.',
                status.HTTP_400_BAD_REQUEST,
                {"id": ["Debe ser un número entero."]},
                codigo="ID_INVALIDO",
            )

        # Un id fuera de rango (0, negativo o gigante) no puede existir:
        # se responde 404 directamente, sin consultar la base de datos.
        producto = None
        if id_en_rango(producto_id):
            producto = Producto.objects.filter(pk=producto_id).first()
        if producto is None:
            return None, respuesta_error(
                f"No existe un producto con id {producto_id}.",
                status.HTTP_404_NOT_FOUND,
                {"id": [f"El producto {producto_id} no existe."]},
                codigo="PRODUCTO_NO_ENCONTRADO",
            )
        return producto, None

    def get_object(self):
        """
        Busca el producto cuyo id viene en la URL (/api/productos/4).

        Es el método original de DRF con dos agregados:
          - un id que no es número o está fuera de rango responde 404 sin
            consultar la base de datos;
          - el mensaje del 404 dice qué id se buscó.
        """
        valor = self.kwargs.get(self.lookup_field)  # lookup_field = "pk"
        try:
            puede_existir = id_en_rango(convertir_id(valor))
        except (TypeError, ValueError):
            puede_existir = False  # ej.: /api/productos/abc

        if puede_existir:
            try:
                return super().get_object()
            except Http404:
                pass  # no existe: se responde el 404 de abajo
        # NotFound es una excepción de DRF: el manejador la convierte en 404 JSON.
        raise NotFound(f"No existe un producto con id {valor}.")


# ----------------------------------------------------------------------
# Vistas que no son de la API
# ----------------------------------------------------------------------
def cliente_rest(request):
    """
    Página HTML que consume la API con fetch() (cliente REST web).

    Requisito: "Debe crear las vistas para consumir los servicios mediante
    cliente REST". Se le pasan las categorías para armar los <select>.
    """
    return render(
        request,
        "productos/cliente.html",
        {"categorias": Producto.Categoria.choices},
    )


def error_404_json(request, exception=None):
    """
    Respuesta 404 en JSON para rutas que no existen.

    Se usa en config/urls.py para cualquier ruta /api/... desconocida, y como
    handler404 de todo el sitio cuando DEBUG=False. Es una vista de Django
    "normal" (no de DRF), por eso usa JsonResponse en vez de Response.
    """
    return JsonResponse(
        {
            "ok": False,
            "status": 404,
            "codigo": "RUTA_NO_ENCONTRADA",
            "mensaje": f"La ruta '{request.path}' no existe.",
            "errores": {},
        },
        status=404,
    )
