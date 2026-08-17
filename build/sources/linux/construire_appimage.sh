#!/usr/bin/env bash
#
# Fabrique apps/linux/Jason-x86_64.AppImage — le fichier unique à distribuer
# sous Linux. Il contient Python, Qt et le moteur de traduction : rien à
# installer sur la machine de destination.
#
#   ./build/sources/linux/construire_appimage.sh
#
# Comptez une dizaine de minutes et 3 Go de place. Les langues ne sont pas
# incluses : Jason les télécharge au premier lancement.

set -euo pipefail

# Trois niveaux sous la racine du dépôt (build/sources/linux/), d'où le
# triple "..".
PROJET="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$PROJET"

# /tmp est un disque en mémoire de 2 Go sur Fedora : PyInstaller y déballe
# Qt et manque de place. On travaille donc sur le vrai disque.
export TMPDIR="$PROJET/build/tmp"
mkdir -p "$TMPDIR"

APPDIR="$TMPDIR/AppDir"
OUTIL="$TMPDIR/appimagetool"

if [ ! -x "$OUTIL" ]; then
    echo "Récupération de l'outil de fabrication…"
    curl -L -o "$OUTIL" \
        "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x "$OUTIL"
fi

echo "== 1/3 — Empaquetage avec PyInstaller =="
# --distpath et --workpath sont explicites : sans eux, PyInstaller écrirait
# à nouveau dist/ et build/ à la racine du dépôt, au lieu de rester dans
# build/ avec le reste de la fabrication.
"$PROJET/.venv/bin/pyinstaller" --noconfirm \
    --distpath build/dist --workpath build/cache_pyinstaller \
    jason.spec

echo "== 2/3 — Préparation du dossier de l'application =="
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
cp -a build/dist/jason/. "$APPDIR/usr/bin/"

# Le raccourci du dépôt suppose un programme installé sur le système ;
# dans une AppImage, c'est AppRun qui lance tout.
sed "s|^Exec=.*|Exec=jason|" build/sources/linux/jason.desktop |
    grep -v '^#!' > "$APPDIR/jason.desktop"

cp build/sources/jason/ui/resources/jason-256.png "$APPDIR/jason.png"
cp "$APPDIR/jason.png" "$APPDIR/.DirIcon"

cat > "$APPDIR/AppRun" <<'FIN'
#!/bin/sh
# Point d'entrée de l'AppImage : lance Jason depuis le dossier extrait.
ICI="$(dirname "$(readlink -f "$0")")"
exec "$ICI/usr/bin/jason" "$@"
FIN
chmod +x "$APPDIR/AppRun"

echo "== 3/3 — Assemblage de l'AppImage =="
mkdir -p apps/linux
# ARCH est obligatoire : sans lui, l'outil refuse de deviner le processeur.
ARCH=x86_64 "$OUTIL" "$APPDIR" apps/linux/Jason-x86_64.AppImage

echo
echo "Vérification : l'AppImage traduit-elle vraiment ?"

# Deux précautions pour que ce contrôle soit fiable :
#
# 1. TMPDIR est remis à sa valeur normale. Une AppImage se monte dans TMPDIR ;
#    le laisser pointer sur le dossier de travail fait disparaître le montage
#    sous les pieds du programme, et le test échoue alors qu'il ne devrait pas.
#
# 2. On lit le compte rendu plutôt que le code de sortie. Une bibliothèque de
#    calcul laisse derrière elle un processus de service qui, lui, se plante
#    au démontage de l'AppImage et affiche une trace d'erreur sans gravité.
COMPTE_RENDU="$(env -u TMPDIR ./apps/linux/Jason-x86_64.AppImage --autotest 2>&1)"
echo "$COMPTE_RENDU" | grep -E "^(langues|traduction|détection|AUTOTEST)" || true

if echo "$COMPTE_RENDU" | grep -q "AUTOTEST RÉUSSI"; then
    echo
    echo "Terminé : apps/linux/Jason-x86_64.AppImage"
else
    echo "L'AppImage a été fabriquée mais ne traduit pas — ne la distribuez pas." >&2
    exit 1
fi
