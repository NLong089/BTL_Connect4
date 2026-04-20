import pygame


SANS_CANDIDATES = [
    "segoeui",
    "arial",
    "tahoma",
    "calibri",
    "verdana",
    "dejavusans",
    "freesans",
]

SERIF_CANDIDATES = [
    "cambria",
    "georgia",
    "timesnewroman",
    "times",
]

_FONT_PATH_CACHE = {}
_FONT_CACHE = {}


def _resolve_font_path(candidates):
    key = tuple(candidates)
    if key in _FONT_PATH_CACHE:
        return _FONT_PATH_CACHE[key]

    for name in candidates:
        path = pygame.font.match_font(name)
        if path:
            _FONT_PATH_CACHE[key] = path
            return path

    _FONT_PATH_CACHE[key] = None
    return None


def get_ui_font(size, bold=False, serif=False):
    cache_key = (size, bold, serif)
    if cache_key in _FONT_CACHE:
        return _FONT_CACHE[cache_key]

    candidates = SERIF_CANDIDATES if serif else SANS_CANDIDATES
    font_path = _resolve_font_path(candidates)

    if font_path:
        font = pygame.font.Font(font_path, size)
    else:
        font = pygame.font.SysFont(None, size)

    font.set_bold(bold)
    _FONT_CACHE[cache_key] = font
    return font
