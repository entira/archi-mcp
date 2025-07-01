"""Internationalization support for ArchiMate MCP server."""

from .translator import ArchiMateTranslator
from .languages import AVAILABLE_LANGUAGES

__all__ = ["ArchiMateTranslator", "AVAILABLE_LANGUAGES"]