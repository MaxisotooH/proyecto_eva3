"""
Manejador global de errores de la API.

Requisito del enunciado: "Cada endpoint debe devolver un JSON ya sea para
éxito o fracaso". DRF ya responde JSON en sus errores, pero cada uno con una
forma distinta ({"detail": ...}, {"campo": [...]}, etc.). Este archivo hace
que TODOS los errores salgan con el MISMO formato:

{
    "ok": false,
    "status": 404,
    "codigo": "NO_ENCONTRADO",
    "mensaje": "Texto legible para el usuario",
    "errores": {...}            <- detalle por campo (vacío si no aplica)
}

Se activa en settings.py:  REST_FRAMEWORK["EXCEPTION_HANDLER"].
"""
import logging

from django.conf import settings
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

# Logger: escribe los errores inesperados en la consola del servidor
# (con el traceback completo), para que el programador pueda revisarlos.
logger = logging.getLogger(__name__)

# Código de texto por defecto para cada estado HTTP.
CODIGOS = {
    400: "DATOS_INVALIDOS",
    404: "NO_ENCONTRADO",
    405: "METODO_NO_PERMITIDO",
    409: "CONFLICTO",
    415: "TIPO_NO_SOPORTADO",
    500: "ERROR_INTERNO",
}


def respuesta_error(mensaje, http_status, errores=None, codigo=None):
    """Arma la respuesta JSON de error estándar (también se usa en views.py)."""
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


def _detalle_interno(exc):
    """
    Detalle técnico de un error inesperado.

    Solo se muestra con DEBUG=True (desarrollo). Con DEBUG=False se oculta:
    los mensajes internos (nombres de tablas, consultas SQL, rutas de
    archivos...) le dan pistas a un atacante y no le sirven al usuario.
    El detalle completo queda igualmente en la consola del servidor (logger).
    """
    return {"detalle": str(exc)} if settings.DEBUG else {}


def manejador_excepciones_json(exc, context):
    """
    DRF llama a esta función cada vez que una vista lanza una excepción.

    exc     -> la excepción (NotFound, ValidationError, IntegrityError...)
    context -> datos de la petición (vista, request, etc.)
    """
    # 1) Primero se deja que DRF procese sus propias excepciones
    #    (400 validación, 404, 405, 415, JSON mal formado...).
    response = exception_handler(exc, context)

    if response is not None:
        datos = response.data
        if isinstance(datos, dict) and set(datos.keys()) == {"detail"}:
            # Errores simples: {"detail": "No encontrado."}
            mensaje, errores = str(datos["detail"]), {}
        else:
            # Errores de validación: {"precio": ["..."], "nombre": ["..."]}
            mensaje, errores = "Los datos enviados no son válidos.", datos
        return respuesta_error(mensaje, response.status_code, errores)

    # 2) Error de la base de datos por una restricción (por ejemplo, dos
    #    peticiones simultáneas que crean el mismo nombre "unique").
    if isinstance(exc, IntegrityError):
        logger.warning("Conflicto de integridad en la base de datos: %s", exc)
        return respuesta_error(
            "La operación viola una restricción de la base de datos.",
            status.HTTP_409_CONFLICT,
            _detalle_interno(exc),
        )

    # 3) Cualquier otro error inesperado: se registra en la consola y se
    #    responde un 500 en JSON (nunca una página HTML).
    logger.exception("Error no controlado en la API")
    return respuesta_error(
        "Ocurrió un error interno en el servidor.",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        _detalle_interno(exc),
    )
