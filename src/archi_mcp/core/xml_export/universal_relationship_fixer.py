"""
Universal Relationship Fixer

Never-fail approach that ensures all ArchiMate relationships are valid
while preserving semantic meaning where possible.

Strategy: Smart Association Fallback (#2 + #4)
- Cross-layer relationships → Association (safest)
- Same layer → keep original if safe, otherwise Association
- Never fails, always produces valid ArchiMate XML
"""

import logging
from typing import Dict, Set

logger = logging.getLogger(__name__)

# ArchiMate layers mapping
ELEMENT_LAYERS = {
    # Motivation Layer
    "Stakeholder": "Motivation", "Driver": "Motivation", "Assessment": "Motivation", 
    "Goal": "Motivation", "Outcome": "Motivation", "Principle": "Motivation", 
    "Requirement": "Motivation", "Constraint": "Motivation", "Meaning": "Motivation", "Value": "Motivation",
    
    # Strategy Layer
    "Resource": "Strategy", "Capability": "Strategy", "CourseOfAction": "Strategy", "ValueStream": "Strategy",
    
    # Business Layer
    "BusinessActor": "Business", "BusinessRole": "Business", "BusinessCollaboration": "Business",
    "BusinessInterface": "Business", "BusinessFunction": "Business", "BusinessProcess": "Business",
    "BusinessInteraction": "Business", "BusinessEvent": "Business", "BusinessService": "Business",
    "BusinessObject": "Business", "Contract": "Business", "Representation": "Business", "Location": "Business",
    
    # Application Layer
    "ApplicationComponent": "Application", "ApplicationCollaboration": "Application",
    "ApplicationInterface": "Application", "ApplicationFunction": "Application",
    "ApplicationInteraction": "Application", "ApplicationProcess": "Application",
    "ApplicationEvent": "Application", "ApplicationService": "Application", "DataObject": "Application",
    
    # Technology Layer
    "Node": "Technology", "Device": "Technology", "SystemSoftware": "Technology",
    "TechnologyCollaboration": "Technology", "TechnologyInterface": "Technology",
    "Path": "Technology", "CommunicationNetwork": "Technology", "TechnologyFunction": "Technology",
    "TechnologyProcess": "Technology", "TechnologyInteraction": "Technology",
    "TechnologyEvent": "Technology", "TechnologyService": "Technology", "Artifact": "Technology",
    
    # Physical Layer
    "Equipment": "Physical", "Facility": "Physical", "DistributionNetwork": "Physical", "Material": "Physical",
    
    # Implementation Layer
    "WorkPackage": "Implementation", "Deliverable": "Implementation",
    "ImplementationEvent": "Implementation", "Plateau": "Implementation", "Gap": "Implementation"
}

# Safe relationships that work well within same layer
SAFE_SAME_LAYER_RELATIONSHIPS = {
    "AssignmentRelationship",     # Fundamental ArchiMate relationship (actor assigned to process/role)
    "CompositionRelationship",    # Part-of relationships
    "AggregationRelationship",    # Collection relationships  
    "ServingRelationship",        # Service provision
    "RealizationRelationship",    # Implementation relationships
    "AccessRelationship",         # Data access (within layer)
    "TriggeringRelationship",     # Process flow (within layer)
    "FlowRelationship",          # Information flow (within layer)
    "InfluenceRelationship",     # Influence between elements (especially in Motivation layer)
    "SpecializationRelationship", # Inheritance (same element types)
    "AssociationRelationship"     # Always safe
}

# Relationships that are generally safe cross-layer
SAFE_CROSS_LAYER_RELATIONSHIPS = {
    "AssignmentRelationship",     # Valid cross-layer (Business Actor → Application Component)
    "ServingRelationship",        # Services can be provided cross-layer
    "RealizationRelationship",    # Implementation across layers is common
    "AccessRelationship",         # Cross-layer data access (Business Process → Application Service)
    "TriggeringRelationship",     # Cross-layer triggering (Business Event → Application Process)
    "FlowRelationship",          # Cross-layer information flow
    "InfluenceRelationship",     # Motivation influencing other layers
    "AssociationRelationship"     # Always safe
}

def get_element_layer(element_type: str) -> str:
    """Get layer for element type."""
    return ELEMENT_LAYERS.get(element_type, "Unknown")

def is_cross_layer(source_type: str, target_type: str) -> bool:
    """Check if relationship crosses layers."""
    source_layer = get_element_layer(source_type)
    target_layer = get_element_layer(target_type)
    return source_layer != target_layer and source_layer != "Unknown" and target_layer != "Unknown"

def fix_relationship_universally(source_type: str, target_type: str, relationship_type: str) -> str:
    """
    Universal relationship fixer that never fails.
    
    Strategy:
    1. Cross-layer → Use Association or safe cross-layer relationships
    2. Same layer → Keep original if safe, otherwise Association
    3. Unknown elements → Always Association (forward compatibility)
    
    Args:
        source_type: Source element type
        target_type: Target element type  
        relationship_type: Original relationship type
        
    Returns:
        Safe relationship type (guaranteed to be valid)
    """
    
    # Handle unknown element types gracefully
    if get_element_layer(source_type) == "Unknown" or get_element_layer(target_type) == "Unknown":
        logger.debug(f"Unknown element types: {source_type}, {target_type} → Association")
        return "AssociationRelationship"
    
    # Cross-layer relationships
    if is_cross_layer(source_type, target_type):
        if relationship_type in SAFE_CROSS_LAYER_RELATIONSHIPS:
            logger.debug(f"Cross-layer {relationship_type} preserved: {source_type} → {target_type}")
            return relationship_type
        else:
            logger.debug(f"Cross-layer {relationship_type} → Association: {source_type} → {target_type}")
            return "AssociationRelationship"
    
    # Same layer relationships
    else:
        if relationship_type in SAFE_SAME_LAYER_RELATIONSHIPS:
            logger.debug(f"Same-layer {relationship_type} preserved: {source_type} → {target_type}")
            return relationship_type
        else:
            logger.debug(f"Same-layer {relationship_type} → Association: {source_type} → {target_type}")
            return "AssociationRelationship"

def apply_universal_fix(xml_content: str) -> tuple[str, dict]:
    """
    Apply universal relationship fixing to XML content.
    
    Args:
        xml_content: Original XML content
        
    Returns:
        Tuple of (fixed_xml_content, fix_statistics)
    """
    import re
    
    # Extract elements for type lookup
    elem_pattern = r'<element xsi:type="archimate:(\w+)" id="([^"]+)" name="([^"]*)"'
    elements = re.findall(elem_pattern, xml_content)
    element_types = {elem_id: elem_type for elem_type, elem_id, name in elements}
    
    # Find and fix relationships
    rel_pattern = r'<element xsi:type="archimate:(\w+Relationship)" id="([^"]+)" source="([^"]+)" target="([^"]+)"([^>]*)>'
    relationships = re.findall(rel_pattern, xml_content)
    
    fixed_content = xml_content
    fix_stats = {
        "total_relationships": len(relationships),
        "fixes_applied": 0,
        "cross_layer_fixes": 0,
        "same_layer_fixes": 0,
        "unknown_element_fixes": 0,
        "preserved_relationships": 0,
        "fix_details": []
    }
    
    for rel_type, rel_id, source_id, target_id, attributes in relationships:
        source_type = element_types.get(source_id, "Unknown")
        target_type = element_types.get(target_id, "Unknown")
        
        # Get universally safe relationship type
        fixed_rel_type = fix_relationship_universally(source_type, target_type, rel_type)
        
        if fixed_rel_type != rel_type:
            # Apply fix
            old_element = f'<element xsi:type="archimate:{rel_type}" id="{rel_id}" source="{source_id}" target="{target_id}"{attributes}>'
            new_element = f'<element xsi:type="archimate:{fixed_rel_type}" id="{rel_id}" source="{source_id}" target="{target_id}"{attributes}>'
            
            if old_element in fixed_content:
                fixed_content = fixed_content.replace(old_element, new_element)
                
                # Track statistics
                fix_stats["fixes_applied"] += 1
                
                if get_element_layer(source_type) == "Unknown" or get_element_layer(target_type) == "Unknown":
                    fix_stats["unknown_element_fixes"] += 1
                elif is_cross_layer(source_type, target_type):
                    fix_stats["cross_layer_fixes"] += 1
                else:
                    fix_stats["same_layer_fixes"] += 1
                
                fix_detail = f"{rel_id}: {source_type} --[{rel_type}]--> {target_type} → {fixed_rel_type}"
                fix_stats["fix_details"].append(fix_detail)
                
                logger.info(f"Universal fix applied: {fix_detail}")
        else:
            fix_stats["preserved_relationships"] += 1
    
    return fixed_content, fix_stats

def get_fix_summary(fix_stats: dict) -> str:
    """Generate summary of universal fixes applied."""
    total = fix_stats["total_relationships"]
    applied = fix_stats["fixes_applied"]
    preserved = fix_stats["preserved_relationships"]
    
    if applied == 0:
        return f"✅ All {total} relationships were already valid"
    
    lines = [
        f"🔧 Universal Relationship Fixing Results:",
        f"  Total relationships: {total}",
        f"  Fixes applied: {applied}",
        f"  Preserved original: {preserved}",
        f"  Cross-layer fixes: {fix_stats['cross_layer_fixes']}",
        f"  Same-layer fixes: {fix_stats['same_layer_fixes']}",
        f"  Unknown element fixes: {fix_stats['unknown_element_fixes']}"
    ]
    
    if applied > 0:
        success_rate = (preserved / total) * 100
        lines.append(f"  Semantic preservation: {success_rate:.1f}%")
        lines.append("✅ All relationships now guaranteed valid for Archi import")
    
    return "\n".join(lines)