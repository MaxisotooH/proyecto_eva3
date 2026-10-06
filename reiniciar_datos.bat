@echo off
chcp 65001 >nul
title Tienda API - Reiniciar datos
cd /d "%~dp0"
REM Deja de nuevo los 8 productos de ejemplo (ids 1 al 8) en MySQL.
REM Usalo despues de cada ensayo; el servidor puede seguir abierto.
set USE_SQLITE=0
set PYTHONIOENCODING=utf-8
call venv\Scripts\activate.bat
python manage.py preparar_demo
pause
