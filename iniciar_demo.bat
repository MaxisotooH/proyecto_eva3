@echo off
chcp 65001 >nul
title Tienda API - Demo
cd /d "%~dp0"

REM ==== Usa MySQL de XAMPP (root sin clave en 127.0.0.1:3306) ====
REM Para una vista previa sin MySQL, cambia la siguiente linea a: set USE_SQLITE=1
set USE_SQLITE=0
set PYTHONIOENCODING=utf-8

where py >nul 2>nul && (set PY=py) || (set PY=python)

if not exist venv (
  echo [1/5] Creando entorno virtual...
  %PY% -m venv venv || goto error
)
call venv\Scripts\activate.bat

echo [1/5] Instalando librerias...
python -m pip install -q -r requirements.txt || goto error

if "%USE_SQLITE%"=="1" goto migrar

echo [2/5] Revisando que MySQL este corriendo en el puerto 3306...
netstat -ano | findstr ":3306" | findstr "LISTENING" >nul
if errorlevel 1 (
  echo.
  echo *** MySQL no esta corriendo. Abre el XAMPP Control Panel, presiona Start en MySQL
  echo     y vuelve a ejecutar este archivo.
  goto error
)

echo [3/5] Creando la base de datos tienda_api si no existe...
set MYSQL_EXE=mysql
if exist "C:\xampp\mysql\bin\mysql.exe" set MYSQL_EXE="C:\xampp\mysql\bin\mysql.exe"
%MYSQL_EXE% -u root -h 127.0.0.1 -e "CREATE DATABASE IF NOT EXISTS tienda_api CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" || goto error

:migrar
echo [4/5] Creando tablas, reiniciando los 8 productos de ejemplo y el usuario admin...
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
echo *** Ocurrio un error. Copia el mensaje de arriba y pegaselo a Claude. ***
:fin
pause
