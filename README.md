# Jason

[Téléchargement](https://github.com/Jason-Translator/jason/releases)

**Traduisez vos textes sans connexion Internet, et sans que rien ne quitte votre ordinateur.**

Jason est un traducteur qui fonctionne entièrement sur votre machine. Aucun
compte, aucune publicité, aucun serveur : le texte que vous écrivez n'est
envoyé nulle part.

Une seule connexion est nécessaire, au premier lancement, pour télécharger les
langues que vous choisissez. Ensuite, Jason fonctionne hors ligne, y compris
dans un train, un avion ou un pays sans forfait de données.

## Utilisation

Au premier lancement, Jason ouvre les **Paramètres** sur la liste des
langues : installez celles dont vous avez besoin d'un clic sur leur flèche de
téléchargement. À tout moment, le bouton rouage rouvre cette même liste, pour
ajouter une langue ou la supprimer (la corbeille) — les Paramètres règlent
aussi le thème clair ou sombre.

Ensuite, écrivez à gauche, lisez à droite. La langue du texte saisi est
reconnue automatiquement ; si elle est ambiguë, Jason vous le dit plutôt que
de deviner au hasard.

## Installation

### Linux

Téléchargez le fichier `Jason.AppImage`, rendez-le exécutable, double-cliquez.
Rien d'autre à installer.

```bash
chmod +x Jason.AppImage
./Jason.AppImage
```

### Windows

Téléchargez `JasonInstallateur.exe`, double-cliquez, suivez les trois écrans.
Rien d'autre à installer, aucun droit administrateur nécessaire.

### Construire depuis les sources

#### Linux

Prérequis à installer une seule fois, à la main :

- **Python 3.11 ou plus récent** (construit et testé avec Python 3.14).

Pour lancer Jason directement depuis les sources :

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
# torch doit venir de l'index processeur, sinon pip télécharge 4,6 Go
# de bibliothèques CUDA parfaitement inutiles ici :
.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu
.venv/bin/python -m jason
```

Fabriquer l'AppImage (la commande qui fait tout, y compris l'installation
des dépendances) : voir `build/GUIDE.md`.

#### Windows

Prérequis à installer une seule fois, à la main :

- **Python 3.11 ou plus récent** (construit et testé avec Python 3.14), en
  cochant *« Add python.exe to PATH »* à l'installation. Si vous ne voyez
  pas cette case à cocher, par exemple si vous avez utilisé
  [Python Install Manager](https://apps.microsoft.com/detail/9nq7512cxl7t),
  lancez python une fois dans la console, puis approuvez `y` l'ajout de
  python dans le PATH.
- [Inno Setup 6](https://jrsoftware.org/isdl.php) (installation par défaut),
  pour fabriquer l'installateur.

Double-cliquez `build\sources\windows\construire_installateur.ps1` — ou,
plus simple, le fichier `.bat` juste à côté, qui l'appelle pour vous sans
passer par la ligne de commande. Il installe les dépendances, empaquette,
vérifie que l'application traduit vraiment, puis produit
`apps\windows\JasonInstallateur.exe`.

## Comment c'est fait

Jason ne réinvente pas la traduction : il s'appuie sur des moteurs libres
existants et leur donne une interface que tout le monde peut utiliser.

| Rôle | Outil |
|---|---|
| Interface | PySide6 (Qt) |
| Traduction | Argos Translate |
| Reconnaissance de la langue | Lingua |

L'organisation du code suit une règle simple : **`core/` ne connaît pas
l'interface, `ui/` ne connaît pas le moteur.** Les deux communiquent par
`workers.py`, qui exécute les calculs dans un thread séparé — sans quoi la
fenêtre se figerait à chaque traduction.

```
apps/                fabriqué → livrable, prêt à distribuer
├── linux/Jason-x86_64.AppImage
└── windows/

build/                tout ce qu'il faut pour fabriquer Jason (voir build/GUIDE.md)
├── sources/
│   ├── jason/           le paquet Python, partagé Linux/Windows (interface comprise)
│   │   ├── core/           traduction, langues, téléchargement (sans Qt)
│   │   │   ├── translator.py
│   │   │   ├── packages.py
│   │   │   ├── detect.py
│   │   │   └── languages.py
│   │   ├── ui/             fenêtre et écran des langues (sans Argos)
│   │   ├── workers.py      le pont entre les deux
│   │   └── app.py
│   ├── linux/            empaquetage Linux : AppImage, raccourci, installateur
│   └── windows/           empaquetage Windows : installateur Inno Setup
├── scripts/              outils de contrôle en console (voir plus bas)
└── cache_pyinstaller/, dist/, tmp/   dossiers de travail régénérables
```

Détail de `build/` dans `build/GUIDE.md`.

## Outils de contrôle

```bash
# Traduire depuis la console, sans interface
.venv/bin/python build/scripts/essai.py fr en "Bonjour le monde"

# Vérifier qu'aucun modèle installé ne produit de texte incohérent
.venv/bin/python build/scripts/audit_modeles.py
```

Le second mérite une explication : certains modèles publiés en amont sont
défectueux et renvoient du charabia. Jason contourne les cas connus
(voir `MODELES_DE_REMPLACEMENT` dans `core/packages.py`) ; ce script sert à en
repérer de nouveaux après avoir installé des langues.

## Limites connues

- La traduction passe par l'anglais pour relier deux autres langues entre
  elles. Espagnol → français est donc un peu moins fidèle que espagnol →
  anglais. C'est le fonctionnement du moteur, pas un réglage.
- Un texte de deux ou trois mots peut être trop court pour reconnaître sa
  langue avec certitude. Dans ce cas, Jason le signale et vous laisse choisir.

## Droits

© François Guerin. Tous droits réservés — l'absence de fichier de licence
est un choix, pas un oubli : le code est publié pour être lu et vérifié,
pas (encore) pour être réutilisé. Les bibliothèques tierces restent sous
leurs licences respectives.
