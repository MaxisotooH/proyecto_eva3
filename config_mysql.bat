@echo off
REM ==========================================================================
REM  Datos de conexion a MySQL. Los usan iniciar_demo.bat y reiniciar_datos.bat
REM  (este archivo no se ejecuta solo).
REM
REM  Valores por defecto = XAMPP: usuario root SIN clave en 127.0.0.1:3306.
REM  Si tu MySQL tiene clave (por ejemplo, MySQL instalado con MySQL Installer),
REM  quita la palabra REM de la linea "set DB_PASSWORD=..." y escribe tu clave.
REM  IMPORTANTE: no subas tu clave real a GitHub.
REM
REM  "if not defined" respeta las variables que ya existan en Windows, asi
REM  tambien se pueden definir desde "Variables de entorno" del sistema.
REM ==========================================================================

if not defined DB_NAME set DB_NAME=tienda_api
if not defined DB_USER set DB_USER=root
if not defined DB_HOST set DB_HOST=127.0.0.1
if not defined DB_PORT set DB_PORT=3306

REM set DB_PASSWORD=escribe_aqui_tu_clave
