"""
Pruebas automáticas de la API.

Una prueba automática es código que llama a la API y COMPRUEBA (assert) que la
respuesta sea la esperada. Si alguien rompe algo, la prueba falla y avisa.

Cómo ejecutarlas (con el entorno virtual activado):
  Con MySQL:          python manage.py test productos
  Sin MySQL (rápido): set USE_SQLITE=1 && python manage.py test productos   (cmd)
                      $env:USE_SQLITE=1; python manage.py test productos    (PowerShell)

Django crea una base de datos TEMPORAL (test_tienda_api) y la borra al final:
las pruebas nunca tocan los datos reales.
"""
import importlib
import warnings
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TransactionTestCase, override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from .exceptions import manejador_excepciones_json
from .models import Producto

URL = "/api/productos/"


class ProductoAPITest(APITestCase):
    """CRUD completo de la API (requisitos del enunciado)."""

    def setUp(self):
        # setUp() se ejecuta ANTES de cada prueba: deja 2 productos conocidos.
        self.p1 = Producto.objects.create(nombre="Teclado", precio=15000, stock=5, categoria="ELECTRONICA")
        self.p2 = Producto.objects.create(nombre="Silla", precio=50000, stock=2, categoria="HOGAR")

    # ---------------- GET ----------------
    def test_listar(self):
        r = self.client.get(URL)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])
        self.assertEqual(r.json()["total"], 2)

    def test_obtener_por_id_sin_barra_final(self):
        # El enunciado escribe "Productos/4" (sin barra final).
        r = self.client.get(f"{URL}{self.p1.id}")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["data"]["nombre"], "Teclado")

    def test_obtener_inexistente_devuelve_json_404(self):
        r = self.client.get(f"{URL}9999")
        self.assertEqual(r.status_code, 404)
        self.assertFalse(r.json()["ok"])
        self.assertEqual(r.json()["codigo"], "NO_ENCONTRADO")

    def test_obtener_id_gigante_o_texto_devuelve_404(self):
        # Antes un id gigante provocaba un error 500 en SQLite.
        for valor in ("99999999999999999999999", "abc", "0"):
            r = self.client.get(f"{URL}{valor}")
            self.assertEqual(r.status_code, 404, valor)
            self.assertEqual(r.json()["codigo"], "NO_ENCONTRADO", valor)

    def test_filtrar(self):
        r = self.client.get(URL, {"categoria": "hogar"})
        self.assertEqual(r.json()["total"], 1)

    # ---------------- POST ----------------
    def test_crear(self):
        r = self.client.post(URL, {"nombre": "Monitor", "precio": 120000, "stock": 3}, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Producto.objects.filter(nombre="Monitor").exists())

    def test_crear_nombre_repetido_falla(self):
        # Requisito: validar que el nombre no exista (sin distinguir mayúsculas).
        r = self.client.post(URL, {"nombre": "  teclado ", "precio": 1000}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("nombre", r.json()["errores"])

    def test_crear_datos_invalidos(self):
        r = self.client.post(URL, {"nombre": "X", "precio": -5}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("precio", r.json()["errores"])

    def test_crear_precio_fuera_de_rango(self):
        r = self.client.post(URL, {"nombre": "Caro", "precio": 99999999999}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("precio", r.json()["errores"])

    def test_crear_con_json_mal_formado(self):
        r = self.client.post(URL, "{malo", content_type="application/json")
        self.assertEqual(r.status_code, 400)
        self.assertFalse(r.json()["ok"])

    # ---------------- PUT ----------------
    def test_put_con_id_en_json(self):
        r = self.client.put(URL, {"id": self.p1.id, "precio": 17000}, format="json")
        self.assertEqual(r.status_code, 200)
        self.p1.refresh_from_db()  # vuelve a leer el producto desde la BD
        self.assertEqual(self.p1.precio, 17000)

    def test_put_id_inexistente_devuelve_error_json(self):
        # Requisito: si el id no existe, devolver un código de error en un JSON.
        r = self.client.put(URL, {"id": 9999, "precio": 1}, format="json")
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json()["codigo"], "PRODUCTO_NO_ENCONTRADO")

    def test_put_id_fuera_de_rango_devuelve_404(self):
        # Antes un id gigante provocaba un error 500 en SQLite.
        for valor in (10**30, 0, -3):
            r = self.client.put(URL, {"id": valor, "precio": 1}, format="json")
            self.assertEqual(r.status_code, 404, valor)
            self.assertEqual(r.json()["codigo"], "PRODUCTO_NO_ENCONTRADO", valor)

    def test_put_id_booleano_o_decimal_falla(self):
        for valor in (True, 1.5, "abc"):
            r = self.client.put(URL, {"id": valor, "precio": 1}, format="json")
            self.assertEqual(r.status_code, 400, valor)
            self.assertEqual(r.json()["codigo"], "ID_INVALIDO")

    def test_put_sin_id(self):
        r = self.client.put(URL, {"precio": 1}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["codigo"], "ID_REQUERIDO")

    def test_put_por_url(self):
        datos = {"nombre": "Teclado mecánico", "precio": 30000, "stock": 1, "categoria": "ELECTRONICA"}
        r = self.client.put(f"{URL}{self.p1.id}/", datos, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["data"]["nombre"], "Teclado mecánico")

    def test_put_nombre_de_otro_producto_falla(self):
        r = self.client.put(URL, {"id": self.p1.id, "nombre": "Silla"}, format="json")
        self.assertEqual(r.status_code, 400)

    # ---------------- Rutas ----------------
    def test_ruta_api_inexistente_devuelve_json(self):
        r = self.client.get("/api/no-existe/")
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json()["codigo"], "RUTA_NO_ENCONTRADA")

    @override_settings(DEBUG=False)
    def test_ruta_fuera_de_la_api_con_debug_false_devuelve_json(self):
        # Con DEBUG=False se usa handler404 (config/urls.py) en todo el sitio.
        r = self.client.get("/no-existe/")
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json()["codigo"], "RUTA_NO_ENCONTRADA")

    # ---------------- DELETE ----------------
    def test_eliminar(self):
        r = self.client.delete(f"{URL}{self.p2.id}")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])
        self.assertFalse(Producto.objects.filter(pk=self.p2.id).exists())

    def test_eliminar_inexistente(self):
        r = self.client.delete(f"{URL}9999")
        self.assertEqual(r.status_code, 404)
        self.assertFalse(r.json()["ok"])

    def test_eliminar_con_id_en_json(self):
        r = self.client.delete(URL, {"id": self.p1.id}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Producto.objects.filter(pk=self.p1.id).exists())

    # ---------------- OPTIONS ----------------
    def test_options_lista(self):
        # Antes respondía 500 (botón OPTIONS de la vista navegable).
        r = self.client.options(URL)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])
        self.assertEqual(list(r.json()["data"]["actions"]), ["POST"])

    def test_options_detalle(self):
        r = self.client.options(f"{URL}{self.p1.id}/")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])
        self.assertIn("PUT", r.json()["data"]["actions"])


class PaginacionTest(APITestCase):
    """Paginación opcional: solo se activa con ?por_pagina=N."""

    def setUp(self):
        for numero in range(1, 6):  # 5 productos
            Producto.objects.create(nombre=f"Producto {numero}", precio=1000 * numero)

    def test_sin_por_pagina_lista_todos(self):
        r = self.client.get(URL)
        self.assertEqual(len(r.json()["data"]), 5)
        self.assertNotIn("pagina", r.json())

    def test_con_por_pagina(self):
        r = self.client.get(URL, {"por_pagina": 2, "pagina": 2})
        cuerpo = r.json()
        self.assertEqual(r.status_code, 200)
        self.assertEqual([p["nombre"] for p in cuerpo["data"]], ["Producto 3", "Producto 4"])
        self.assertEqual(cuerpo["total"], 5)
        self.assertEqual(cuerpo["pagina"], 2)
        self.assertEqual(cuerpo["total_paginas"], 3)
        self.assertIsNotNone(cuerpo["siguiente"])
        self.assertIsNotNone(cuerpo["anterior"])

    def test_pagina_inexistente_devuelve_404_json(self):
        r = self.client.get(URL, {"por_pagina": 2, "pagina": 99})
        self.assertEqual(r.status_code, 404)
        self.assertFalse(r.json()["ok"])


class ManejadorErroresTest(SimpleTestCase):
    """El detalle técnico de un error 500 solo se muestra con DEBUG=True."""

    def _error_500(self):
        # assertLogs: comprueba que el error quede registrado en la consola
        # del servidor (y evita que ese mensaje ensucie la salida de las pruebas).
        with self.assertLogs("productos.exceptions", level="ERROR"):
            return manejador_excepciones_json(RuntimeError("clave secreta de la BD"), {})

    @override_settings(DEBUG=False)
    def test_error_500_oculta_detalle_sin_debug(self):
        respuesta = self._error_500()
        self.assertEqual(respuesta.status_code, 500)
        self.assertEqual(respuesta.data["errores"], {})

    @override_settings(DEBUG=True)
    def test_error_500_muestra_detalle_con_debug(self):
        respuesta = self._error_500()
        self.assertEqual(respuesta.data["errores"], {"detalle": "clave secreta de la BD"})


class CrearBaseDatosTest(SimpleTestCase):
    """Comando "python manage.py crear_base_datos" (sin tocar el MySQL real)."""

    def _ejecutar_con(self, **base_de_datos):
        """Ejecuta el comando con una configuración de MySQL de prueba."""
        configuracion = {"ENGINE": "django.db.backends.mysql", "NAME": "tienda_api", "USER": "root",
                         "PASSWORD": "", "HOST": "127.0.0.1", "PORT": "3306", **base_de_datos}
        # Django advierte que cambiar DATABASES en una prueba es delicado; aquí
        # es seguro porque el comando no usa la conexión de Django, así que se
        # silencia ese aviso.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with override_settings(DATABASES={"default": configuracion}):
                call_command("crear_base_datos", stdout=StringIO())

    def test_rechaza_nombre_peligroso(self):
        # Un nombre con ";" podría usarse para inyección SQL: se rechaza antes de conectar.
        with self.assertRaisesMessage(CommandError, "Nombre de base de datos no válido"):
            self._ejecutar_con(NAME="mala;base")

    def test_error_de_conexion_da_mensaje_claro(self):
        # Se carga el backend MySQL de Django, como ocurre al usar manage.py con
        # MySQL (con USE_SQLITE=1 no se cargaría). Ese import es el que cambia
        # pymysql.err (ver el comentario en crear_base_datos.py).
        importlib.import_module("django.db.backends.mysql.base")
        # Puerto 1: no hay ningún MySQL escuchando -> mensaje de ayuda.
        with self.assertRaisesMessage(CommandError, "No se pudo conectar a MySQL"):
            self._ejecutar_con(PORT="1")


class PrepararDemoTest(TransactionTestCase):
    """El comando deja exactamente los 8 productos del fixture y el próximo id es el 9."""

    def test_reinicia_productos_y_crea_admin(self):
        Producto.objects.create(nombre="Sobrante", precio=1000)
        call_command("preparar_demo", stdout=StringIO())
        call_command("preparar_demo", stdout=StringIO())  # repetirlo no falla
        self.assertEqual(Producto.objects.count(), 8)
        self.assertFalse(Producto.objects.filter(nombre="Sobrante").exists())
        self.assertTrue(get_user_model().objects.filter(username="admin", is_superuser=True).exists())
        r = self.client.post(URL, {"nombre": "Nuevo", "precio": 1000}, format="json")
        self.assertEqual(r.json()["data"]["id"], 9)


class VistaNavegableTest(APITestCase):
    """La vista navegable de DRF (navegador) muestra formularios útiles."""

    def setUp(self):
        self.p1 = Producto.objects.create(nombre="Teclado", precio=15000)

    def test_formulario_put_del_detalle_viene_relleno(self):
        r = self.client.get(f"{URL}{self.p1.id}/", HTTP_ACCEPT="text/html")
        self.assertContains(r, 'value="Teclado"')

    def test_lista_no_muestra_formulario_put_ni_boton_delete(self):
        # En la lista, PUT y DELETE necesitan el id en el JSON (pestaña "Raw data").
        r = self.client.get(URL, HTTP_ACCEPT="text/html")
        self.assertContains(r, 'method="POST" enctype="multipart/form-data"')
        self.assertNotContains(r, 'data-method="PUT" enctype="multipart/form-data"')
        self.assertNotContains(r, 'data-method="DELETE"')

    def test_detalle_si_muestra_boton_delete(self):
        r = self.client.get(f"{URL}{self.p1.id}/", HTTP_ACCEPT="text/html")
        self.assertContains(r, 'data-method="DELETE"')

    def test_boton_options_en_el_navegador_no_falla(self):
        r = self.client.options(URL, HTTP_ACCEPT="text/html")
        self.assertEqual(r.status_code, 200)
