"""
Manejador global de errores: garantiza que TODA respuesta de error de la API
sea un JSON con el mismo formato:

{
    "ok": false,
    "status": 404,
    "codigo": "NO_ENCONTRADO",
    "mensaje": "Texto legible",
    "errores": {...}
}
"""
import logging

from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

CODIGOS = {
    400: "DATOS_INVALIDOS",
    401: "NO_AUTENTICADO",
    403: "PROHIBIDO",
    404: "NO_ENCONTRADO",
    405: "METODO_NO_PERMITIDO",
    409: "CONFLICTO",
    415: "TIPO_NO_SOPORTADO",
    500: "ERROR_INTERNO",
}


def respuesta_error(mensaje, http_status, errores=None, codigo=None):
    """Arma la respuesta JSON de error estándar (se usa también en las vistas)."""
    return Response(
        {
            "ok": False,
            "status": http_status,
            "codigo": codigo or CODIGOS.get(http_status, "ERROR"),
            "mensaje": mensaje,
            "errores": errores or {},
        },
        status=http_status,
    )


def manejador_excepciones_json(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        datos = response.data
        if isinstance(datos, dict) and set(datos.keys()) == {"detail"}:
            mensaje, errores = str(datos["detail"]), {}
        else:
            mensaje, errores = "Los datos enviados no son válidos.", datos
        return respuesta_error(mensaje, response.status_code, errores)

    if isinstance(exc, IntegrityError):
        return respuesta_error(
            "La operación viola una restricción de la base de datos.",
            status.HTTP_409_CONFLICT,
            {"detalle": str(exc)},
        )

    # Cualquier otro error inesperado también responde JSON
    logger.exception("Error no controlado en la API")
    return respuesta_error(
        "Ocurrió un error interno en el servidor.",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        {"detalle": str(exc)},
    )
