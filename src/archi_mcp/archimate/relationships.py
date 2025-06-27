"""ArchiMate relationship definitions."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

from ..utils.exceptions import ArchiMateRelationshipError


class RelationshipType(str, Enum):
    """ArchiMate relationship types according to ArchiMate 3.2 specification."""
    ACCESS = "Access"
    AGGREGATION = "Aggregation"
    ASSIGNMENT = "Assignment"
    ASSOCIATION = "Association"
    COMPOSITION = "Composition"
    FLOW = "Flow"
    INFLUENCE = "Influence"
    REALIZATION = "Realization"
    SERVING = "Serving"
    SPECIALIZATION = "Specialization"
    TRIGGERING = "Triggering"


class RelationshipDirection(str, Enum):
    """Relationship direction modifiers for PlantUML."""
    UP = "Up"
    DOWN = "Down"
    LEFT = "Left"
    RIGHT = "Right"


class ArchiMateRelationship(BaseModel):
    """ArchiMate relationship definition."""
    
    id: str = Field(..., description="Unique identifier for the relationship")
    from_element: str = Field(..., description="Source element ID")
    to_element: str = Field(..., description="Target element ID")
    relationship_type: RelationshipType = Field(..., description="Type of relationship")
    direction: Optional[RelationshipDirection] = Field(None, description="Optional direction")
    description: Optional[str] = Field(None, description="Relationship description")
    label: Optional[str] = Field(None, description="Relationship label")
    properties: dict = Field(default_factory=dict, description="Additional properties")
    
    def to_plantuml(self) -> str:
        """Generate PlantUML code for this relationship.
        
        Returns:
            PlantUML relationship code string
        """
        # Build relationship type with direction
        rel_type = self.relationship_type.value
        if self.direction:
            rel_type = f"{rel_type}_{self.direction.value}"
        
        # Build label
        label = self.label or self.description or ""
        if label:
            label = f'"{label}"'
        else:
            # Use relationship type as default label
            label = f'"{rel_type.lower()}"'
        
        # Generate PlantUML relationship
        plantuml_code = f'Rel_{rel_type}({self.from_element}, {self.to_element}, {label})'
        
        return plantuml_code
    
    def validate_relationship(self, elements: dict) -> List[str]:
        """Validate the relationship according to ArchiMate specification.
        
        Args:
            elements: Dictionary of element IDs to ArchiMateElement objects
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check if elements exist
        if self.from_element not in elements:
            errors.append(f"Source element '{self.from_element}' not found")
        if self.to_element not in elements:
            errors.append(f"Target element '{self.to_element}' not found")
            
        if errors:
            return errors
        
        # Get element objects
        from_elem = elements[self.from_element]
        to_elem = elements[self.to_element]
        
        # Validate relationship type constraints
        validation_errors = self._validate_relationship_constraints(from_elem, to_elem)
        errors.extend(validation_errors)
        
        return errors
    
    def _validate_relationship_constraints(self, from_elem, to_elem) -> List[str]:
        """Validate ArchiMate relationship constraints.
        
        Args:
            from_elem: Source ArchiMateElement
            to_elem: Target ArchiMateElement
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Basic validation - more complex rules would be implemented here
        # For now, we'll do basic type checking
        
        # Access relationships typically connect active structure to passive structure
        if self.relationship_type == RelationshipType.ACCESS:
            if (from_elem.aspect.value != "Active Structure" or 
                to_elem.aspect.value != "Passive Structure"):
                errors.append(
                    f"Access relationship typically connects Active Structure to Passive Structure"
                )
        
        # Composition requires compatible layers
        if self.relationship_type == RelationshipType.COMPOSITION:
            if from_elem.layer != to_elem.layer:
                errors.append(
                    f"Composition relationship should connect elements within the same layer"
                )
        
        # Add more constraint validations as needed
        
        return errors
    
    def __str__(self) -> str:
        return f"{self.from_element} --{self.relationship_type.value}--> {self.to_element}"
    
    def __repr__(self) -> str:
        return (f"ArchiMateRelationship(id='{self.id}', "
                f"from='{self.from_element}', to='{self.to_element}', "
                f"type='{self.relationship_type.value}')")


# Registry of all ArchiMate relationships
ARCHIMATE_RELATIONSHIPS = {
    "Access": RelationshipType.ACCESS,
    "Aggregation": RelationshipType.AGGREGATION,
    "Assignment": RelationshipType.ASSIGNMENT,
    "Association": RelationshipType.ASSOCIATION,
    "Composition": RelationshipType.COMPOSITION,
    "Flow": RelationshipType.FLOW,
    "Influence": RelationshipType.INFLUENCE,
    "Realization": RelationshipType.REALIZATION,
    "Serving": RelationshipType.SERVING,
    "Specialization": RelationshipType.SPECIALIZATION,
    "Triggering": RelationshipType.TRIGGERING,
}


def create_relationship(
    relationship_id: str,
    from_element: str,
    to_element: str,
    relationship_type: str,
    direction: Optional[str] = None,
    description: Optional[str] = None,
    label: Optional[str] = None,
    **kwargs
) -> ArchiMateRelationship:
    """Create an ArchiMate relationship.
    
    Args:
        relationship_id: Unique identifier for the relationship
        from_element: Source element ID
        to_element: Target element ID
        relationship_type: Type of relationship
        direction: Optional direction (Up, Down, Left, Right)
        description: Optional description
        label: Optional label
        **kwargs: Additional properties
        
    Returns:
        ArchiMateRelationship instance
        
    Raises:
        ArchiMateRelationshipError: If relationship type is invalid
    """
    # Validate relationship type
    if relationship_type not in ARCHIMATE_RELATIONSHIPS:
        valid_types = list(ARCHIMATE_RELATIONSHIPS.keys())
        raise ArchiMateRelationshipError(
            f"Invalid relationship type '{relationship_type}'. "
            f"Valid types: {valid_types}",
            from_element=from_element,
            to_element=to_element,
            relationship_type=relationship_type
        )
    
    # Validate direction if provided
    direction_enum = None
    if direction:
        try:
            direction_enum = RelationshipDirection(direction)
        except ValueError:
            valid_directions = [d.value for d in RelationshipDirection]
            raise ArchiMateRelationshipError(
                f"Invalid direction '{direction}'. "
                f"Valid directions: {valid_directions}",
                from_element=from_element,
                to_element=to_element,
                relationship_type=relationship_type
            )
    
    return ArchiMateRelationship(
        id=relationship_id,
        from_element=from_element,
        to_element=to_element,
        relationship_type=ARCHIMATE_RELATIONSHIPS[relationship_type],
        direction=direction_enum,
        description=description,
        label=label,
        properties=kwargs
    )