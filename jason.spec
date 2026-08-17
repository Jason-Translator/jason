# Recette d'empaquetage de Jason (PyInstaller).
#
#     .venv/bin/pyinstaller --noconfirm jason.spec
#
# Produit dist/jason/, un dossier autonome contenant Python, Qt, le moteur de
# traduction et le détecteur de langue. L'utilisateur n'installe rien.
#
# Les modèles de langues n'y sont PAS inclus : ils sont téléchargés au premier
# lancement, selon les langues choisies. C'est ce qui garde le paquet à une
# taille raisonnable et laisse l'utilisateur maître de ce qu'il installe.

import sys

from PyInstaller.utils.hooks import collect_all, collect_data_files

# Windows n'accepte que le format .ico ; ailleurs l'icône vient du fichier
# .desktop et non de l'exécutable.
ICONE = "build/sources/jason/ui/resources/jason.ico" if sys.platform == "win32" else None

donnees = [
    # Nos propres ressources. Le code les cherche à côté de app.py, donc on
    # reproduit l'arborescence du paquet à l'intérieur du bundle.
    ("build/sources/jason/ui/style.qss", "jason/ui"),
    ("build/sources/jason/ui/resources", "jason/ui/resources"),
]
binaires = []
imports_caches = []

# Ces bibliothèques chargent des fichiers de données ou des bibliothèques
# natives que PyInstaller ne repère pas en lisant seulement les imports :
#   lingua        les modèles de reconnaissance de langue (~290 Mo)
#   stanza        les ressources de découpage en phrases
#   ctranslate2   le moteur de calcul, en bibliothèque native
#   sentencepiece le tokeniseur, également natif
for paquet in ("lingua", "stanza", "ctranslate2", "sentencepiece", "argostranslate"):
    d, b, i = collect_all(paquet)
    donnees += d
    binaires += b
    imports_caches += i

# spacy déclare ses composants via des points d'entrée, invisibles à l'analyse.
donnees += collect_data_files("spacy")
imports_caches += ["spacy", "thinc", "blis", "srsly", "catalogue", "cymem", "preshed"]

analyse = Analysis(
    ["build/sources/jason/__main__.py"],
    pathex=["build/sources"],
    binaries=binaires,
    datas=donnees,
    hiddenimports=imports_caches,
    excludes=[
        # Jamais utilisés par Jason, et volumineux.
        "tkinter",
        "matplotlib",
        "IPython",
        "pytest",
    ],
    noarchive=False,
)

pyz = PYZ(analyse.pure)

exe = EXE(
    pyz,
    analyse.scripts,
    [],
    exclude_binaries=True,
    name="jason",
    console=False,  # pas de fenêtre de terminal derrière l'application
    icon=ICONE,
)

COLLECT(
    exe,
    analyse.binaries,
    analyse.datas,
    strip=False,
    upx=False,  # la compression UPX casse certaines bibliothèques natives
    name="jason",
)
