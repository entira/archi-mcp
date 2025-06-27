"""Architecture pattern templates."""

from typing import Dict, List, Any, Optional
from .viewpoints import ViewpointTemplate


class PatternTemplate:
    """Template for architecture patterns."""
    
    def __init__(
        self,
        name: str,
        description: str,
        elements: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        layout: Dict[str, Any] = None,
        pattern_type: str = "general"
    ):
        self.name = name
        self.description = description
        self.elements = elements
        self.relationships = relationships
        self.layout = layout or {}
        self.pattern_type = pattern_type


# Architecture pattern templates
ARCHITECTURE_PATTERNS = {
    "three_tier": PatternTemplate(
        name="Three-Tier Architecture",
        description="Classic three-tier architecture pattern with presentation, business logic, and data layers",
        elements=[
            {
                "id": "presentation_layer",
                "name": "Presentation Layer",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "User interface components"
            },
            {
                "id": "business_logic_layer",
                "name": "Business Logic Layer",
                "element_type": "Application_Component", 
                "layer": "Application",
                "description": "Business rules and processing"
            },
            {
                "id": "data_access_layer",
                "name": "Data Access Layer",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Data persistence and access"
            },
            {
                "id": "database",
                "name": "Database",
                "element_type": "Technology_Node",
                "layer": "Technology",
                "description": "Data storage system"
            }
        ],
        relationships=[
            {
                "id": "presentation_to_business",
                "from_element": "presentation_layer",
                "to_element": "business_logic_layer",
                "relationship_type": "Flow"
            },
            {
                "id": "business_to_data",
                "from_element": "business_logic_layer",
                "to_element": "data_access_layer",
                "relationship_type": "Flow"
            },
            {
                "id": "data_to_database",
                "from_element": "data_access_layer",
                "to_element": "database",
                "relationship_type": "Access"
            }
        ],
        layout={"direction": "vertical", "group_by_layer": True}
    ),
    
    "three_tier_architecture": PatternTemplate(
        name="Three-Tier Architecture",
        description="Classic three-tier architecture pattern with presentation, business logic, and data layers",
        elements=[
            {
                "id": "presentation_layer",
                "name": "Presentation Layer",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "User interface components"
            },
            {
                "id": "business_logic_layer",
                "name": "Business Logic Layer",
                "element_type": "Application_Component", 
                "layer": "Application",
                "description": "Business rules and processing"
            },
            {
                "id": "data_access_layer",
                "name": "Data Access Layer",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Data persistence and access"
            },
            {
                "id": "database",
                "name": "Database",
                "element_type": "Data_Object",
                "layer": "Application",
                "description": "Persistent data storage"
            }
        ],
        relationships=[
            {
                "id": "pres_to_business",
                "from_element": "presentation_layer",
                "to_element": "business_logic_layer",
                "relationship_type": "Serving",
                "direction": "Down"
            },
            {
                "id": "business_to_data",
                "from_element": "business_logic_layer",
                "to_element": "data_access_layer",
                "relationship_type": "Serving",
                "direction": "Down"
            },
            {
                "id": "data_access_db",
                "from_element": "data_access_layer",
                "to_element": "database",
                "relationship_type": "Access"
            }
        ],
        layout={"direction": "vertical", "spacing": "wide"},
        pattern_type="architectural"
    ),
    
    "microservices": PatternTemplate(
        name="Microservices Architecture",
        description="Microservices pattern with independent services and API gateway",
        elements=[
            {
                "id": "api_gateway",
                "name": "API Gateway",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Single entry point for client requests"
            },
            {
                "id": "service_a",
                "name": "User Service",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "User management microservice"
            },
            {
                "id": "service_b",
                "name": "Order Service",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Order processing microservice"
            },
            {
                "id": "service_c",
                "name": "Payment Service",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Payment processing microservice"
            },
            {
                "id": "service_discovery",
                "name": "Service Discovery",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Service registry and discovery"
            },
            {
                "id": "message_queue",
                "name": "Message Queue",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Asynchronous communication"
            }
        ],
        relationships=[
            {
                "id": "gateway_user_service",
                "from_element": "api_gateway",
                "to_element": "service_a",
                "relationship_type": "Serving"
            },
            {
                "id": "gateway_order_service",
                "from_element": "api_gateway",
                "to_element": "service_b",
                "relationship_type": "Serving"
            },
            {
                "id": "gateway_payment_service",
                "from_element": "api_gateway",
                "to_element": "service_c",
                "relationship_type": "Serving"
            },
            {
                "id": "services_discovery",
                "from_element": "service_a",
                "to_element": "service_discovery",
                "relationship_type": "Access"
            },
            {
                "id": "order_payment_async",
                "from_element": "service_b",
                "to_element": "message_queue",
                "relationship_type": "Flow"
            },
            {
                "id": "payment_from_queue",
                "from_element": "message_queue",
                "to_element": "service_c",
                "relationship_type": "Flow"
            }
        ],
        layout={"direction": "horizontal", "spacing": "wide"},
        pattern_type="architectural"
    ),
    
    "event_driven": PatternTemplate(
        name="Event-Driven Architecture",
        description="Event-driven architecture with producers, consumers, and event bus",
        elements=[
            {
                "id": "event_producer",
                "name": "Event Producer",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Generates business events"
            },
            {
                "id": "event_bus",
                "name": "Event Bus",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Event routing and distribution"
            },
            {
                "id": "event_consumer_1",
                "name": "Event Consumer A",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Processes specific event types"
            },
            {
                "id": "event_consumer_2",
                "name": "Event Consumer B",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Processes different event types"
            },
            {
                "id": "event_store",
                "name": "Event Store",
                "element_type": "Data_Object",
                "layer": "Application",
                "description": "Persistent event storage"
            }
        ],
        relationships=[
            {
                "id": "producer_to_bus",
                "from_element": "event_producer",
                "to_element": "event_bus",
                "relationship_type": "Flow"
            },
            {
                "id": "bus_to_consumer_1",
                "from_element": "event_bus",
                "to_element": "event_consumer_1",
                "relationship_type": "Flow"
            },
            {
                "id": "bus_to_consumer_2",
                "from_element": "event_bus",
                "to_element": "event_consumer_2",
                "relationship_type": "Flow"
            },
            {
                "id": "bus_to_store",
                "from_element": "event_bus",
                "to_element": "event_store",
                "relationship_type": "Access"
            }
        ],
        layout={"direction": "horizontal", "spacing": "normal"},
        pattern_type="architectural"
    ),
    
    "layered_service": PatternTemplate(
        name="Layered Service Architecture",
        description="Service-oriented layered architecture with clear separation of concerns",
        elements=[
            {
                "id": "ui_layer",
                "name": "User Interface",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "User interface components"
            },
            {
                "id": "service_layer",
                "name": "Service Layer",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Business services and APIs"
            },
            {
                "id": "domain_layer",
                "name": "Domain Layer",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Business logic and domain objects"
            },
            {
                "id": "infrastructure_layer",
                "name": "Infrastructure Layer",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Technical infrastructure services"
            },
            {
                "id": "external_service",
                "name": "External Service",
                "element_type": "Application_Service",
                "layer": "Application",
                "description": "Third-party services"
            }
        ],
        relationships=[
            {
                "id": "ui_to_service",
                "from_element": "ui_layer",
                "to_element": "service_layer",
                "relationship_type": "Serving",
                "direction": "Down"
            },
            {
                "id": "service_to_domain",
                "from_element": "service_layer",
                "to_element": "domain_layer",
                "relationship_type": "Serving",
                "direction": "Down"
            },
            {
                "id": "domain_to_infrastructure",
                "from_element": "domain_layer",
                "to_element": "infrastructure_layer",
                "relationship_type": "Serving",
                "direction": "Down"
            },
            {
                "id": "infrastructure_external",
                "from_element": "infrastructure_layer",
                "to_element": "external_service",
                "relationship_type": "Serving"
            }
        ],
        layout={"direction": "vertical", "group_by_layer": False},
        pattern_type="architectural"
    ),
    
    "cqrs": PatternTemplate(
        name="CQRS Pattern",
        description="Command Query Responsibility Segregation pattern",
        elements=[
            {
                "id": "command_api",
                "name": "Command API",
                "element_type": "Application_Interface",
                "layer": "Application",
                "description": "Handles write operations"
            },
            {
                "id": "query_api",
                "name": "Query API",
                "element_type": "Application_Interface",
                "layer": "Application",
                "description": "Handles read operations"
            },
            {
                "id": "write_model",
                "name": "Write Model",
                "element_type": "Data_Object",
                "layer": "Application",
                "description": "Optimized for writes"
            },
            {
                "id": "read_model",
                "name": "Read Model",
                "element_type": "Data_Object",
                "layer": "Application",
                "description": "Optimized for reads"
            },
            {
                "id": "event_store_cqrs",
                "name": "Event Store",
                "element_type": "Data_Object",
                "layer": "Application",
                "description": "Event sourcing store"
            },
            {
                "id": "projection_service",
                "name": "Projection Service",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Updates read models from events"
            }
        ],
        relationships=[
            {
                "id": "command_write",
                "from_element": "command_api",
                "to_element": "write_model",
                "relationship_type": "Access"
            },
            {
                "id": "query_read",
                "from_element": "query_api",
                "to_element": "read_model",
                "relationship_type": "Access"
            },
            {
                "id": "write_events",
                "from_element": "write_model",
                "to_element": "event_store_cqrs",
                "relationship_type": "Flow"
            },
            {
                "id": "projection_events",
                "from_element": "event_store_cqrs",
                "to_element": "projection_service",
                "relationship_type": "Flow"
            },
            {
                "id": "projection_read",
                "from_element": "projection_service",
                "to_element": "read_model",
                "relationship_type": "Access"
            }
        ],
        layout={"direction": "horizontal", "spacing": "wide"},
        pattern_type="architectural"
    )
}


def get_pattern_template(pattern_name: str) -> Optional[PatternTemplate]:
    """Get pattern template by name.
    
    Args:
        pattern_name: Name of the pattern
        
    Returns:
        PatternTemplate if found, None otherwise
    """
    return ARCHITECTURE_PATTERNS.get(pattern_name)


def list_available_patterns() -> List[str]:
    """Get list of available pattern names.
    
    Returns:
        List of pattern names
    """
    return list(ARCHITECTURE_PATTERNS.keys())


def get_patterns_by_type(pattern_type: str) -> List[str]:
    """Get patterns by type.
    
    Args:
        pattern_type: Type of pattern to filter by
        
    Returns:
        List of pattern names matching the type
    """
    return [
        name for name, pattern in ARCHITECTURE_PATTERNS.items()
        if pattern.pattern_type == pattern_type
    ]