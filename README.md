# Jason

[English](README.en.md) · [Téléchargements](https://github.com/Jason-Translator/jason/releases)

**Traduisez sans connexion Internet, sans que rien ne quitte votre ordinateur.**

Jason traduit entièrement en local : aucun compte, aucune publicité, aucun
serveur. Une seule connexion est nécessaire, au premier lancement, pour
télécharger les langues choisies ; ensuite, tout fonctionne hors ligne.

## Utilisation

Au premier lancement, choisissez vos langues dans les **Paramètres** (flèche
de téléchargement). Le bouton rouage rouvre cette liste à tout moment, pour
en ajouter, en supprimer, ou changer de thème.

Écrivez à gauche, lisez à droite. La langue saisie est détectée
automatiquement ; en cas d'ambiguïté, Jason vous demande de préciser.

## Installation

### Linux

Téléchargez `Jason.AppImage`, rendez-le exécutable, double-cliquez :

```bash
chmod +x Jason.AppImage
./Jason.AppImage
```

Sans terminal : clic droit → *Propriétés* → *Permissions* → « Autoriser
l'exécution du fichier comme un programme ».

### Windows

Téléchargez `JasonInstallateur.exe`, double-cliquez, suivez les trois écrans.
Aucun droit administrateur requis.

Désactivez votre antivirus (Avast, Bitdefender, AVG...) **avant**
l'installation : certains la corrompent silencieusement. Si SmartScreen
s'affiche, cliquez sur *Informations complémentaires* → *Exécuter quand
même* — Jason n'est pas signé chez Microsoft, faute de budget.

### Construire depuis les sources

#### Linux

Prérequis : **Python 3.11+**.

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
# torch depuis l'index CPU, sinon pip télécharge 4,6 Go de CUDA inutiles :
.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu
.venv/bin/python -m jason
```

Pour fabriquer l'AppImage : voir `build/GUIDE.md`.

#### Windows

Prérequis :

- **Python 3.11+**, avec *« Add python.exe to PATH »* coché à l'installation
  (sinon, lancez `python` une fois en console et approuvez l'ajout au PATH).
- [Inno Setup 6](https://jrsoftware.org/isdl.php) (installation par défaut).

Double-cliquez `build\sources\windows\construire_installateur.ps1` (ou le
`.bat` à côté). Il installe les dépendances, empaquette, teste, et produit
`apps\windows\JasonInstallateur.exe`.

## Comment c'est fait

Jason s'appuie sur des moteurs libres existants :

| Rôle | Outil |
|---|---|
| Interface | PySide6 (Qt) |
| Traduction | Argos Translate |
| Reconnaissance de la langue | Lingua |

Règle du code : **`core/` ignore l'interface, `ui/` ignore le moteur.**
`workers.py` les relie, dans un thread séparé pour ne pas geler la fenêtre.

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

## Outils de contrôle

```bash
# Traduire depuis la console, sans interface
.venv/bin/python build/scripts/essai.py fr en "Bonjour le monde"

# Vérifier qu'aucun modèle installé ne produit de texte incohérent
.venv/bin/python build/scripts/audit_modeles.py
```

Le second existe parce que certains modèles publiés en amont sont
défectueux ; Jason contourne les cas connus (`MODELES_DE_REMPLACEMENT` dans
`core/packages.py`) et ce script en repère de nouveaux.

## Dépendances

| Bibliothèque / outil | Rôle | Licence |
|---|---|---|
| [Argos Translate](https://github.com/argosopentech/argos-translate) | moteur de traduction | MIT |
| [CTranslate2](https://github.com/OpenNMT/CTranslate2) | inférence (utilisé par Argos Translate) | MIT |
| [Stanza](https://github.com/stanfordnlp/stanza) | découpage de phrases | Apache-2.0 |
| [Lingua](https://github.com/pemistahl/lingua-rs) | reconnaissance de la langue | Apache-2.0 |
| [SentencePiece](https://github.com/google/sentencepiece) | tokenisation (dépendance d'Argos Translate) | Apache-2.0 |
| [Sacremoses](https://github.com/hplt-project/sacremoses) | dépendance d'Argos Translate | MIT |
| [PyTorch](https://github.com/pytorch/pytorch) | calcul (utilisé par Stanza) | BSD-3-Clause |
| [PySide6 (Qt for Python)](https://www.qt.io/qt-for-python) | interface graphique | LGPL-3.0 |
| [Python](https://www.python.org/) | langage | PSF License |
| [Hatchling](https://github.com/pypa/hatch) | build backend | MIT |
| [PyInstaller](https://github.com/pyinstaller/pyinstaller) | empaquetage en exécutable | GPLv2+ (avec exception pour l'exécutable produit) |
| [AppImageKit](https://github.com/AppImage/AppImageKit) | empaquetage Linux (AppImage) | MIT |
| [Inno Setup](https://jrsoftware.org/isinfo.php) | empaquetage Windows (installateur) | Licence Inno Setup (gratuite, non-OSI) |

PySide6/Qt est distribué en liaison dynamique : Jason lui-même reste sous
licence MIT, seule cette dépendance reste sous LGPL-3.0.

## Limites connues

- La traduction passe toujours par l'anglais : espagnol → français est donc
  un peu moins fidèle qu'espagnol → anglais.
- Un texte trop court peut empêcher une détection fiable de la langue ;
  Jason vous laisse alors choisir.

## Droits

© François Guerin. Publié sous licence [MIT](LICENSE). Bibliothèques
tierces sous leurs licences respectives (voir Dépendances ci-dessus).
