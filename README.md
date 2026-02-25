# Sokoban Neo — version Windows (desktop)

Cette version cible **Windows** en mode natif desktop (Pygame), avec option de génération en `.exe`.

## 1) Installation rapide (Windows)

1. Installer Python 3.11+ (python.org ou Microsoft Store).
2. Ouvrir PowerShell dans le dossier du projet.
3. Exécuter :

```powershell
py -m pip install -r requirements.txt
py main.py
```

## 2) Lancement en un clic (double-clic)

- `launch_windows.bat`

Le script crée automatiquement un environnement virtuel `.venv` (si absent), installe les dépendances, puis lance le jeu.

## 3) Générer un exécutable `.exe`

Exécuter dans PowerShell :

```powershell
powershell -ExecutionPolicy Bypass -File .\build_windows_exe.ps1
```

Résultat :

- `dist\SokobanNeo.exe`

## Contrôles

- `← ↑ ↓ →` ou `WASD` : bouger
- `Z` : annuler le dernier mouvement
- `R` : redémarrer le niveau
- `N` : niveau suivant
- `ESC` : quitter

## Fichiers Windows ajoutés

- `launch_windows.bat` : lancement desktop 1 clic
- `build_windows_exe.ps1` : build PyInstaller pour Windows

## Note

Les fichiers web (`index.html`, `styles.css`, `sokoban.js`) peuvent rester pour une version navigateur, mais la cible principale ici est la **version Windows native**.
