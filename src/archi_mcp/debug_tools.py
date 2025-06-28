"""Debug tools for ArchiMate MCP server analysis."""

from typing import Dict, List, Any
from .archimate.generator import ArchiMateGenerator
from .archimate.validator import ArchiMateValidator
from .element_normalizer import normalize_for_plantuml


def analyze_generator_state(generator: ArchiMateGenerator) -> Dict[str, Any]:
    """Analyze the current state of the ArchiMate generator.
    
    Args:
        generator: ArchiMate generator instance
        
    Returns:
        Analysis results
    """
    analysis = {
        "element_count": generator.get_element_count(),
        "relationship_count": generator.get_relationship_count(),
        "layers_used": generator.get_layers_used(),
        "elements": {},
        "relationships": [],
        "validation_issues": []
    }
    
    # Analyze elements
    for element_id, element in generator.elements.items():
        analysis["elements"][element_id] = {
            "name": element.name,
            "element_type": element.element_type,
            "layer": element.layer.value,
            "aspect": element.aspect.value,
            "plantuml_output": element.to_plantuml()
        }
    
    # Analyze relationships
    for rel in generator.relationships:
        analysis["relationships"].append({
            "id": rel.id,
            "relationship_type": rel.relationship_type.value,
            "from_element": rel.from_element,
            "to_element": rel.to_element,
            "plantuml_output": rel.to_plantuml()
        })
    
    # Validate elements
    validation_errors = generator.validate_diagram()
    analysis["validation_issues"] = validation_errors
    
    return analysis


def analyze_element_normalization_issues() -> Dict[str, Any]:
    """Analyze common element normalization issues.
    
    Returns:
        Analysis of normalization problems
    """
    test_cases = [
        # Business layer
        ("Actor", "business"),
        ("Service", "business"),
        ("Process", "business"),
        ("Object", "business"),
        
        # Application layer  
        ("Component", "application"),
        ("Service", "application"),
        ("DataObject", "application"),
        ("Data_Object", "application"),
        
        # Technology layer
        ("Node", "technology"),
        ("Device", "technology"),
        ("Service", "technology"),
        
        # Motivation layer
        ("Stakeholder", "motivation"),
        ("Driver", "motivation"),
        ("Goal", "motivation"),
        ("Requirement", "motivation"),
        
        # Implementation layer
        ("Workpackage", "implementation"),
        ("Work_Package", "implementation"),
        ("WorkPackage", "implementation"),
        ("Deliverable", "implementation"),
    ]
    
    results = {
        "test_cases": [],
        "issues_found": [],
        "layer_specific_mappings": {}
    }
    
    for element_type, layer in test_cases:
        try:
            normalized = normalize_for_plantuml(element_type, layer)
            results["test_cases"].append({
                "input_type": element_type,
                "layer": layer,
                "normalized": normalized,
                "status": "success"
            })
            
            # Track layer-specific mappings
            if layer not in results["layer_specific_mappings"]:
                results["layer_specific_mappings"][layer] = {}
            results["layer_specific_mappings"][layer][element_type] = normalized
            
        except Exception as e:
            results["test_cases"].append({
                "input_type": element_type,
                "layer": layer,
                "normalized": None,
                "status": "error",
                "error": str(e)
            })
            results["issues_found"].append({
                "element_type": element_type,
                "layer": layer,
                "error": str(e)
            })
    
    return results


def identify_architecture_problems(generator: ArchiMateGenerator, validator: ArchiMateValidator) -> Dict[str, Any]:
    """Identify common problems in ArchiMate architecture.
    
    Args:
        generator: ArchiMate generator instance
        validator: ArchiMate validator instance
        
    Returns:
        Identified problems and recommendations
    """
    problems = {
        "critical_issues": [],
        "warnings": [],
        "recommendations": [],
        "summary": {}
    }
    
    # Check if generator has any content
    if generator.get_element_count() == 0:
        problems["critical_issues"].append({
            "issue": "Empty Architecture",
            "description": "No elements are currently defined in the generator",
            "severity": "high",
            "recommendation": "Create elements using create_archimate_diagram or add_archimate_element tools"
        })
    
    # Check for orphaned elements (no relationships)
    if generator.get_element_count() > 0 and generator.get_relationship_count() == 0:
        problems["warnings"].append({
            "issue": "No Relationships Defined",
            "description": f"{generator.get_element_count()} elements exist but no relationships are defined",
            "severity": "medium",
            "recommendation": "Add relationships using add_archimate_relationship tool"
        })
    
    # Check layer distribution
    layers_used = generator.get_layers_used()
    if len(layers_used) == 1:
        problems["warnings"].append({
            "issue": "Single Layer Architecture",
            "description": f"Only {layers_used[0]} layer is used",
            "severity": "low",
            "recommendation": "Consider adding elements from other layers for complete architecture"
        })
    
    # Validate element naming conventions
    element_issues = []
    for element_id, element in generator.elements.items():
        try:
            plantuml = element.to_plantuml()
            
            # Check for common naming issues
            if element.element_type.islower():
                element_issues.append({
                    "element_id": element_id,
                    "issue": "Lowercase element type",
                    "current": element.element_type,
                    "recommendation": "Use proper casing (e.g., Business_Actor)"
                })
            
            # Check for spaces in element IDs
            if ' ' in element.id:
                element_issues.append({
                    "element_id": element_id,
                    "issue": "Spaces in element ID",
                    "current": element.id,
                    "recommendation": "Use underscores instead of spaces"
                })
                
        except Exception as e:
            element_issues.append({
                "element_id": element_id,
                "issue": "PlantUML generation error",
                "error": str(e),
                "recommendation": "Check element type normalization"
            })
    
    if element_issues:
        problems["critical_issues"].extend(element_issues)
    
    # Validate relationships
    relationship_issues = []
    for rel in generator.relationships:
        try:
            plantuml = rel.to_plantuml()
            
            # Check if relationship endpoints exist
            if rel.from_element not in generator.elements:
                relationship_issues.append({
                    "relationship_id": rel.id,
                    "issue": "Missing source element",
                    "from_element": rel.from_element,
                    "recommendation": "Add missing element or fix relationship reference"
                })
            
            if rel.to_element not in generator.elements:
                relationship_issues.append({
                    "relationship_id": rel.id,
                    "issue": "Missing target element", 
                    "to_element": rel.to_element,
                    "recommendation": "Add missing element or fix relationship reference"
                })
                
        except Exception as e:
            relationship_issues.append({
                "relationship_id": rel.id,
                "issue": "PlantUML generation error",
                "error": str(e),
                "recommendation": "Check relationship type and syntax"
            })
    
    if relationship_issues:
        problems["critical_issues"].extend(relationship_issues)
    
    # Generate summary
    problems["summary"] = {
        "total_issues": len(problems["critical_issues"]),
        "total_warnings": len(problems["warnings"]),
        "elements_count": generator.get_element_count(),
        "relationships_count": generator.get_relationship_count(),
        "layers_used": layers_used,
        "overall_health": "healthy" if len(problems["critical_issues"]) == 0 else "issues_found"
    }
    
    # Add general recommendations
    if generator.get_element_count() > 0:
        problems["recommendations"].extend([
            "Test PlantUML generation with validate_archimate_model tool",
            "Generate PNG diagrams to /tmp for visual verification",
            "Use export_archimate_diagram to save PlantUML code",
            "Consider using templates for standard architecture patterns"
        ])
    
    return problems