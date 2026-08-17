# Guide de ce dossier

Ce dossier contient tout ce qu'il faut pour **fabriquer** Jason — le
contraire de `apps/`, à la racine du dépôt, qui contient les applications
déjà prêtes à l'emploi.

## Ce que contient chaque sous-dossier

- **`sources/`** — le code du projet.
  - `sources/jason/` : le paquet Python de Jason, interface graphique
    comprise. Une seule version, partagée par Linux et Windows.
  - `sources/linux/` : empaquetage Linux (AppImage, raccourci de menu).
  - `sources/windows/` : empaquetage Windows (installateur Inno Setup).
- **`scripts/`** — petits outils de contrôle en console, sans rapport avec
  une plateforme en particulier (`essai.py`, `audit_modeles.py`).
- **`cache_pyinstaller/`, `dist/`, `tmp/`** — dossiers de travail, produits
  automatiquement à la fabrication. **On peut les supprimer sans risque** :
  ils sont recréés à la prochaine construction. Rien d'utile n'y est écrit à
  la main.

## Les commandes à connaître

Toutes se lancent depuis la racine du dépôt.

**Sous Linux :**

```bash
# Fabrique apps/linux/Jason-x86_64.AppImage à partir des sources
./build/sources/linux/construire_appimage.sh

# Refait l'AppImage ET la réinstalle dans le menu des applications, en une fois
./build/sources/linux/redeployer_local.sh
```

La seconde est la plus pratique pendant le développement : elle enchaîne la
première avec l'installation, pour tester directement le résultat.

**Sous Windows** (dans PowerShell) :

```powershell
# Fabrique apps\windows\JasonInstallateur.exe à partir des sources
.\build\sources\windows\construire_installateur.ps1
```

Prérequis à installer une fois pour toutes, à la main : Python (avec
« Add python.exe to PATH » coché) et Inno Setup 6. Le script s'occupe du
reste — environnement virtuel, dépendances, empaquetage, vérification et
installateur.

**Attention à l'encodage** : `construire_installateur.ps1` doit rester en
**UTF-8 avec BOM** (Windows PowerShell 5.1 lit sinon le fichier en ANSI et
mutile les accents), et le `.bat` reste volontairement sans accents. Ne pas
« nettoyer » ces fichiers avec un éditeur qui retire le BOM.
