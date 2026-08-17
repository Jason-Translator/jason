# Construit JasonInstallateur.exe à partir des sources, sous Windows.
#
#   .\build\sources\windows\construire_installateur.ps1
#
# IMPORTANT : ce fichier doit rester encodé en UTF-8 AVEC BOM. Sans le BOM,
# Windows PowerShell 5.1 lit le fichier en ANSI et mutile tous les accents,
# dans les messages comme dans les comparaisons. Ne pas « nettoyer » le BOM.
#
# Prérequis à installer une seule fois, à la main (pas automatisable
# simplement depuis un script) :
#   - Python 3.11 ou plus récent (construit et testé avec Python 3.14),
#     en cochant "Add python.exe to PATH" à l'installation :
#     https://python.org/downloads
#   - Inno Setup 6, installation par défaut : https://jrsoftware.org/isdl.php
#
# Comptez une dizaine de minutes et quelques Go de place. Les langues ne sont
# pas incluses : Jason les télécharge au premier lancement.
#
# Le script affiche tout, volontairement : pas de barre de progression qui
# masquerait une étape bloquée. Il s'adresse au développeur — l'utilisateur
# final, lui, passe par l'installateur produit à la fin.

$ErrorActionPreference = "Stop"

$Projet = (Resolve-Path "$PSScriptRoot\..\..\..").Path
Set-Location $Projet

# --- 1/4 — Environnement Python ----------------------------------------------
Write-Host "== 1/4 — Environnement Python et dépendances =="

$Venv = Join-Path $Projet ".venv"
if (-not (Test-Path "$Venv\Scripts\python.exe")) {
    python -m venv $Venv
}

$Pip = "$Venv\Scripts\pip.exe"

& $Pip install --upgrade pip
& $Pip install -e .
# torch doit venir de l'index processeur : sinon pip télécharge 4,6 Go
# de bibliothèques CUDA parfaitement inutiles ici (Jason n'utilise que le
# processeur). On le réinstalle donc par-dessus, depuis le bon index.
& $Pip install torch --index-url https://download.pytorch.org/whl/cpu
& $Pip install pyinstaller

# --- 2/4 — Empaquetage avec PyInstaller --------------------------------------
Write-Host "== 2/4 — Empaquetage avec PyInstaller =="

& "$Venv\Scripts\pyinstaller.exe" --noconfirm `
    --distpath build\dist --workpath build\cache_pyinstaller `
    jason.spec

# --- 3/4 — Vérification : l'application fonctionne-t-elle vraiment ? ---------
Write-Host "== 3/4 — Vérification de l'exécutable =="

# L'application est « fenêtrée », sans console : son compte rendu est écrit
# dans autotest.log, à côté de l'exécutable. On efface celui d'une éventuelle
# construction précédente pour ne pas lire un résultat périmé, et on attend
# explicitement la fin du programme — sans -Wait, PowerShell n'attend pas
# les applications à fenêtre.
$LogPath = Join-Path $Projet "build\dist\jason\autotest.log"
Remove-Item $LogPath -ErrorAction SilentlyContinue

$Exe = Join-Path $Projet "build\dist\jason\jason.exe"
Start-Process -FilePath $Exe -ArgumentList "--autotest" -Wait

# Le log est en UTF-8 : sans -Encoding UTF8, PowerShell 5.1 le lirait en
# ANSI et « RÉUSSI » ne correspondrait jamais.
$Log = if (Test-Path $LogPath) { Get-Content $LogPath -Raw -Encoding UTF8 } else { "" }
Write-Host $Log

if ($Log -match "AUTOTEST INCOMPLET") {
    # Cas normal d'une machine de construction vierge : aucune langue Argos
    # n'y est installée, la traduction elle-même ne peut donc pas être
    # testée. L'exécutable démarre et son moteur se charge : on continue.
    Write-Warning ("Aucune langue installée sur cette machine : la " +
        "traduction n'a pas pu être testée. L'exécutable démarre " +
        "correctement, on continue.")
} elseif ($Log -notmatch "AUTOTEST RÉUSSI") {
    Write-Error "L'application ne fonctionne pas — installateur non construit."
    exit 1
}

# --- 4/4 — Installateur Inno Setup -------------------------------------------
Write-Host "== 4/4 — Construction de l'installateur =="

$Iscc = (Get-Command "ISCC.exe" -ErrorAction SilentlyContinue).Source
if (-not $Iscc) {
    $Iscc = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
}
if (-not (Test-Path $Iscc)) {
    Write-Error "Inno Setup introuvable. Installez-le : https://jrsoftware.org/isdl.php"
    exit 1
}
& $Iscc "build\sources\windows\installateur.iss"

Write-Host ""
Write-Host "Terminé : apps\windows\JasonInstallateur.exe"
