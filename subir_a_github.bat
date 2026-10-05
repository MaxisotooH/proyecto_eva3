@echo off
cd /d "%~dp0"
set /p REPO=Pega la URL del repositorio (ej: https://github.com/MaxisotooH/proyecto_eva3.git): 
git init
git add .
git commit -m "Evaluacion 3: API REST Django + DRF + MySQL"
git branch -M main
git remote remove origin 2>nul
git remote add origin %REPO%
git push -u origin main
pause
