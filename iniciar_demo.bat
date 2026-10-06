@echo off
chcp 65001 >nul
title Tienda API - Demo
REM Ir a la carpeta donde esta este archivo (la del proyecto).
cd /d "%~dp0"

REM ==========================================================================
REM  Deja el proyecto funcionando de principio a fin:
REM    1. busca Python 3.12 / 3.11 / 3.10 y crea el entorno virtual "venv"
REM    2. instala las librerias de requirements.txt
REM    3. crea la base de datos en MySQL (si no existe)
REM    4. crea las tablas y carga los 8 productos de ejemplo + usuario admin
REM    5. levanta el servidor y abre el navegador
REM  Datos de conexion a MySQL: ver config_mysql.bat
REM ==========================================================================

REM Para una vista previa SIN MySQL, cambia la siguiente linea a: set USE_SQLITE=1
set USE_SQLITE=0
set PYTHONIOENCODING=utf-8
call "%~dp0config_mysql.bat"

echo [1/5] Preparando Python y el entorno virtual...
if exist venv\Scripts\python.exe goto revisar_venv

REM Django 4.2 funciona con Python 3.10, 3.11 o 3.12 (NO con 3.13 ni 3.14).
REM Se prueba el lanzador "py" con cada version compatible, de la mas nueva a la mas antigua.
set PY=
for %%V in (3.12 3.11 3.10) do (
  if not defined PY (
    py -%%V -c "import sys" >nul 2>nul && set "PY=py -%%V"
  )
)
REM Si no hay lanzador "py" (Linux/Mac o instalaciones especiales), se prueba "python".
if not defined PY (
  python -c "import sys; sys.exit(0 if (3, 10) <= sys.version_info[:2] <= (3, 12) else 1)" >nul 2>nul && set "PY=python"
)
if not defined PY (
  echo.
  echo *** No se encontro Python 3.10, 3.11 ni 3.12.
  echo     Instala Python 3.12 desde https://www.python.org/downloads/ y vuelve a ejecutar este archivo.
  goto error
)
echo     Creando entorno virtual con: %PY%
%PY% -m venv venv || goto error

:revisar_venv
REM Si la carpeta venv ya existia, se comprueba que su Python sea compatible.
venv\Scripts\python.exe -c "import sys; sys.exit(0 if (3, 10) <= sys.version_info[:2] <= (3, 12) else 1)"
if errorlevel 1 (
  echo.
  echo *** La carpeta "venv" fue creada con una version de Python no compatible.
  echo     Borra la carpeta "venv" y vuelve a ejecutar este archivo.
  goto error
)
call venv\Scripts\activate.bat

echo [2/5] Instalando librerias...
python -m pip install -q -r requirements.txt || goto error

if "%USE_SQLITE%"=="1" goto migrar

echo [3/5] Creando la base de datos %DB_NAME% en MySQL (%DB_HOST%:%DB_PORT%, usuario %DB_USER%)...
python manage.py crear_base_datos || goto error

:migrar
echo [4/5] Creando tablas, cargando los 8 productos de ejemplo y el usuario admin...
python manage.py migrate --noinput || goto error
python manage.py preparar_demo || goto error

echo [5/5] Iniciando servidor en http://127.0.0.1:8000/
echo     API:   http://127.0.0.1:8000/api/productos/
echo     Admin: http://127.0.0.1:8000/admin/   (usuario: admin  clave: admin123)
echo     Para detener: Ctrl+C
start "" http://127.0.0.1:8000/
python manage.py runserver
goto fin

:error
echo.
echo *** Ocurrio un error. Revisa el mensaje de arriba y la seccion
echo     "Problemas comunes" de DOCUMENTACION.md.
:fin
pause
