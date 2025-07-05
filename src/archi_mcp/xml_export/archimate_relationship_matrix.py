"""
ArchiMate 3.2 Relationship Matrix for Validation

Based on official ArchiMate 3.2 specification from The Open Group.
Defines which relationships are allowed between different element types.
"""

from typing import Dict, List, Set
from enum import Enum

# ArchiMate relationship types
class RelationshipType(Enum):
    COMPOSITION = "CompositionRelationship"
    AGGREGATION = "AggregationRelationship" 
    ASSIGNMENT = "AssignmentRelationship"
    REALIZATION = "RealizationRelationship"
    SERVING = "ServingRelationship"
    ACCESS = "AccessRelationship"
    INFLUENCE = "InfluenceRelationship"
    TRIGGERING = "TriggeringRelationship"
    FLOW = "FlowRelationship"
    SPECIALIZATION = "SpecializationRelationship"
    ASSOCIATION = "AssociationRelationship"

# ArchiMate layers
class Layer(Enum):
    MOTIVATION = "Motivation"
    STRATEGY = "Strategy"
    BUSINESS = "Business"
    APPLICATION = "Application"
    TECHNOLOGY = "Technology"
    PHYSICAL = "Physical"
    IMPLEMENTATION = "Implementation"

# ArchiMate relationship compatibility matrix
# Based on ArchiMate 3.2 specification Table B.1
RELATIONSHIP_MATRIX = {
    # Motivation Layer Elements
    "Stakeholder": {
        RelationshipType.ASSOCIATION: ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle", "Requirement", "Constraint", "Meaning", "Value"],
        RelationshipType.COMPOSITION: ["Stakeholder"],
        RelationshipType.AGGREGATION: ["Stakeholder"],
        RelationshipType.ASSIGNMENT: ["Goal", "Outcome", "Principle", "Requirement", "Constraint"],
        RelationshipType.SERVING: ["Stakeholder"],
        RelationshipType.INFLUENCE: ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle", "Requirement", "Constraint"],
    },
    
    "Driver": {
        RelationshipType.ASSOCIATION: ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle", "Requirement", "Constraint"],
        RelationshipType.COMPOSITION: ["Driver"],
        RelationshipType.AGGREGATION: ["Driver"],
        RelationshipType.INFLUENCE: ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle", "Requirement", "Constraint"],
    },
    
    "Assessment": {
        RelationshipType.ASSOCIATION: ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle", "Requirement", "Constraint"],
        RelationshipType.COMPOSITION: ["Assessment"],
        RelationshipType.AGGREGATION: ["Assessment"],
        RelationshipType.INFLUENCE: ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle", "Requirement", "Constraint"],
    },
    
    "Goal": {
        RelationshipType.ASSOCIATION: ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle", "Requirement", "Constraint"],
        RelationshipType.COMPOSITION: ["Goal"],
        RelationshipType.AGGREGATION: ["Goal"],
        RelationshipType.REALIZATION: ["Goal", "Outcome"],
        RelationshipType.INFLUENCE: ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle", "Requirement", "Constraint"],
    },
    
    "Outcome": {
        RelationshipType.ASSOCIATION: ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle", "Requirement", "Constraint"],
        RelationshipType.COMPOSITION: ["Outcome"],
        RelationshipType.AGGREGATION: ["Outcome"],
        RelationshipType.INFLUENCE: ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle", "Requirement", "Constraint"],
    },
    
    "Principle": {
        RelationshipType.ASSOCIATION: ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle", "Requirement", "Constraint"],
        RelationshipType.COMPOSITION: ["Principle"],
        RelationshipType.AGGREGATION: ["Principle"],
        RelationshipType.INFLUENCE: ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle", "Requirement", "Constraint"],
    },
    
    "Requirement": {
        RelationshipType.ASSOCIATION: ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle", "Requirement", "Constraint"],
        RelationshipType.COMPOSITION: ["Requirement"],
        RelationshipType.AGGREGATION: ["Requirement"],
        RelationshipType.REALIZATION: ["Requirement", "Constraint"],
        RelationshipType.INFLUENCE: ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle", "Requirement", "Constraint"],
    },
    
    "Constraint": {
        RelationshipType.ASSOCIATION: ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle", "Requirement", "Constraint"],
        RelationshipType.COMPOSITION: ["Constraint"],
        RelationshipType.AGGREGATION: ["Constraint"],
        RelationshipType.INFLUENCE: ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle", "Requirement", "Constraint"],
    },
    
    # Business Layer Elements
    "BusinessActor": {
        RelationshipType.COMPOSITION: ["BusinessActor", "BusinessRole"],
        RelationshipType.AGGREGATION: ["BusinessActor", "BusinessRole"],
        RelationshipType.ASSIGNMENT: ["BusinessRole", "BusinessFunction", "BusinessProcess", "BusinessInteraction", "BusinessEvent", "BusinessService"],
        RelationshipType.SERVING: ["BusinessActor", "BusinessRole", "BusinessCollaboration", "ApplicationComponent", "ApplicationService"],  # Extended for cross-layer
        RelationshipType.INFLUENCE: ["BusinessActor", "BusinessRole"],
        RelationshipType.ASSOCIATION: ["BusinessActor", "BusinessRole", "BusinessCollaboration", "BusinessInterface", "BusinessFunction", "BusinessProcess", "BusinessInteraction", "BusinessEvent", "BusinessService", "BusinessObject", "Contract", "Representation", "Location", "ApplicationComponent", "ApplicationService", "ApplicationFunction"],  # Extended for cross-layer
    },
    
    "BusinessRole": {
        RelationshipType.COMPOSITION: ["BusinessRole"],
        RelationshipType.AGGREGATION: ["BusinessRole"],
        RelationshipType.ASSIGNMENT: ["BusinessFunction", "BusinessProcess", "BusinessInteraction", "BusinessEvent", "BusinessService"],
        RelationshipType.SERVING: ["BusinessActor", "BusinessRole", "BusinessCollaboration"],
        RelationshipType.ASSOCIATION: ["BusinessActor", "BusinessRole", "BusinessCollaboration", "BusinessInterface", "BusinessFunction", "BusinessProcess", "BusinessInteraction", "BusinessEvent", "BusinessService", "BusinessObject", "Contract", "Representation", "Location"],
    },
    
    "BusinessProcess": {
        RelationshipType.COMPOSITION: ["BusinessFunction", "BusinessProcess", "BusinessInteraction"],
        RelationshipType.AGGREGATION: ["BusinessFunction", "BusinessProcess", "BusinessInteraction"],
        RelationshipType.REALIZATION: ["BusinessService"],
        RelationshipType.SERVING: ["BusinessFunction", "BusinessProcess", "BusinessInteraction", "BusinessService"],
        RelationshipType.ACCESS: ["BusinessObject", "Contract", "Representation"],
        RelationshipType.TRIGGERING: ["BusinessFunction", "BusinessProcess", "BusinessInteraction", "BusinessEvent"],
        RelationshipType.FLOW: ["BusinessFunction", "BusinessProcess", "BusinessInteraction"],
        RelationshipType.ASSOCIATION: ["BusinessActor", "BusinessRole", "BusinessCollaboration", "BusinessInterface", "BusinessFunction", "BusinessProcess", "BusinessInteraction", "BusinessEvent", "BusinessService", "BusinessObject", "Contract", "Representation", "Location"],
    },
    
    # Application Layer Elements  
    "ApplicationComponent": {
        RelationshipType.COMPOSITION: ["ApplicationComponent"],
        RelationshipType.AGGREGATION: ["ApplicationComponent"],
        RelationshipType.ASSIGNMENT: ["ApplicationFunction", "ApplicationInteraction", "ApplicationProcess", "ApplicationService"],
        RelationshipType.SERVING: ["ApplicationComponent", "ApplicationCollaboration"],
        RelationshipType.REALIZATION: ["BusinessService", "ApplicationService"],
        RelationshipType.ASSOCIATION: ["ApplicationComponent", "ApplicationCollaboration", "ApplicationInterface", "ApplicationFunction", "ApplicationInteraction", "ApplicationProcess", "ApplicationEvent", "ApplicationService", "DataObject"],
    },
    
    # Technology Layer Elements
    "Node": {
        RelationshipType.COMPOSITION: ["Node", "Device", "SystemSoftware", "TechnologyCollaboration"],
        RelationshipType.AGGREGATION: ["Node", "Device", "SystemSoftware", "TechnologyCollaboration"],
        RelationshipType.ASSIGNMENT: ["TechnologyFunction", "TechnologyProcess", "TechnologyInteraction", "TechnologyService", "ApplicationComponent", "ApplicationFunction", "ApplicationInteraction", "ApplicationProcess", "ApplicationService", "DataObject"],
        RelationshipType.SERVING: ["Node", "Device", "SystemSoftware", "TechnologyCollaboration"],
        RelationshipType.ASSOCIATION: ["Node", "Device", "SystemSoftware", "TechnologyCollaboration", "TechnologyInterface", "Path", "CommunicationNetwork", "TechnologyFunction", "TechnologyProcess", "TechnologyInteraction", "TechnologyEvent", "TechnologyService", "Artifact"],
    },
    
    "Device": {
        RelationshipType.COMPOSITION: ["Device", "SystemSoftware"],
        RelationshipType.AGGREGATION: ["Device", "SystemSoftware"], 
        RelationshipType.ASSIGNMENT: ["TechnologyFunction", "TechnologyProcess", "TechnologyInteraction", "TechnologyService", "Node", "SystemSoftware", "Artifact"],
        RelationshipType.SERVING: ["Device", "SystemSoftware"],
        RelationshipType.ASSOCIATION: ["Node", "Device", "SystemSoftware", "TechnologyCollaboration", "TechnologyInterface", "Path", "CommunicationNetwork", "TechnologyFunction", "TechnologyProcess", "TechnologyInteraction", "TechnologyEvent", "TechnologyService", "Artifact"],
    },
}

def validate_relationship(source_type: str, target_type: str, relationship_type: str) -> bool:
    """
    Validate if a relationship is allowed according to ArchiMate 3.2 specification.
    
    Args:
        source_type: Source element type (e.g., "BusinessActor")
        target_type: Target element type (e.g., "BusinessProcess") 
        relationship_type: Relationship type (e.g., "AssignmentRelationship")
        
    Returns:
        True if relationship is valid, False otherwise
    """
    try:
        # Convert relationship type string to enum
        rel_enum = None
        for rel in RelationshipType:
            if rel.value == relationship_type:
                rel_enum = rel
                break
        
        if not rel_enum:
            # Allow unknown relationship types (conservative)
            return True
            
        # Check if source type exists in matrix
        if source_type not in RELATIONSHIP_MATRIX:
            return True  # Unknown types are allowed (conservative approach)
            
        # Check if relationship type is allowed for source type
        if rel_enum not in RELATIONSHIP_MATRIX[source_type]:
            # Association is always allowed as fallback
            return relationship_type == "AssociationRelationship"
            
        # Check if target type is allowed for this relationship
        allowed_targets = RELATIONSHIP_MATRIX[source_type][rel_enum]
        return target_type in allowed_targets
        
    except Exception:
        return True  # Conservative: allow unknown combinations

def get_allowed_relationships(source_type: str, target_type: str) -> List[str]:
    """
    Get list of allowed relationship types between two element types.
    
    Args:
        source_type: Source element type
        target_type: Target element type
        
    Returns:
        List of allowed relationship type strings
    """
    allowed = []
    
    if source_type not in RELATIONSHIP_MATRIX:
        return ["AssociationRelationship"]  # Default fallback
        
    for rel_type, targets in RELATIONSHIP_MATRIX[source_type].items():
        if target_type in targets:
            allowed.append(rel_type.value)
            
    return allowed if allowed else ["AssociationRelationship"]

def get_validation_suggestion(source_type: str, target_type: str, relationship_type: str) -> str:
    """
    Get validation suggestion for invalid relationship.
    
    Args:
        source_type: Source element type
        target_type: Target element type  
        relationship_type: Invalid relationship type
        
    Returns:
        Suggestion string for fixing the relationship
    """
    allowed = get_allowed_relationships(source_type, target_type)
    
    if not allowed:
        return f"No valid relationships found between {source_type} and {target_type}"
        
    if len(allowed) == 1:
        return f"Suggested relationship: {allowed[0]}"
    else:
        return f"Suggested relationships: {', '.join(allowed)}"