@echo off
cd /d "%~dp0"
echo Subiendo a https://github.com/MaxisotooH/proyecto_eva3 ...
git add -A
git commit -m "Actualizacion" 2>nul
git push -u origin main
pause
