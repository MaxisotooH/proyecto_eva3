@echo off
chcp 65001 >nul
title Tienda API - Demo
cd /d "%~dp0"

REM ==== Modo vista previa: usa SQLite (no necesita MySQL) ====
REM Para usar MySQL, borra la siguiente linea o cambiala a: set USE_SQLITE=0
set USE_SQLITE=1

where py >nul 2>nul && (set PY=py) || (set PY=python)

if not exist venv (
  echo [1/4] Creando entorno virtual...
  %PY% -m venv venv || goto error
)
call venv\Scripts\activate.bat

echo [2/4] Instalando librerias...
python -m pip install -q -r requirements.txt || goto error

echo [3/4] Creando tablas y cargando productos de ejemplo...
python manage.py migrate --noinput || goto error
python manage.py loaddata productos || goto error

echo [4/4] Iniciando servidor en http://127.0.0.1:8000/
echo     Admin: crea un usuario con "python manage.py createsuperuser" en otra ventana.
echo     Para detener: Ctrl+C
start "" http://127.0.0.1:8000/
python manage.py runserver
goto fin

:error
echo.
echo *** Ocurrio un error. Copia el mensaje de arriba y pegaselo a Claude. ***
:fin
pause
