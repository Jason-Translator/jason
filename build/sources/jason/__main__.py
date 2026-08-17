"""Permet de lancer Jason par `python -m jason`.

L'import est volontairement absolu et non relatif : ce fichier sert aussi de
point d'entrée à l'application empaquetée, où il est exécuté comme un script
isolé, sans paquet parent — un import relatif y échouerait.
"""

import multiprocessing
import sys

if __name__ == "__main__":
    # Indispensable pour un exécutable figé (PyInstaller/AppImage). Le
    # découpage de phrases avant traduction charge `torch`, qui démarre en
    # coulisses une petite tâche `multiprocessing.resource_tracker` — en la
    # relançant via `sys.executable`. Sans cette ligne, l'exécutable figé ne
    # reconnaît pas cette relance interne et exécute Jason en entier une
    # deuxième fois : une fenêtre en trop, et deux processus qui tentent de
    # charger les mêmes bibliothèques natives en même temps (source du
    # plantage SIGBUS observé). `freeze_support()` intercepte cette relance
    # avant qu'elle n'atteigne le reste du programme.
    multiprocessing.freeze_support()

    from jason.app import main

    sys.exit(main())
