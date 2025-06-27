"""Base ArchiMate element definition."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ArchiMateLayer(str, Enum):
    """ArchiMate layers according to ArchiMate 3.2 specification."""
    BUSINESS = "Business"
    APPLICATION = "Application"
    TECHNOLOGY = "Technology"
    PHYSICAL = "Physical"
    MOTIVATION = "Motivation"
    STRATEGY = "Strategy"
    IMPLEMENTATION = "Implementation"


class ArchiMateAspect(str, Enum):
    """ArchiMate aspects according to ArchiMate 3.2 specification."""
    ACTIVE_STRUCTURE = "Active Structure"
    PASSIVE_STRUCTURE = "Passive Structure"
    BEHAVIOR = "Behavior"


class ArchiMateElement(BaseModel):
    """Base class for all ArchiMate elements."""
    
    id: str = Field(..., description="Unique identifier for the element")
    name: str = Field(..., description="Display name of the element")
    element_type: str = Field(..., description="ArchiMate element type")
    layer: ArchiMateLayer = Field(..., description="ArchiMate layer")
    aspect: ArchiMateAspect = Field(..., description="ArchiMate aspect")
    description: Optional[str] = Field(None, description="Element description")
    stereotype: Optional[str] = Field(None, description="Element stereotype")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties")
    documentation: Optional[str] = Field(None, description="Element documentation")
    
    def to_plantuml(self) -> str:
        """Generate PlantUML code for this element.
        
        Returns:
            PlantUML code string
        """
        # Get color based on layer
        color = self._get_layer_color()
        
        # Build stereotype if present
        stereotype_str = ""
        if self.stereotype:
            stereotype_str = f" <<{self.stereotype}>>"
        
        # Use element_type directly - it should already be normalized by element_normalizer
        # DO NOT normalize again to avoid double normalization bug
        element_type = self.element_type
        
        # Generate PlantUML archimate element
        # Element type from normalizer already includes layer prefix (e.g., "Business_Actor")
        # Ensure proper UTF-8 encoding for names with diacritics
        safe_name = self.name.encode('utf-8').decode('utf-8')
        plantuml_code = f'{element_type}({self.id}, "{safe_name}"{stereotype_str})'
        
        return plantuml_code
    
    def _get_layer_color(self) -> str:
        """Get the default color for this layer.
        
        Returns:
            Color string for PlantUML
        """
        layer_colors = {
            ArchiMateLayer.BUSINESS: "Business",
            ArchiMateLayer.APPLICATION: "Application", 
            ArchiMateLayer.TECHNOLOGY: "Technology",
            ArchiMateLayer.PHYSICAL: "Physical",
            ArchiMateLayer.MOTIVATION: "Motivation",
            ArchiMateLayer.STRATEGY: "Strategy",
            ArchiMateLayer.IMPLEMENTATION: "Implementation",
        }
        return layer_colors.get(self.layer, "Technology")
    
    def _normalize_element_type(self, element_type: str) -> str:
        """Normalize element type for PlantUML compatibility.
        
        Args:
            element_type: Raw element type string
            
        Returns:
            Normalized element type for PlantUML
        """
        # Replace hyphens with underscores and ensure proper capitalization
        normalized = element_type.replace('-', '_')
        
        # Handle common element type patterns
        type_mappings = {
            'business_actor': 'Business_Actor',
            'business_role': 'Business_Role', 
            'business_collaboration': 'Business_Collaboration',
            'business_interface': 'Business_Interface',
            'business_process': 'Business_Process',
            'business_function': 'Business_Function',
            'business_interaction': 'Business_Interaction',
            'business_event': 'Business_Event',
            'business_service': 'Business_Service',
            'business_object': 'Business_Object',
            'business_contract': 'Business_Contract',
            'business_representation': 'Business_Representation',
            'application_component': 'Application_Component',
            'application_collaboration': 'Application_Collaboration',
            'application_interface': 'Application_Interface',
            'application_function': 'Application_Function',
            'application_interaction': 'Application_Interaction',
            'application_process': 'Application_Process',
            'application_event': 'Application_Event',
            'application_service': 'Application_Service',
            'data_object': 'DataObject',
            'technology_interface': 'Technology_Interface',
            'technology_function': 'Technology_Function',
            'technology_process': 'Technology_Process',
            'technology_interaction': 'Technology_Interaction',
            'technology_event': 'Technology_Event',
            'technology_service': 'Technology_Service',
            'system_software': 'SystemSoftware',
            'technology_collaboration': 'Technology_Collaboration',
            'communication_network': 'Communication_Network',
            'distribution_network': 'Distribution_Network',
            'work_package': 'Work_Package'
        }
        
        # Convert to lowercase for lookup
        lookup_key = normalized.lower()
        if lookup_key in type_mappings:
            return type_mappings[lookup_key]
        
        # Default: capitalize each word separated by underscore
        parts = normalized.split('_')
        return '_'.join(word.capitalize() for word in parts)
    
    def validate_element(self) -> List[str]:
        """Validate the element according to ArchiMate specification.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required fields
        if not self.id:
            errors.append("Element ID is required")
        if not self.name:
            errors.append("Element name is required")
        if not self.element_type:
            errors.append("Element type is required")
            
        # Check ID format (alphanumeric and underscore only)
        if self.id and not self.id.replace("_", "").isalnum():
            errors.append("Element ID must contain only alphanumeric characters and underscores")
            
        return errors
    
    def __str__(self) -> str:
        return f"{self.element_type}({self.id}): {self.name}"
    
    def __repr__(self) -> str:
        return f"ArchiMateElement(id='{self.id}', name='{self.name}', type='{self.element_type}')"