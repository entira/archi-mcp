"""
ArchiMate Core Module - Shared logic for MCP server and Claude Agent Skill

This module contains the core ArchiMate functionality that can be used
by both the MCP server and the Claude Agent Skill implementations.

Author: Mgr. Patrik Skovajsa
"""

from .archimate.generator import ArchiMateGenerator
from .archimate.validator import ArchiMateValidator
from .archimate.relationships import ArchiMateRelationship, RelationshipType
from .archimate.elements import (
    ArchiMateElement,
    ArchiMateLayer,
    ArchiMateAspect,
)

__all__ = [
    "ArchiMateGenerator",
    "ArchiMateValidator",
    "ArchiMateRelationship",
    "RelationshipType",
    "ArchiMateElement",
    "ArchiMateLayer",
    "ArchiMateAspect",
]
