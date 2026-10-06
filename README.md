# Tienda API — Evaluación 3 Programación Backend (V-FB50-N4-P14-C1)

[![Pruebas con MariaDB 10.4](https://github.com/MaxisotooH/proyecto_eva3/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/MaxisotooH/proyecto_eva3/actions/workflows/ci.yml)

API RESTful en **Django + Django REST Framework** con base de datos **MySQL**, que permite
crear, listar, actualizar y borrar productos. Todas las respuestas (éxito y error) son **JSON**.

![Vista navegable de DRF con la lista de productos](docs/capturas/01_api_lista.png)

- 🧭 **Revisión:** cada criterio de la rúbrica con enlaces a la línea exacta del código, y
  las capturas de la API funcionando con MySQL →
  [Guía de revisión y evidencias](DOCUMENTACION.md#10-guía-de-revisión-y-evidencias)
- 📘 **Manual completo** (instalación paso a paso en cualquier PC, configuración, pruebas y
  explicación del código) → [DOCUMENTACION.md](DOCUMENTACION.md)
- ✅ **Pruebas:** el indicador de arriba muestra el resultado de las 36 pruebas automáticas,
  que GitHub ejecuta contra MariaDB 10.4 en cada cambio.

## Requisitos

- **Python 3.10, 3.11 o 3.12** (recomendado 3.12). ⚠️ Python 3.13 y 3.14 no son compatibles
  con Django 4.2: el admin y la vista navegable fallan. Pueden convivir instalados con la 3.12.
- **MySQL 8** o **MariaDB** (XAMPP), iniciado.

## Inicio rápido

**Windows (automático):** iniciar MySQL (XAMPP → Start) y doble clic en **`iniciar_demo.bat`**.
Si tu MySQL tiene clave, escríbela antes en `config_mysql.bat`.

**Manual (Windows / macOS / Linux)**, dentro de la carpeta del proyecto:

```bash
py -3.12 -m venv venv                 # macOS/Linux: python3.12 -m venv venv
venv\Scripts\activate                 # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py crear_base_datos     # crea la base "tienda_api" en MySQL
python manage.py migrate              # crea las tablas
python manage.py preparar_demo        # 8 productos de ejemplo + usuario admin / admin123
python manage.py runserver
```

Si MySQL tiene clave, defínela antes: `set DB_PASSWORD=tu_clave` (cmd) o
`$env:DB_PASSWORD="tu_clave"` (PowerShell). Ver
[Variables de entorno](DOCUMENTACION.md#6-variables-de-entorno-configuración).

| URL | Qué es |
| --- | --- |
| http://127.0.0.1:8000/ | Cliente REST web (consume la API con `fetch`) |
| http://127.0.0.1:8000/api/productos/ | API (JSON / vista navegable de DRF) |
| http://127.0.0.1:8000/admin/ | Administración de Django (`admin` / `admin123`) |

## Endpoints

Base: `http://127.0.0.1:8000/api` — la barra final es opcional.

| Método | Ruta | Acción |
| --- | --- | --- |
| GET | `/productos/` | Lista todos los productos (filtros `?buscar=`, `?categoria=`, `?activo=`; paginación `?por_pagina=&pagina=`) |
| GET | `/productos/4` | Devuelve solo el producto 4 |
| POST | `/productos/` | Crea un producto. **Valida que el nombre no exista** |
| PUT | `/productos/` | Actualiza el producto cuyo `id` viene en el JSON. Si no existe → **404 JSON** |
| PUT / PATCH | `/productos/4` | Actualiza el producto 4 (completo / parcial) |
| DELETE | `/productos/4` | Elimina el producto 4 (también `DELETE /productos/` con `{"id": 4}`) |
| OPTIONS | `/productos/` | Describe los campos que acepta la API |

Formato de las respuestas, códigos de error y ejemplos:
[DOCUMENTACION.md § 7](DOCUMENTACION.md#7-endpoints-de-la-api).
Colección de Postman: `docs/Eva3_API_Productos.postman_collection.json`.

## Pruebas automáticas

```bash
python manage.py test productos       # 36 pruebas (con MySQL; sin MySQL: USE_SQLITE=1)
```

En cada `push`, GitHub Actions ejecuta las pruebas contra MariaDB 10.4 (`.github/workflows/ci.yml`).
