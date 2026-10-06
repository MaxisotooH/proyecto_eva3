from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnDict

from .exceptions import respuesta_error
from .models import Producto
from .serializers import ProductoSerializer


def respuesta_ok(mensaje, data=None, http_status=status.HTTP_200_OK, **extra):
    """Respuesta JSON estándar de éxito."""
    cuerpo = {"ok": True, "status": http_status, "mensaje": mensaje}
    cuerpo.update(extra)
    cuerpo["data"] = data
    serializer = getattr(data, "serializer", None)
    if serializer is not None:
        # Mantiene el serializer para que la vista navegable de DRF rellene el formulario
        cuerpo = ReturnDict(cuerpo, serializer=serializer)
    return Response(cuerpo, status=http_status)


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
    """

    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    # ------------------------------------------------------------------
    # Filtros simples por query params
    # ------------------------------------------------------------------
    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        buscar = params.get("buscar")
        categoria = params.get("categoria")
        activo = params.get("activo")
        if buscar:
            qs = qs.filter(Q(nombre__icontains=buscar) | Q(descripcion__icontains=buscar))
        if categoria:
            qs = qs.filter(categoria__iexact=categoria)
        if activo is not None and activo.lower() in ("true", "1", "false", "0"):
            qs = qs.filter(activo=activo.lower() in ("true", "1"))
        return qs

    # ------------------------------------------------------------------
    # GET
    # ------------------------------------------------------------------
    def list(self, request, *args, **kwargs):
        productos = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(productos, many=True)
        return respuesta_ok(
            "Listado de productos obtenido correctamente.",
            serializer.data,
            total=len(serializer.data),
        )

    def retrieve(self, request, *args, **kwargs):
        producto = self.get_object()  # si no existe -> 404 JSON (exceptions.py)
        return respuesta_ok(
            f"Producto {producto.pk} encontrado.",
            self.get_serializer(producto).data,
        )

    # ------------------------------------------------------------------
    # POST
    # ------------------------------------------------------------------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # incluye validación de nombre único
        self.perform_create(serializer)
        return respuesta_ok(
            "Producto creado correctamente.",
            serializer.data,
            http_status=status.HTTP_201_CREATED,
        )

    # ------------------------------------------------------------------
    # PUT / PATCH con id en la URL
    # ------------------------------------------------------------------
    def update(self, request, *args, **kwargs):
        parcial = kwargs.pop("partial", False)
        producto = self.get_object()
        return self._actualizar(producto, request.data, parcial)

    # ------------------------------------------------------------------
    # PUT /api/productos/  con el id dentro del JSON (requisito del enunciado)
    # ------------------------------------------------------------------
    def actualizar_por_json(self, request, *args, **kwargs):
        producto, error = self._buscar_por_id_en_json(request)
        if error:
            return error
        # Se actualizan solo los campos enviados junto al "id"
        return self._actualizar(producto, request.data, parcial=True)

    def _actualizar(self, producto, datos, parcial):
        serializer = self.get_serializer(producto, data=datos, partial=parcial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return respuesta_ok(
            f"Producto {producto.pk} actualizado correctamente.",
            serializer.data,
        )

    # ------------------------------------------------------------------
    # DELETE
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
        datos = self.get_serializer(producto).data
        producto_id = producto.pk
        producto.delete()
        # Se usa 200 (y no 204) para poder devolver un JSON de confirmación
        return respuesta_ok(f"Producto {producto_id} eliminado correctamente.", datos)

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def _buscar_por_id_en_json(self, request):
        """Obtiene el producto a partir del campo "id" del JSON recibido."""
        datos = request.data
        if not hasattr(datos, "get") or datos.get("id") in (None, ""):
            return None, respuesta_error(
                'Debe enviar el campo "id" del producto en el JSON.',
                status.HTTP_400_BAD_REQUEST,
                {"id": ["Este campo es obligatorio."]},
                codigo="ID_REQUERIDO",
            )
        valor = datos.get("id")
        try:
            # true/false o 1.5 no son ids válidos (int(True) daría 1)
            if isinstance(valor, bool) or (isinstance(valor, float) and not valor.is_integer()):
                raise ValueError
            producto_id = int(valor)
        except (TypeError, ValueError):
            return None, respuesta_error(
                'El campo "id" debe ser un número entero.',
                status.HTTP_400_BAD_REQUEST,
                {"id": ["Debe ser un número entero."]},
                codigo="ID_INVALIDO",
            )
        try:
            return Producto.objects.get(pk=producto_id), None
        except Producto.DoesNotExist:
            return None, respuesta_error(
                f"No existe un producto con id {producto_id}.",
                status.HTTP_404_NOT_FOUND,
                {"id": [f"El producto {producto_id} no existe."]},
                codigo="PRODUCTO_NO_ENCONTRADO",
            )

    def get_object(self):
        """Igual que el original, pero con mensaje propio cuando no existe."""
        try:
            return super().get_object()
        except Http404:
            raise NotFound(f"No existe un producto con id {self.kwargs.get('pk')}.")


# ----------------------------------------------------------------------
# Vistas que no son de la API
# ----------------------------------------------------------------------
def cliente_rest(request):
    """Página HTML que consume la API con fetch() (cliente REST web)."""
    return render(
        request,
        "productos/cliente.html",
        {"categorias": Producto.Categoria.choices},
    )


def error_404_json(request, exception=None):
    """Cualquier ruta inexistente devuelve JSON (activo cuando DEBUG=False)."""
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
