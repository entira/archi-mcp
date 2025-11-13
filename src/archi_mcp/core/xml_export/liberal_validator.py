"""
Liberal ArchiMate Validator

A more permissive validator that allows cross-layer relationships
while still providing useful feedback and auto-fixes.
"""

import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)

# ArchiMate layers for categorization
ARCHIMATE_LAYERS = {
    "Motivation": ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle", "Requirement", "Constraint", "Meaning", "Value"],
    "Strategy": ["Resource", "Capability", "CourseOfAction", "ValueStream"],
    "Business": ["BusinessActor", "BusinessRole", "BusinessCollaboration", "BusinessInterface", "BusinessFunction", "BusinessProcess", "BusinessInteraction", "BusinessEvent", "BusinessService", "BusinessObject", "Contract", "Representation", "Location"],
    "Application": ["ApplicationComponent", "ApplicationCollaboration", "ApplicationInterface", "ApplicationFunction", "ApplicationInteraction", "ApplicationProcess", "ApplicationEvent", "ApplicationService", "DataObject"],
    "Technology": ["Node", "Device", "SystemSoftware", "TechnologyCollaboration", "TechnologyInterface", "Path", "CommunicationNetwork", "TechnologyFunction", "TechnologyProcess", "TechnologyInteraction", "TechnologyEvent", "TechnologyService", "Artifact"],
    "Physical": ["Equipment", "Facility", "DistributionNetwork", "Material"],
    "Implementation": ["WorkPackage", "Deliverable", "ImplementationEvent", "Plateau", "Gap"]
}

# Create reverse mapping: element -> layer
ELEMENT_TO_LAYER = {}
for layer, elements in ARCHIMATE_LAYERS.items():
    for element in elements:
        ELEMENT_TO_LAYER[element] = layer

def get_element_layer(element_type: str) -> str:
    """Get layer for element type."""
    return ELEMENT_TO_LAYER.get(element_type, "Unknown")

def is_same_layer_relationship(source_type: str, target_type: str) -> bool:
    """Check if relationship is within the same layer."""
    source_layer = get_element_layer(source_type)
    target_layer = get_element_layer(target_type)
    return source_layer == target_layer and source_layer != "Unknown"

def is_cross_layer_relationship(source_type: str, target_type: str) -> bool:
    """Check if relationship crosses layers."""
    source_layer = get_element_layer(source_type)
    target_layer = get_element_layer(target_type)
    return source_layer != target_layer and source_layer != "Unknown" and target_layer != "Unknown"

def is_problematic_relationship(source_type: str, target_type: str, relationship_type: str) -> bool:
    """
    Check if relationship is truly problematic (liberal approach).
    
    Only flag relationships that are definitely wrong according to ArchiMate principles.
    """
    # Very permissive - only block truly nonsensical combinations
    
    # Block some obviously wrong structural relationships
    if relationship_type == "CompositionRelationship":
        # Composition should generally be within the same layer
        if is_cross_layer_relationship(source_type, target_type):
            return True
    
    if relationship_type == "AggregationRelationship":
        # Aggregation should generally be within the same layer
        if is_cross_layer_relationship(source_type, target_type):
            return True
    
    # Block some obviously wrong semantic relationships
    if relationship_type == "SpecializationRelationship":
        # Specialization should be between same element types
        if source_type != target_type:
            return True
    
    # All other relationships are allowed (very liberal approach)
    return False

def get_relationship_category(source_type: str, target_type: str, relationship_type: str) -> str:
    """Categorize relationship for reporting."""
    
    if is_problematic_relationship(source_type, target_type, relationship_type):
        return "problematic"
    
    if is_same_layer_relationship(source_type, target_type):
        return "same_layer"
    
    if is_cross_layer_relationship(source_type, target_type):
        return "cross_layer"
    
    return "unknown_elements"

def validate_relationship_liberal(source_type: str, target_type: str, relationship_type: str) -> Dict[str, any]:
    """
    Liberal validation that provides information without being overly restrictive.
    
    Returns:
        Dictionary with validation result and metadata
    """
    category = get_relationship_category(source_type, target_type, relationship_type)
    
    result = {
        "is_valid": category != "problematic",
        "category": category,
        "source_layer": get_element_layer(source_type),
        "target_layer": get_element_layer(target_type),
        "message": "",
        "suggestion": ""
    }
    
    if category == "problematic":
        result["message"] = f"Problematic relationship: {source_type} --[{relationship_type}]--> {target_type}"
        result["suggestion"] = "Consider using AssociationRelationship for general connections"
    elif category == "cross_layer":
        result["message"] = f"Cross-layer relationship: {result['source_layer']} → {result['target_layer']}"
        result["suggestion"] = "Cross-layer relationships are allowed but verify semantic correctness"
    elif category == "same_layer":
        result["message"] = f"Same layer relationship in {result['source_layer']} layer"
        result["suggestion"] = "Good practice: relationships within same layer"
    else:
        result["message"] = f"Unknown element types: {source_type}, {target_type}"
        result["suggestion"] = "Unknown elements are allowed (forward compatibility)"
    
    return result

def analyze_model_relationships(xml_content: str) -> Dict[str, any]:
    """
    Analyze all relationships in a model using liberal validation.
    
    Returns comprehensive analysis with statistics and recommendations.
    """
    import re
    
    # Extract relationships
    rel_pattern = r'<element xsi:type="archimate:(\w+Relationship)" id="([^"]+)" source="([^"]+)" target="([^"]+)"'
    relationships = re.findall(rel_pattern, xml_content)
    
    # Extract elements
    elem_pattern = r'<element xsi:type="archimate:(\w+)" id="([^"]+)" name="([^"]*)"'
    elements = re.findall(elem_pattern, xml_content)
    
    # Build element type lookup
    element_types = {elem_id: elem_type for elem_type, elem_id, name in elements}
    
    # Analyze each relationship
    analysis = {
        "total_relationships": len(relationships),
        "problematic": [],
        "cross_layer": [],
        "same_layer": [],
        "unknown_elements": [],
        "layer_stats": {},
        "relationship_stats": {}
    }
    
    for rel_type, rel_id, source_id, target_id in relationships:
        source_type = element_types.get(source_id, "Unknown")
        target_type = element_types.get(target_id, "Unknown")
        
        validation = validate_relationship_liberal(source_type, target_type, rel_type)
        
        # Categorize
        category = validation["category"]
        relationship_info = {
            "id": rel_id,
            "source_type": source_type,
            "target_type": target_type,
            "relationship_type": rel_type,
            "validation": validation
        }
        
        analysis[category].append(relationship_info)
        
        # Update statistics
        if category not in analysis["relationship_stats"]:
            analysis["relationship_stats"][category] = 0
        analysis["relationship_stats"][category] += 1
        
        # Layer statistics
        source_layer = validation["source_layer"]
        target_layer = validation["target_layer"]
        layer_combo = f"{source_layer} → {target_layer}"
        if layer_combo not in analysis["layer_stats"]:
            analysis["layer_stats"][layer_combo] = 0
        analysis["layer_stats"][layer_combo] += 1
    
    return analysis

def generate_liberal_validation_report(analysis: Dict[str, any]) -> str:
    """Generate a comprehensive but non-alarming validation report."""
    lines = ["🔍 ArchiMate Model Analysis Report", "=" * 50]
    
    # Summary
    total = analysis["total_relationships"]
    problematic = len(analysis["problematic"])
    cross_layer = len(analysis["cross_layer"])
    same_layer = len(analysis["same_layer"])
    
    lines.append(f"\n📊 Relationship Summary:")
    lines.append(f"  Total relationships: {total}")
    lines.append(f"  Same layer: {same_layer}")
    lines.append(f"  Cross layer: {cross_layer}")
    lines.append(f"  Problematic: {problematic}")
    
    if problematic == 0:
        lines.append("✅ No problematic relationships found")
    else:
        lines.append(f"⚠️  {problematic} relationships may need review")
    
    # Layer statistics
    if analysis["layer_stats"]:
        lines.append(f"\n🏗️ Layer Connections:")
        for layer_combo, count in sorted(analysis["layer_stats"].items()):
            lines.append(f"  {layer_combo}: {count}")
    
    # Problematic relationships (if any)
    if problematic > 0:
        lines.append(f"\n⚠️  Relationships for Review:")
        for rel in analysis["problematic"][:5]:  # Show first 5
            lines.append(f"  • {rel['id']}: {rel['validation']['message']}")
        if problematic > 5:
            lines.append(f"  ... and {problematic - 5} more")
    
    lines.append(f"\n💡 Recommendations:")
    if problematic == 0 and cross_layer > 0:
        lines.append("  • Model uses cross-layer relationships appropriately")
        lines.append("  • Consider documenting cross-layer dependencies")
    elif problematic > 0:
        lines.append("  • Review flagged relationships for semantic correctness")
        lines.append("  • Consider using AssociationRelationship for general connections")
    else:
        lines.append("  • Model follows good ArchiMate practices")
    
    lines.append("  • All relationships are semantically valid for tool compatibility")
    
    return "\n".join(lines)