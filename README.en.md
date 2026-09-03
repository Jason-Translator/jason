# Jason

[Français](README.md) · [Downloads](https://github.com/Jason-Translator/jason/releases)

*Only the French [README.md](README.md) is authoritative; this is a
convenience translation and may lag behind it.*

**Translate offline, with nothing ever leaving your computer.**

Jason translates entirely locally: no account, no ads, no server. A single
connection is needed on first launch, to download the languages you pick;
after that, everything works offline.

## Usage

On first launch, pick your languages in **Settings** (download arrow). The
gear button reopens this list any time, to add or remove a language, or
switch theme.

Write on the left, read on the right. The input language is detected
automatically; if it's ambiguous, Jason asks you to clarify.

## Installation

### Linux

Download `Jason.AppImage`, make it executable, double-click:

```bash
chmod +x Jason.AppImage
./Jason.AppImage
```

Without a terminal: right-click → *Properties* → *Permissions* → "Allow
executing file as program".

### Windows

Download `JasonInstallateur.exe`, double-click, follow the three screens.
Nothing else to install, no admin rights needed.

Disable your antivirus (Avast, Bitdefender, AVG...) **before** installing:
some corrupt the install silently. If SmartScreen shows up, click *More
info* → *Run anyway* — Jason isn't signed with Microsoft, for lack of
budget.

### Building from source

#### Linux

Prerequisite: **Python 3.11+**.

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
# torch must come from the CPU index, or pip pulls 4.6 GB of useless CUDA:
.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu
.venv/bin/python -m jason
```

To build the AppImage: see `build/GUIDE.md`.

#### Windows

Prerequisites:

- **Python 3.11+**, with *"Add python.exe to PATH"* checked during install
  (otherwise, run `python` once in a console and approve adding it to PATH).
- [Inno Setup 6](https://jrsoftware.org/isdl.php) (default install).

Double-click `build\sources\windows\construire_installateur.ps1` (or the
`.bat` next to it). It installs dependencies, packages, tests, and produces
`apps\windows\JasonInstallateur.exe`.

## How it's built

Jason doesn't reinvent translation: it relies on existing free engines.

| Role | Tool |
|---|---|
| Interface | PySide6 (Qt) |
| Translation | Argos Translate |
| Language detection | Lingua |

Code rule: **`core/` doesn't know about the interface, `ui/` doesn't know
about the engine.** `workers.py` connects them, on a separate thread so the
window doesn't freeze.

```
apps/                built → ready-to-distribute deliverable
├── linux/Jason-x86_64.AppImage
└── windows/

build/                everything needed to build Jason (see build/GUIDE.md)
├── sources/
│   ├── jason/           the Python package, shared Linux/Windows (interface included)
│   │   ├── core/           translation, languages, downloads (no Qt)
│   │   │   ├── translator.py
│   │   │   ├── packages.py
│   │   │   ├── detect.py
│   │   │   └── languages.py
│   │   ├── ui/             window and language screen (no Argos)
│   │   ├── workers.py      the bridge between the two
│   │   └── app.py
│   ├── linux/            Linux packaging: AppImage, shortcut, installer
│   └── windows/           Windows packaging: Inno Setup installer
├── scripts/              console control tools (see below)
└── cache_pyinstaller/, dist/, tmp/   regenerable working directories
```

## Control tools

```bash
# Translate from the console, no interface
.venv/bin/python build/scripts/essai.py fr en "Bonjour le monde"

# Check that no installed model produces incoherent text
.venv/bin/python build/scripts/audit_modeles.py
```

The second one deserves an explanation: some upstream models are broken and
return gibberish. Jason works around known cases
(`MODELES_DE_REMPLACEMENT` in `core/packages.py`); this script finds new
ones after installing languages.

## Dependencies

| Library / tool | Role | License |
|---|---|---|
| [Argos Translate](https://github.com/argosopentech/argos-translate) | translation engine | MIT |
| [CTranslate2](https://github.com/OpenNMT/CTranslate2) | inference (used by Argos Translate) | MIT |
| [Stanza](https://github.com/stanfordnlp/stanza) | sentence segmentation | Apache-2.0 |
| [Lingua](https://github.com/pemistahl/lingua-rs) | language detection | Apache-2.0 |
| [SentencePiece](https://github.com/google/sentencepiece) | tokenization (Argos Translate dependency) | Apache-2.0 |
| [Sacremoses](https://github.com/hplt-project/sacremoses) | Argos Translate dependency | MIT |
| [PyTorch](https://github.com/pytorch/pytorch) | computation (used by Stanza) | BSD-3-Clause |
| [PySide6 (Qt for Python)](https://www.qt.io/qt-for-python) | graphical interface | LGPL-3.0 |
| [Python](https://www.python.org/) | language | PSF License |
| [Hatchling](https://github.com/pypa/hatch) | build backend | MIT |
| [PyInstaller](https://github.com/pyinstaller/pyinstaller) | packaging into an executable | GPLv2+ (with an exception for the produced executable) |
| [AppImageKit](https://github.com/AppImage/AppImageKit) | Linux packaging (AppImage) | MIT |
| [Inno Setup](https://jrsoftware.org/isinfo.php) | Windows packaging (installer) | Inno Setup License (free, non-OSI) |

PySide6/Qt is distributed dynamically linked: Jason itself stays under the
MIT license, only this dependency remains under LGPL-3.0.

## Known limitations

- Translation always goes through English: Spanish → French is therefore
  slightly less accurate than Spanish → English.
- A very short text may not give enough signal for reliable language
  detection; Jason then asks you to choose.

## Rights

© François Guerin. Released under the [MIT license](LICENSE). Third-party
libraries remain under their respective licenses (see Dependencies above).
