"""
Pruebas automáticas del CRUD.
Con MySQL:          python manage.py test
Sin MySQL (rápido): set USE_SQLITE=1 && python manage.py test     (Windows cmd)
                    $env:USE_SQLITE=1; python manage.py test      (PowerShell)
"""
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Producto

URL = "/api/productos/"


class ProductoAPITest(APITestCase):
    def setUp(self):
        self.p1 = Producto.objects.create(nombre="Teclado", precio=15000, stock=5, categoria="ELECTRONICA")
        self.p2 = Producto.objects.create(nombre="Silla", precio=50000, stock=2, categoria="HOGAR")

    # ---------------- GET ----------------
    def test_listar(self):
        r = self.client.get(URL)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])
        self.assertEqual(r.json()["total"], 2)

    def test_obtener_por_id_sin_barra_final(self):
        r = self.client.get(f"{URL}{self.p1.id}")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["data"]["nombre"], "Teclado")

    def test_obtener_inexistente_devuelve_json_404(self):
        r = self.client.get(f"{URL}9999")
        self.assertEqual(r.status_code, 404)
        self.assertFalse(r.json()["ok"])
        self.assertEqual(r.json()["codigo"], "NO_ENCONTRADO")

    def test_filtrar(self):
        r = self.client.get(URL, {"categoria": "hogar"})
        self.assertEqual(r.json()["total"], 1)

    # ---------------- POST ----------------
    def test_crear(self):
        r = self.client.post(URL, {"nombre": "Monitor", "precio": 120000, "stock": 3}, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Producto.objects.filter(nombre="Monitor").exists())

    def test_crear_nombre_repetido_falla(self):
        r = self.client.post(URL, {"nombre": "teclado", "precio": 1000}, format="json")
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

    # ---------------- PUT ----------------
    def test_put_con_id_en_json(self):
        r = self.client.put(URL, {"id": self.p1.id, "precio": 17000}, format="json")
        self.assertEqual(r.status_code, 200)
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.precio, 17000)

    def test_put_id_inexistente_devuelve_error_json(self):
        r = self.client.put(URL, {"id": 9999, "precio": 1}, format="json")
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json()["codigo"], "PRODUCTO_NO_ENCONTRADO")

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
