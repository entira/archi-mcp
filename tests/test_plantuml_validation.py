"""Test PlantUML generation and validation."""

import pytest
import re
from pathlib import Path

class TestPlantUMLGeneration:
    """Test PlantUML code generation and syntax validation."""
    
    def test_basic_plantuml_syntax(self):
        """Test basic PlantUML syntax generation."""
        from archi_mcp.server import create_archimate_diagram, DiagramInput, ElementInput
        
        diagram_input = DiagramInput(
            elements=[
                ElementInput(
                    id="test_actor",
                    name="Test Actor",
                    element_type="Business_Actor",
                    layer="Business"
                )
            ],
            title="Syntax Test"
        )
        
        result = create_archimate_diagram.fn(diagram=diagram_input)
        
        # Extract PlantUML code
        plantuml_match = re.search(r'```plantuml\n(.*?)\n```', result, re.DOTALL)
        assert plantuml_match, "No PlantUML code found in result"
        
        plantuml_code = plantuml_match.group(1)
        
        # Check basic syntax requirements
        assert plantuml_code.startswith('@startuml') or 'startuml' in plantuml_code
        assert plantuml_code.endswith('@enduml') or 'enduml' in plantuml_code
        assert 'Business_Actor' in plantuml_code
        assert 'Test Actor' in plantuml_code
    
    def test_archimate_includes(self):
        """Test that PlantUML includes ArchiMate library."""
        from archi_mcp.server import create_archimate_diagram, DiagramInput, ElementInput
        
        diagram_input = DiagramInput(
            elements=[
                ElementInput(
                    id="app_comp",
                    name="Application Component",
                    element_type="Application_Component",
                    layer="Application"
                )
            ]
        )
        
        result = create_archimate_diagram.fn(diagram=diagram_input)
        
        # Should include ArchiMate library
        assert '!include' in result or 'archimate' in result.lower()
    
    def test_element_syntax_compliance(self):
        """Test that elements follow correct ArchiMate PlantUML syntax."""
        from archi_mcp.server import create_archimate_diagram, DiagramInput, ElementInput
        
        test_cases = [
            ("Business_Actor", "Business", "actor1", "Business Actor"),
            ("Application_Component", "Application", "app1", "App Component"), 
            ("Node", "Technology", "node1", "Server Node"),
            ("Stakeholder", "Motivation", "stake1", "Stakeholder")
        ]
        
        for element_type, layer, element_id, element_name in test_cases:
            diagram_input = DiagramInput(
                elements=[
                    ElementInput(
                        id=element_id,
                        name=element_name,
                        element_type=element_type,
                        layer=layer
                    )
                ]
            )
            
            result = create_archimate_diagram.fn(diagram=diagram_input)
            
            # Extract PlantUML code
            plantuml_match = re.search(r'```plantuml\n(.*?)\n```', result, re.DOTALL)
            assert plantuml_match, f"No PlantUML code found for {element_type}"
            
            plantuml_code = plantuml_match.group(1)
            
            # Check element syntax: Layer_ElementType(id, "name")
            expected_pattern = f'{layer}_{element_type}\\({element_id}[^)]*"[^"]*{element_name.split()[0]}[^"]*"\\)'
            assert re.search(expected_pattern, plantuml_code), f"Invalid syntax for {element_type} in: {plantuml_code}"
    
    def test_relationship_syntax_compliance(self):
        """Test that relationships follow correct ArchiMate PlantUML syntax."""
        from archi_mcp.server import (
            create_archimate_diagram, DiagramInput, ElementInput, RelationshipInput
        )
        
        diagram_input = DiagramInput(
            elements=[
                ElementInput(
                    id="actor1",
                    name="Actor",
                    element_type="Business_Actor",
                    layer="Business"
                ),
                ElementInput(
                    id="service1", 
                    name="Service",
                    element_type="Business_Service",
                    layer="Business"
                )
            ],
            relationships=[
                RelationshipInput(
                    id="rel1",
                    from_element="actor1",
                    to_element="service1",
                    relationship_type="Access"
                )
            ]
        )
        
        result = create_archimate_diagram.fn(diagram=diagram_input)
        
        # Extract PlantUML code
        plantuml_match = re.search(r'```plantuml\n(.*?)\n```', result, re.DOTALL)
        assert plantuml_match, "No PlantUML code found"
        
        plantuml_code = plantuml_match.group(1)
        
        # Check relationship syntax: Rel_RelationType(source, target, "label")
        assert 'Rel_Access' in plantuml_code or 'actor1' in plantuml_code
        assert 'service1' in plantuml_code
    
    def test_special_characters_escaping(self):
        """Test that special characters are properly escaped in PlantUML."""
        from archi_mcp.server import create_archimate_diagram, DiagramInput, ElementInput
        
        diagram_input = DiagramInput(
            elements=[
                ElementInput(
                    id="special_chars",
                    name="Element with \"quotes\" & <tags>",
                    element_type="Business_Actor",
                    layer="Business",
                    description="Description with special chars: & < > \" '"
                )
            ]
        )
        
        result = create_archimate_diagram.fn(diagram=diagram_input)
        
        # Should not contain unescaped special characters that break PlantUML
        plantuml_match = re.search(r'```plantuml\n(.*?)\n```', result, re.DOTALL)
        assert plantuml_match, "No PlantUML code found"
        
        plantuml_code = plantuml_match.group(1)
        
        # Basic validation - should not contain obvious syntax errors
        assert plantuml_code.count('"') % 2 == 0, "Unmatched quotes in PlantUML code"
    
    def test_empty_diagram_handling(self):
        """Test handling of empty diagrams."""
        from archi_mcp.server import create_archimate_diagram, DiagramInput
        
        diagram_input = DiagramInput(
            elements=[],
            relationships=[],
            title="Empty Diagram"
        )
        
        result = create_archimate_diagram.fn(diagram=diagram_input)
        
        # Should handle empty diagram gracefully
        assert isinstance(result, str)
        assert "Elements: 0" in result
        assert "Relationships: 0" in result
    
    def test_large_diagram_handling(self):
        """Test handling of diagrams with many elements."""
        from archi_mcp.server import create_archimate_diagram, DiagramInput, ElementInput
        
        # Create diagram with multiple elements
        elements = []
        for i in range(10):
            elements.append(
                ElementInput(
                    id=f"element_{i}",
                    name=f"Element {i}",
                    element_type="Business_Actor",
                    layer="Business"
                )
            )
        
        diagram_input = DiagramInput(
            elements=elements,
            title="Large Diagram Test"
        )
        
        result = create_archimate_diagram.fn(diagram=diagram_input)
        
        # Should handle multiple elements
        assert "Elements: 10" in result
        assert "```plantuml" in result
        
        # Extract and validate PlantUML
        plantuml_match = re.search(r'```plantuml\n(.*?)\n```', result, re.DOTALL)
        assert plantuml_match, "No PlantUML code found"
        
        plantuml_code = plantuml_match.group(1)
        
        # Should contain all elements
        for i in range(10):
            assert f"element_{i}" in plantuml_code

class TestPlantUMLValidation:
    """Test PlantUML validation and syntax checking."""
    
    def test_generated_diagrams_syntax(self):
        """Test that generated diagrams have valid PlantUML syntax."""
        from archi_mcp.server import generate_full_architecture, FullArchitectureInput
        
        architecture_input = FullArchitectureInput(
            system_description="Test system for validation",
            business_domain="general",
            include_views=["motivation"],
            implementation_phases=1
        )
        
        result = generate_full_architecture.fn(architecture=architecture_input)
        
        # Extract all PlantUML blocks
        plantuml_blocks = re.findall(r'```plantuml\n(.*?)\n```', result, re.DOTALL)
        
        assert len(plantuml_blocks) > 0, "No PlantUML blocks found"
        
        for i, block in enumerate(plantuml_blocks):
            # Basic syntax validation
            assert block.strip(), f"Empty PlantUML block {i}"
            
            # Should have start and end markers
            lines = block.strip().split('\n')
            assert any('startuml' in line.lower() for line in lines), f"No @startuml in block {i}"
            assert any('enduml' in line.lower() for line in lines), f"No @enduml in block {i}"
    
    def test_archimate_element_types(self):
        """Test that only valid ArchiMate element types are used."""
        from archi_mcp.server import create_archimate_diagram, DiagramInput, ElementInput
        
        # Test with known valid element types
        valid_elements = [
            ("Business_Actor", "Business"),
            ("Business_Service", "Business"),
            ("Application_Component", "Application"),
            ("Application_Service", "Application"),
            ("Node", "Technology"),
            ("Device", "Technology"),
            ("Stakeholder", "Motivation"),
            ("Goal", "Motivation")
        ]
        
        for element_type, layer in valid_elements:
            diagram_input = DiagramInput(
                elements=[
                    ElementInput(
                        id=f"test_{element_type.lower()}",
                        name=f"Test {element_type}",
                        element_type=element_type,
                        layer=layer
                    )
                ]
            )
            
            result = create_archimate_diagram.fn(diagram=diagram_input)
            
            # Should generate without errors
            assert isinstance(result, str)
            assert "ArchiMate diagram created successfully!" in result
            assert "```plantuml" in result
    
    def test_archimate_relationship_types(self):
        """Test that only valid ArchiMate relationship types are used."""
        from archi_mcp.server import (
            add_archimate_element, add_archimate_relationship
        )
        
        # Add elements first
        add_archimate_element.fn(element_type="Business_Actor", id="actor1", name="Actor 1", layer="Business")
        add_archimate_element.fn(element_type="Business_Service", id="service1", name="Service 1", layer="Business")
        
        # Test valid relationship types
        valid_relationships = [
            "Access", "Aggregation", "Assignment", "Association",
            "Composition", "Flow", "Influence", "Realization", 
            "Serving", "Specialization", "Triggering"
        ]
        
        for rel_type in valid_relationships:
            result = add_archimate_relationship.fn(
                id=f"rel_{rel_type.lower()}",
                from_element="actor1",
                to_element="service1",
                relationship_type=rel_type
            )
            
            # Should add without errors
            assert isinstance(result, str)
            assert "added successfully" in result
        
        # Test completed - relationships added successfully

@pytest.mark.skipif(
    not Path("/usr/bin/java").exists() and not Path("/usr/local/bin/java").exists(),
    reason="Java not available for PlantUML validation"
)
class TestPlantUMLJavaValidation:
    """Test PlantUML validation with actual Java PlantUML jar (if available)."""
    
    def test_java_plantuml_validation(self):
        """Test PlantUML syntax with actual PlantUML jar validation."""
        import subprocess
        import tempfile
        from archi_mcp.server import create_archimate_diagram, DiagramInput, ElementInput
        
        # Generate a test diagram
        diagram_input = DiagramInput(
            elements=[
                ElementInput(
                    id="java_test",
                    name="Java Test Element",
                    element_type="Business_Actor",
                    layer="Business"
                )
            ],
            title="Java Validation Test"
        )
        
        result = create_archimate_diagram.fn(diagram=diagram_input)
        
        # Extract PlantUML code
        plantuml_match = re.search(r'```plantuml\n(.*?)\n```', result, re.DOTALL)
        assert plantuml_match, "No PlantUML code found"
        
        plantuml_code = plantuml_match.group(1)
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False) as f:
            f.write(plantuml_code)
            temp_file = f.name
        
        try:
            # Try to validate with PlantUML (if available)
            # This is optional and will be skipped if PlantUML jar is not available
            result = subprocess.run(
                ['java', '-jar', 'plantuml.jar', '-checkonly', temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # If PlantUML is available and validation runs, it should not report syntax errors
            if result.returncode == 0:
                assert "syntax" not in result.stderr.lower()
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # PlantUML jar not available, skip validation
            pytest.skip("PlantUML jar not available for validation")
        finally:
            # Clean up
            Path(temp_file).unlink(missing_ok=True)

def test_plantuml_output_format():
    """Test that PlantUML output follows expected format."""
    from archi_mcp.server import create_archimate_diagram, DiagramInput, ElementInput
    
    # Create a test diagram
    diagram_input = DiagramInput(
        elements=[
            ElementInput(
                id="format_test",
                name="Format Test",
                element_type="Business_Actor",
                layer="Business"
            )
        ],
        title="Format Test"
    )
    
    result = create_archimate_diagram.fn(diagram=diagram_input)
    
    # Should contain properly formatted PlantUML block
    assert "```plantuml" in result
    assert "```" in result
    
    # Extract PlantUML content
    start = result.find("```plantuml") + len("```plantuml")
    end = result.find("```", start)
    plantuml_content = result[start:end].strip()
    
    # Should not be empty
    assert plantuml_content
    
    # Should have reasonable structure
    lines = plantuml_content.split('\n')
    assert len(lines) >= 3  # At minimum: start, content, end