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
        
        # Generate PlantUML archimate element
        # Handle element types that already contain layer prefix
        if self.element_type.startswith(f'{self.layer.value}_'):
            plantuml_code = f'{self.element_type}({self.id}, "{self.name}"{stereotype_str})'
        else:
            plantuml_code = f'{self.layer.value}_{self.element_type}({self.id}, "{self.name}"{stereotype_str})'
        
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