"""Noms de langues lisibles par un humain.

Le moteur de traduction ne connaît que des codes ("fr", "en", "pt").
L'interface, elle, ne doit jamais afficher un code brut : ce module fait la
traduction entre les deux mondes.

Chaque langue s'affiche sous la forme « CODE - nom natif » (ex.
« FRA - Français », « JPN - 日本語 ») : le code à trois lettres, toujours en
alphabet latin, aligne la liste et sert de repère universel ; le nom natif se
reconnaît d'un coup d'œil par qui parle la langue. Les drapeaux emoji ont été
abandonnés : ni Qt sous Linux, ni Windows ne savent les dessiner (voir le
journal du projet).
"""

# Code à trois lettres de chaque langue, d'après la norme ISO 639-2.
# Deux entorses assumées, pour que chaque entrée ait un code unique :
# PTB (portugais du Brésil, code repris de Microsoft) et ZHT (chinois
# traditionnel, usage informel répandu) — l'ISO ne distingue ni l'un ni
# l'autre de leur variante principale (POR, ZHO).
CODES_3 = {
    "ar": "ARA",
    "az": "AZE",
    "bg": "BUL",
    "bn": "BEN",
    "ca": "CAT",
    "cs": "CES",
    "da": "DAN",
    "de": "DEU",
    "el": "ELL",
    "en": "ENG",
    "eo": "EPO",
    "es": "SPA",
    "et": "EST",
    "eu": "EUS",
    "fa": "FAS",
    "fi": "FIN",
    "fr": "FRA",
    "ga": "GLE",
    "gl": "GLG",
    "he": "HEB",
    "hi": "HIN",
    "hu": "HUN",
    "id": "IND",
    "it": "ITA",
    "ja": "JPN",
    "ko": "KOR",
    "ky": "KIR",
    "lt": "LIT",
    "lv": "LAV",
    "ms": "MSA",
    "nb": "NOB",
    "nl": "NLD",
    "pb": "PTB",
    "pl": "POL",
    "pt": "POR",
    "ro": "RON",
    "ru": "RUS",
    "sk": "SLK",
    "sl": "SLV",
    "sq": "SQI",
    "sv": "SWE",
    "sw": "SWA",
    "th": "THA",
    "tl": "TGL",
    "tr": "TUR",
    "uk": "UKR",
    "ur": "URD",
    "vi": "VIE",
    "zh": "ZHO",
    "zt": "ZHT",
}

# Nom de chaque langue dans sa propre écriture.
NOMS_NATIFS = {
    "ar": "العربية",
    "az": "Azərbaycanca",
    "bg": "Български",
    "bn": "বাংলা",
    "ca": "Català",
    "cs": "Čeština",
    "da": "Dansk",
    "de": "Deutsch",
    "el": "Ελληνικά",
    "en": "English",
    "eo": "Esperanto",
    "es": "Español",
    "et": "Eesti",
    "eu": "Euskara",
    "fa": "فارسی",
    "fi": "Suomi",
    "fr": "Français",
    "ga": "Gaeilge",
    "gl": "Galego",
    "he": "עברית",
    "hi": "हिन्दी",
    "hu": "Magyar",
    "id": "Bahasa Indonesia",
    "it": "Italiano",
    "ja": "日本語",
    "ko": "한국어",
    "ky": "Кыргызча",
    "lt": "Lietuvių",
    "lv": "Latviešu",
    "ms": "Bahasa Melayu",
    "nb": "Norsk",
    "nl": "Nederlands",
    "pb": "Português (Brasil)",
    "pl": "Polski",
    "pt": "Português (Europa)",
    "ro": "Română",
    "ru": "Русский",
    "sk": "Slovenčina",
    "sl": "Slovenščina",
    "sq": "Shqip",
    "sv": "Svenska",
    "sw": "Kiswahili",
    "th": "ไทย",
    "tl": "Tagalog",
    "tr": "Türkçe",
    "uk": "Українська",
    "ur": "اردو",
    "vi": "Tiếng Việt",
    "zh": "简体中文",
    "zt": "繁體中文",
}


def code_3(code: str) -> str:
    """Code à trois lettres d'une langue, utilisé pour l'affichage et le tri."""
    return CODES_3.get(code, code.upper())


def nom(code: str) -> str:
    """Nom affichable d'une langue : « CODE - nom natif ».

    Si une langue inconnue apparaît un jour dans le catalogue, on affiche
    son code seul plutôt que de planter : l'interface reste utilisable.
    """
    natif = NOMS_NATIFS.get(code)
    if natif is None:
        return code.upper()
    return f"{code_3(code)} - {natif}"


def trier_par_nom(codes: list[str]) -> list[str]:
    """Ordonne des codes de langue par ordre alphabétique du code affiché.

    Le nom natif mélangerait plusieurs écritures (latin, cyrillique,
    idéogrammes...) dans un ordre qui ne voudrait rien dire ; le code à
    trois lettres, affiché en tête de chaque entrée, donne un ordre visible
    et cohérent.
    """
    return sorted(codes, key=code_3)
