$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

if (-not (Test-Path .venv)) {
  Write-Host "[INFO] Creation de l'environnement virtuel..."
  py -m venv .venv
}

Write-Host "[INFO] Installation des dependances et de PyInstaller..."
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller

Write-Host "[INFO] Build de SokobanNeo.exe..."
.\.venv\Scripts\pyinstaller.exe --noconfirm --onefile --windowed --name SokobanNeo main.py

Write-Host "[OK] Build termine: dist\SokobanNeo.exe"
