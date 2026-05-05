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
import threading
import socket
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Literal, Union
from pathlib import Path
import glob
from enum import Enum

from fastmcp import FastMCP, utilities
from pydantic import BaseModel, Field, model_validator
from PIL import Image
import io

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

LANGUAGE_INDICATORS = {
    "sk": [
        'zákazník', 'podpora', 'služba', 'proces', 'objekt', 'komponent',
        'podnikový', 'zákaznícky', 'proaktívna', 'inteligentý', 'znalostná',
        'konverzačná', 'vylepšený', 'starostlivosť', 'riešenie', 'problémov',
        'schopnosť', 'platforma', 'báza', 'profil', 'analýza', 'nálady',
        'spokojnosť', 'sledovanie', 'emócií', 'monitoruje', 'aktualizuje',
        'pristupuje', 'spúšťa', 'umožňuje', 'napájaný', 'asistovaný',
        'ň', 'ť', 'ž', 'č', 'š', 'ľ', 'ý', 'á', 'í', 'é', 'ó', 'ú', 'ô'
    ],
    "cs": [
        'zákazník', 'podpora', 'služba', 'proces', 'objekt', 'komponenta',
        'podnikový', 'zákaznícký', 'proaktívní', 'inteligentní', 'znalostní',
        'konverzační', 'vylepšený', 'starostlivost', 'řešení', 'problémů',
        'schopnost', 'platforma', 'báze', 'profil', 'analýza', 'nálady',
        'spokojnost', 'sledování', 'emocí', 'monitoruje', 'aktualizuje',
        'přistupuje', 'spouští', 'umožňuje', 'napájený', 'asistovaný',
        'á', 'č', 'ď', 'é', 'ě', 'í', 'ň', 'ó', 'ř', 'š', 'ť', 'ú', 'ů', 'ž'
    ],
}

LANGUAGE_DETECTION_THRESHOLD = 3

def detect_language_from_content(diagram) -> str:
    """Automatically detect language from diagram content.

    Args:
        diagram: DiagramInput with elements and relationships

    Returns:
        Language code (e.g., "sk", "cs", "en")
    """
    # Collect all text content
    all_text = []

    for element in diagram.elements:
        if element.name:
            all_text.append(element.name.lower())
        if element.description:
            all_text.append(element.description.lower())

    for rel in diagram.relationships:
        if rel.label:
            all_text.append(rel.label.lower())
        if rel.description:
            all_text.append(rel.description.lower())

    if diagram.title:
        all_text.append(diagram.title.lower())
    if diagram.description:
        all_text.append(diagram.description.lower())

    content = ' '.join(all_text)

    scores = {
        lang: sum(1 for indicator in indicators if indicator in content)
        for lang, indicators in LANGUAGE_INDICATORS.items()
    }

    best_lang = max(scores, key=lambda lang: scores[lang])
    if scores[best_lang] >= LANGUAGE_DETECTION_THRESHOLD:
        return best_lang

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
    
    # Check length - max 4 words or 30 characters (relaxed for better expressiveness)
    words = custom_name.strip().split()
    if len(words) > 4:
        return False, f"Custom relationship name must be maximum 4 words. Current: '{custom_name}' ({len(words)} words). Try: '{' '.join(words[:4])}'"
    
    if len(custom_name) > 30:
        return False, f"Custom relationship name must be maximum 30 characters. Current: '{custom_name}' ({len(custom_name)} chars)"
    
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

# HTTP Server for serving SVG files
http_server_port = None
http_server_thread = None
http_server_running = False

def find_free_port():
    """Find a free port for the HTTP server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def start_http_server():
    """Start HTTP server for serving static files from exports directory."""
    global http_server_port, http_server_thread, http_server_running
    
    if http_server_running:
        return http_server_port
    
    # Find free port
    http_server_port = find_free_port()
    
    # Create Starlette app for static files
    try:
        from starlette.applications import Starlette
        from starlette.routing import Mount
        from starlette.staticfiles import StaticFiles
        import uvicorn
        
        # Ensure exports directory exists
        exports_dir = os.path.join(os.getcwd(), "exports")
        os.makedirs(exports_dir, exist_ok=True)
        
        app = Starlette(routes=[
            Mount("/exports", StaticFiles(directory=exports_dir), name="exports"),
        ])
        
        def run_server():
            uvicorn.run(app, host="127.0.0.1", port=http_server_port, log_level="warning")
        
        http_server_thread = threading.Thread(target=run_server, daemon=True)
        http_server_thread.start()
        http_server_running = True
        
        logger.info(f"HTTP server started on http://127.0.0.1:{http_server_port}")
        return http_server_port
        
    except ImportError as e:
        logger.error(f"Failed to start HTTP server: {e}. Install starlette and uvicorn.")
        return None

# Comprehensive ArchiMate Element Type Enums by Layer
class BusinessElementType(str, Enum):
    """Business Layer elements - actors, roles, processes, services, and objects."""
    BUSINESS_ACTOR = "Business_Actor"
    BUSINESS_ROLE = "Business_Role"
    BUSINESS_COLLABORATION = "Business_Collaboration"
    BUSINESS_INTERFACE = "Business_Interface"
    BUSINESS_FUNCTION = "Business_Function"
    BUSINESS_PROCESS = "Business_Process"
    BUSINESS_EVENT = "Business_Event"
    BUSINESS_SERVICE = "Business_Service"
    BUSINESS_OBJECT = "Business_Object"
    BUSINESS_CONTRACT = "Business_Contract"
    BUSINESS_REPRESENTATION = "Business_Representation"
    LOCATION = "Location"

class ApplicationElementType(str, Enum):
    """Application Layer elements - components, services, interfaces, and data objects."""
    APPLICATION_COMPONENT = "Application_Component"
    APPLICATION_COLLABORATION = "Application_Collaboration"
    APPLICATION_INTERFACE = "Application_Interface"
    APPLICATION_FUNCTION = "Application_Function"
    APPLICATION_INTERACTION = "Application_Interaction"
    APPLICATION_PROCESS = "Application_Process"
    APPLICATION_EVENT = "Application_Event"
    APPLICATION_SERVICE = "Application_Service"
    DATA_OBJECT = "Data_Object"

class TechnologyElementType(str, Enum):
    """Technology Layer elements - nodes, devices, software, networks, and artifacts."""
    NODE = "Node"
    DEVICE = "Device"
    SYSTEM_SOFTWARE = "System_Software"
    TECHNOLOGY_COLLABORATION = "Technology_Collaboration"
    TECHNOLOGY_INTERFACE = "Technology_Interface"
    PATH = "Path"
    COMMUNICATION_NETWORK = "Communication_Network"
    TECHNOLOGY_FUNCTION = "Technology_Function"
    TECHNOLOGY_PROCESS = "Technology_Process"
    TECHNOLOGY_INTERACTION = "Technology_Interaction"
    TECHNOLOGY_EVENT = "Technology_Event"
    TECHNOLOGY_SERVICE = "Technology_Service"
    ARTIFACT = "Artifact"

class PhysicalElementType(str, Enum):
    """Physical Layer elements - equipment, facilities, distribution networks, and materials."""
    EQUIPMENT = "Equipment"
    FACILITY = "Facility"
    DISTRIBUTION_NETWORK = "Distribution_Network"
    MATERIAL = "Material"

class MotivationElementType(str, Enum):
    """Motivation Layer elements - stakeholders, drivers, goals, requirements, and principles."""
    STAKEHOLDER = "Stakeholder"
    DRIVER = "Driver"
    ASSESSMENT = "Assessment"
    GOAL = "Goal"
    OUTCOME = "Outcome"
    PRINCIPLE = "Principle"
    REQUIREMENT = "Requirement"
    CONSTRAINT = "Constraint"
    MEANING = "Meaning"
    VALUE = "Value"

class StrategyElementType(str, Enum):
    """Strategy Layer elements - resources, capabilities, courses of action, and value streams."""
    RESOURCE = "Resource"
    CAPABILITY = "Capability"
    COURSE_OF_ACTION = "Course_of_Action"
    VALUE_STREAM = "Value_Stream"

class ImplementationElementType(str, Enum):
    """Implementation Layer elements - work packages, deliverables, events, plateaus, and gaps."""
    WORK_PACKAGE = "Work_Package"
    DELIVERABLE = "Deliverable"
    IMPLEMENTATION_EVENT = "Implementation_Event"
    PLATEAU = "Plateau"
    GAP = "Gap"

class ArchiMateLayerType(str, Enum):
    """ArchiMate 3.2 specification layers."""
    BUSINESS = "Business"
    APPLICATION = "Application"
    TECHNOLOGY = "Technology"
    PHYSICAL = "Physical"
    MOTIVATION = "Motivation"
    STRATEGY = "Strategy"
    IMPLEMENTATION = "Implementation"

class ArchiMateRelationshipType(str, Enum):
    """Complete ArchiMate 3.2 relationship types with descriptions."""
    ACCESS = "Access"  # Element can access another element
    AGGREGATION = "Aggregation"  # Whole-part relationship, parts can exist independently
    ASSIGNMENT = "Assignment"  # Element is assigned to another element
    ASSOCIATION = "Association"  # General relationship between elements
    COMPOSITION = "Composition"  # Whole-part relationship, parts cannot exist independently
    FLOW = "Flow"  # Transfer of information, money, goods, etc.
    INFLUENCE = "Influence"  # Element influences another element
    REALIZATION = "Realization"  # Element realizes or implements another element
    SERVING = "Serving"  # Element serves another element
    SPECIALIZATION = "Specialization"  # Is-a relationship, inheritance
    TRIGGERING = "Triggering"  # Element triggers another element

class LayoutDirectionType(str, Enum):
    """Layout direction options for diagram generation."""
    TOP_BOTTOM = "top-bottom"
    LEFT_RIGHT = "left-right"
    BOTTOM_TOP = "bottom-top"
    RIGHT_LEFT = "right-left"

class LayoutSpacingType(str, Enum):
    """Layout spacing options for diagram generation."""
    COMPACT = "compact"
    NORMAL = "normal"
    WIDE = "wide"

class BooleanStringType(str, Enum):
    """Boolean values as strings (required for layout parameters)."""
    TRUE = "true"
    FALSE = "false"

# Pydantic models for input validation with comprehensive schema
class ElementInput(BaseModel):
    """ArchiMate element with comprehensive validation and capability discovery.
    
    Element types are organized by ArchiMate 3.2 layers:
    - Business: Business_Actor, Business_Role, Business_Process, Business_Service, etc.
    - Application: Application_Component, Application_Service, Data_Object, etc.
    - Technology: Node, Device, System_Software, Technology_Service, etc.  
    - Physical: Equipment, Facility, Distribution_Network, Material
    - Motivation: Stakeholder, Driver, Goal, Requirement, Principle, etc.
    - Strategy: Resource, Capability, Course_of_Action, Value_Stream
    - Implementation: Work_Package, Deliverable, Implementation_Event, Plateau, Gap
    """
    id: str = Field(..., 
        description="Unique element identifier (e.g., 'customer_portal', 'user_mgmt_service')")
    
    name: str = Field(..., 
        description="Element display name (e.g., 'Customer Portal', 'User Management Service')")
    
    element_type: str = Field(..., 
        description="""ArchiMate element type. Choose from layer-specific options:
        
        BUSINESS LAYER:
        • Business_Actor, Business_Role, Business_Collaboration, Business_Interface
        • Business_Function, Business_Process, Business_Event, Business_Service
        • Business_Object, Business_Contract, Business_Representation, Location
        
        APPLICATION LAYER:
        • Application_Component, Application_Collaboration, Application_Interface
        • Application_Function, Application_Interaction, Application_Process
        • Application_Event, Application_Service, Data_Object
        
        TECHNOLOGY LAYER:
        • Node, Device, System_Software, Technology_Collaboration, Technology_Interface
        • Path, Communication_Network, Technology_Function, Technology_Process
        • Technology_Interaction, Technology_Event, Technology_Service, Artifact
        
        PHYSICAL LAYER:
        • Equipment, Facility, Distribution_Network, Material
        
        MOTIVATION LAYER:
        • Stakeholder, Driver, Assessment, Goal, Outcome, Principle
        • Requirement, Constraint, Meaning, Value
        
        STRATEGY LAYER:
        • Resource, Capability, Course_of_Action, Value_Stream
        
        IMPLEMENTATION LAYER:
        • Work_Package, Deliverable, Implementation_Event, Plateau, Gap""")
    
    layer: ArchiMateLayerType = Field(..., 
        description="ArchiMate layer: Business, Application, Technology, Physical, Motivation, Strategy, Implementation")
    
    description: Optional[str] = Field(None, 
        description="Element description for documentation")
    
    stereotype: Optional[str] = Field(None, 
        description="Element stereotype for specialized notation")
    
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, 
        description="Additional element properties as key-value pairs")

class RelationshipInput(BaseModel):
    """ArchiMate relationship with comprehensive validation and capability discovery.
    
    Supports all 12 ArchiMate 3.2 relationship types:
    - Access: Element can access another element
    - Aggregation: Whole-part relationship (parts can exist independently)  
    - Assignment: Element is assigned to another element
    - Association: General relationship between elements
    - Composition: Whole-part relationship (parts cannot exist independently)
    - Flow: Transfer of information, money, goods, etc.
    - Influence: Element influences another element  
    - Realization: Element realizes or implements another element
    - Serving: Element serves another element
    - Specialization: Is-a relationship, inheritance
    - Triggering: Element triggers another element
    """
    id: str = Field(..., 
        description="Unique relationship identifier (e.g., 'portal_serves_customer', 'db_supports_service')")
    
    from_element: str = Field(..., 
        description="Source element ID (must match an element.id)")
    
    to_element: str = Field(..., 
        description="Target element ID (must match an element.id)")
    
    relationship_type: ArchiMateRelationshipType = Field(..., 
        description="""ArchiMate relationship type. Choose from:
        • Access - Element can access another element
        • Aggregation - Whole-part relationship (parts can exist independently)
        • Assignment - Element is assigned to another element  
        • Association - General relationship between elements
        • Composition - Whole-part relationship (parts cannot exist independently)
        • Flow - Transfer of information, money, goods, etc.
        • Influence - Element influences another element
        • Realization - Element realizes or implements another element
        • Serving - Element serves another element
        • Specialization - Is-a relationship, inheritance
        • Triggering - Element triggers another element""")
    
    description: Optional[str] = Field(None, 
        description="Relationship description for documentation")
    
    direction: Optional[LayoutDirectionType] = Field(None, 
        description="Direction hint for layout: top-bottom, left-right, bottom-top, right-left")
    
    label: Optional[str] = Field(None, 
        description="Custom relationship label (max 3 words, 30 chars). If not provided, uses translated relationship type.")

class DiagramInput(BaseModel):
    """Complete ArchiMate diagram specification with comprehensive capability discovery.
    
    Generates production-ready PlantUML diagrams with PNG/SVG output and live HTTP server URLs.
    Supports automatic language detection (Slovak/English) and intelligent layout optimization.
    """
    elements: List[ElementInput] = Field(..., 
        description="""ArchiMate elements organized by layer. Example:
        [
          {
            "id": "customer_portal", 
            "name": "Customer Portal",
            "element_type": "Application_Component",
            "layer": "Application",
            "description": "Web-based customer interface"
          }
        ]""")
    
    relationships: List[RelationshipInput] = Field(default_factory=list, 
        description="""ArchiMate relationships between elements. Example:
        [
          {
            "id": "portal_serves_customer",
            "from_element": "customer_portal", 
            "to_element": "customer_actor",
            "relationship_type": "Serving",
            "label": "provides interface"
          }
        ]""")
    
    title: Optional[str] = Field(None, 
        description="Diagram title (e.g., 'Customer Service Architecture', 'System Overview')")
    
    description: Optional[str] = Field(None, 
        description="Diagram description for documentation")
    
    layout: Optional[Dict[str, Any]] = Field(default_factory=dict, 
        description="""Layout configuration options. All values must be STRINGS:
        
        LAYOUT DIRECTION:
        • "direction": "top-bottom" | "left-right" | "bottom-top" | "right-left"
        
        LAYOUT SPACING:  
        • "spacing": "compact" | "normal" | "wide"
        
        DISPLAY OPTIONS (use "true" or "false" as strings, NOT booleans):
        • "show_legend": "true" | "false" 
        • "show_title": "true" | "false"
        • "group_by_layer": "true" | "false"
        • "show_element_types": "true" | "false" 
        • "show_relationship_labels": "true" | "false"
        
        EXAMPLE:
        {
          "direction": "top-bottom",
          "spacing": "compact", 
          "show_legend": "false",
          "group_by_layer": "true"
        }
        
        CRITICAL: Use string values like "true"/"false", NOT boolean true/false!""")
    
    language: Optional[Literal["en", "sk"]] = Field("en",
        description="""Language for diagram labels and layer names:
        • "en" - English (default)
        • "sk" - Slovak

        Language is automatically detected from element/relationship text content.
        Slovak detection triggers automatic translation of layer names and relationship labels.""")

    @model_validator(mode='before')
    @classmethod
    def parse_json_string(cls, data: Any) -> Any:
        """Parse JSON string to dict for Claude Code compatibility.

        Claude Code sends parameters as JSON strings, while Claude Desktop sends objects.
        This validator handles both cases automatically.
        """
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string for diagram parameter: {e}")
        return data

# Element type normalization mapping - input formats to internal format
ELEMENT_TYPE_MAPPING = {
    # Business Layer - normalize to internal format (with underscores)
    "BusinessActor": "Business_Actor",
    "Business_Actor": "Business_Actor",  # Identity mapping for correct format
    "BusinessRole": "Business_Role",
    "Business_Role": "Business_Role",  # Identity mapping
    "BusinessCollaboration": "Business_Collaboration",
    "Business_Collaboration": "Business_Collaboration",  # Identity mapping
    "BusinessInterface": "Business_Interface", 
    "Business_Interface": "Business_Interface",  # Identity mapping
    "BusinessFunction": "Business_Function",
    "Business_Function": "Business_Function",  # Identity mapping
    "BusinessProcess": "Business_Process",
    "Business_Process": "Business_Process",  # Identity mapping
    "BusinessEvent": "Business_Event",
    "Business_Event": "Business_Event",  # Identity mapping
    "BusinessService": "Business_Service",
    "Business_Service": "Business_Service",  # Identity mapping
    "BusinessObject": "Business_Object",
    "Business_Object": "Business_Object",  # Identity mapping
    "Contract": "Contract",
    "Business_Contract": "Contract",  # Normalize to shorter form
    "Representation": "Representation", 
    "Business_Representation": "Representation",  # Normalize to shorter form
    "Location": "Location",
    
    # Application Layer
    "ApplicationComponent": "Application_Component",
    "Application_Component": "Application_Component",  # Identity mapping
    "ApplicationCollaboration": "Application_Collaboration",
    "Application_Collaboration": "Application_Collaboration",  # Identity mapping
    "ApplicationInterface": "Application_Interface",
    "Application_Interface": "Application_Interface",  # Identity mapping
    "ApplicationFunction": "Application_Function",
    "Application_Function": "Application_Function",  # Identity mapping
    "ApplicationInteraction": "Application_Interaction",
    "Application_Interaction": "Application_Interaction",  # Identity mapping
    "ApplicationProcess": "Application_Process",
    "Application_Process": "Application_Process",  # Identity mapping
    "ApplicationEvent": "Application_Event",
    "Application_Event": "Application_Event",  # Identity mapping
    "ApplicationService": "Application_Service",
    "Application_Service": "Application_Service",  # Identity mapping
    "DataObject": "Data_Object",
    "Data_Object": "Data_Object",  # Identity mapping
    
    # Technology Layer
    "Node": "Node",
    "Device": "Device", 
    "SystemSoftware": "System_Software",
    "System_Software": "System_Software",  # Identity mapping
    "TechnologyCollaboration": "Technology_Collaboration",
    "Technology_Collaboration": "Technology_Collaboration",  # Identity mapping
    "TechnologyInterface": "Technology_Interface",
    "Technology_Interface": "Technology_Interface",  # Identity mapping
    "Path": "Path",
    "CommunicationNetwork": "Communication_Network",
    "Communication_Network": "Communication_Network",  # Identity mapping
    "TechnologyFunction": "Technology_Function",
    "Technology_Function": "Technology_Function",  # Identity mapping
    "TechnologyProcess": "Technology_Process",
    "Technology_Process": "Technology_Process",  # Identity mapping
    "TechnologyInteraction": "Technology_Interaction",
    "Technology_Interaction": "Technology_Interaction",  # Identity mapping
    "TechnologyEvent": "Technology_Event",
    "Technology_Event": "Technology_Event",  # Identity mapping
    "TechnologyService": "Technology_Service",
    "Technology_Service": "Technology_Service",  # Identity mapping
    "Artifact": "Artifact",
    
    # Physical Layer  
    "Equipment": "Equipment",
    "Facility": "Facility",
    "DistributionNetwork": "Distribution_Network",
    "Distribution_Network": "Distribution_Network",  # Identity mapping
    "Material": "Material",
    
    # Motivation Layer
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
    "CourseOfAction": "Course_of_Action",
    "Course_of_Action": "Course_of_Action",  # Identity mapping
    "ValueStream": "Value_Stream", 
    "Value_Stream": "Value_Stream",  # Identity mapping
    
    # Implementation Layer
    "WorkPackage": "Work_Package",
    "Work_Package": "Work_Package",  # Identity mapping
    "Deliverable": "Deliverable",
    "ImplementationEvent": "Implementation_Event",
    "Implementation_Event": "Implementation_Event",  # Identity mapping
    "Plateau": "Plateau",
    "Gap": "Gap"
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

def _build_enhanced_error_response(original_error: Exception, debug_log: list, error_export_dir, plantuml_code: str = None) -> str:
    """Build comprehensive error response with debugging information for MCP tool."""
    try:
        # Extract Java PlantUML output from debug log
        plantuml_return_code = None
        plantuml_stderr = None
        plantuml_command = None
        error_line = None
        
        for entry in debug_log:
            if 'details' in entry:
                details = entry['details']
                # Extract PlantUML execution details
                if 'png_return_code' in details:
                    plantuml_return_code = details['png_return_code']
                if 'command' in details and 'plantuml.jar' in details['command']:
                    plantuml_command = details['command']
                if 'output' in details and ('Error line' in details['output'] or 'Some diagram description contains errors' in details['output']):
                    plantuml_stderr = details['output']
                    # Extract line number from error
                    if 'Error line' in details['output']:
                        import re
                        line_match = re.search(r'Error line (\d+)', details['output'])
                        if line_match:
                            error_line = int(line_match.group(1))
        
        # Build enhanced error message
        error_parts = []
        error_parts.append(f"❌ **PNG Generation Failed**")
        
        if plantuml_return_code:
            error_parts.append(f"**PlantUML Return Code:** {plantuml_return_code}")
        
        if plantuml_stderr:
            error_parts.append(f"**PlantUML Error:** {plantuml_stderr.strip()}")
        
        # Add problematic PlantUML line if available
        if plantuml_code and error_line:
            lines = plantuml_code.split('\n')
            if 1 <= error_line <= len(lines):
                problematic_line = lines[error_line - 1].strip()
                error_parts.append(f"**Problematic Line {error_line}:** `{problematic_line}`")
                
                # Add context (line before and after)
                context_lines = []
                if error_line > 1:
                    context_lines.append(f"{error_line-1:2d}: {lines[error_line-2].strip()}")
                context_lines.append(f"{error_line:2d}: {problematic_line} ⚠️")
                if error_line < len(lines):
                    context_lines.append(f"{error_line+1:2d}: {lines[error_line].strip()}")
                
                error_parts.append("**Context:**")
                error_parts.append("```")
                error_parts.extend(context_lines)
                error_parts.append("```")
        
        # Add debugging information with actual log contents
        if error_export_dir:
            # Try to read and include generation.log contents
            try:
                log_file_path = os.path.join(error_export_dir, "generation.log")
                if os.path.exists(log_file_path):
                    with open(log_file_path, 'r', encoding='utf-8') as f:
                        log_contents = f.read()
                    error_parts.append("**🔍 Debug Log:**")
                    error_parts.append("```")
                    error_parts.append(log_contents)
                    error_parts.append("```")
                else:
                    error_parts.append(f"**🔍 Debug Files:** {error_export_dir}")
                    error_parts.append("- `generation.log` - Complete debug trace")
            except Exception as log_read_error:
                error_parts.append(f"**🔍 Debug Files:** {error_export_dir} (log read error: {log_read_error})")
                error_parts.append("- `generation.log` - Complete debug trace")
            
            if plantuml_code:
                error_parts.append("**📄 Debug Files Available:**")
                error_parts.append(f"- `{error_export_dir}/diagram.puml` - Generated PlantUML code")
                error_parts.append(f"- `{error_export_dir}/input.json` - Original input data")
        
        # Add troubleshooting suggestions
        error_parts.append("**🛠️ Troubleshooting:**")
        if error_line and plantuml_code:
            lines = plantuml_code.split('\n')
            if 1 <= error_line <= len(lines):
                problematic_line = lines[error_line - 1].strip()
                if "Application_Application_" in problematic_line:
                    error_parts.append("- **Duplicate layer prefix detected** - This is a known issue being fixed")
                elif "_" not in problematic_line and "(" in problematic_line:
                    error_parts.append("- **Missing element type prefix** - Check element type normalization")
                else:
                    error_parts.append("- Check PlantUML syntax on the problematic line")
                    error_parts.append("- Verify element types and relationship syntax")
        
        if plantuml_command:
            error_parts.append(f"- **Test PlantUML directly:** `{plantuml_command.replace('/tmp/tmp', 'path/to/diagram')}`")
        
        return "\n".join(error_parts)
        
    except Exception as build_error:
        # Fallback to simple error if enhancement fails
        return f"Failed to create diagram: {str(original_error)}\n\nNote: Enhanced error details unavailable due to: {str(build_error)}"

def _save_failed_attempt(plantuml_code: str, diagram_input: DiagramInput, debug_log: list, error_message: str) -> None:
    """Save complete failure context for debugging: PlantUML code, input JSON, and debug logs."""
    try:
        import json
        from datetime import datetime
        
        # Create failed_attempts directory
        exports_dir = get_exports_directory()
        failed_attempts_dir = exports_dir / "failed_attempts" 
        failed_attempts_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped failure directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        failure_dir = failed_attempts_dir / timestamp
        failure_dir.mkdir(exist_ok=True)
        
        # Save PlantUML code
        puml_file = failure_dir / "diagram.puml"
        with open(puml_file, 'w', encoding='utf-8') as f:
            f.write(plantuml_code)
        
        # Save input JSON (convert DiagramInput to dict for serialization)
        input_file = failure_dir / "input.json"
        with open(input_file, 'w', encoding='utf-8') as f:
            # Convert Pydantic model to dict for JSON serialization
            input_dict = diagram_input.model_dump() if hasattr(diagram_input, 'model_dump') else diagram_input.dict()
            json.dump(input_dict, f, indent=2, ensure_ascii=False)
        
        # Save debug log with error message
        log_file = failure_dir / "generation.log"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"FAILURE: {error_message}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write("=" * 60 + "\n\n")
            
            # Write debug log entries
            for entry in debug_log:
                f.write(f"[{entry['timestamp']}] {entry['level']}: {entry['message']}\n")
                if 'details' in entry:
                    f.write(f"  Details: {entry['details']}\n")
                f.write("\n")
        
        logger.info(f"Saved failed attempt context to: {failure_dir}")
        
    except Exception as save_error:
        logger.error(f"Failed to save failure context: {save_error}")

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
    
    # Extract translator from generator if available
    translator = getattr(generator, 'translator', None)
    
    # Header - diagram name
    md_content.append(f"# {title}")
    md_content.append("")
    
    # Slovný popis diagramu
    if description:
        md_content.append(description)
        md_content.append("")
    
    
    # Samotný diagram
    md_content.append(f"![{title}]({png_filename})")
    md_content.append("")
    
    # Detailný popis diagramu (niekoľko viet až odstavcov)
    md_content.append(_generate_detailed_description(generator, title, translator))
    md_content.append("")
    
    # Overview sekcia s podporou slovenčiny
    if translator and translator.language == 'sk':
        md_content.append("## Prehľad")
        md_content.append("")
        md_content.append(f"- **Celkom prvkov:** {generator.get_element_count()}")
        md_content.append(f"- **Celkom vzťahov:** {generator.get_relationship_count()}")
        md_content.append(f"- **Používané vrstvy:** {', '.join(generator.get_layers_used())}")
        md_content.append("")
        
        # Elements by layer (slovensky)
        md_content.append("## Architektonické prvky podľa vrstiev")
    else:
        md_content.append("## Overview")
        md_content.append("")
        md_content.append(f"- **Total Elements:** {generator.get_element_count()}")
        md_content.append(f"- **Total Relationships:** {generator.get_relationship_count()}")
        md_content.append(f"- **Layers Used:** {', '.join(generator.get_layers_used())}")
        md_content.append("")
        
        # Elements by layer (anglicky)
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
        if translator and translator.language == 'sk':
            md_content.append(f"### {layer_name} vrstva")
        else:
            md_content.append(f"### {layer_name} Layer")
        md_content.append("")
        
        elements = elements_by_layer[layer_name]
        if elements:
            if translator and translator.language == 'sk':
                md_content.append("| ID | Názov | Typ | Popis |")
            else:
                md_content.append("| ID | Name | Type | Description |")
            md_content.append("|---|---|---|---|")
            
            for element in sorted(elements, key=lambda e: e.id):
                desc = element.description or "-"
                element_type = element.element_type.replace("_", " ")
                md_content.append(f"| `{element.id}` | **{element.name}** | {element_type} | {desc} |")
            
            md_content.append("")
    
    # Relationships
    if translator and translator.language == 'sk':
        md_content.append("## Vzťahy")
    else:
        md_content.append("## Relationships")
    md_content.append("")
    
    if generator.relationships:
        if translator and translator.language == 'sk':
            md_content.append("| Od | Vzťah | Do | Popis |")
        else:
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
        if translator and translator.language == 'sk':
            md_content.append("*Žiadne vzťahy nedefinované*")
        else:
            md_content.append("*No relationships defined*")
        md_content.append("")
    
    # Architecture insights s podporou slovenčiny
    if translator and translator.language == 'sk':
        md_content.append("## Architektonické poznatky")
    else:
        md_content.append("## Architecture Insights")
    md_content.append("")
    
    # Layer distribution
    layer_counts = {}
    for element in generator.elements.values():
        layer = element.layer.value
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
    
    if translator and translator.language == 'sk':
        md_content.append("### Rozdelenie vrstiev")
        md_content.append("")
        for layer, count in sorted(layer_counts.items()):
            percentage = (count / generator.get_element_count()) * 100
            md_content.append(f"- **{layer}**: {count} prvkov ({percentage:.1f}%)")
    else:
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
    
    if translator and translator.language == 'sk':
        md_content.append("### Typy prvkov")
    else:
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
        
        if translator and translator.language == 'sk':
            md_content.append("### Typy vzťahov")
        else:
            md_content.append("### Relationship Types")
        md_content.append("")
        for rel_type, count in sorted(rel_types.items()):
            md_content.append(f"- {rel_type}: {count}")
        md_content.append("")
    
    # Footer (bez Source Files sekcie)
    md_content.append("---")
    if translator and translator.language == 'sk':
        md_content.append(f"*Vygenerované ArchiMate MCP Serverom @ {datetime.now().strftime('%d.%m.%Y o %H:%M')}*")
    else:
        md_content.append(f"*Generated by ArchiMate MCP Server @ {datetime.now().strftime('%Y-%m-%d at %H:%M')}*")
    
    return "\n".join(md_content)

def _generate_detailed_description(generator, title: str, translator=None) -> str:
    """Generate detailed description for the diagram based on its content."""
    
    # Analyze the diagram content
    element_count = generator.get_element_count()
    relationship_count = generator.get_relationship_count()
    layers = generator.get_layers_used()
    
    # Generate contextual description based on diagram characteristics
    description_parts = []
    
    # Translation templates
    if translator and translator.language == 'sk':
        # Slovak templates
        templates = {
            'basic_overview': "Tento diagram {title} ilustruje komplexný architektonický pohľad s {element_count} prvkami a {relationship_count} vzťahmi.",
            'single_layer': "Diagram sa zameriava na vrstvu {layer}, poskytujúc detailný náhľad na tento špecifický architektonický aspekt.",
            'multi_layer': "Architektúra zahŕňa viacero vrstiev vrátane {layer_list}, čo demonštruje integráciu a závislosti medzi vrstvami.",
            'multi_layer_simple': "Architektúra zahŕňa {layer1} a {layer2} vrstvy, čo demonštruje integráciu a závislosti medzi vrstvami.",
            'diverse_components': "Diagram predstavuje rôznorodé architektonické komponenty s {type_count} rôznymi typmi prvkov, čo odráža bohatý a komplexný systémový dizajn.",
            'relationships': "Prepojenia demonštrujú {rel_count} typov vzťahov, čo poukazuje na sofistikované architektonické vzory a závislosti.",
            'purpose': "Tento architektonický pohľad slúži ako základ pre pochopenie systémového dizajnu, podporu rozhodovania a uľahčenie komunikácie medzi zainteresovanými stranami."
        }
    else:
        # English templates (default)
        templates = {
            'basic_overview': "This {title} diagram illustrates a comprehensive architectural view with {element_count} elements and {relationship_count} relationships.",
            'single_layer': "The diagram focuses on the {layer} layer, providing detailed insight into this specific architectural aspect.",
            'multi_layer': "The architecture spans multiple layers including {layer_list}, demonstrating cross-layer integration and dependencies.",
            'multi_layer_simple': "The architecture spans {layer1} and {layer2} layers, demonstrating cross-layer integration and dependencies.",
            'diverse_components': "The diagram showcases diverse architectural components with {type_count} different element types, reflecting a rich and complex system design.",
            'relationships': "The interconnections demonstrate {rel_count} types of relationships, indicating sophisticated architectural patterns and dependencies.",
            'purpose': "This architectural view serves as a foundation for understanding system design, supporting decision-making, and facilitating communication among stakeholders."
        }
    
    # Basic overview
    if element_count > 0:
        description_parts.append(templates['basic_overview'].format(
            title=title.lower(), 
            element_count=element_count, 
            relationship_count=relationship_count
        ))
    
    # Layer analysis
    if len(layers) == 1:
        description_parts.append(templates['single_layer'].format(layer=layers[0]))
    elif len(layers) == 2:
        description_parts.append(templates['multi_layer_simple'].format(
            layer1=layers[0], 
            layer2=layers[1]
        ))
    elif len(layers) > 2:
        layer_list = ", ".join(layers[:-1]) + f", and {layers[-1]}" if translator and translator.language != 'sk' else ", ".join(layers[:-1]) + f" a {layers[-1]}"
        description_parts.append(templates['multi_layer'].format(layer_list=layer_list))
    
    # Element diversity analysis
    if element_count > 0:
        element_types = set()
        for element in generator.elements.values():
            element_types.add(element.element_type)
        
        if len(element_types) > 3:
            description_parts.append(templates['diverse_components'].format(type_count=len(element_types)))
        
    # Relationship insights
    if relationship_count > 0:
        rel_types = set()
        for rel in generator.relationships:
            rel_type = rel.relationship_type.value if hasattr(rel.relationship_type, 'value') else str(rel.relationship_type)
            rel_types.add(rel_type)
        
        if len(rel_types) > 1:
            description_parts.append(templates['relationships'].format(rel_count=len(rel_types)))
    
    # Purpose and value statement
    description_parts.append(templates['purpose'])
    
    return " ".join(description_parts)

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
        # Find layer-specific element types for better error message
        layer_elements = []
        for key, value in ELEMENT_TYPE_MAPPING.items():
            if normalized_layer.lower() in key.lower():
                layer_elements.append(key)
        
        if layer_elements:
            return False, f"Invalid element type: '{element.element_type}' for {normalized_layer} layer. Valid {normalized_layer} types: {layer_elements}"
        else:
            valid_types = list(ELEMENT_TYPE_MAPPING.keys())
            return False, f"Invalid element type: '{element.element_type}'. Use 'node' instead of 'technology_node'. Valid types: {valid_types[:10]}..."
    
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
    """Generate production-ready ArchiMate diagrams with comprehensive capability discovery.
    
    🏗️ COMPLETE ARCHIMATE 3.2 SUPPORT:
    • ALL 55+ elements across 7 layers (Business, Application, Technology, Physical, Motivation, Strategy, Implementation)
    • ALL 12 relationship types with directional variants
    • Universal PlantUML generation with proper layer prefixes (Physical_, Strategy_, Implementation_, Motivation_)
    
    📋 SUPPORTED ELEMENTS BY LAYER:
    
    BUSINESS: Business_Actor, Business_Role, Business_Collaboration, Business_Interface, Business_Function, 
              Business_Process, Business_Event, Business_Service, Business_Object, Business_Contract, 
              Business_Representation, Location
              
    APPLICATION: Application_Component, Application_Collaboration, Application_Interface, Application_Function,
                 Application_Interaction, Application_Process, Application_Event, Application_Service, Data_Object
                 
    TECHNOLOGY: Node, Device, System_Software, Technology_Collaboration, Technology_Interface, Path,
                Communication_Network, Technology_Function, Technology_Process, Technology_Interaction,
                Technology_Event, Technology_Service, Artifact
                
    PHYSICAL: Equipment, Facility, Distribution_Network, Material
    
    MOTIVATION: Stakeholder, Driver, Assessment, Goal, Outcome, Principle, Requirement, Constraint, Meaning, Value
    
    STRATEGY: Resource, Capability, Course_of_Action, Value_Stream
    
    IMPLEMENTATION: Work_Package, Deliverable, Implementation_Event, Plateau, Gap
    
    🔗 SUPPORTED RELATIONSHIPS:
    • Access, Aggregation, Assignment, Association, Composition, Flow
    • Influence, Realization, Serving, Specialization, Triggering
    
    ⚙️ LAYOUT CONFIGURATION (all values as STRINGS):
    • direction: "top-bottom" | "left-right" | "bottom-top" | "right-left"
    • spacing: "compact" | "normal" | "wide" 
    • show_legend: "true" | "false"
    • show_title: "true" | "false"
    • group_by_layer: "true" | "false"
    • show_element_types: "true" | "false"
    • show_relationship_labels: "true" | "false"
    
    🌍 LANGUAGE SUPPORT:
    • Automatic language detection (Slovak/English)
    • Slovak detection via text patterns and diacritics
    • Auto-translation of layer names and relationship labels
    
    📦 OUTPUT ARTIFACTS (saved to CWD/exports/YYYYMMDD_HHMMSS/):
    • diagram.puml: Validated PlantUML source code
    • diagram.png: Production-ready PNG image 
    • diagram.svg: Vector SVG format
    • architecture.md: Extended documentation with embedded images
    • generation.log: Comprehensive debug information
    • metadata.json: Diagram statistics and metadata
    
    🌐 LIVE PREVIEW:
    • Automatic HTTP server for instant diagram viewing
    • Base64 data URLs for immediate browser display
    • Direct PlantUML server integration for online rendering
    
    ⚡ ERROR PREVENTION:
    This enhanced schema prevents the 5 main error types identified in testing:
    1. Strategy/Physical/Implementation layer element type validation
    2. Layout parameter data type validation (strings, not booleans) 
    3. Comprehensive relationship type enumeration
    4. Layer-specific element type guidance
    5. Fallback strategies for unsupported elements
    
    📚 ARCHITECTURE PATTERN EXAMPLES:
    
    SIMPLE SERVICE ARCHITECTURE:
    {
      "elements": [
        {"id": "customer", "name": "Customer", "element_type": "Business_Actor", "layer": "Business"},
        {"id": "portal", "name": "Customer Portal", "element_type": "Application_Component", "layer": "Application"},
        {"id": "database", "name": "Customer DB", "element_type": "Node", "layer": "Technology"}
      ],
      "relationships": [
        {"id": "r1", "from_element": "portal", "to_element": "customer", "relationship_type": "Serving"},
        {"id": "r2", "from_element": "database", "to_element": "portal", "relationship_type": "Serving"}
      ],
      "layout": {"direction": "top-bottom", "spacing": "compact", "show_legend": "false"}
    }
    
    COMPLETE ENTERPRISE ARCHITECTURE:
    {
      "elements": [
        {"id": "architect", "name": "Enterprise Architect", "element_type": "Stakeholder", "layer": "Motivation"},
        {"id": "goal", "name": "Digital Transformation", "element_type": "Goal", "layer": "Motivation"},
        {"id": "capability", "name": "Service Integration", "element_type": "Capability", "layer": "Strategy"},
        {"id": "process", "name": "Order Management", "element_type": "Business_Process", "layer": "Business"},
        {"id": "service", "name": "Order Service", "element_type": "Application_Service", "layer": "Application"},
        {"id": "server", "name": "Application Server", "element_type": "Node", "layer": "Technology"},
        {"id": "datacenter", "name": "Primary Datacenter", "element_type": "Facility", "layer": "Physical"},
        {"id": "project", "name": "Service Migration", "element_type": "Work_Package", "layer": "Implementation"}
      ],
      "relationships": [
        {"id": "r1", "from_element": "architect", "to_element": "goal", "relationship_type": "Assignment"},
        {"id": "r2", "from_element": "goal", "to_element": "capability", "relationship_type": "Realization"},
        {"id": "r3", "from_element": "capability", "to_element": "process", "relationship_type": "Realization"},
        {"id": "r4", "from_element": "process", "to_element": "service", "relationship_type": "Realization"},
        {"id": "r5", "from_element": "service", "to_element": "server", "relationship_type": "Assignment"},
        {"id": "r6", "from_element": "server", "to_element": "datacenter", "relationship_type": "Assignment"},
        {"id": "r7", "from_element": "project", "to_element": "service", "relationship_type": "Realization"}
      ],
      "layout": {"direction": "top-bottom", "group_by_layer": "true", "spacing": "normal"}
    }
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
            show_legend=(get_layout_setting('ARCHI_MCP_DEFAULT_SHOW_LEGEND', str(layout_config.get('show_legend', 'true'))).lower() == 'true'),
            show_title=(get_layout_setting('ARCHI_MCP_DEFAULT_SHOW_TITLE', str(layout_config.get('show_title', 'true'))).lower() == 'true'),
            group_by_layer=(get_layout_setting('ARCHI_MCP_DEFAULT_GROUP_BY_LAYER', str(layout_config.get('group_by_layer', 'false'))).lower() == 'true'),
            spacing=get_layout_setting('ARCHI_MCP_DEFAULT_SPACING', layout_config.get('spacing')),
            show_element_types=(get_layout_setting('ARCHI_MCP_DEFAULT_SHOW_ELEMENT_TYPES', str(layout_config.get('show_element_types', 'false'))).lower() == 'true'),
            show_relationship_labels=(get_layout_setting('ARCHI_MCP_DEFAULT_SHOW_RELATIONSHIP_LABELS', str(layout_config.get('show_relationship_labels', 'true'))).lower() == 'true')
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
        
        log_debug('INFO', f'PlantUML validation VERIFIED ✅: {error_msg}')
        
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
                error_msg = """PlantUML jar not found. Download it by running:
curl -L https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar -o plantuml.jar

The jar should be placed in the project root directory or one of these locations:
- ./plantuml.jar (current directory)
- /usr/local/bin/plantuml.jar
- /opt/homebrew/bin/plantuml.jar"""
                raise Exception(error_msg)
            
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
                    # Save failure context before raising error
                    _save_failed_attempt(plantuml_code, diagram, debug_log, f"PNG validation failed: {png_validation_error}, file size: {file_size} bytes")
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
                # Save failure context before raising error
                _save_failed_attempt(plantuml_code, diagram, debug_log, f"PNG generation failed: return code {png_result.returncode}, stderr: {png_result.stderr}")
                raise Exception(f"PNG generation failed: return code {png_result.returncode}, stderr: {png_result.stderr}")
                
            # Cleanup temporary files
            try:
                os.unlink(temp_puml_path)
            except:
                pass
                
        except subprocess.TimeoutExpired:
            log_debug('ERROR', 'PNG and SVG generation timed out after 60 seconds')
            # Save failure context before raising error
            _save_failed_attempt(plantuml_code, diagram, debug_log, "PNG generation timed out after 60 seconds")
            raise ArchiMateGenerationError("PNG generation timed out after 60 seconds")
        except Exception as png_error:
            log_debug('ERROR', f'PNG and SVG generation failed: {str(png_error)}', {
                'error_type': type(png_error).__name__
            })
            # Save failure context before raising error
            _save_failed_attempt(plantuml_code, diagram, debug_log, f"PNG generation failed: {str(png_error)}")
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
        
        # Generate ArchiMate XML Exchange export (only after successful PNG generation)
        try:
            from .xml_export import ArchiMateXMLExporter
            xml_exporter = ArchiMateXMLExporter()
            
            # Extract elements and relationships from generator
            elements = list(generator_with_translator.elements.values())
            relationships = generator_with_translator.relationships
            
            # Export to XML
            xml_file = export_dir / "archimate_model.archimate"
            xml_content = xml_exporter.export_to_xml(
                elements=elements,
                relationships=relationships,
                model_name=title or "ArchiMate Model",
                output_path=xml_file
            )
            
            log_debug('INFO', f'Generated ArchiMate XML Exchange export: {xml_file}')
            
        except ImportError:
            log_debug('INFO', 'XML export module not available (lxml not installed)')
        except Exception as xml_error:
            log_debug('WARNING', f'XML export failed: {str(xml_error)}')
        
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
        
        # Start HTTP server and generate URLs for diagram viewing
        diagram_urls = {}
        try:
            port = start_http_server()
            if port and svg_generated:
                svg_relative_path = os.path.relpath(export_dir / "diagram.svg", os.getcwd())
                diagram_urls["svg"] = f"http://127.0.0.1:{port}/{svg_relative_path}"
                log_debug('INFO', f'HTTP server running on port {port}, SVG URL: {diagram_urls["svg"]}')
            elif port:
                png_relative_path = os.path.relpath(export_dir / "diagram.png", os.getcwd()) 
                diagram_urls["png"] = f"http://127.0.0.1:{port}/{png_relative_path}"
                log_debug('INFO', f'HTTP server running on port {port}, PNG URL: {diagram_urls["png"]}')
        except Exception as http_error:
            log_debug('WARNING', f'Failed to start HTTP server: {http_error}')
        
        # Enhanced success message with URL
        success_message = f"✅ ArchiMate diagram created successfully in {export_dir}"
        if diagram_urls:
            if "svg" in diagram_urls:
                success_message += f"\n\n🔗 **View SVG diagram:** {diagram_urls['svg']}"
            elif "png" in diagram_urls:
                success_message += f"\n\n🔗 **View PNG diagram:** {diagram_urls['png']}"
        
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
            "diagram_urls": diagram_urls,
            "statistics": metadata["statistics"],
            "message": success_message,
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
        error_export_dir = None
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
        
        # Extract detailed error information from debug log and original error
        enhanced_error_info = _build_enhanced_error_response(e, debug_log, error_export_dir, locals().get('plantuml_code'))
        
        # Raise enhanced error with comprehensive debugging information
        raise ArchiMateGenerationError(enhanced_error_info)

# Removed validate_archimate_model - not needed in simplified API

# Debug tools

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





# Server startup
def main():
    """Main entry point for the ArchiMate MCP server."""
    logger.info("Starting ArchiMate MCP Server with FastMCP")
    logger.info(f"Available tools: create_archimate_diagram, test_element_normalization")
    
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    main()
