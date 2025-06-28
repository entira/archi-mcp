"""Tests for ArchiMate diagram generator."""

import pytest
from pathlib import Path
import tempfile
from archi_mcp.archimate.generator import ArchiMateGenerator, DiagramLayout
from archi_mcp.archimate.elements.base import ArchiMateElement, ArchiMateLayer, ArchiMateAspect
from archi_mcp.archimate.relationships import ArchiMateRelationship, RelationshipType
from archi_mcp.utils.exceptions import ArchiMateGenerationError


class TestArchiMateGenerator:
    """Test ArchiMate diagram generator."""
    
    def create_test_element(self, id_suffix="1"):
        """Create a test element."""
        return ArchiMateElement(
            id=f"test_element_{id_suffix}",
            name=f"Test Element {id_suffix}",
            element_type="Business_Service",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.BEHAVIOR
        )
    
    def create_test_relationship(self, from_id, to_id, rel_id="1"):
        """Create a test relationship."""
        return ArchiMateRelationship(
            id=f"test_rel_{rel_id}",
            from_element=from_id,
            to_element=to_id,
            relationship_type=RelationshipType.SERVING
        )
    
    def test_generator_initialization(self):
        """Test generator initialization."""
        generator = ArchiMateGenerator()
        
        assert len(generator.elements) == 0
        assert len(generator.relationships) == 0
        assert generator.layout is not None
    
    def test_add_element_success(self):
        """Test successful element addition."""
        generator = ArchiMateGenerator()
        element = self.create_test_element()
        
        generator.add_element(element)
        
        assert len(generator.elements) == 1
        assert generator.elements[element.id] == element
    
    def test_add_element_duplicate_id(self):
        """Test adding element with duplicate ID."""
        generator = ArchiMateGenerator()
        element1 = self.create_test_element("1")
        element2 = ArchiMateElement(
            id="test_element_1",  # Same ID as element1
            name="Different Element",
            element_type="Business_Actor",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE
        )
        
        generator.add_element(element1)
        
        with pytest.raises(ArchiMateGenerationError) as exc_info:
            generator.add_element(element2)
        
        assert "already exists" in str(exc_info.value)
    
    def test_add_relationship_success(self):
        """Test successful relationship addition."""
        generator = ArchiMateGenerator()
        element1 = self.create_test_element("1")
        element2 = self.create_test_element("2")
        
        generator.add_element(element1)
        generator.add_element(element2)
        
        relationship = self.create_test_relationship(element1.id, element2.id)
        generator.add_relationship(relationship)
        
        assert len(generator.relationships) == 1
        assert generator.relationships[0] == relationship
    
    def test_add_relationship_missing_elements(self):
        """Test adding relationship with missing elements."""
        generator = ArchiMateGenerator()
        relationship = self.create_test_relationship("missing_1", "missing_2")
        
        with pytest.raises(ArchiMateGenerationError) as exc_info:
            generator.add_relationship(relationship)
        
        assert "validation failed" in str(exc_info.value).lower()
    
    def test_set_layout(self):
        """Test setting diagram layout."""
        generator = ArchiMateGenerator()
        layout = DiagramLayout(
            direction="vertical",
            show_legend=False,
            group_by_layer=True
        )
        
        generator.set_layout(layout)
        
        assert generator.layout.direction == "vertical"
        assert generator.layout.show_legend is False
        assert generator.layout.group_by_layer is True
    
    def test_generate_plantuml_empty(self):
        """Test PlantUML generation with empty diagram."""
        generator = ArchiMateGenerator()
        
        with pytest.raises(ArchiMateGenerationError) as exc_info:
            generator.generate_plantuml()
        
        assert "No elements defined" in str(exc_info.value)
    
    def test_generate_plantuml_simple(self):
        """Test simple PlantUML generation."""
        generator = ArchiMateGenerator()
        element = self.create_test_element()
        generator.add_element(element)
        
        plantuml = generator.generate_plantuml(title="Test Diagram")
        
        assert "@startuml" in plantuml
        assert "@enduml" in plantuml
        assert "!include <archimate/Archimate>" in plantuml
        assert "title Test Diagram" in plantuml
        assert element.to_plantuml() in plantuml
    
    def test_generate_plantuml_with_relationships(self):
        """Test PlantUML generation with relationships."""
        generator = ArchiMateGenerator()
        element1 = self.create_test_element("1")
        element2 = self.create_test_element("2")
        
        generator.add_element(element1)
        generator.add_element(element2)
        
        relationship = self.create_test_relationship(element1.id, element2.id)
        generator.add_relationship(relationship)
        
        plantuml = generator.generate_plantuml()
        
        assert element1.to_plantuml() in plantuml
        assert element2.to_plantuml() in plantuml
        assert relationship.to_plantuml() in plantuml
        assert "' Elements" in plantuml
        assert "' Relationships" in plantuml
    
    def test_generate_plantuml_with_legend(self):
        """Test PlantUML generation with legend."""
        generator = ArchiMateGenerator()
        element = self.create_test_element()
        generator.add_element(element)
        
        layout = DiagramLayout(show_legend=True)
        generator.set_layout(layout)
        
        plantuml = generator.generate_plantuml()
        
        assert "legend" in plantuml
        assert "Business Layer" in plantuml
        assert "end legend" in plantuml
    
    def test_generate_plantuml_group_by_layer(self):
        """Test PlantUML generation grouped by layer."""
        generator = ArchiMateGenerator()
        
        # Add elements from different layers
        business_element = ArchiMateElement(
            id="business_elem",
            name="Business Element",
            element_type="Business_Service",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.BEHAVIOR
        )
        
        app_element = ArchiMateElement(
            id="app_elem",
            name="Application Element",
            element_type="Application_Component",
            layer=ArchiMateLayer.APPLICATION,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE
        )
        
        generator.add_element(business_element)
        generator.add_element(app_element)
        
        layout = DiagramLayout(group_by_layer=True)
        generator.set_layout(layout)
        
        plantuml = generator.generate_plantuml()
        
        assert "package \"Business Layer\"" in plantuml
        assert "package \"Application Layer\"" in plantuml
    
    def test_clear_diagram(self):
        """Test clearing diagram."""
        generator = ArchiMateGenerator()
        element = self.create_test_element()
        generator.add_element(element)
        
        assert len(generator.elements) == 1
        
        generator.clear()
        
        assert len(generator.elements) == 0
        assert len(generator.relationships) == 0
    
    def test_get_element_count(self):
        """Test getting element count."""
        generator = ArchiMateGenerator()
        
        assert generator.get_element_count() == 0
        
        generator.add_element(self.create_test_element("1"))
        assert generator.get_element_count() == 1
        
        generator.add_element(self.create_test_element("2"))
        assert generator.get_element_count() == 2
    
    def test_get_relationship_count(self):
        """Test getting relationship count."""
        generator = ArchiMateGenerator()
        element1 = self.create_test_element("1")
        element2 = self.create_test_element("2")
        
        generator.add_element(element1)
        generator.add_element(element2)
        
        assert generator.get_relationship_count() == 0
        
        relationship = self.create_test_relationship(element1.id, element2.id)
        generator.add_relationship(relationship)
        
        assert generator.get_relationship_count() == 1
    
    def test_get_layers_used(self):
        """Test getting layers used in diagram."""
        generator = ArchiMateGenerator()
        
        # Add elements from different layers
        business_element = ArchiMateElement(
            id="business_elem",
            name="Business Element",
            element_type="Business_Service",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.BEHAVIOR
        )
        
        tech_element = ArchiMateElement(
            id="tech_elem",
            name="Technology Element",
            element_type="Node",
            layer=ArchiMateLayer.TECHNOLOGY,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE
        )
        
        generator.add_element(business_element)
        generator.add_element(tech_element)
        
        layers = generator.get_layers_used()
        
        assert "Business" in layers
        assert "Technology" in layers
        assert len(layers) == 2
    
    def test_validate_diagram_success(self):
        """Test successful diagram validation."""
        generator = ArchiMateGenerator()
        element = self.create_test_element()
        generator.add_element(element)
        
        errors = generator.validate_diagram()
        
        assert len(errors) == 0
    
    def test_validate_diagram_with_errors(self):
        """Test diagram validation with errors."""
        generator = ArchiMateGenerator()
        
        # Add element with invalid ID
        invalid_element = ArchiMateElement(
            id="",  # Invalid empty ID
            name="Invalid Element",
            element_type="Business_Service",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.BEHAVIOR
        )
        
        generator.elements[invalid_element.id or "empty"] = invalid_element
        
        errors = generator.validate_diagram()
        
        assert len(errors) > 0
        assert any("Element ID is required" in error for error in errors)
    
    def test_export_to_file(self):
        """Test exporting diagram to file."""
        generator = ArchiMateGenerator()
        element = self.create_test_element()
        generator.add_element(element)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False) as f:
            temp_path = f.name
        
        try:
            generator.export_to_file(temp_path, title="Test Export")
            
            # Verify file was created and contains expected content
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert "@startuml" in content
            assert "@enduml" in content
            assert "title Test Export" in content
            assert element.to_plantuml() in content
        
        finally:
            # Clean up
            Path(temp_path).unlink(missing_ok=True)
    
    def test_export_to_file_invalid_path(self):
        """Test exporting to invalid file path."""
        generator = ArchiMateGenerator()
        element = self.create_test_element()
        generator.add_element(element)
        
        invalid_path = "/invalid/path/that/does/not/exist/diagram.puml"
        
        with pytest.raises(ArchiMateGenerationError) as exc_info:
            generator.export_to_file(invalid_path)
        
        assert "Failed to export diagram to file" in str(exc_info.value)


class TestDiagramLayout:
    """Test diagram layout configuration."""
    
    def test_default_layout(self):
        """Test default layout configuration."""
        layout = DiagramLayout()
        
        assert layout.direction == "horizontal"
        assert layout.show_legend is True
        assert layout.show_title is True
        assert layout.group_by_layer is False
        assert layout.spacing == "normal"
    
    def test_custom_layout(self):
        """Test custom layout configuration."""
        layout = DiagramLayout(
            direction="vertical",
            show_legend=False,
            show_title=False,
            group_by_layer=True,
            spacing="compact"
        )
        
        assert layout.direction == "vertical"
        assert layout.show_legend is False
        assert layout.show_title is False
        assert layout.group_by_layer is True
        assert layout.spacing == "compact"