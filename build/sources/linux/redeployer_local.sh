#!/usr/bin/env bash
#
# Outil de développement : reconstruit l'AppImage et la met à jour dans le
# menu des applications, en une seule commande. Sert à vérifier rapidement
# une modification des sources dans l'application réellement installée.
#
# `construire_appimage.sh` et `installer_linux.sh` restent les scripts de
# référence ; celui-ci ne fait que les enchaîner.
#
#   ./build/sources/linux/redeployer_local.sh

set -euo pipefail

# Trois niveaux sous la racine du dépôt (build/sources/linux/), d'où le
# triple "..".
PROJET="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

"$PROJET/build/sources/linux/construire_appimage.sh"
"$PROJET/build/sources/linux/installer_linux.sh"

echo
echo "Jason est à jour dans le menu des applications."
