# Tienda API — Evaluación 3 Programación Backend (V-FB50-N4-P14-C1)

API RESTful en **Django + Django REST Framework** con base de datos **MySQL**, que permite
crear, listar, actualizar y borrar productos. Todas las respuestas (éxito y error) son **JSON**.

## Estructura

```
proyecto_eva3/
├── manage.py
├── requirements.txt
├── config/                 # proyecto Django
│   ├── __init__.py         # PyMySQL como conector MySQL
│   ├── settings.py         # INSTALLED_APPS, MySQL, configuración DRF
│   └── urls.py             # /admin/, /api/, cliente web
├── productos/              # app
│   ├── models.py           # modelo Producto (tabla "productos")
│   ├── serializers.py      # JSON <-> modelo + validación de nombre único
│   ├── views.py            # ProductoViewSet (ModelViewSet) con respuestas JSON
│   ├── urls.py             # Router de DRF (ViewSet)
│   ├── exceptions.py       # todos los errores salen en JSON con el mismo formato
│   ├── admin.py            # administración del modelo
│   ├── tests.py            # 18 pruebas automáticas del CRUD
│   ├── fixtures/productos.json   # datos de ejemplo
│   └── templates/productos/cliente.html  # cliente REST web propio
└── docs/
    ├── crear_base_datos.sql
    └── Eva3_API_Productos.postman_collection.json
```

## Instalación (Windows, laboratorio)

> Requisitos: Python 3.10+ y MySQL Server corriendo (XAMPP, MySQL Installer o Docker).

```bat
:: 1. Entrar a la carpeta y crear entorno virtual
cd proyecto_eva3
python -m venv venv
venv\Scripts\activate

:: 2. Instalar librerías
pip install -r requirements.txt

:: 3. Crear la base de datos (o ejecutar docs\crear_base_datos.sql en Workbench)
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS tienda_api CHARACTER SET utf8mb4;"
```

4. **Revisar usuario y clave de MySQL** en `config/settings.py` → `DATABASES`
   (por defecto `root` sin clave en `127.0.0.1:3306`). También se pueden pasar por variables de entorno:
   `set DB_PASSWORD=miclave`.

```bat
:: 5. Crear tablas, cargar datos de ejemplo y crear usuario admin
python manage.py migrate
python manage.py loaddata productos
python manage.py createsuperuser

:: 6. Levantar el servidor
python manage.py runserver
```

| URL | Qué es |
| --- | --- |
| http://127.0.0.1:8000/ | Cliente REST web (consume la API con `fetch`) |
| http://127.0.0.1:8000/api/productos/ | API (JSON / vista navegable de DRF) |
| http://127.0.0.1:8000/admin/ | Administración de Django |

## Endpoints

Base: `http://127.0.0.1:8000/api` — la barra final es opcional (`/productos/4` y `/productos/4/` funcionan).

| Método | Ruta | Acción |
| --- | --- | --- |
| GET | `/productos/` | Lista todos los productos (filtros opcionales `?buscar=`, `?categoria=`, `?activo=`) |
| GET | `/productos/4` | Devuelve solo el producto 4 |
| POST | `/productos/` | Crea un producto. **Valida que el nombre no exista** (sin distinguir mayúsculas) |
| PUT | `/productos/` | Actualiza el producto cuyo `id` viene en el JSON. Si no existe → **404 JSON** |
| PUT | `/productos/4` | Actualiza el producto 4 (todos los campos) |
| PATCH | `/productos/4` | Actualiza solo los campos enviados |
| DELETE | `/productos/4` | Elimina el producto 4 |
| DELETE | `/productos/` | Elimina el producto cuyo `id` viene en el JSON |

### Formato de respuesta

Éxito:
```json
{ "ok": true, "status": 200, "mensaje": "Producto 4 encontrado.",
  "data": { "id": 4, "nombre": "Café en grano 1kg", "descripcion": "...", "precio": 15990,
            "stock": 40, "categoria": "ALIMENTOS", "categoria_nombre": "Alimentos",
            "activo": true, "fecha_creacion": "...", "fecha_actualizacion": "..." } }
```

Error:
```json
{ "ok": false, "status": 404, "codigo": "PRODUCTO_NO_ENCONTRADO",
  "mensaje": "No existe un producto con id 9999.",
  "errores": { "id": ["El producto 9999 no existe."] } }
```

Códigos usados: `200` OK, `201` creado, `400` datos inválidos / nombre repetido / falta id,
`404` no existe, `405` método no permitido, `409` conflicto en BD, `500` error interno.

## Probar con Postman / Thunder Client

Importar `docs/Eva3_API_Productos.postman_collection.json`. Trae todas las peticiones
(casos de éxito y de error) agrupadas por verbo, con la variable `base_url`.

## Pruebas automáticas

```bat
python manage.py test productos           :: usa MySQL (crea test_tienda_api)
set USE_SQLITE=1 && python manage.py test productos   :: sin MySQL
```

---

## Guion para la demostración (mapeado a la rúbrica)

**Criterio 1 — Implementa DRF (settings, MySQL, librerías)**
1. Mostrar `requirements.txt` (Django, djangorestframework, PyMySQL).
2. `config/settings.py`: `rest_framework` y `productos` en `INSTALLED_APPS`; bloque `DATABASES` con
   `django.db.backends.mysql`; bloque `REST_FRAMEWORK` (renderers JSON, manejador de errores).
3. `config/__init__.py`: `pymysql.install_as_MySQLdb()`.
4. En MySQL Workbench: `SELECT * FROM tienda_api.productos;` → la tabla existe y tiene datos.

**Criterio 2 — CRUD con salidas JSON (Postman)**
1. GET lista → GET `/productos/4` → GET `/productos/9999` (404 JSON).
2. POST producto nuevo (201) → POST con nombre repetido (400 JSON).
3. PUT `/productos/` con `{"id": 4, ...}` (200) → PUT con id 9999 (404 JSON).
4. DELETE `/productos/4` (200 JSON) → repetir el SELECT en MySQL para mostrar que cambió.

**Criterio 3 — Vistas, rutas, admin y ViewSet**
1. `productos/views.py`: `ProductoViewSet(viewsets.ModelViewSet)`.
2. `productos/urls.py`: `router.register("productos", ProductoViewSet)`; `config/urls.py` incluye `api/`.
3. `/admin/`: listar, buscar, filtrar, editar precio/stock en la lista, crear y borrar productos.
4. Aporte extra: cliente REST web en `/`, filtros de búsqueda, errores JSON uniformes,
   barra final opcional, rutas /api/ inexistentes en JSON, pruebas automáticas.

## Problemas comunes

| Error | Solución |
| --- | --- |
| `Access denied for user 'root'` | Poner la clave correcta en `DATABASES['default']['PASSWORD']` |
| `Unknown database 'tienda_api'` | Ejecutar `docs/crear_base_datos.sql` |
| `Can't connect to MySQL server` | Iniciar MySQL (XAMPP → Start MySQL / servicio MySQL80) o revisar el puerto |
| `cryptography package is required` | `pip install cryptography` (ya está en requirements) |
| `MariaDB 10.5 or later is required` (XAMPP antiguo) | `pip install "Django>=4.2,<5.0"` — Django 4.2 soporta MariaDB 10.4 y el código funciona igual |
| `No module named 'pymysql'` | Activar el venv y `pip install -r requirements.txt` |
