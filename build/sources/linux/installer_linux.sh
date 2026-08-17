#!/usr/bin/env bash
#
# Installe Jason dans le menu des applications, sous Linux.
#
# Une AppImage se lance en double-cliquant dessus, mais elle reste un fichier
# perdu dans un dossier : elle n'apparaît ni dans le menu, ni dans la
# recherche du bureau. Ce script la range et l'y déclare.
#
#   ./build/sources/linux/installer_linux.sh            (depuis le dossier du projet)
#   ./build/sources/linux/installer_linux.sh chemin/vers/Jason-x86_64.AppImage
#
# Rien n'est installé pour tout le système : tout va dans le dossier
# personnel, donc aucun mot de passe administrateur n'est demandé.
# Pour désinstaller : ./build/sources/linux/installer_linux.sh --desinstaller

set -euo pipefail

# Trois niveaux sous la racine du dépôt (build/sources/linux/), d'où le
# triple "..".
PROJET="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
DESTINATION="$HOME/.local/share/jason"
RACCOURCI="$HOME/.local/share/applications/jason.desktop"
ICONES="$HOME/.local/share/icons/hicolor"

rafraichir_le_menu() {
    # Sans cela, le nouveau raccourci peut n'apparaître qu'à la session suivante.
    command -v update-desktop-database >/dev/null &&
        update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    command -v gtk-update-icon-cache >/dev/null &&
        gtk-update-icon-cache -f -t "$ICONES" 2>/dev/null || true
}

if [ "${1:-}" = "--desinstaller" ]; then
    rm -rf "$DESTINATION" "$RACCOURCI"
    rm -f "$ICONES"/*/apps/jason.png "$ICONES/scalable/apps/jason.svg"
    rafraichir_le_menu
    echo "Jason a été retiré du menu."
    echo "Les langues téléchargées restent dans ~/.local/share/argos-translate."
    exit 0
fi

APPIMAGE="${1:-$PROJET/apps/linux/Jason-x86_64.AppImage}"

if [ ! -f "$APPIMAGE" ]; then
    echo "AppImage introuvable : $APPIMAGE" >&2
    echo "Construisez-la d'abord, ou indiquez son chemin en argument." >&2
    exit 1
fi

mkdir -p "$DESTINATION"
install -m 755 "$APPIMAGE" "$DESTINATION/Jason.AppImage"

# Icônes, dans les tailles attendues par les environnements de bureau.
for taille in 16 32 48 64 128 256; do
    mkdir -p "$ICONES/${taille}x${taille}/apps"
    install -m 644 "$PROJET/build/sources/jason/ui/resources/jason-$taille.png" \
        "$ICONES/${taille}x${taille}/apps/jason.png"
done
mkdir -p "$ICONES/scalable/apps"
install -m 644 "$PROJET/build/sources/jason/ui/resources/jason.svg" \
    "$ICONES/scalable/apps/jason.svg"

# Le raccourci du projet indique « Exec=jason », qui suppose un programme
# installé sur le système. Ici l'application est un fichier unique : on écrit
# son chemin complet, sans quoi le menu ne lance rien du tout.
mkdir -p "$(dirname "$RACCOURCI")"
sed "s|^Exec=.*|Exec=$DESTINATION/Jason.AppImage|" \
    "$PROJET/build/sources/linux/jason.desktop" > "$RACCOURCI"
chmod 644 "$RACCOURCI"

rafraichir_le_menu

echo "Jason est installé."
echo "Cherchez « Jason » dans le menu des applications."
