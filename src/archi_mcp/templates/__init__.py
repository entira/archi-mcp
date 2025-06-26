"""ArchiMate templates and patterns."""

from .viewpoints import ARCHIMATE_VIEWPOINTS, get_viewpoint_template
from .patterns import ARCHITECTURE_PATTERNS, get_pattern_template
from .industry import INDUSTRY_TEMPLATES, get_industry_template

__all__ = [
    "ARCHIMATE_VIEWPOINTS",
    "get_viewpoint_template",
    "ARCHITECTURE_PATTERNS", 
    "get_pattern_template",
    "INDUSTRY_TEMPLATES",
    "get_industry_template",
]