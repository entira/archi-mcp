"""ArchiMate XML Exchange Export Module

Modular and easily removable XML export functionality for ArchiMate Exchange format.
Supports ArchiMate 3.2 elements exported using ArchiMate 3.0 XML schema (backward compatible).

This module is designed to be:
- Easily portable between projects
- Completely removable without affecting core functionality
- Standards-compliant with Open Group ArchiMate Exchange specification
"""

from .exporter import ArchiMateXMLExporter
from .validator import ArchiMateXMLValidator
from .templates import XMLTemplates

__version__ = "1.0.0"
__author__ = "Mgr. Patrik Skovajsa, Claude Code Assistant"

__all__ = [
    "ArchiMateXMLExporter",
    "ArchiMateXMLValidator", 
    "XMLTemplates"
]