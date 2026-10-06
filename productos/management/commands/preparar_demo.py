"""
Deja la base lista para la demostración (se puede repetir las veces que se quiera):
  - borra todos los productos y vuelve a cargar los 8 del fixture (ids 1 al 8),
  - reinicia el contador de ids para que el próximo producto creado sea el 9,
  - crea el usuario administrador si no existe.

Uso:  python manage.py preparar_demo
      python manage.py preparar_demo --usuario profe --clave otraclave
"""
import os

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection, transaction

from productos.models import Producto


class Command(BaseCommand):
    help = "Reinicia los productos de ejemplo y crea el usuario admin para la demo."

    def add_arguments(self, parser):
        parser.add_argument("--usuario", default=os.environ.get("DEMO_ADMIN_USER", "admin"))
        parser.add_argument("--clave", default=os.environ.get("DEMO_ADMIN_PASSWORD", "admin123"))

    def handle(self, *args, **opciones):
        with transaction.atomic():
            borrados, _ = Producto.objects.all().delete()
            call_command("loaddata", "productos", verbosity=0)
        self._reiniciar_contador_ids()
        total = Producto.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"Productos reiniciados: {borrados} borrados, {total} cargados del fixture."
        ))

        User = get_user_model()
        usuario, clave = opciones["usuario"], opciones["clave"]
        if User.objects.filter(username=usuario).exists():
            self.stdout.write(f"El usuario admin '{usuario}' ya existe (no se modificó).")
        else:
            User.objects.create_superuser(username=usuario, email="", password=clave)
            self.stdout.write(self.style.SUCCESS(
                f"Usuario admin creado -> usuario: {usuario}  clave: {clave}"
            ))

    def _reiniciar_contador_ids(self):
        siguiente = (Producto.objects.order_by("-id").values_list("id", flat=True).first() or 0) + 1
        tabla = Producto._meta.db_table
        with connection.cursor() as cursor:
            if connection.vendor == "mysql":
                cursor.execute(f"ALTER TABLE `{tabla}` AUTO_INCREMENT = {siguiente}")
            elif connection.vendor == "sqlite":
                cursor.execute("UPDATE sqlite_sequence SET seq = %s WHERE name = %s", [siguiente - 1, tabla])
