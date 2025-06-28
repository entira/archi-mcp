"""Tests for ArchiMate elements."""

import pytest
from archi_mcp.archimate.elements import (
    ArchiMateElement,
    BusinessElement,
    ApplicationElement,
    TechnologyElement,
    PhysicalElement,
    MotivationElement,
    StrategyElement,
    ImplementationElement,
    ARCHIMATE_ELEMENTS,
)
from archi_mcp.archimate.elements.base import ArchiMateLayer, ArchiMateAspect


class TestArchiMateElement:
    """Test ArchiMateElement base class."""
    
    def test_element_creation(self):
        """Test basic element creation."""
        element = ArchiMateElement(
            id="test_element",
            name="Test Element",
            element_type="Business_Actor",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE
        )
        
        assert element.id == "test_element"
        assert element.name == "Test Element"
        assert element.element_type == "Business_Actor"
        assert element.layer == ArchiMateLayer.BUSINESS
        assert element.aspect == ArchiMateAspect.ACTIVE_STRUCTURE
    
    def test_element_plantuml_generation(self):
        """Test PlantUML code generation."""
        element = ArchiMateElement(
            id="test_actor",
            name="Test Actor",
            element_type="Business_Actor",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE
        )
        
        plantuml = element.to_plantuml()
        expected = 'Business_Actor(test_actor, "Test Actor")'
        assert plantuml == expected
    
    def test_element_validation_success(self):
        """Test successful element validation."""
        element = ArchiMateElement(
            id="valid_element",
            name="Valid Element",
            element_type="Business_Service",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.BEHAVIOR
        )
        
        errors = element.validate_element()
        assert len(errors) == 0
    
    def test_element_validation_failures(self):
        """Test element validation failures."""
        # Missing ID
        element = ArchiMateElement(
            id="",
            name="Test Element",
            element_type="Business_Actor",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE
        )
        
        errors = element.validate_element()
        assert "Element ID is required" in errors
        
        # Invalid ID format
        element.id = "test-element-with-dashes"
        errors = element.validate_element()
        assert any("alphanumeric characters and underscores" in error for error in errors)
    
    def test_element_with_stereotype(self):
        """Test element with stereotype."""
        element = ArchiMateElement(
            id="test_server",
            name="Web Server",
            element_type="Node",
            layer=ArchiMateLayer.TECHNOLOGY,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            stereotype="web-server"
        )
        
        plantuml = element.to_plantuml()
        assert "<<web-server>>" in plantuml


class TestBusinessElements:
    """Test Business layer elements."""
    
    def test_business_actor_creation(self):
        """Test Business Actor creation."""
        actor = BusinessElement.create_business_actor(
            id="customer",
            name="Customer",
            description="Bank customer"
        )
        
        assert actor.element_type == "Actor"
        assert actor.layer == ArchiMateLayer.BUSINESS
        assert actor.aspect == ArchiMateAspect.ACTIVE_STRUCTURE
        assert actor.name == "Customer"
    
    def test_business_service_creation(self):
        """Test Business Service creation."""
        service = BusinessElement.create_business_service(
            id="account_mgmt",
            name="Account Management",
            description="Account management services"
        )
        
        assert service.element_type == "Service"
        assert service.layer == ArchiMateLayer.BUSINESS
        assert service.aspect == ArchiMateAspect.BEHAVIOR
    
    def test_business_object_creation(self):
        """Test Business Object creation."""
        obj = BusinessElement.create_business_object(
            id="contract",
            name="Service Contract",
            description="Customer service contract"
        )
        
        assert obj.element_type == "Object"
        assert obj.layer == ArchiMateLayer.BUSINESS
        assert obj.aspect == ArchiMateAspect.PASSIVE_STRUCTURE


class TestApplicationElements:
    """Test Application layer elements."""
    
    def test_application_component_creation(self):
        """Test Application Component creation."""
        component = ApplicationElement.create_application_component(
            id="web_app",
            name="Web Application",
            description="Customer-facing web application"
        )
        
        assert component.element_type == "Component"
        assert component.layer == ArchiMateLayer.APPLICATION
        assert component.aspect == ArchiMateAspect.ACTIVE_STRUCTURE
    
    def test_application_service_creation(self):
        """Test Application Service creation."""
        service = ApplicationElement.create_application_service(
            id="user_service",
            name="User Service",
            description="User management service"
        )
        
        assert service.element_type == "Service"
        assert service.layer == ArchiMateLayer.APPLICATION
        assert service.aspect == ArchiMateAspect.BEHAVIOR
    
    def test_data_object_creation(self):
        """Test Data Object creation."""
        data = ApplicationElement.create_data_object(
            id="user_data",
            name="User Database",
            description="User information storage"
        )
        
        assert data.element_type == "DataObject"
        assert data.layer == ArchiMateLayer.APPLICATION
        assert data.aspect == ArchiMateAspect.PASSIVE_STRUCTURE


class TestTechnologyElements:
    """Test Technology layer elements."""
    
    def test_node_creation(self):
        """Test Node creation."""
        node = TechnologyElement.create_node(
            id="app_server",
            name="Application Server",
            description="Main application server"
        )
        
        assert node.element_type == "Node"
        assert node.layer == ArchiMateLayer.TECHNOLOGY
        assert node.aspect == ArchiMateAspect.ACTIVE_STRUCTURE
    
    def test_device_creation(self):
        """Test Device creation."""
        device = TechnologyElement.create_device(
            id="database_server",
            name="Database Server",
            description="Database hardware"
        )
        
        assert device.element_type == "Device"
        assert device.layer == ArchiMateLayer.TECHNOLOGY
        assert device.aspect == ArchiMateAspect.ACTIVE_STRUCTURE
    
    def test_artifact_creation(self):
        """Test Artifact creation."""
        artifact = TechnologyElement.create_artifact(
            id="config_file",
            name="Configuration File",
            description="Application configuration"
        )
        
        assert artifact.element_type == "Artifact"
        assert artifact.layer == ArchiMateLayer.TECHNOLOGY
        assert artifact.aspect == ArchiMateAspect.PASSIVE_STRUCTURE


class TestPhysicalElements:
    """Test Physical layer elements."""
    
    def test_equipment_creation(self):
        """Test Equipment creation."""
        equipment = PhysicalElement.create_equipment(
            id="rack_server",
            name="Rack Server",
            description="Physical server hardware"
        )
        
        assert equipment.element_type == "Equipment"
        assert equipment.layer == ArchiMateLayer.PHYSICAL
        assert equipment.aspect == ArchiMateAspect.ACTIVE_STRUCTURE
    
    def test_facility_creation(self):
        """Test Facility creation."""
        facility = PhysicalElement.create_facility(
            id="data_center",
            name="Data Center",
            description="Primary data center facility"
        )
        
        assert facility.element_type == "Facility"
        assert facility.layer == ArchiMateLayer.PHYSICAL
        assert facility.aspect == ArchiMateAspect.ACTIVE_STRUCTURE


class TestMotivationElements:
    """Test Motivation layer elements."""
    
    def test_stakeholder_creation(self):
        """Test Stakeholder creation."""
        stakeholder = MotivationElement.create_stakeholder(
            id="business_owner",
            name="Business Owner",
            description="Product business owner"
        )
        
        assert stakeholder.element_type == "Stakeholder"
        assert stakeholder.layer == ArchiMateLayer.MOTIVATION
        assert stakeholder.aspect == ArchiMateAspect.ACTIVE_STRUCTURE
    
    def test_goal_creation(self):
        """Test Goal creation."""
        goal = MotivationElement.create_goal(
            id="improve_efficiency",
            name="Improve Efficiency",
            description="Increase operational efficiency"
        )
        
        assert goal.element_type == "Goal"
        assert goal.layer == ArchiMateLayer.MOTIVATION
        assert goal.aspect == ArchiMateAspect.BEHAVIOR
    
    def test_requirement_creation(self):
        """Test Requirement creation."""
        requirement = MotivationElement.create_requirement(
            id="performance_req",
            name="Performance Requirement",
            description="System performance requirements"
        )
        
        assert requirement.element_type == "Requirement"
        assert requirement.layer == ArchiMateLayer.MOTIVATION
        assert requirement.aspect == ArchiMateAspect.BEHAVIOR


class TestStrategyElements:
    """Test Strategy layer elements."""
    
    def test_capability_creation(self):
        """Test Capability creation."""
        capability = StrategyElement.create_capability(
            id="data_analytics",
            name="Data Analytics",
            description="Data analysis capability"
        )
        
        assert capability.element_type == "Capability"
        assert capability.layer == ArchiMateLayer.STRATEGY
        assert capability.aspect == ArchiMateAspect.BEHAVIOR
    
    def test_resource_creation(self):
        """Test Resource creation."""
        resource = StrategyElement.create_resource(
            id="dev_team",
            name="Development Team",
            description="Software development team"
        )
        
        assert resource.element_type == "Resource"
        assert resource.layer == ArchiMateLayer.STRATEGY
        assert resource.aspect == ArchiMateAspect.ACTIVE_STRUCTURE


class TestImplementationElements:
    """Test Implementation layer elements."""
    
    def test_work_package_creation(self):
        """Test Work Package creation."""
        work_package = ImplementationElement.create_work_package(
            id="migration_project",
            name="System Migration",
            description="Legacy system migration project"
        )
        
        assert work_package.element_type == "Work_Package"
        assert work_package.layer == ArchiMateLayer.IMPLEMENTATION
        assert work_package.aspect == ArchiMateAspect.BEHAVIOR
    
    def test_deliverable_creation(self):
        """Test Deliverable creation."""
        deliverable = ImplementationElement.create_deliverable(
            id="migration_plan",
            name="Migration Plan",
            description="Detailed migration plan document"
        )
        
        assert deliverable.element_type == "Deliverable"
        assert deliverable.layer == ArchiMateLayer.IMPLEMENTATION
        assert deliverable.aspect == ArchiMateAspect.PASSIVE_STRUCTURE


class TestElementRegistry:
    """Test element registry."""
    
    def test_element_registry_completeness(self):
        """Test that all element types are registered."""
        # Check that we have a reasonable number of elements
        assert len(ARCHIMATE_ELEMENTS) >= 55  # ArchiMate 3.2 has 55+ elements
        
        # Check some key elements are present
        assert "Business_Actor" in ARCHIMATE_ELEMENTS
        assert "Business_Service" in ARCHIMATE_ELEMENTS
        assert "Application_Component" in ARCHIMATE_ELEMENTS
        assert "Application_Service" in ARCHIMATE_ELEMENTS
        assert "Node" in ARCHIMATE_ELEMENTS
        assert "Technology_Service" in ARCHIMATE_ELEMENTS
        assert "Stakeholder" in ARCHIMATE_ELEMENTS
        assert "Goal" in ARCHIMATE_ELEMENTS
    
    def test_element_registry_types(self):
        """Test that registry contains correct element classes."""
        assert ARCHIMATE_ELEMENTS["Business_Actor"] == BusinessElement
        assert ARCHIMATE_ELEMENTS["Application_Component"] == ApplicationElement
        assert ARCHIMATE_ELEMENTS["Node"] == TechnologyElement
        assert ARCHIMATE_ELEMENTS["Equipment"] == PhysicalElement
        assert ARCHIMATE_ELEMENTS["Stakeholder"] == MotivationElement
        assert ARCHIMATE_ELEMENTS["Capability"] == StrategyElement
        assert ARCHIMATE_ELEMENTS["Work_Package"] == ImplementationElement