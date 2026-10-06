"""
Crea en MySQL la base de datos configurada en settings.py (si no existe).

Uso:  python manage.py crear_base_datos

¿Por qué un comando y no solo el script SQL?
  "python manage.py migrate" crea las TABLAS, pero la BASE DE DATOS tiene que
  existir antes. Este comando la crea usando los mismos datos de conexión de
  settings.py (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT), así funciona en
  cualquier PC sin buscar dónde está instalado mysql.exe (XAMPP, MySQL
  Installer, Linux, etc.). Equivale a docs/crear_base_datos.sql.
"""
import re

import pymysql
from django.conf import settings
# La excepción se importa DIRECTAMENTE desde pymysql.err (y no se usa
# "pymysql.err.OperationalError" más abajo) por un detalle de PyMySQL:
# install_as_MySQLdb() hace que "MySQLdb" sea el mismo objeto que "pymysql".
# Cuando Django carga su backend MySQL importa "MySQLdb.err", y Python vuelve
# a cargar err.py y reemplaza el atributo pymysql.err por esa copia nueva. Desde
# ese momento "pymysql.err.OperationalError" es OTRA clase, distinta de la que
# PyMySQL realmente lanza, y el "except" no la atraparía.
from pymysql.err import OperationalError
from django.core.management.base import BaseCommand, CommandError

# Mensajes claros para los errores de conexión más comunes (código de MySQL).
ERRORES_FRECUENTES = {
    1045: (
        "MySQL rechazó el usuario o la clave. Revisa DB_USER y DB_PASSWORD "
        "(ver DOCUMENTACION.md, sección 'Variables de entorno')."
    ),
    2003: (
        "No se pudo conectar a MySQL. ¿Está iniciado? (XAMPP: botón Start en "
        "MySQL; Windows: servicio MySQL80). Revisa también DB_HOST y DB_PORT."
    ),
}


class Command(BaseCommand):
    help = "Crea en MySQL la base de datos de settings.py si todavía no existe."

    # Este comando se ejecuta ANTES de que exista la base: se desactivan los
    # chequeos automáticos de Django para que no intente conectarse a ella.
    requires_system_checks = []

    def handle(self, *args, **opciones):
        bd = settings.DATABASES["default"]
        if "mysql" not in bd["ENGINE"]:
            self.stdout.write("La base configurada no es MySQL (USE_SQLITE=1): no hay nada que crear.")
            return

        nombre = bd["NAME"]
        # El nombre de una base de datos no se puede pasar como parámetro (%s)
        # en SQL, así que se valida que solo tenga letras, números y "_" para
        # evitar inyección SQL.
        if not re.fullmatch(r"[A-Za-z0-9_]+", nombre):
            raise CommandError(f"Nombre de base de datos no válido: {nombre!r}")

        try:
            # Se conecta al servidor SIN indicar base (todavía no existe).
            conexion = pymysql.connect(
                host=bd["HOST"] or "127.0.0.1",
                port=int(bd["PORT"] or 3306),
                user=bd["USER"],
                password=bd["PASSWORD"],
                charset="utf8mb4",
            )
        except OperationalError as error:
            codigo = error.args[0] if error.args else None
            ayuda = ERRORES_FRECUENTES.get(codigo, "")
            raise CommandError(f"{error}\n{ayuda}".strip())

        with conexion:
            with conexion.cursor() as cursor:
                # IF NOT EXISTS: si ya existe no hace nada (se puede repetir sin problema).
                # utf8mb4 + utf8mb4_unicode_ci: tildes, ñ, y comparaciones sin
                # distinguir mayúsculas (igual que la validación del nombre).
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{nombre}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
        self.stdout.write(self.style.SUCCESS(
            f"Base de datos '{nombre}' lista en {bd['HOST']}:{bd['PORT']} (usuario {bd['USER']})."
        ))
