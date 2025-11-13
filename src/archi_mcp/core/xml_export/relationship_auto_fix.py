"""
ArchiMate Relationship Auto-Fix System

Automatically fixes common relationship validation errors while preserving
PlantUML generation and maintaining semantic correctness.
"""

import logging
import re
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

# Auto-fix rules based on comprehensive analysis of existing exports
# Pattern: (source_type, target_type, invalid_rel) -> suggested_rel
AUTO_FIX_RULES = {
    # Cross-layer access issues - use Association instead
    ("BusinessActor", "ApplicationComponent", "AccessRelationship"): "AssociationRelationship",
    ("BusinessActor", "ApplicationFunction", "AccessRelationship"): "AssociationRelationship", 
    ("BusinessActor", "ApplicationService", "AssignmentRelationship"): "ServingRelationship",
    
    # Application to Technology layer issues
    ("ApplicationComponent", "TechnologyService", "ServingRelationship"): "AssociationRelationship",
    ("ApplicationComponent", "ApplicationService", "AccessRelationship"): "ServingRelationship",
    
    # Business process realization issues
    ("BusinessProcess", "ApplicationComponent", "RealizationRelationship"): "TriggeringRelationship",
    ("BusinessProcess", "TechnologyService", "RealizationRelationship"): "TriggeringRelationship",
    ("BusinessProcess", "BusinessObject", "RealizationRelationship"): "AccessRelationship",
    ("BusinessProcess", "Value", "RealizationRelationship"): "AssociationRelationship",
    
    # Cross-layer influence issues
    ("Assessment", "ApplicationComponent", "InfluenceRelationship"): "AssociationRelationship",
    ("Constraint", "BusinessProcess", "InfluenceRelationship"): "AssociationRelationship",
    ("Constraint", "TechnologyProcess", "InfluenceRelationship"): "AssociationRelationship",
    
    # Process triggering issues
    ("BusinessProcess", "ApplicationProcess", "TriggeringRelationship"): "ServingRelationship",
    
    # NEW RULES based on latest error analysis
    # Implementation and Migration layer issues
    ("BusinessRole", "Deliverable", "AssignmentRelationship"): "AssociationRelationship",
    ("BusinessRole", "WorkPackage", "AssignmentRelationship"): "AssociationRelationship", 
    ("BusinessActor", "WorkPackage", "AssignmentRelationship"): "AssociationRelationship",
    
    # Motivation to Implementation layer issues
    ("Principle", "Deliverable", "InfluenceRelationship"): "AssociationRelationship",
    ("Constraint", "WorkPackage", "InfluenceRelationship"): "AssociationRelationship",
    ("Requirement", "WorkPackage", "InfluenceRelationship"): "AssociationRelationship",
    
    # Motivation to Business layer issues  
    ("Goal", "BusinessRole", "InfluenceRelationship"): "AssociationRelationship",
    ("Driver", "BusinessActor", "InfluenceRelationship"): "AssociationRelationship",
    ("BusinessActor", "Requirement", "AssociationRelationship"): "AssociationRelationship",
    
    # Business layer internal issues
    ("BusinessRole", "Location", "AssignmentRelationship"): "AssociationRelationship",
    ("BusinessRole", "BusinessObject", "AccessRelationship"): "AssociationRelationship",
}

# Common relationship type mappings for readability
RELATIONSHIP_DESCRIPTIONS = {
    "AssociationRelationship": "Association (general relationship)",
    "ServingRelationship": "Serving (provides services to)",
    "TriggeringRelationship": "Triggering (initiates or starts)",
    "AccessRelationship": "Access (reads, writes, or accesses)",
    "RealizationRelationship": "Realization (implements or realizes)",
    "InfluenceRelationship": "Influence (affects positively or negatively)",
    "AssignmentRelationship": "Assignment (is allocated to)",
}

class RelationshipAutoFixer:
    """
    Automatically fixes problematic ArchiMate relationships while preserving semantics.
    """
    
    def __init__(self, enable_auto_fix: bool = True):
        """
        Initialize auto-fixer.
        
        Args:
            enable_auto_fix: Enable automatic fixing (can be controlled via env var)
        """
        self.enable_auto_fix = enable_auto_fix
        self.fixes_applied = []
        
    def fix_xml_relationships(self, xml_content: str) -> Tuple[str, List[str]]:
        """
        Fix problematic relationships in XML content.
        
        Args:
            xml_content: Original XML content
            
        Returns:
            Tuple of (fixed_xml_content, list_of_fixes_applied)
        """
        if not self.enable_auto_fix:
            return xml_content, []
            
        self.fixes_applied = []
        fixed_content = xml_content
        
        # Extract elements for type lookup
        elem_pattern = r'<element xsi:type="archimate:(\w+)" id="([^"]+)" name="([^"]*)"'
        elements = re.findall(elem_pattern, xml_content)
        element_types = {elem_id: elem_type for elem_type, elem_id, name in elements}
        
        # Find and fix relationships
        rel_pattern = r'<element xsi:type="archimate:(\w+Relationship)" id="([^"]+)" source="([^"]+)" target="([^"]+)"([^>]*)>'
        relationships = re.findall(rel_pattern, xml_content)
        
        for rel_type, rel_id, source_id, target_id, attributes in relationships:
            source_type = element_types.get(source_id, "Unknown")
            target_type = element_types.get(target_id, "Unknown")
            
            if source_type == "Unknown" or target_type == "Unknown":
                continue
                
            # Check if this relationship needs fixing
            fix_key = (source_type, target_type, rel_type)
            if fix_key in AUTO_FIX_RULES:
                new_rel_type = AUTO_FIX_RULES[fix_key]
                
                # Apply fix
                old_element = f'<element xsi:type="archimate:{rel_type}" id="{rel_id}" source="{source_id}" target="{target_id}"{attributes}>'
                new_element = f'<element xsi:type="archimate:{new_rel_type}" id="{rel_id}" source="{source_id}" target="{target_id}"{attributes}>'
                
                if old_element in fixed_content:
                    fixed_content = fixed_content.replace(old_element, new_element)
                    
                    fix_description = f"Fixed {rel_id}: {source_type} --[{rel_type}]--> {target_type} → {new_rel_type}"
                    self.fixes_applied.append(fix_description)
                    
                    logger.info(f"Auto-fix applied: {fix_description}")
                    
        return fixed_content, self.fixes_applied
        
    def get_fix_summary(self) -> str:
        """Get summary of fixes applied."""
        if not self.fixes_applied:
            return "✅ No relationship fixes needed"
            
        lines = [f"🔧 Applied {len(self.fixes_applied)} relationship fixes:"]
        for fix in self.fixes_applied:
            lines.append(f"  • {fix}")
            
        return "\n".join(lines)
        
    def get_suggested_fixes(self, xml_content: str) -> List[str]:
        """
        Get list of suggested fixes without applying them.
        
        Args:
            xml_content: XML content to analyze
            
        Returns:
            List of suggested fix descriptions
        """
        suggestions = []
        
        # Extract elements for type lookup
        elem_pattern = r'<element xsi:type="archimate:(\w+)" id="([^"]+)" name="([^"]*)"'
        elements = re.findall(elem_pattern, xml_content)
        element_types = {elem_id: elem_type for elem_type, elem_id, name in elements}
        
        # Find relationships that could be fixed
        rel_pattern = r'<element xsi:type="archimate:(\w+Relationship)" id="([^"]+)" source="([^"]+)" target="([^"]+)"'
        relationships = re.findall(rel_pattern, xml_content)
        
        for rel_type, rel_id, source_id, target_id in relationships:
            source_type = element_types.get(source_id, "Unknown")
            target_type = element_types.get(target_id, "Unknown")
            
            if source_type == "Unknown" or target_type == "Unknown":
                continue
                
            # Check if this relationship could be fixed
            fix_key = (source_type, target_type, rel_type)
            if fix_key in AUTO_FIX_RULES:
                new_rel_type = AUTO_FIX_RULES[fix_key]
                new_description = RELATIONSHIP_DESCRIPTIONS.get(new_rel_type, new_rel_type)
                
                suggestion = f"{rel_id}: {source_type} --[{rel_type}]--> {target_type} → Suggest: {new_rel_type} ({new_description})"
                suggestions.append(suggestion)
                
        return suggestions

def apply_auto_fix(xml_content: str, enable_fix: bool = True) -> Tuple[str, Dict[str, any]]:
    """
    Apply auto-fix to XML content and return results.
    
    Args:
        xml_content: Original XML content
        enable_fix: Whether to actually apply fixes
        
    Returns:
        Tuple of (fixed_content, fix_info_dict)
    """
    fixer = RelationshipAutoFixer(enable_auto_fix=enable_fix)
    
    if enable_fix:
        fixed_content, fixes_applied = fixer.fix_xml_relationships(xml_content)
        suggestions = []
    else:
        fixed_content = xml_content
        fixes_applied = []
        suggestions = fixer.get_suggested_fixes(xml_content)
    
    fix_info = {
        "fixes_applied": fixes_applied,
        "suggestions": suggestions,
        "fix_count": len(fixes_applied),
        "suggestion_count": len(suggestions),
        "summary": fixer.get_fix_summary() if fixes_applied else f"💡 Found {len(suggestions)} fixable relationships"
    }
    
    return fixed_content, fix_info