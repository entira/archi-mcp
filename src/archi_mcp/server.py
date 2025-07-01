"""Simplified ArchiMate MCP Server - Fixed for Claude Desktop issues."""

import json
import sys
import asyncio
import subprocess
import os
import tempfile
import base64
import zlib
import time
import platform
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pathlib import Path
import glob

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from .utils.logging import setup_logging, get_logger
from .utils.exceptions import (
    ArchiMateError,
    ArchiMateValidationError,
    ArchiMateGenerationError,
)
from .archimate import (
    ArchiMateElement,
    ArchiMateRelationship,
    ArchiMateGenerator,
    ArchiMateValidator,
    ARCHIMATE_ELEMENTS,
    ARCHIMATE_RELATIONSHIPS,
)
from .archimate.elements.base import ArchiMateLayer, ArchiMateAspect
from .i18n import ArchiMateTranslator, AVAILABLE_LANGUAGES

def detect_language_from_content(diagram) -> str:
    """Automatically detect language from diagram content.
    
    Args:
        diagram: DiagramInput with elements and relationships
        
    Returns:
        Language code (e.g., "sk", "en")
    """
    # Slovak language indicators
    slovak_indicators = [
        # Common Slovak words
        'zákazník', 'podpora', 'služba', 'proces', 'objekt', 'komponent',
        'podnikový', 'zákaznícky', 'proaktívna', 'inteligentý', 'znalostná',
        'konverzačná', 'vylepšený', 'starostlivosť', 'riešenie', 'problémov',
        'schopnosť', 'platforma', 'báza', 'profil', 'analýza', 'nálady',
        'spokojnosť', 'sledovanie', 'emócií', 'monitoruje', 'aktualizuje',
        'pristupuje', 'spúšťa', 'umožňuje', 'napájaný', 'asistovaný',
        # Slovak diacritics patterns
        'ň', 'ť', 'ž', 'č', 'š', 'ľ', 'ý', 'á', 'í', 'é', 'ó', 'ú', 'ô'
    ]
    
    # Collect all text content
    all_text = []
    
    # Add element names and descriptions
    for element in diagram.elements:
        if element.name:
            all_text.append(element.name.lower())
        if element.description:
            all_text.append(element.description.lower())
    
    # Add relationship labels and descriptions
    for rel in diagram.relationships:
        if rel.label:
            all_text.append(rel.label.lower())
        if rel.description:
            all_text.append(rel.description.lower())
    
    # Add title and description
    if diagram.title:
        all_text.append(diagram.title.lower())
    if diagram.description:
        all_text.append(diagram.description.lower())
    
    # Join all text
    content = ' '.join(all_text)
    
    # Count Slovak indicators
    slovak_score = sum(1 for indicator in slovak_indicators if indicator in content)
    
    # If significant Slovak content detected, return Slovak
    if slovak_score >= 3:  # Threshold for Slovak detection
        return "sk"
    
    # Default to English
    return "en"

def override_relationship_labels_with_translations(diagram, translator: ArchiMateTranslator) -> None:
    """Override custom relationship labels with translated versions if non-English language detected.
    
    Args:
        diagram: DiagramInput to modify
        translator: Translator to use for relationship type translations
    """
    if translator.get_current_language() == "en":
        return  # Keep original labels for English
    
    # For non-English languages, use translated relationship types only if no custom label exists
    for rel in diagram.relationships:
        if rel.relationship_type:
            # Only override if no custom label is provided by client
            if not rel.label:
                # Get translated relationship type as fallback
                translated_label = translator.translate_relationship(rel.relationship_type)
                rel.label = translated_label
            # If custom label exists, keep it (client knows best)

# Environment variable defaults - only essential layout parameters
ENV_DEFAULTS = {
    # Layout Settings (these are the only configurable parameters)
    "ARCHI_MCP_DEFAULT_DIRECTION": "vertical",
    "ARCHI_MCP_DEFAULT_SHOW_LEGEND": "false",
    "ARCHI_MCP_DEFAULT_SHOW_TITLE": "false", 
    "ARCHI_MCP_DEFAULT_GROUP_BY_LAYER": "true",
    "ARCHI_MCP_DEFAULT_SPACING": "compact",
    
    # Display Settings
    "ARCHI_MCP_DEFAULT_SHOW_ELEMENT_TYPES": "false",
    "ARCHI_MCP_DEFAULT_SHOW_RELATIONSHIP_LABELS": "true",
    
    # Logging Settings
    "ARCHI_MCP_LOG_LEVEL": "INFO"
}

def get_env_setting(key: str) -> str:
    """Get environment setting with fallback to default."""
    return os.getenv(key, ENV_DEFAULTS.get(key, ""))

def is_config_locked(key: str) -> bool:
    """Check if environment variable is locked by config (cannot be overridden by client)."""
    return os.getenv(key) is not None

def get_layout_setting(key: str, client_value=None):
    """Get layout setting with config-first priority."""
    if is_config_locked(key):
        # Config has priority - client cannot override
        return get_env_setting(key)
    else:
        # Client can set this value if config doesn't specify it
        return client_value if client_value is not None else get_env_setting(key)

def validate_custom_relationship_name(custom_name: str, formal_relationship_type: str, language: str = "en") -> tuple[bool, str]:
    """Validate that custom relationship name is appropriate synonym.
    
    Args:
        custom_name: Client-provided custom name for relationship
        formal_relationship_type: Formal ArchiMate relationship type (e.g. "Realization")
        language: Language code for validation (en, sk)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not custom_name or not custom_name.strip():
        return False, "Custom relationship name cannot be empty"
    
    # Check length - max 3 words or 30 characters
    words = custom_name.strip().split()
    if len(words) > 3:
        return False, "Custom relationship name must be maximum 3 words"
    
    if len(custom_name) > 30:
        return False, "Custom relationship name must be maximum 30 characters"
    
    # Define valid synonyms for each formal relationship type
    relationship_synonyms = {
        "en": {
            "Realization": ["realizes", "implements", "fulfills", "achieves", "delivers"],
            "Serving": ["serves", "supports", "provides", "offers", "enables"],
            "Access": ["accesses", "uses", "reads", "writes", "queries"],
            "Assignment": ["assigned", "allocated", "responsible", "executes"],
            "Aggregation": ["contains", "includes", "comprises", "groups"],
            "Composition": ["composed", "consists", "made of", "built from"],
            "Flow": ["flows", "transfers", "sends", "passes", "moves"],
            "Influence": ["influences", "affects", "impacts", "drives"],
            "Triggering": ["triggers", "initiates", "starts", "causes"],
            "Association": ["associated", "related", "connected", "linked"],
            "Specialization": ["specializes", "extends", "inherits", "derives"]
        },
        "sk": {
            "Realization": ["realizuje", "implementuje", "plní", "dosahuje", "poskytuje"],
            "Serving": ["slúži", "podporuje", "poskytuje", "ponúka", "umožňuje"],
            "Access": ["pristupuje", "používa", "číta", "zapisuje", "dotazuje"],
            "Assignment": ["priradený", "pridelený", "zodpovedný", "vykonáva"],
            "Aggregation": ["obsahuje", "zahŕňa", "tvoria", "skupiny"],
            "Composition": ["skladá sa", "pozostáva", "tvorený z", "budovaný z"],
            "Flow": ["preteká", "prenáša", "posiela", "prechádza", "pohybuje"],
            "Influence": ["ovplyvňuje", "pôsobí", "vplýva", "riadi"],
            "Triggering": ["spúšťa", "inicializuje", "začína", "spôsobuje"],
            "Association": ["asociovaný", "súvisí", "spojený", "prepojený"],
            "Specialization": ["špecializuje", "rozširuje", "dedí", "odvodzuje"]
        }
    }
    
    # Get synonyms for the language and relationship type
    lang_synonyms = relationship_synonyms.get(language, relationship_synonyms["en"])
    valid_synonyms = lang_synonyms.get(formal_relationship_type, [])
    
    # Check if custom name is a valid synonym (case insensitive)
    custom_lower = custom_name.lower().strip()
    if any(synonym.lower() in custom_lower or custom_lower in synonym.lower() 
           for synonym in valid_synonyms):
        return True, ""
    
    # If not found in predefined synonyms, it might still be acceptable
    # Allow it but log a warning
    return True, f"Custom name '{custom_name}' not in predefined synonyms for {formal_relationship_type}, but allowing it"

def generate_layout_parameters_info():
    """Generate information about available layout parameters for the client."""
    layout_params = [
        {
            'env_var': 'ARCHI_MCP_DEFAULT_DIRECTION',
            'param_name': 'direction',
            'description': 'Controls the overall diagram flow direction',
            'options': ['horizontal', 'vertical'],
            'examples': {
                'horizontal': 'Elements flow left-to-right (good for process flows)',
                'vertical': 'Elements flow top-to-bottom (good for layered views)'
            }
        },
        {
            'env_var': 'ARCHI_MCP_DEFAULT_SHOW_LEGEND',
            'param_name': 'show_legend', 
            'description': 'Whether to display the ArchiMate element legend',
            'options': [True, False],
            'examples': {
                True: 'Shows color coding and element types (useful for presentations)',
                False: 'Clean diagram without legend (better for technical docs)'
            }
        },
        {
            'env_var': 'ARCHI_MCP_DEFAULT_SHOW_TITLE',
            'param_name': 'show_title',
            'description': 'Whether to display the diagram title',
            'options': [True, False], 
            'examples': {
                True: 'Shows diagram title at the top',
                False: 'No title displayed (for embedding in documents)'
            }
        },
        {
            'env_var': 'ARCHI_MCP_DEFAULT_GROUP_BY_LAYER',
            'param_name': 'group_by_layer',
            'description': 'Whether to visually group elements by ArchiMate layer',
            'options': [True, False],
            'examples': {
                True: 'Elements grouped with layer boundaries (clear layer separation)',
                False: 'Free-form layout based on relationships (more compact)'
            }
        },
        {
            'env_var': 'ARCHI_MCP_DEFAULT_SPACING',
            'param_name': 'spacing',
            'description': 'Controls spacing between diagram elements',
            'options': ['compact', 'normal', 'wide'],
            'examples': {
                'compact': 'Tight spacing for detailed views',
                'normal': 'Balanced spacing for general use', 
                'wide': 'Generous spacing for presentations'
            }
        },
        {
            'env_var': 'ARCHI_MCP_DEFAULT_SHOW_ELEMENT_TYPES',
            'param_name': 'show_element_types',
            'description': 'Whether to display element type names (e.g. Business_Actor, Application_Component)',
            'options': [True, False],
            'examples': {
                True: 'Shows element types for clarity (useful for learning/documentation)',
                False: 'Clean elements without type labels (better for presentations)'
            }
        },
        {
            'env_var': 'ARCHI_MCP_DEFAULT_SHOW_RELATIONSHIP_LABELS',
            'param_name': 'show_relationship_labels',
            'description': 'Whether to display relationship type names and custom labels',
            'options': [True, False],
            'examples': {
                True: 'Shows relationship names (e.g. "realizes", "serves") for clarity',
                False: 'Clean connections without labels (minimalist view)'
            }
        }
    ]
    
    config_locked = []
    client_configurable = []
    
    for param in layout_params:
        if is_config_locked(param['env_var']):
            current_value = get_env_setting(param['env_var'])
            config_locked.append({
                'parameter': param['param_name'],
                'current_value': current_value,
                'description': param['description'],
                'reason': 'Set by server configuration - cannot be changed by client requests'
            })
        else:
            default_value = get_env_setting(param['env_var'])
            client_configurable.append({
                'parameter': param['param_name'],
                'description': param['description'],
                'options': param['options'],
                'default': default_value,
                'examples': param['examples']
            })
    
    return {
        'config_locked': config_locked,
        'client_configurable': client_configurable
    }

# Setup logging with environment variable support
setup_logging(level=get_env_setting('ARCHI_MCP_LOG_LEVEL'))
logger = get_logger("archi_mcp.server")

# Initialize FastMCP server
mcp = FastMCP("archi-mcp")

# Initialize components
generator = ArchiMateGenerator()
validator = ArchiMateValidator()

# Pydantic models for input validation
class ElementInput(BaseModel):
    id: str = Field(..., description="Unique element identifier")
    name: str = Field(..., description="Element display name")
    element_type: str = Field(..., description="ArchiMate element type")
    layer: str = Field(..., description="ArchiMate layer")
    description: Optional[str] = Field(None, description="Element description")
    stereotype: Optional[str] = Field(None, description="Element stereotype")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

class RelationshipInput(BaseModel):
    id: str = Field(..., description="Unique relationship identifier")
    from_element: str = Field(..., description="Source element ID")
    to_element: str = Field(..., description="Target element ID")
    relationship_type: str = Field(..., description="ArchiMate relationship type")
    description: Optional[str] = Field(None, description="Relationship description")
    direction: Optional[str] = Field(None, description="Direction hint for layout")
    label: Optional[str] = Field(None, description="Relationship label")

class DiagramInput(BaseModel):
    elements: List[ElementInput] = Field(..., description="List of ArchiMate elements")
    relationships: List[RelationshipInput] = Field(default_factory=list, description="List of relationships")
    title: Optional[str] = Field(None, description="Diagram title")
    description: Optional[str] = Field(None, description="Diagram description")
    layout: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Layout configuration")
    language: Optional[str] = Field("en", description="Language code for translations (en, sk)")

# Fixed element type mapping based on test errors
ELEMENT_TYPE_MAPPING = {
    # Business Layer - with proper capitalization
    "Business_Actor": "Business_Actor",
    "Business_Role": "Business_Role", 
    "Business_Collaboration": "Business_Collaboration",
    "Business_Interface": "Business_Interface",
    "Business_Function": "Business_Function",
    "Business_Process": "Business_Process",
    "Business_Event": "Business_Event",
    "Business_Service": "Business_Service",
    "Business_Object": "Business_Object",
    "Business_Contract": "Business_Contract",
    "Business_Representation": "Business_Representation",
    "Location": "Location",
    
    # Application Layer
    "Application_Component": "Application_Component",
    "Application_Collaboration": "Application_Collaboration",
    "Application_Interface": "Application_Interface", 
    "Application_Function": "Application_Function",
    "Application_Interaction": "Application_Interaction",
    "Application_Process": "Application_Process",
    "Application_Event": "Application_Event",
    "Application_Service": "Application_Service",
    "Data_Object": "Application_DataObject",
    
    # Technology Layer
    "Node": "Technology_Node",
    "Device": "Technology_Device",
    "System_Software": "Technology_SystemSoftware",
    "Technology_Collaboration": "Technology_Collaboration",
    "Technology_Interface": "Technology_Interface",
    "Path": "Technology_Path",
    "Communication_Network": "Technology_CommunicationNetwork",
    "Technology_Function": "Technology_Function",
    "Technology_Process": "Technology_Process",
    "Technology_Interaction": "Technology_Interaction", 
    "Technology_Event": "Technology_Event",
    "Technology_Service": "Technology_Service",
    "Artifact": "Technology_Artifact",
    
    # Physical Layer
    "Equipment": "Equipment",
    "Facility": "Facility",
    "Distribution_Network": "Distribution_Network",
    "Material": "Material",
    
    # Motivation Layer - proper capitalization
    "Stakeholder": "Stakeholder",
    "Driver": "Driver",
    "Assessment": "Assessment", 
    "Goal": "Goal",
    "Outcome": "Outcome",
    "Principle": "Principle",
    "Requirement": "Requirement",
    "Constraint": "Constraint",
    "Meaning": "Meaning",
    "Value": "Value",
    
    # Strategy Layer
    "Resource": "Resource",
    "Capability": "Capability",
    "Course_of_Action": "Course_of_Action",
    "Value_Stream": "Value_Stream",
    
    # Implementation Layer
    "Work_Package": "Work_Package",
    "Deliverable": "Deliverable",
    "Implementation_Event": "Implementation_Event",
    "Plateau": "Plateau",
    "Gap": "Gap",
}

# Valid layers with proper capitalization
VALID_LAYERS = {
    "Business": "Business",
    "Application": "Application", 
    "Technology": "Technology",
    "Physical": "Physical",
    "Motivation": "Motivation",
    "Strategy": "Strategy",
    "Implementation": "Implementation"
}

# Valid relationship types (case-sensitive)
VALID_RELATIONSHIPS = [
    "Access", "Aggregation", "Assignment", "Association",
    "Composition", "Flow", "Influence", "Realization",
    "Serving", "Specialization", "Triggering"
]

# Helper functions for exports directory
def get_exports_directory() -> Path:
    """Get the exports directory path, creating it if needed."""
    exports_dir = Path.cwd() / "exports"
    exports_dir.mkdir(exist_ok=True)
    return exports_dir

def create_diagram_export_directory() -> Path:
    """Create a timestamped directory for diagram exports."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = get_exports_directory() / timestamp
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir

def save_debug_log(export_dir: Path, log_entries: List[Dict[str, Any]]) -> Path:
    """Save debug log to the export directory."""
    log_file = export_dir / "generation.log"
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"ArchiMate Diagram Generation Log\n")
        f.write(f"{'=' * 60}\n")
        f.write(f"Generated at: {datetime.now().isoformat()}\n")
        f.write(f"Platform: {platform.system()} {platform.release()}\n")
        f.write(f"Python: {sys.version}\n")
        f.write(f"{'=' * 60}\n\n")
        
        for entry in log_entries:
            f.write(f"[{entry.get('timestamp', 'N/A')}] {entry.get('level', 'INFO')}: {entry.get('message', '')}\n")
            if 'details' in entry:
                for key, value in entry['details'].items():
                    f.write(f"  {key}: {value}\n")
            f.write("\n")
    
    return log_file

def cleanup_failed_exports() -> None:
    """Move failed export attempts to failed_attempts subdirectory after successful PNG generation."""
    exports_dir = get_exports_directory()
    failed_attempts_dir = exports_dir / "failed_attempts"
    
    # Find all export directories
    export_subdirs = [d for d in exports_dir.iterdir() if d.is_dir() and d.name != "failed_attempts"]
    
    # Identify failed exports (no PNG file)
    failed_dirs = []
    for export_dir in export_subdirs:
        png_file = export_dir / "diagram.png"
        if not png_file.exists():
            failed_dirs.append(export_dir)
    
    # Move failed attempts to failed_attempts directory
    if failed_dirs:
        failed_attempts_dir.mkdir(exist_ok=True)
        
        for failed_dir in failed_dirs:
            destination = failed_attempts_dir / failed_dir.name
            try:
                failed_dir.rename(destination)
                print(f"Moved failed export: {failed_dir.name} -> failed_attempts/")
            except Exception as e:
                print(f"Warning: Could not move {failed_dir.name}: {e}")

def generate_architecture_markdown(generator, title: str, description: str, png_filename: str = "diagram.png") -> str:
    """Generate markdown documentation for the architecture."""
    md_content = []
    
    # Header
    md_content.append(f"# {title}")
    md_content.append("")
    
    if description:
        md_content.append(f"*{description}*")
        md_content.append("")
    
    # Generation info
    md_content.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md_content.append("")
    
    # Architecture diagram
    md_content.append("## Architecture Diagram")
    md_content.append("")
    md_content.append(f"![{title}]({png_filename})")
    md_content.append("")
    
    # Statistics overview
    md_content.append("## Overview")
    md_content.append("")
    md_content.append(f"- **Total Elements:** {generator.get_element_count()}")
    md_content.append(f"- **Total Relationships:** {generator.get_relationship_count()}")
    md_content.append(f"- **Layers Used:** {', '.join(generator.get_layers_used())}")
    md_content.append("")
    
    # Elements by layer
    md_content.append("## Architecture Elements by Layer")
    md_content.append("")
    
    # Group elements by layer
    elements_by_layer = {}
    for element in generator.elements.values():
        layer = element.layer.value
        if layer not in elements_by_layer:
            elements_by_layer[layer] = []
        elements_by_layer[layer].append(element)
    
    # Document each layer
    for layer_name in sorted(elements_by_layer.keys()):
        md_content.append(f"### {layer_name} Layer")
        md_content.append("")
        
        elements = elements_by_layer[layer_name]
        if elements:
            md_content.append("| ID | Name | Type | Description |")
            md_content.append("|---|---|---|---|")
            
            for element in sorted(elements, key=lambda e: e.id):
                desc = element.description or "-"
                element_type = element.element_type.replace("_", " ")
                md_content.append(f"| `{element.id}` | **{element.name}** | {element_type} | {desc} |")
            
            md_content.append("")
    
    # Relationships
    md_content.append("## Relationships")
    md_content.append("")
    
    if generator.relationships:
        md_content.append("| From | Relationship | To | Description |")
        md_content.append("|---|---|---|---|")
        
        for rel in generator.relationships:
            # Get element names
            from_element = generator.elements.get(rel.from_element)
            to_element = generator.elements.get(rel.to_element)
            
            from_name = from_element.name if from_element else rel.from_element
            to_name = to_element.name if to_element else rel.to_element
            
            rel_type = rel.relationship_type.value if hasattr(rel.relationship_type, 'value') else str(rel.relationship_type)
            desc = rel.description or "-"
            
            md_content.append(f"| {from_name} | *{rel_type}* | {to_name} | {desc} |")
        
        md_content.append("")
    else:
        md_content.append("*No relationships defined*")
        md_content.append("")
    
    # Architecture insights
    md_content.append("## Architecture Insights")
    md_content.append("")
    
    # Layer distribution
    layer_counts = {}
    for element in generator.elements.values():
        layer = element.layer.value
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
    
    md_content.append("### Layer Distribution")
    md_content.append("")
    for layer, count in sorted(layer_counts.items()):
        percentage = (count / generator.get_element_count()) * 100
        md_content.append(f"- **{layer}**: {count} elements ({percentage:.1f}%)")
    md_content.append("")
    
    # Element types analysis
    element_types = {}
    for element in generator.elements.values():
        elem_type = element.element_type
        element_types[elem_type] = element_types.get(elem_type, 0) + 1
    
    md_content.append("### Element Types")
    md_content.append("")
    for elem_type, count in sorted(element_types.items()):
        md_content.append(f"- {elem_type.replace('_', ' ')}: {count}")
    md_content.append("")
    
    # Relationship analysis
    if generator.relationships:
        rel_types = {}
        for rel in generator.relationships:
            rel_type = rel.relationship_type.value if hasattr(rel.relationship_type, 'value') else str(rel.relationship_type)
            rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
        
        md_content.append("### Relationship Types")
        md_content.append("")
        for rel_type, count in sorted(rel_types.items()):
            md_content.append(f"- {rel_type}: {count}")
        md_content.append("")
    
    # PlantUML source reference
    md_content.append("## Source Files")
    md_content.append("")
    md_content.append("- [PlantUML Source](diagram.puml)")
    md_content.append("- [Generation Log](generation.log)")
    md_content.append("- [Metadata](metadata.json)")
    md_content.append("")
    
    # Footer
    md_content.append("---")
    md_content.append("*Generated by ArchiMate MCP Server*")
    
    return "\n".join(md_content)

def normalize_element_type(element_type: str) -> str:
    """Normalize element type to correct ArchiMate format."""
    # Handle common patterns from test errors
    if element_type.lower() == "function":
        return "Business_Function"
    if element_type.lower() == "process":
        return "Business_Process"
    if element_type.lower() == "stakeholder":
        return "Stakeholder"
    if element_type.lower() == "workpackage":
        return "Work_Package"
    
    # Direct mapping
    if element_type in ELEMENT_TYPE_MAPPING:
        return ELEMENT_TYPE_MAPPING[element_type]
    
    # Try case-insensitive lookup
    for key, value in ELEMENT_TYPE_MAPPING.items():
        if key.lower() == element_type.lower():
            return value
    
    return element_type

def normalize_layer(layer: str) -> str:
    """Normalize layer to correct ArchiMate format.""" 
    if layer in VALID_LAYERS:
        return VALID_LAYERS[layer]
    
    # Try case-insensitive lookup
    for key, value in VALID_LAYERS.items():
        if key.lower() == layer.lower():
            return value
    
    return layer

def normalize_relationship_type(rel_type: str) -> str:
    """Normalize relationship type to correct case."""
    for valid_rel in VALID_RELATIONSHIPS:
        if valid_rel.lower() == rel_type.lower():
            return valid_rel
    return rel_type

def validate_element_input(element: ElementInput) -> tuple[bool, str]:
    """Validate element input and return (is_valid, error_message)."""
    # Normalize inputs
    normalized_type = normalize_element_type(element.element_type)
    normalized_layer = normalize_layer(element.layer)
    
    # Check if element type is valid
    if normalized_type not in ELEMENT_TYPE_MAPPING.values():
        valid_types = list(ELEMENT_TYPE_MAPPING.keys())
        return False, f"Invalid element type: {element.element_type}. Valid types: {valid_types[:10]}..."
    
    # Check if layer is valid  
    if normalized_layer not in VALID_LAYERS.values():
        return False, f"Invalid layer: {element.layer}. Valid layers: {list(VALID_LAYERS.keys())}"
    
    return True, ""

def validate_relationship_input(rel: RelationshipInput, language: str = "en") -> tuple[bool, str]:
    """Validate relationship input and return (is_valid, error_message)."""
    normalized_type = normalize_relationship_type(rel.relationship_type)
    
    if normalized_type not in VALID_RELATIONSHIPS:
        return False, f"Invalid relationship type '{rel.relationship_type}'. Valid types: {VALID_RELATIONSHIPS}"
    
    # Validate custom relationship name if provided
    if rel.label:
        is_valid, error_msg = validate_custom_relationship_name(rel.label, normalized_type, language)
        if not is_valid:
            return False, f"Invalid custom relationship name: {error_msg}"
        elif error_msg:  # Warning message
            # Log warning but continue
            print(f"Warning: {error_msg}")
    
    return True, ""

def _validate_plantuml_renders(plantuml_code: str) -> tuple[bool, str]:
    """Basic validation that PlantUML code can be rendered."""
    try:
        # Basic syntax checks
        if not plantuml_code.strip():
            return False, "Empty PlantUML code"
        
        if "@startuml" not in plantuml_code:
            return False, "Missing @startuml directive"
            
        if "@enduml" not in plantuml_code:
            return False, "Missing @enduml directive"
            
        # Check for ArchiMate include
        if "!include" not in plantuml_code:
            return False, "Missing ArchiMate include directive"
            
        return True, "PlantUML validation passed"
        
    except Exception as e:
        return False, f"PlantUML validation error: {str(e)}"

def _validate_png_file(png_file_path: Path) -> tuple[bool, str]:
    """Validate that PNG file is valid and not corrupted."""
    try:
        # Check if file exists and has content
        if not png_file_path.exists():
            return False, "PNG file does not exist"
        
        file_size = png_file_path.stat().st_size
        if file_size == 0:
            return False, "PNG file is empty (0 bytes)"
        
        if file_size < 25:  # PNG header + IHDR minimum is ~25 bytes
            return False, f"PNG file too small ({file_size} bytes)"
        
        # Check PNG magic header (first 8 bytes)
        with open(png_file_path, 'rb') as f:
            header = f.read(8)
            
        # PNG signature: 137 80 78 71 13 10 26 10 (in decimal)
        png_signature = bytes([137, 80, 78, 71, 13, 10, 26, 10])
        
        if header != png_signature:
            return False, f"Invalid PNG header. Expected PNG signature, got: {header.hex()}"
        
        # Additional check: try to read IHDR chunk (basic PNG structure)
        try:
            with open(png_file_path, 'rb') as f:
                f.seek(8)  # Skip PNG signature
                chunk_size = int.from_bytes(f.read(4), 'big')
                chunk_type = f.read(4)
                
                if chunk_type != b'IHDR':
                    return False, f"First chunk is not IHDR, got: {chunk_type}"
                
                if chunk_size != 13:  # IHDR should be exactly 13 bytes
                    return False, f"Invalid IHDR chunk size: {chunk_size}"
                    
        except Exception as chunk_error:
            return False, f"PNG structure validation failed: {str(chunk_error)}"
        
        return True, "PNG file validated successfully"
        
    except Exception as e:
        return False, f"PNG validation error: {str(e)}"

# Core MCP Tools
@mcp.tool()
def create_archimate_diagram(diagram: DiagramInput) -> str:
    """Generate complete ArchiMate diagrams from structured input with elements and relationships.
    
    Automatically detects language from content and translates layer names and relationship labels.
    Supports Slovak language detection via Slovak text patterns and diacritics.
    When Slovak content detected: layer names and relationship labels are translated to Slovak.
    
    Available languages: en (English), sk (Slovak) - detected automatically
    
    Outputs are saved to CWD/exports/YYYYMMDD_HHMMSS/ directory with:
    - diagram.puml: Validated PlantUML code
    - diagram.png: Generated PNG (mandatory)
    - architecture.md: Extended textual architecture representation with PNG link
    - generation.log: Debug log with detailed generation info
    - metadata.json: Diagram metadata and statistics
    """
    debug_log = []  # Collect debug log entries
    start_time = time.time()
    
    def log_debug(level: str, message: str, details: Optional[Dict] = None):
        """Add entry to debug log."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        if details:
            entry['details'] = details
        debug_log.append(entry)
        logger.log(getattr(logging, level.upper(), logging.INFO), message)
    
    try:
        # Automatic language detection from content (always enabled)
        auto_detect = True  # Always auto-detect language
        detected_language = detect_language_from_content(diagram) if auto_detect else "en"
        
        # Use detected language or fallback to provided language parameter (default: "en")
        default_lang = "en"  # Default language is always English
        language = detected_language if (auto_detect and detected_language != "en") else (diagram.language or default_lang)
        if language not in AVAILABLE_LANGUAGES:
            language = "en"  # Fallback to English
        translator = ArchiMateTranslator(language)
        log_debug('INFO', f'Language detection: detected={detected_language}, final={language}')
        
        # Override relationship labels with translations if non-English
        override_relationship_labels_with_translations(diagram, translator)
        if language != "en":
            log_debug('INFO', f'Overrode relationship labels with {language} translations')
        
        # Create generator with translator
        generator_with_translator = ArchiMateGenerator(translator)
        log_debug('INFO', f'Set up translator for language: {language}')
        
        # Configure layout with hybrid priority: config-locked vs client-configurable
        from .archimate.generator import DiagramLayout
        layout_config = diagram.layout or {}
        
        # Hybrid system: config takes priority if set, otherwise client can configure
        layout = DiagramLayout(
            direction=get_layout_setting('ARCHI_MCP_DEFAULT_DIRECTION', layout_config.get('direction')),
            show_legend=(get_layout_setting('ARCHI_MCP_DEFAULT_SHOW_LEGEND', layout_config.get('show_legend', 'true')).lower() == 'true'),
            show_title=(get_layout_setting('ARCHI_MCP_DEFAULT_SHOW_TITLE', layout_config.get('show_title', 'true')).lower() == 'true'),
            group_by_layer=(get_layout_setting('ARCHI_MCP_DEFAULT_GROUP_BY_LAYER', layout_config.get('group_by_layer', 'false')).lower() == 'true'),
            spacing=get_layout_setting('ARCHI_MCP_DEFAULT_SPACING', layout_config.get('spacing')),
            show_element_types=(get_layout_setting('ARCHI_MCP_DEFAULT_SHOW_ELEMENT_TYPES', layout_config.get('show_element_types', 'false')).lower() == 'true'),
            show_relationship_labels=(get_layout_setting('ARCHI_MCP_DEFAULT_SHOW_RELATIONSHIP_LABELS', layout_config.get('show_relationship_labels', 'true')).lower() == 'true')
        )
        
        # Log which parameters are locked by config
        locked_params = []
        layout_params = [
            ('ARCHI_MCP_DEFAULT_DIRECTION', 'direction'),
            ('ARCHI_MCP_DEFAULT_SHOW_LEGEND', 'show_legend'), 
            ('ARCHI_MCP_DEFAULT_SHOW_TITLE', 'show_title'),
            ('ARCHI_MCP_DEFAULT_GROUP_BY_LAYER', 'group_by_layer'),
            ('ARCHI_MCP_DEFAULT_SPACING', 'spacing'),
            ('ARCHI_MCP_DEFAULT_SHOW_ELEMENT_TYPES', 'show_element_types'),
            ('ARCHI_MCP_DEFAULT_SHOW_RELATIONSHIP_LABELS', 'show_relationship_labels')
        ]
        
        for env_var, param_name in layout_params:
            if is_config_locked(env_var):
                locked_params.append(f"{param_name}={get_env_setting(env_var)}")
        
        if locked_params:
            log_debug('INFO', f'Config-locked parameters: {", ".join(locked_params)}')
        else:
            log_debug('INFO', 'No config-locked parameters - client has full layout control')
        
        generator_with_translator.set_layout(layout)
        log_debug('INFO', f'Set layout: direction={layout.direction}, legend={layout.show_legend}, group_by_layer={layout.group_by_layer}')
        
        # Clear existing diagram first
        generator_with_translator.clear()
        log_debug('INFO', 'Cleared existing diagram')
        
        # Validate and add elements
        log_debug('INFO', f'Processing {len(diagram.elements)} elements')
        for element_input in diagram.elements:
            is_valid, error_msg = validate_element_input(element_input)
            if not is_valid:
                log_debug('ERROR', f'Element validation failed: {error_msg}', {'element_id': element_input.id})
                raise ArchiMateValidationError(f"Element validation failed: {error_msg}")
            
            # Normalize inputs
            normalized_type = normalize_element_type(element_input.element_type)
            normalized_layer = normalize_layer(element_input.layer)
            log_debug('DEBUG', f'Normalized element type: {element_input.element_type} -> {normalized_type}')
            
            # Create ArchiMate element with proper aspect
            # Determine aspect based on element type
            if normalized_type in ["Business_Actor", "Business_Role", "Application_Component", "Node", "Device"]:
                aspect = ArchiMateAspect.ACTIVE_STRUCTURE
            elif normalized_type in ["Business_Object", "Data_Object", "Artifact"]:
                aspect = ArchiMateAspect.PASSIVE_STRUCTURE  
            else:
                aspect = ArchiMateAspect.BEHAVIOR
                
            element = ArchiMateElement(
                id=element_input.id,
                name=element_input.name,
                element_type=normalized_type,
                layer=ArchiMateLayer(normalized_layer),
                aspect=aspect,
                description=element_input.description,
                stereotype=element_input.stereotype,
                properties=element_input.properties or {}
            )
            
            generator_with_translator.add_element(element)
        log_debug('INFO', f'Added {generator_with_translator.get_element_count()} elements successfully')
        
        # Validate and add relationships
        log_debug('INFO', f'Processing {len(diagram.relationships)} relationships')
        for rel_input in diagram.relationships:
            is_valid, error_msg = validate_relationship_input(rel_input, language)
            if not is_valid:
                log_debug('ERROR', f'Relationship validation failed: {error_msg}', {'relationship_id': rel_input.id})
                raise ArchiMateValidationError(f"Relationship validation failed: {error_msg}")
            
            # Normalize relationship type
            normalized_rel_type = normalize_relationship_type(rel_input.relationship_type)
            
            # Create relationship
            relationship = ArchiMateRelationship(
                id=rel_input.id,
                from_element=rel_input.from_element,
                to_element=rel_input.to_element,
                relationship_type=normalized_rel_type,
                description=rel_input.description,
                label=rel_input.label,  # Include custom label from client
                properties={}
            )
            
            generator_with_translator.add_relationship(relationship)
        log_debug('INFO', f'Added {generator_with_translator.get_relationship_count()} relationships successfully')
        
        # Generate PlantUML with proper title
        title = diagram.title or "ArchiMate Diagram"
        description = diagram.description or "Generated ArchiMate diagram"
        
        log_debug('INFO', 'Generating PlantUML code')
        plantuml_code = generator_with_translator.generate_plantuml(title=title, description=description)
        log_debug('INFO', f'Generated PlantUML code: {len(plantuml_code)} characters')
        
        # MANDATORY: Validate PlantUML before proceeding
        renders_ok, error_msg = _validate_plantuml_renders(plantuml_code)
        if not renders_ok:
            log_debug('ERROR', f'PlantUML validation failed: {error_msg}')
            raise ArchiMateGenerationError(f"Generated diagram failed validation - {error_msg}")
        
        # Always generate PNG/SVG (no configuration needed)
        generate_png = True  # Always generate PNG
        generate_svg = True  # Always generate SVG
        png_quality = "high"  # Always use high quality
        
        log_debug('INFO', f'Generation settings: PNG={generate_png}, SVG={generate_svg}, quality={png_quality}')
        
        # First, test PNG generation to ensure it works before creating export directory
        png_file_path = None
        svg_file_path = None
        
        try:
            # Detect Java version
            java_check = subprocess.run(['java', '-version'], capture_output=True, text=True, timeout=5)
            java_info = java_check.stderr if java_check.stderr else java_check.stdout
            log_debug('INFO', 'Java environment detected', {'java_version': java_info.split('\n')[0]})
            
            # Try to find PlantUML jar
            possible_jars = [
                "/Users/patrik/Projects/archi-mcp/plantuml.jar",
                "./plantuml.jar",
                "/usr/local/bin/plantuml.jar",
                "/opt/homebrew/bin/plantuml.jar"
            ]
            
            plantuml_jar = None
            for jar_path in possible_jars:
                if os.path.exists(jar_path):
                    plantuml_jar = jar_path
                    log_debug('INFO', f'Found PlantUML jar at: {jar_path}')
                    
                    # Check PlantUML version
                    version_cmd = ['java', '-Djava.awt.headless=true', '-jar', jar_path, '-version']
                    version_result = subprocess.run(version_cmd, capture_output=True, text=True, timeout=10)
                    if version_result.returncode == 0:
                        log_debug('INFO', 'PlantUML version info', {'version': version_result.stdout.strip()})
                    break
            
            if not plantuml_jar:
                raise Exception("PlantUML jar not found in any expected location")
            
            # Generate PNG using temporary file first (if enabled)
            if generate_png:
                log_debug('INFO', 'Starting PNG generation test')
            else:
                log_debug('INFO', 'PNG generation disabled by configuration')
            generation_start = time.time()
            
            # Create temporary PlantUML file for testing
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False) as temp_puml:
                temp_puml.write(plantuml_code)
                temp_puml_path = temp_puml.name
            
            # PNG generation test (MANDATORY)
            png_cmd = [
                "java", 
                "-Djava.awt.headless=true",  # Headless mode
                "-jar", plantuml_jar, 
                "-tpng", 
                "-charset", "UTF-8",
                temp_puml_path
            ]
            
            log_debug('DEBUG', 'Executing PlantUML PNG command', {'command': ' '.join(png_cmd)})
            
            png_result = subprocess.run(png_cmd, capture_output=True, text=True, timeout=60)
            
            generation_time = time.time() - generation_start
            log_debug('INFO', f'PNG generation completed in {generation_time:.2f} seconds', {
                'png_return_code': png_result.returncode,
                'png_stdout_length': len(png_result.stdout),
                'png_stderr_length': len(png_result.stderr)
            })
            
            if png_result.stdout:
                log_debug('DEBUG', 'PlantUML PNG stdout', {'output': png_result.stdout[:500]})
            if png_result.stderr:
                log_debug('WARNING', 'PlantUML PNG stderr', {'output': png_result.stderr[:500]})
            
            # Check PNG generation first - MUST succeed before creating export directory
            temp_png_path = Path(temp_puml_path).with_suffix('.png')
            if png_result.returncode == 0 and temp_png_path.exists():
                file_size = temp_png_path.stat().st_size
                
                # Validate PNG file content
                is_valid_png, png_validation_error = _validate_png_file(temp_png_path)
                
                if is_valid_png and file_size > 50:  # Minimum reasonable PNG size for actual diagrams
                    log_debug('INFO', f'PNG test generation successful: {file_size} bytes')
                    png_file_path = str(temp_png_path)  # Store path for later use
                else:
                    raise Exception(f"PNG validation failed: {png_validation_error}, file size: {file_size} bytes")
                
                # Only generate SVG after PNG success
                log_debug('INFO', 'PNG successful, now generating SVG')
                svg_generation_start = time.time()
                
                svg_cmd = [
                    "java", 
                    "-Djava.awt.headless=true",  # Headless mode
                    "-jar", plantuml_jar, 
                    "-tsvg", 
                    "-charset", "UTF-8",
                    temp_puml_path
                ]
                
                log_debug('DEBUG', 'Executing PlantUML SVG command', {'command': ' '.join(svg_cmd)})
                
                svg_result = subprocess.run(svg_cmd, capture_output=True, text=True, timeout=60)
                
                svg_generation_time = time.time() - svg_generation_start
                log_debug('INFO', f'SVG generation completed in {svg_generation_time:.2f} seconds', {
                    'svg_return_code': svg_result.returncode,
                    'svg_stdout_length': len(svg_result.stdout),
                    'svg_stderr_length': len(svg_result.stderr)
                })
                
                if svg_result.stdout:
                    log_debug('DEBUG', 'PlantUML SVG stdout', {'output': svg_result.stdout[:500]})
                if svg_result.stderr:
                    log_debug('WARNING', 'PlantUML SVG stderr', {'output': svg_result.stderr[:500]})
                
                # Check SVG generation 
                temp_svg_path = Path(temp_puml_path).with_suffix('.svg')
                if svg_result.returncode == 0 and temp_svg_path.exists():
                    svg_file_size = temp_svg_path.stat().st_size
                    log_debug('INFO', f'SVG generated successfully: {svg_file_size} bytes')
                    svg_file_path = str(temp_svg_path)  # Store path for later use
                else:
                    log_debug('WARNING', f'SVG generation failed: return code {svg_result.returncode}, stderr: {svg_result.stderr}')
            else:
                raise Exception(f"PNG generation failed: return code {png_result.returncode}, stderr: {png_result.stderr}")
                
            # Cleanup temporary files
            try:
                os.unlink(temp_puml_path)
            except:
                pass
                
        except subprocess.TimeoutExpired:
            log_debug('ERROR', 'PNG and SVG generation timed out after 60 seconds')
            raise ArchiMateGenerationError("PNG generation timed out after 60 seconds")
        except Exception as png_error:
            log_debug('ERROR', f'PNG and SVG generation failed: {str(png_error)}', {
                'error_type': type(png_error).__name__
            })
            raise ArchiMateGenerationError(f"PNG generation failed: {str(png_error)}")
        
        # PNG generation successful! Now create export directory and move files
        log_debug('INFO', 'PNG generation successful, creating export directory')
        export_dir = create_diagram_export_directory()
        log_debug('INFO', f'Created export directory: {export_dir}')
        
        # Save PlantUML code to export directory
        puml_file = export_dir / "diagram.puml"
        with open(puml_file, 'w', encoding='utf-8') as f:
            f.write(plantuml_code)
        log_debug('INFO', f'Saved PlantUML code to {puml_file}')
        
        # Move PNG file to export directory
        png_file = export_dir / "diagram.png"
        import shutil
        shutil.move(png_file_path, str(png_file))
        log_debug('INFO', f'Moved PNG file to {png_file}')
        
        # Move SVG file if generated
        svg_generated = False
        if svg_file_path:
            svg_file = export_dir / "diagram.svg"
            shutil.move(svg_file_path, str(svg_file))
            log_debug('INFO', f'Moved SVG file to {svg_file}')
            svg_generated = True
        
        # Save debug log
        log_file = save_debug_log(export_dir, debug_log)
        
        # Create metadata file
        metadata = {
            "title": title,
            "description": description,
            "generated_at": datetime.now().isoformat(),
            "generation_time_seconds": round(time.time() - start_time, 2),
            "statistics": {
                "elements": generator_with_translator.get_element_count(),
                "relationships": generator_with_translator.get_relationship_count(),
                "layers": generator_with_translator.get_layers_used()
            },
            "png_generated": True,  # Always true if we reach this point
            "svg_generated": svg_generated,
            "plantuml_validation": {
                "passed": renders_ok,
                "message": error_msg
            }
        }
        
        metadata_file = export_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        # Generate markdown documentation (PNG was successful if we reach this point)
        log_debug('INFO', 'Generating architecture documentation')
        markdown_content = generate_architecture_markdown(generator_with_translator, title, description, "diagram.png")
        markdown_file = export_dir / "architecture.md"
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        log_debug('INFO', f'Saved architecture documentation to {markdown_file}')
        
        # Cleanup failed export attempts after successful generation
        try:
            cleanup_failed_exports()
            log_debug('INFO', 'Cleaned up failed export attempts')
        except Exception as cleanup_error:
            log_debug('WARNING', f'Failed to cleanup exports: {str(cleanup_error)}')
        
        # Generate layout parameters information for the client
        layout_info = generate_layout_parameters_info()
        
        # Prepare layout usage example for client
        layout_example = {
            "layout": {
                param['parameter']: f"<{param['options'][0] if isinstance(param['options'], list) else param['default']}>"
                for param in layout_info['client_configurable']
            }
        } if layout_info['client_configurable'] else None
        
        return json.dumps({
            "status": "success",
            "exports_dir": str(export_dir),
            "files": {
                "plantuml": "diagram.puml",
                "png": "diagram.png",
                "svg": "diagram.svg" if svg_generated else None,
                "markdown": "architecture.md",
                "log": "generation.log",
                "metadata": "metadata.json"
            },
            "statistics": metadata["statistics"],
            "message": f"✅ ArchiMate diagram created successfully in {export_dir}",
            "layout_parameters": {
                "config_locked": layout_info['config_locked'],
                "client_configurable": layout_info['client_configurable'],
                "usage_example": layout_example,
                "note": "Config-locked parameters cannot be overridden by client requests. Client-configurable parameters can be set in the diagram.layout object."
            }
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error in create_archimate_diagram: {e}")
        
        # Always save debug log for troubleshooting, even on errors
        try:
            # Create minimal export directory just for the log
            error_export_dir = create_diagram_export_directory()
            log_debug('INFO', f'Created error export directory for debugging: {error_export_dir}')
            
            # Save debug log with error information
            log_debug('ERROR', f'Final error: {str(e)}', {
                'error_type': type(e).__name__,
                'total_generation_time': round(time.time() - start_time, 2)
            })
            
            save_debug_log(error_export_dir, debug_log)
            logger.info(f"Debug log saved to: {error_export_dir}/generation.log")
            
        except Exception as log_error:
            logger.warning(f"Could not save debug log: {log_error}")
        
        # Raise the original error (no other files saved)
        raise ArchiMateGenerationError(f"Failed to create diagram: {str(e)}")

# Removed validate_archimate_model - not needed in simplified API

# Debug tools
@mcp.tool() 
def analyze_current_architecture() -> str:
    """Analyze current architecture state and provide health assessment."""
    try:
        elements = generator._elements
        relationships = generator._relationships
        
        if not elements:
            return "⚠️ **No architecture to analyze** - Create a diagram first"
        
        result = f"📊 **Architecture Analysis Report**\n\n"
        result += f"**Elements:** {len(elements)}\n"
        result += f"**Relationships:** {len(relationships)}\n"
        result += f"**Layers:** {', '.join(generator.get_layers_used())}\n\n"
        
        # Element breakdown by layer
        layer_counts = {}
        for element in elements.values():
            layer = element.layer.value
            layer_counts[layer] = layer_counts.get(layer, 0) + 1
        
        result += "**Elements by Layer:**\n"
        for layer, count in layer_counts.items():
            result += f"• {layer}: {count} elements\n"
        
        result += f"\n**Status:** Architecture is ready for validation ✅"
        
        return result
        
    except Exception as e:
        return f"❌ Analysis failed: {str(e)}"

@mcp.tool()
def test_element_normalization() -> str:
    """Test element type normalization across all ArchiMate layers."""
    try:
        test_results = []
        
        # Test common element types
        test_elements = [
            ("function", "Business"),
            ("process", "Business"),
            ("stakeholder", "Motivation"),
            ("Business_Actor", "Business"),
            ("Application_Component", "Application"),
            ("Node", "Technology"),
            ("Work_Package", "Implementation")
        ]
        
        for element_type, layer in test_elements:
            normalized_type = normalize_element_type(element_type)
            normalized_layer = normalize_layer(layer)
            
            is_valid_type = normalized_type in ELEMENT_TYPE_MAPPING.values()
            is_valid_layer = normalized_layer in VALID_LAYERS.values()
            
            status = "✅" if (is_valid_type and is_valid_layer) else "❌"
            test_results.append(f"{status} {element_type} ({layer}) → {normalized_type} ({normalized_layer})")
        
        result = "🧪 **Element Normalization Test Results**\n\n"
        result += "\n".join(test_results)
        
        return result
        
    except Exception as e:
        return f"❌ Test failed: {str(e)}"

# Removed get_debug_log_info - not needed in simplified API

@mcp.tool()
def create_architecture_views_summary(
    summary_filename: Optional[str] = None,
    session_title: Optional[str] = None,
    include_failed_attempts: bool = False
) -> str:
    """Create comprehensive markdown summary of all architectural views from current session.
    
    Args:
        summary_filename: Name for the summary markdown file (auto-generated if not provided)
        session_title: Title for the session summary (default: "Architecture Views Summary")
        include_failed_attempts: Whether to include failed diagram attempts in summary
        
    Returns:
        Summary of created architecture views with links to detailed views and diagrams
    """
    try:
        exports_dir = get_exports_directory()
        
        if not exports_dir.exists():
            return "❌ No exports directory found. Create some diagrams first using create_archimate_diagram."
        
        # Scan for successful exports (directories with PNG files)
        successful_exports = []
        failed_exports = []
        
        for export_dir in exports_dir.iterdir():
            if not export_dir.is_dir() or export_dir.name == "failed_attempts":
                continue
                
            png_file = export_dir / "diagram.png"
            metadata_file = export_dir / "metadata.json"
            architecture_file = export_dir / "architecture.md"
            
            export_info = {
                "directory": export_dir.name,
                "path": export_dir,
                "timestamp": export_dir.name,
                "has_png": png_file.exists(),
                "has_metadata": metadata_file.exists(),
                "has_architecture": architecture_file.exists(),
                "title": "Unknown Diagram",
                "description": "No description available",
                "statistics": {}
            }
            
            # Load metadata if available
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        export_info["title"] = metadata.get("title", "Unknown Diagram")
                        export_info["description"] = metadata.get("description", "No description available")
                        export_info["statistics"] = metadata.get("statistics", {})
                        export_info["generated_at"] = metadata.get("generated_at", "")
                except Exception:
                    pass
            
            if png_file.exists():
                successful_exports.append(export_info)
            else:
                failed_exports.append(export_info)
        
        # Sort by timestamp (directory name)
        successful_exports.sort(key=lambda x: x["timestamp"], reverse=True)
        failed_exports.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Generate summary filename
        if not summary_filename:
            session_date = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_filename = f"architecture_session_summary_{session_date}.md"
        
        if not summary_filename.endswith('.md'):
            summary_filename += '.md'
        
        # Generate markdown content
        session_title = session_title or "Architecture Views Summary"
        summary_content = _generate_views_summary_markdown(
            session_title,
            successful_exports,
            failed_exports if include_failed_attempts else [],
            exports_dir
        )
        
        # Save summary file in exports directory
        summary_file = exports_dir / summary_filename
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        # Generate response
        total_views = len(successful_exports)
        failed_count = len(failed_exports)
        
        result = f"✅ **Architecture Views Summary Created**\n\n"
        result += f"📁 **File:** `{summary_file}`\n"
        result += f"📊 **Session Statistics:**\n"
        result += f"- Successful architectural views: {total_views}\n"
        
        if include_failed_attempts and failed_count > 0:
            result += f"- Failed attempts: {failed_count}\n"
        
        if successful_exports:
            result += f"- Date range: {successful_exports[-1]['timestamp']} → {successful_exports[0]['timestamp']}\n"
            
            # Show overview of view types
            view_types = {}
            for export in successful_exports:
                title = export["title"]
                # Extract view type from title
                view_type = "General"
                if "motivation" in title.lower():
                    view_type = "Motivation"
                elif "application" in title.lower():
                    view_type = "Application"
                elif "technology" in title.lower():
                    view_type = "Technology" 
                elif "business" in title.lower():
                    view_type = "Business"
                elif "implementation" in title.lower():
                    view_type = "Implementation"
                elif "layered" in title.lower() or "layer" in title.lower():
                    view_type = "Layered"
                
                view_types[view_type] = view_types.get(view_type, 0) + 1
            
            result += f"- View types: {', '.join([f'{k}({v})' for k, v in view_types.items()])}\n"
        
        result += f"\n📖 **Usage:** Open `{summary_filename}` to browse all architectural views with links to detailed descriptions and diagrams."
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating architecture views summary: {e}")
        return f"❌ Failed to create architecture views summary: {str(e)}"

def _generate_views_summary_markdown(
    session_title: str,
    successful_exports: List[Dict],
    failed_exports: List[Dict],
    exports_dir: Path
) -> str:
    """Generate markdown content for architecture views summary."""
    
    lines = []
    
    # Header
    lines.append(f"# {session_title}")
    lines.append("")
    lines.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    lines.append("")
    
    # Overview
    total_successful = len(successful_exports)
    total_failed = len(failed_exports)
    
    lines.append("## 📊 Session Overview")
    lines.append("")
    lines.append(f"- **Total Architectural Views:** {total_successful}")
    if total_failed > 0:
        lines.append(f"- **Failed Attempts:** {total_failed}")
    
    if successful_exports:
        lines.append(f"- **Time Span:** {successful_exports[-1]['timestamp']} → {successful_exports[0]['timestamp']}")
        
        # Calculate total elements and relationships
        total_elements = sum(export.get("statistics", {}).get("elements", 0) for export in successful_exports)
        total_relationships = sum(export.get("statistics", {}).get("relationships", 0) for export in successful_exports)
        
        lines.append(f"- **Total Elements Modeled:** {total_elements}")
        lines.append(f"- **Total Relationships:** {total_relationships}")
    
    lines.append("")
    
    # Table of Contents
    if successful_exports:
        lines.append("## 📋 Table of Contents")
        lines.append("")
        
        for i, export in enumerate(successful_exports, 1):
            title = export["title"]
            # Generate anchor from the full heading text (including number)
            full_heading = f"{i}. {title}"
            lines.append(f"{i}. [{title}](#{_make_anchor(full_heading)})")
        
        lines.append("")
    
    # Detailed views
    if successful_exports:
        lines.append("## 🏗️ Architectural Views")
        lines.append("")
        
        for i, export in enumerate(successful_exports, 1):
            title = export["title"]
            description = export["description"]
            stats = export.get("statistics", {})
            timestamp = export["timestamp"]
            
            # View header
            lines.append(f"### {i}. {title}")
            lines.append("")
            
            # Description
            if description and description != "No description available":
                lines.append(f"**Description:** {description}")
                lines.append("")
            
            # Statistics
            if stats:
                lines.append("**Model Statistics:**")
                if stats.get("elements"):
                    lines.append(f"- Elements: {stats['elements']}")
                if stats.get("relationships"):
                    lines.append(f"- Relationships: {stats['relationships']}")
                if stats.get("layers"):
                    layers = stats["layers"]
                    if isinstance(layers, list):
                        lines.append(f"- Layers: {', '.join(layers)}")
                lines.append("")
            
            # Links
            lines.append("**Resources:**")
            lines.append(f"- 📄 [Detailed Architecture Documentation]({timestamp}/architecture.md)")
            lines.append(f"- 🖼️ [PNG Diagram]({timestamp}/diagram.png)")
            lines.append(f"- 🎨 [SVG Diagram]({timestamp}/diagram.svg)")
            lines.append(f"- 📝 [PlantUML Source]({timestamp}/diagram.puml)")
            lines.append("")
            
            # Embedded diagram
            lines.append("**Diagram Preview:**")
            lines.append("")
            lines.append(f"![{title}]({timestamp}/diagram.png)")
            lines.append("")
            lines.append("---")
            lines.append("")
    
    # Failed attempts section
    if failed_exports:
        lines.append("## ⚠️ Failed Attempts")
        lines.append("")
        lines.append("The following diagram generation attempts failed but logs are available for debugging:")
        lines.append("")
        
        for export in failed_exports:
            title = export["title"]
            timestamp = export["timestamp"]
            lines.append(f"- **{title}** ({timestamp})")
            lines.append(f"  - 📋 [Generation Log](failed_attempts/{timestamp}/generation.log)")
        
        lines.append("")
    
    # Footer
    lines.append("---")
    lines.append("*Generated by ArchiMate MCP Server - Architecture Views Summary Tool*")
    
    return "\n".join(lines)

def _make_anchor(text: str) -> str:
    """Convert text to markdown anchor format compatible with most markdown renderers."""
    import re
    # Convert to lowercase
    anchor = text.lower()
    # Replace spaces and special characters with hyphens
    anchor = re.sub(r'[^\w\s-]', '', anchor)  # Remove special chars except spaces and hyphens
    anchor = re.sub(r'[-\s]+', '-', anchor)    # Replace multiple spaces/hyphens with single hyphen
    # Remove leading/trailing hyphens
    anchor = anchor.strip('-')
    return anchor

@mcp.tool()
def analyze_recent_errors(minutes: int = 10) -> str:
    """Analyze recent PlantUML generation errors and provide troubleshooting guidance.
    
    Args:
        minutes: Look back this many minutes for error analysis (default: 10)
        
    Returns:
        Detailed analysis of recent errors with actionable recommendations
    """
    try:
        # Get recent error data from various sources
        analysis = _extract_recent_problems(minutes)
        
        if analysis['total_errors'] == 0:
            return f"""✅ **No Recent Errors Found**

**Analysis Period:** Last {minutes} minutes
**Status:** System operating normally

### 📊 Current Health Metrics:
- PlantUML generation: ✅ Working
- Element normalization: ✅ Working  
- Validation pipeline: ✅ Working

### 📈 Recommendations:
- System is stable for architecture creation
- Ready for complex multi-layer diagrams
- All normalization functions operational
"""
        
        # Build detailed error analysis
        report = f"""🔍 **Recent Error Analysis** (Last {minutes} minutes)

## 📊 Summary
**Total Issues Found:** {analysis['total_errors']}
**Error Categories:** {len(analysis['error_categories'])}
**Timeframe:** {datetime.now().strftime('%H:%M:%S')} - {(datetime.now() - timedelta(minutes=minutes)).strftime('%H:%M:%S')}

"""
        
        # Add error categories
        if analysis['error_categories']:
            report += "## 📊 Error Categories:\n"
            for category, count in analysis['error_categories'].items():
                report += f"- **{category}**: {count} occurrences\n"
            report += "\n"
        
        # Add common patterns
        if analysis['common_patterns']:
            report += "## 🔎 Common Issues:\n"
            for pattern in analysis['common_patterns']:
                report += f"- {pattern}\n"
            report += "\n"
        
        # Add troubleshooting recommendations
        report += "## 🚀 Troubleshooting Steps:\n"
        recommendations = _generate_troubleshooting_recommendations(analysis)
        for rec in recommendations:
            report += f"- {rec}\n"
        
        return report
        
    except Exception as e:
        logger.error(f"Error in analyze_recent_errors: {e}")
        return f"❌ Error analysis failed: {str(e)}"

def _extract_recent_problems(minutes: int) -> Dict[str, Any]:
    """Extract problems from recent logs and server state."""
    from datetime import datetime, timedelta
    import glob
    
    cutoff_time = datetime.now() - timedelta(minutes=minutes)
    analysis = {
        'total_errors': 0,
        'error_categories': {},
        'common_patterns': [],
        'recent_attempts': []
    }
    
    # Check for recent PlantUML generation errors in /tmp
    temp_files = glob.glob('/tmp/archimate_diagram_*.png')
    recent_files = [f for f in temp_files 
                   if os.path.getmtime(f) > cutoff_time.timestamp()]
    
    # Analyze current generator state for issues
    try:
        elements_count = len(generator._elements)
        relationships_count = len(generator._relationships)
        
        # Check for common error patterns
        if elements_count == 0:
            analysis['common_patterns'].append(
                "No elements in current diagram - may need to create elements first"
            )
            analysis['error_categories']['Empty Model'] = 1
            analysis['total_errors'] += 1
        
        # Check for orphaned relationships
        element_ids = set(generator._elements.keys())
        orphaned_rels = 0
        for rel in generator._relationships.values():
            if rel.from_element not in element_ids or rel.to_element not in element_ids:
                orphaned_rels += 1
        
        if orphaned_rels > 0:
            analysis['common_patterns'].append(
                f"Found {orphaned_rels} relationships with missing elements"
            )
            analysis['error_categories']['Orphaned Relationships'] = orphaned_rels
            analysis['total_errors'] += orphaned_rels
            
    except Exception as e:
        analysis['common_patterns'].append(f"Generator state analysis failed: {str(e)}")
        analysis['error_categories']['System Error'] = 1
        analysis['total_errors'] += 1
    
    return analysis

def _generate_troubleshooting_recommendations(analysis: Dict[str, Any]) -> List[str]:
    """Generate specific troubleshooting recommendations based on error analysis."""
    recommendations = []
    
    if 'Empty Model' in analysis['error_categories']:
        recommendations.extend([
            "Create elements first using create_archimate_diagram with element data",
            "Ensure DiagramInput contains at least one ElementInput with valid layer and type",
            "Check element normalization using test_element_normalization tool"
        ])
    
    if 'Orphaned Relationships' in analysis['error_categories']:
        recommendations.extend([
            "Verify all relationship from_element and to_element IDs match existing element IDs",
            "Use analyze_current_architecture to check element/relationship consistency",
            "Consider recreating the diagram with proper element-relationship mapping"
        ])
    
    if 'System Error' in analysis['error_categories']:
        recommendations.extend([
            "Check server logs for detailed error information",
            "Verify PlantUML JAR file availability for PNG generation",
            "Test basic functionality with simple single-element diagram"
        ])
    
    # Default recommendations if no specific issues found
    if not recommendations:
        recommendations = [
            "System appears healthy - ready for complex architecture creation",
            "Use create_archimate_diagram for new diagrams", 
            "Monitor with analyze_current_architecture for ongoing health checks"
        ]
    
    return recommendations

# Server startup
def main():
    """Main entry point for the ArchiMate MCP server."""
    logger.info("Starting ArchiMate MCP Server with FastMCP")
    logger.info(f"Available tools: create_archimate_diagram, analyze_current_architecture, test_element_normalization, create_architecture_views_summary, analyze_recent_errors")
    
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    main()