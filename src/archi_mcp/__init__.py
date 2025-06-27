"""
ArchiMate MCP Server

A specialized MCP (Model Context Protocol) server for generating PlantUML ArchiMate diagrams
with comprehensive enterprise architecture modeling support.

This package provides:
- Full ArchiMate 3.2 specification support
- All 55+ ArchiMate elements across 7 layers
- All 12 ArchiMate relationship types
- Enterprise architecture templates and patterns
- PlantUML code generation and validation
"""

__version__ = "1.0.0"
__author__ = "Mgr. Patrik Skovajsa, Claude Code Assistant"
__email__ = ""
__license__ = "MIT"

from .server import mcp

__all__ = ["mcp"]