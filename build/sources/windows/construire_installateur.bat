@echo off
REM Double-cliquez ce fichier pour lancer la construction de Jason -
REM evite d'avoir a ouvrir PowerShell et taper une commande.
REM (Fichier volontairement sans accents : cmd.exe lit une page de code
REM OEM, pas de l'UTF-8.)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0construire_installateur.ps1"
pause
