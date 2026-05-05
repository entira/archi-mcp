"""Language dictionary modules for multilingual support."""

from .english import ENGLISH_DICT
from .slovak import SLOVAK_DICT
from .czech import CZECH_DICT

AVAILABLE_LANGUAGES = {
    "en": ENGLISH_DICT,
    "sk": SLOVAK_DICT,
    "cs": CZECH_DICT,
}

__all__ = ["ENGLISH_DICT", "SLOVAK_DICT", "CZECH_DICT", "AVAILABLE_LANGUAGES"]
