"""ArchiMate model validation."""

from typing import Dict, List, Optional, Set, Tuple
from .elements.base import ArchiMateElement, ArchiMateLayer
from .relationships import ArchiMateRelationship, RelationshipType
from ..utils.exceptions import ArchiMateValidationError


class ArchiMateValidator:
    """Validator for ArchiMate models according to ArchiMate 3.2 specification."""
    
    def __init__(self, strict: bool = False):
        """Initialize validator.
        
        Args:
            strict: Whether to apply strict validation rules
        """
        self.strict = strict
        self._relationship_matrix = self._build_relationship_matrix()
    
    def validate_model(
        self,
        elements: Dict[str, ArchiMateElement],
        relationships: List[ArchiMateRelationship]
    ) -> List[str]:
        """Validate complete ArchiMate model.
        
        Args:
            elements: Dictionary of elements by ID
            relationships: List of relationships
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate individual elements
        element_errors = self._validate_elements(elements)
        errors.extend(element_errors)
        
        # Validate individual relationships
        relationship_errors = self._validate_relationships(relationships, elements)
        errors.extend(relationship_errors)
        
        # Validate model consistency
        consistency_errors = self._validate_model_consistency(elements, relationships)
        errors.extend(consistency_errors)
        
        # Validate ArchiMate rules if strict mode
        if self.strict:
            rule_errors = self._validate_archimate_rules(elements, relationships)
            errors.extend(rule_errors)
        
        return errors
    
    def _validate_elements(self, elements: Dict[str, ArchiMateElement]) -> List[str]:
        """Validate individual elements."""
        errors = []
        
        for element_id, element in elements.items():
            # Validate element itself
            element_errors = element.validate_element()
            errors.extend([f"Element {element_id}: {error}" for error in element_errors])
            
            # Check ID consistency
            if element.id != element_id:
                errors.append(
                    f"Element ID mismatch: key='{element_id}', element.id='{element.id}'"
                )
        
        return errors
    
    def _validate_relationships(
        self,
        relationships: List[ArchiMateRelationship],
        elements: Dict[str, ArchiMateElement]
    ) -> List[str]:
        """Validate individual relationships."""
        errors = []
        
        for relationship in relationships:
            rel_errors = relationship.validate_relationship(elements)
            errors.extend([f"Relationship {relationship.id}: {error}" for error in rel_errors])
        
        return errors
    
    def _validate_model_consistency(
        self,
        elements: Dict[str, ArchiMateElement],
        relationships: List[ArchiMateRelationship]
    ) -> List[str]:
        """Validate model consistency."""
        errors = []
        
        # Check for duplicate relationship IDs
        relationship_ids = [rel.id for rel in relationships]
        duplicate_rel_ids = set([x for x in relationship_ids if relationship_ids.count(x) > 1])
        for dup_id in duplicate_rel_ids:
            errors.append(f"Duplicate relationship ID: '{dup_id}'")
        
        # Check for orphaned relationships
        element_ids = set(elements.keys())
        for relationship in relationships:
            if relationship.from_element not in element_ids:
                errors.append(
                    f"Relationship {relationship.id}: "
                    f"source element '{relationship.from_element}' not found"
                )
            if relationship.to_element not in element_ids:
                errors.append(
                    f"Relationship {relationship.id}: "
                    f"target element '{relationship.to_element}' not found"
                )
        
        return errors
    
    def _validate_archimate_rules(
        self,
        elements: Dict[str, ArchiMateElement],
        relationships: List[ArchiMateRelationship]
    ) -> List[str]:
        """Validate ArchiMate-specific rules."""
        errors = []
        
        # Validate relationship compatibility matrix
        for relationship in relationships:
            if (relationship.from_element in elements and 
                relationship.to_element in elements):
                
                from_elem = elements[relationship.from_element]
                to_elem = elements[relationship.to_element]
                
                compatibility_errors = self._check_relationship_compatibility(
                    from_elem, to_elem, relationship
                )
                errors.extend(compatibility_errors)
        
        return errors
    
    def _check_relationship_compatibility(
        self,
        from_elem: ArchiMateElement,
        to_elem: ArchiMateElement,
        relationship: ArchiMateRelationship
    ) -> List[str]:
        """Check if relationship is compatible with element types."""
        errors = []
        
        # Get compatibility from matrix
        from_key = f"{from_elem.layer.value}_{from_elem.element_type}"
        to_key = f"{to_elem.layer.value}_{to_elem.element_type}"
        rel_type = relationship.relationship_type
        
        # For now, we'll implement basic rules
        # A full implementation would check the complete ArchiMate relationship matrix
        
        if rel_type == RelationshipType.ACCESS:
            # Access typically from active structure to passive structure
            if (from_elem.aspect.value != "Active Structure" or 
                to_elem.aspect.value != "Passive Structure"):
                errors.append(
                    f"Access relationship should connect Active Structure to Passive Structure"
                )
        
        elif rel_type == RelationshipType.ASSIGNMENT:
            # Assignment typically from active structure to behavior
            if (from_elem.aspect.value != "Active Structure" or 
                to_elem.aspect.value != "Behavior"):
                errors.append(
                    f"Assignment relationship should connect Active Structure to Behavior"
                )
        
        elif rel_type == RelationshipType.SERVING:
            # Serving can cross layers but has specific patterns
            if from_elem.layer == to_elem.layer:
                # Same layer - check aspects
                if (from_elem.aspect.value == "Passive Structure" and 
                    to_elem.aspect.value == "Active Structure"):
                    errors.append(
                        f"Serving relationship cannot go from Passive to Active Structure"
                    )
        
        return errors
    
    def _build_relationship_matrix(self) -> Dict[Tuple[str, str, str], bool]:
        """Build ArchiMate relationship compatibility matrix.
        
        Returns:
            Dictionary mapping (from_type, to_type, relationship_type) to validity
        """
        # This would be a complete implementation of the ArchiMate relationship matrix
        # For now, we return an empty matrix and rely on basic validation
        return {}
    
    def validate_element_type(self, element_type: str, layer: ArchiMateLayer) -> bool:
        """Validate if element type is valid for the specified layer.
        
        Args:
            element_type: Element type to validate
            layer: ArchiMate layer
            
        Returns:
            True if valid, False otherwise
        """
        # Valid element types by layer
        valid_types = {
            ArchiMateLayer.BUSINESS: [
                "Business_Actor", "Business_Role", "Business_Collaboration",
                "Business_Interface", "Business_Function", "Business_Process",
                "Business_Event", "Business_Service", "Business_Object",
                "Business_Contract", "Business_Representation", "Location"
            ],
            ArchiMateLayer.APPLICATION: [
                "Application_Component", "Application_Collaboration",
                "Application_Interface", "Application_Function",
                "Application_Interaction", "Application_Process",
                "Application_Event", "Application_Service", "Data_Object"
            ],
            ArchiMateLayer.TECHNOLOGY: [
                "Node", "Device", "System_Software", "Technology_Collaboration",
                "Technology_Interface", "Path", "Communication_Network",
                "Technology_Function", "Technology_Process",
                "Technology_Interaction", "Technology_Event",
                "Technology_Service", "Artifact"
            ],
            ArchiMateLayer.PHYSICAL: [
                "Equipment", "Facility", "Distribution_Network", "Material"
            ],
            ArchiMateLayer.MOTIVATION: [
                "Stakeholder", "Driver", "Assessment", "Goal", "Outcome",
                "Principle", "Requirement", "Constraint", "Meaning", "Value"
            ],
            ArchiMateLayer.STRATEGY: [
                "Resource", "Capability", "Course_of_Action", "Value_Stream"
            ],
            ArchiMateLayer.IMPLEMENTATION: [
                "Work_Package", "Deliverable", "Implementation_Event",
                "Plateau", "Gap"
            ]
        }
        
        return element_type in valid_types.get(layer, [])
    
    def get_valid_relationships(
        self,
        from_element: ArchiMateElement,
        to_element: ArchiMateElement
    ) -> List[RelationshipType]:
        """Get list of valid relationship types between two elements.
        
        Args:
            from_element: Source element
            to_element: Target element
            
        Returns:
            List of valid relationship types
        """
        # This would implement the full ArchiMate relationship matrix
        # For now, return common relationships
        valid_relationships = []
        
        # Association is generally valid between most elements
        valid_relationships.append(RelationshipType.ASSOCIATION)
        
        # Serving is common for services
        if "Service" in from_element.element_type:
            valid_relationships.append(RelationshipType.SERVING)
        
        # Realization for implementation relationships
        if (from_element.layer.value in ["Application", "Technology"] and
            to_element.layer.value == "Business"):
            valid_relationships.append(RelationshipType.REALIZATION)
        
        # Access for data/object access
        if (from_element.aspect.value == "Active Structure" and
            to_element.aspect.value == "Passive Structure"):
            valid_relationships.append(RelationshipType.ACCESS)
        
        return valid_relationships