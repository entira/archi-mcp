"""Pytest configuration and fixtures for ArchiMate MCP tests."""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List

from archi_mcp.archimate.elements.base import ArchiMateElement, ArchiMateLayer, ArchiMateAspect
from archi_mcp.archimate.relationships import ArchiMateRelationship, RelationshipType
from archi_mcp.archimate.generator import ArchiMateGenerator
from archi_mcp.archimate.validator import ArchiMateValidator
from archi_mcp.server import mcp


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_business_element():
    """Create a sample business element for testing."""
    return ArchiMateElement(
        id="sample_business_service",
        name="Sample Business Service",
        element_type="Business_Service",
        layer=ArchiMateLayer.BUSINESS,
        aspect=ArchiMateAspect.BEHAVIOR,
        description="A sample business service for testing"
    )


@pytest.fixture
def sample_application_element():
    """Create a sample application element for testing."""
    return ArchiMateElement(
        id="sample_app_component",
        name="Sample Application Component",
        element_type="Application_Component",
        layer=ArchiMateLayer.APPLICATION,
        aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
        description="A sample application component for testing"
    )


@pytest.fixture
def sample_technology_element():
    """Create a sample technology element for testing."""
    return ArchiMateElement(
        id="sample_node",
        name="Sample Node",
        element_type="Node",
        layer=ArchiMateLayer.TECHNOLOGY,
        aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
        description="A sample technology node for testing"
    )


@pytest.fixture
def sample_elements(sample_business_element, sample_application_element, sample_technology_element):
    """Create a collection of sample elements."""
    return {
        sample_business_element.id: sample_business_element,
        sample_application_element.id: sample_application_element,
        sample_technology_element.id: sample_technology_element
    }


@pytest.fixture
def sample_relationship():
    """Create a sample relationship for testing."""
    return ArchiMateRelationship(
        id="sample_realization",
        from_element="sample_app_component",
        to_element="sample_business_service",
        relationship_type=RelationshipType.REALIZATION,
        description="Application component realizes business service"
    )


@pytest.fixture
def sample_relationships(sample_relationship):
    """Create a collection of sample relationships."""
    return [sample_relationship]


@pytest.fixture
def generator_with_sample_data(sample_elements, sample_relationships):
    """Create a generator with sample data loaded."""
    generator = ArchiMateGenerator()
    
    # Add elements
    for element in sample_elements.values():
        generator.add_element(element)
    
    # Add relationships
    for relationship in sample_relationships:
        generator.add_relationship(relationship)
    
    return generator


@pytest.fixture
def validator():
    """Create a validator instance."""
    return ArchiMateValidator()


@pytest.fixture
def strict_validator():
    """Create a strict validator instance."""
    return ArchiMateValidator(strict=True)


@pytest.fixture
def archi_server():
    """Create an ArchiMate MCP server instance."""
    return mcp


@pytest.fixture
def layered_architecture_elements():
    """Create elements for a layered architecture example."""
    return {
        "customer": ArchiMateElement(
            id="customer",
            name="Customer",
            element_type="Business_Actor",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE
        ),
        "order_service": ArchiMateElement(
            id="order_service",
            name="Order Service",
            element_type="Business_Service",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.BEHAVIOR
        ),
        "order_app": ArchiMateElement(
            id="order_app",
            name="Order Application",
            element_type="Application_Component",
            layer=ArchiMateLayer.APPLICATION,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE
        ),
        "order_data": ArchiMateElement(
            id="order_data",
            name="Order Database",
            element_type="Data_Object",
            layer=ArchiMateLayer.APPLICATION,
            aspect=ArchiMateAspect.PASSIVE_STRUCTURE
        ),
        "app_server": ArchiMateElement(
            id="app_server",
            name="Application Server",
            element_type="Node",
            layer=ArchiMateLayer.TECHNOLOGY,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE
        ),
        "db_server": ArchiMateElement(
            id="db_server",
            name="Database Server",
            element_type="Node",
            layer=ArchiMateLayer.TECHNOLOGY,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE
        )
    }


@pytest.fixture
def layered_architecture_relationships():
    """Create relationships for a layered architecture example."""
    return [
        ArchiMateRelationship(
            id="customer_uses_service",
            from_element="customer",
            to_element="order_service",
            relationship_type=RelationshipType.SERVING
        ),
        ArchiMateRelationship(
            id="app_realizes_service",
            from_element="order_app",
            to_element="order_service",
            relationship_type=RelationshipType.REALIZATION
        ),
        ArchiMateRelationship(
            id="app_accesses_data",
            from_element="order_app",
            to_element="order_data",
            relationship_type=RelationshipType.ACCESS
        ),
        ArchiMateRelationship(
            id="app_deployed_on_server",
            from_element="app_server",
            to_element="order_app",
            relationship_type=RelationshipType.ASSIGNMENT
        ),
        ArchiMateRelationship(
            id="data_deployed_on_db",
            from_element="db_server",
            to_element="order_data",
            relationship_type=RelationshipType.ASSIGNMENT
        )
    ]


@pytest.fixture
def complete_layered_architecture(layered_architecture_elements, layered_architecture_relationships):
    """Create a complete layered architecture example."""
    generator = ArchiMateGenerator()
    
    # Add elements
    for element in layered_architecture_elements.values():
        generator.add_element(element)
    
    # Add relationships
    for relationship in layered_architecture_relationships:
        generator.add_relationship(relationship)
    
    return generator


# Utility functions for tests
def assert_plantuml_valid(plantuml_code: str):
    """Assert that PlantUML code has basic valid structure."""
    assert "@startuml" in plantuml_code
    assert "@enduml" in plantuml_code
    assert "!include <archimate/Archimate>" in plantuml_code


def assert_element_in_plantuml(plantuml_code: str, element: ArchiMateElement):
    """Assert that an element is properly represented in PlantUML code."""
    element_code = element.to_plantuml()
    assert element_code in plantuml_code


def assert_relationship_in_plantuml(plantuml_code: str, relationship: ArchiMateRelationship):
    """Assert that a relationship is properly represented in PlantUML code."""
    relationship_code = relationship.to_plantuml()
    assert relationship_code in plantuml_code


# Make utility functions available to tests
pytest.assert_plantuml_valid = assert_plantuml_valid
pytest.assert_element_in_plantuml = assert_element_in_plantuml
pytest.assert_relationship_in_plantuml = assert_relationship_in_plantuml