@echo off
setlocal

cd /d "%~dp0"

if not exist .venv (
  echo [INFO] Creation de l'environnement virtuel...
  py -m venv .venv
  if errorlevel 1 goto :error
)

echo [INFO] Installation / verification des dependances...
call .venv\Scripts\python.exe -m pip install --upgrade pip >nul
call .venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo [INFO] Lancement de Sokoban Neo...
call .venv\Scripts\python.exe main.py
if errorlevel 1 goto :error

goto :eof

:error
echo.
echo [ERREUR] Echec pendant le lancement. Verifiez Python/py launcher et votre connexion internet.
pause
exit /b 1
