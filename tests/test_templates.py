"""Tests for ArchiMate templates."""

import pytest
from archi_mcp.templates import (
    get_viewpoint_template,
    get_pattern_template,
    get_industry_template,
    ARCHIMATE_VIEWPOINTS,
    ARCHITECTURE_PATTERNS,
    INDUSTRY_TEMPLATES,
)
from archi_mcp.templates.viewpoints import ViewpointTemplate, list_available_viewpoints
from archi_mcp.templates.patterns import PatternTemplate, list_available_patterns, get_patterns_by_type
from archi_mcp.templates.industry import IndustryTemplate, list_available_industry_templates, get_templates_by_industry


class TestViewpointTemplates:
    """Test ArchiMate viewpoint templates."""
    
    def test_viewpoint_registry_not_empty(self):
        """Test that viewpoint registry is not empty."""
        assert len(ARCHIMATE_VIEWPOINTS) > 0
    
    def test_essential_viewpoints_present(self):
        """Test that essential viewpoints are present."""
        essential_viewpoints = [
            "layered",
            "service_realization", 
            "application_cooperation",
            "technology_usage",
            "motivation"
        ]
        
        for viewpoint in essential_viewpoints:
            assert viewpoint in ARCHIMATE_VIEWPOINTS
    
    def test_get_viewpoint_template_success(self):
        """Test successful viewpoint template retrieval."""
        template = get_viewpoint_template("layered")
        
        assert template is not None
        assert isinstance(template, ViewpointTemplate)
        assert template.name == "Layered Viewpoint"
        assert len(template.elements) > 0
        assert len(template.relationships) > 0
    
    def test_get_viewpoint_template_not_found(self):
        """Test viewpoint template not found."""
        template = get_viewpoint_template("nonexistent_viewpoint")
        assert template is None
    
    def test_list_available_viewpoints(self):
        """Test listing available viewpoints."""
        viewpoints = list_available_viewpoints()
        
        assert isinstance(viewpoints, list)
        assert len(viewpoints) > 0
        assert "layered" in viewpoints
    
    def test_layered_viewpoint_structure(self):
        """Test layered viewpoint structure."""
        template = get_viewpoint_template("layered")
        
        assert template.name == "Layered Viewpoint"
        assert "layers" in template.description.lower()
        
        # Check elements have required fields
        for element in template.elements:
            assert "id" in element
            assert "name" in element
            assert "element_type" in element
            assert "layer" in element
        
        # Check relationships have required fields
        for relationship in template.relationships:
            assert "id" in relationship
            assert "from_element" in relationship
            assert "to_element" in relationship
            assert "relationship_type" in relationship
    
    def test_service_realization_viewpoint(self):
        """Test service realization viewpoint."""
        template = get_viewpoint_template("service_realization")
        
        assert template is not None
        assert "service" in template.name.lower()
        assert "realization" in template.name.lower()
        
        # Should contain business and application elements
        element_types = [elem["element_type"] for elem in template.elements]
        assert any("Business" in elem_type for elem_type in element_types)
        assert any("Application" in elem_type for elem_type in element_types)


class TestPatternTemplates:
    """Test architecture pattern templates."""
    
    def test_pattern_registry_not_empty(self):
        """Test that pattern registry is not empty."""
        assert len(ARCHITECTURE_PATTERNS) > 0
    
    def test_essential_patterns_present(self):
        """Test that essential patterns are present."""
        essential_patterns = [
            "three_tier",
            "microservices",
            "event_driven",
            "layered_service"
        ]
        
        for pattern in essential_patterns:
            assert pattern in ARCHITECTURE_PATTERNS
    
    def test_get_pattern_template_success(self):
        """Test successful pattern template retrieval."""
        template = get_pattern_template("three_tier")
        
        assert template is not None
        assert isinstance(template, PatternTemplate)
        assert template.name == "Three-Tier Architecture"
        assert len(template.elements) > 0
        assert len(template.relationships) > 0
    
    def test_get_pattern_template_not_found(self):
        """Test pattern template not found."""
        template = get_pattern_template("nonexistent_pattern")
        assert template is None
    
    def test_list_available_patterns(self):
        """Test listing available patterns."""
        patterns = list_available_patterns()
        
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        assert "three_tier" in patterns
    
    def test_get_patterns_by_type(self):
        """Test getting patterns by type."""
        architectural_patterns = get_patterns_by_type("architectural")
        
        assert isinstance(architectural_patterns, list)
        assert len(architectural_patterns) > 0
        assert "three_tier" in architectural_patterns
    
    def test_three_tier_pattern_structure(self):
        """Test three-tier pattern structure."""
        template = get_pattern_template("three_tier")
        
        assert template.name == "Three-Tier Architecture"
        assert template.pattern_type == "architectural"
        
        # Should have presentation, business, and data layers
        element_names = [elem["name"].lower() for elem in template.elements]
        assert any("presentation" in name for name in element_names)
        assert any("business" in name or "logic" in name for name in element_names)
        assert any("data" in name for name in element_names)
    
    def test_microservices_pattern_structure(self):
        """Test microservices pattern structure."""
        template = get_pattern_template("microservices")
        
        assert template.name == "Microservices Architecture"
        
        # Should have API gateway and multiple services
        element_names = [elem["name"].lower() for elem in template.elements]
        assert any("gateway" in name for name in element_names)
        assert any("service" in name for name in element_names)
        
        # Should have service discovery and message queue
        assert any("discovery" in name for name in element_names)
        assert any("queue" in name or "message" in name for name in element_names)


class TestIndustryTemplates:
    """Test industry-specific templates."""
    
    def test_industry_registry_not_empty(self):
        """Test that industry registry is not empty."""
        assert len(INDUSTRY_TEMPLATES) > 0
    
    def test_essential_industry_templates_present(self):
        """Test that essential industry templates are present."""
        essential_templates = [
            "banking_core",
            "ecommerce_platform",
            "healthcare_his",
            "manufacturing_mes"
        ]
        
        for template in essential_templates:
            assert template in INDUSTRY_TEMPLATES
    
    def test_get_industry_template_success(self):
        """Test successful industry template retrieval."""
        template = get_industry_template("banking_core")
        
        assert template is not None
        assert isinstance(template, IndustryTemplate)
        assert template.name == "Core Banking System"
        assert template.industry == "banking"
        assert len(template.elements) > 0
        assert len(template.relationships) > 0
    
    def test_get_industry_template_not_found(self):
        """Test industry template not found."""
        template = get_industry_template("nonexistent_template")
        assert template is None
    
    def test_list_available_industry_templates(self):
        """Test listing available industry templates."""
        templates = list_available_industry_templates()
        
        assert isinstance(templates, list)
        assert len(templates) > 0
        assert "banking_core" in templates
    
    def test_get_templates_by_industry(self):
        """Test getting templates by industry."""
        banking_templates = get_templates_by_industry("banking")
        
        assert isinstance(banking_templates, list)
        assert "banking_core" in banking_templates
        
        retail_templates = get_templates_by_industry("retail")
        assert "ecommerce_platform" in retail_templates
    
    def test_banking_template_structure(self):
        """Test banking template structure."""
        template = get_industry_template("banking_core")
        
        assert template.industry == "banking"
        assert "banking" in template.name.lower()
        
        # Should have typical banking elements
        element_names = [elem["name"].lower() for elem in template.elements]
        assert any("customer" in name for name in element_names)
        assert any("account" in name for name in element_names)
        assert any("transaction" in name for name in element_names)
    
    def test_ecommerce_template_structure(self):
        """Test e-commerce template structure."""
        template = get_industry_template("ecommerce_platform")
        
        assert template.industry == "retail"
        assert "commerce" in template.name.lower()
        
        # Should have typical e-commerce elements
        element_names = [elem["name"].lower() for elem in template.elements]
        assert any("customer" in name for name in element_names)
        assert any("catalog" in name or "product" in name for name in element_names)
        assert any("order" in name for name in element_names)
        assert any("payment" in name for name in element_names)
    
    def test_healthcare_template_structure(self):
        """Test healthcare template structure."""
        template = get_industry_template("healthcare_his")
        
        assert template.industry == "healthcare"
        assert "hospital" in template.name.lower()
        
        # Should have typical healthcare elements
        element_names = [elem["name"].lower() for elem in template.elements]
        assert any("patient" in name for name in element_names)
        assert any("doctor" in name for name in element_names)
        assert any("medical" in name for name in element_names)


class TestTemplateIntegration:
    """Test template integration and consistency."""
    
    def test_all_templates_have_required_fields(self):
        """Test that all templates have required fields."""
        # Test viewpoints
        for name, template in ARCHIMATE_VIEWPOINTS.items():
            assert hasattr(template, 'name')
            assert hasattr(template, 'description')
            assert hasattr(template, 'elements')
            assert hasattr(template, 'relationships')
            assert isinstance(template.elements, list)
            assert isinstance(template.relationships, list)
        
        # Test patterns
        for name, template in ARCHITECTURE_PATTERNS.items():
            assert hasattr(template, 'name')
            assert hasattr(template, 'description')
            assert hasattr(template, 'elements')
            assert hasattr(template, 'relationships')
            assert hasattr(template, 'pattern_type')
            assert isinstance(template.elements, list)
            assert isinstance(template.relationships, list)
        
        # Test industry templates
        for name, template in INDUSTRY_TEMPLATES.items():
            assert hasattr(template, 'name')
            assert hasattr(template, 'description')
            assert hasattr(template, 'industry')
            assert hasattr(template, 'elements')
            assert hasattr(template, 'relationships')
            assert isinstance(template.elements, list)
            assert isinstance(template.relationships, list)
    
    def test_template_element_consistency(self):
        """Test that template elements have consistent structure."""
        all_templates = list(ARCHIMATE_VIEWPOINTS.values()) + \
                       list(ARCHITECTURE_PATTERNS.values()) + \
                       list(INDUSTRY_TEMPLATES.values())
        
        for template in all_templates:
            for element in template.elements:
                # Required fields
                assert "id" in element
                assert "name" in element
                assert "element_type" in element
                assert "layer" in element
                
                # Valid element types (basic validation)
                assert isinstance(element["id"], str)
                assert isinstance(element["name"], str)
                assert isinstance(element["element_type"], str)
                assert isinstance(element["layer"], str)
    
    def test_template_relationship_consistency(self):
        """Test that template relationships have consistent structure."""
        all_templates = list(ARCHIMATE_VIEWPOINTS.values()) + \
                       list(ARCHITECTURE_PATTERNS.values()) + \
                       list(INDUSTRY_TEMPLATES.values())
        
        for template in all_templates:
            for relationship in template.relationships:
                # Required fields
                assert "id" in relationship
                assert "from_element" in relationship
                assert "to_element" in relationship
                assert "relationship_type" in relationship
                
                # Valid relationship types (basic validation)
                assert isinstance(relationship["id"], str)
                assert isinstance(relationship["from_element"], str)
                assert isinstance(relationship["to_element"], str)
                assert isinstance(relationship["relationship_type"], str)
    
    def test_template_reference_integrity(self):
        """Test that template relationships reference existing elements."""
        all_templates = list(ARCHIMATE_VIEWPOINTS.values()) + \
                       list(ARCHITECTURE_PATTERNS.values()) + \
                       list(INDUSTRY_TEMPLATES.values())
        
        for template in all_templates:
            element_ids = {elem["id"] for elem in template.elements}
            
            for relationship in template.relationships:
                from_id = relationship["from_element"]
                to_id = relationship["to_element"]
                
                assert from_id in element_ids, f"From element '{from_id}' not found in template '{template.name}'"
                assert to_id in element_ids, f"To element '{to_id}' not found in template '{template.name}'"