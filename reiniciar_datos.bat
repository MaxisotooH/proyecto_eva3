@echo off
chcp 65001 >nul
title Tienda API - Reiniciar datos
cd /d "%~dp0"
REM Deja de nuevo los 8 productos de ejemplo (ids 1 al 8) en MySQL.
REM Usalo despues de cada ensayo; el servidor puede seguir abierto.
REM Requiere haber ejecutado antes iniciar_demo.bat (que crea "venv").
set USE_SQLITE=0
set PYTHONIOENCODING=utf-8
call "%~dp0config_mysql.bat"

if not exist venv\Scripts\activate.bat (
  echo *** No existe el entorno virtual. Ejecuta primero iniciar_demo.bat
  goto fin
)
call venv\Scripts\activate.bat
python manage.py preparar_demo
:fin
pause
