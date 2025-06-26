"""ArchiMate viewpoint templates."""

from typing import Dict, List, Any, Optional
from ..archimate.elements import ArchiMateElement
from ..archimate.relationships import ArchiMateRelationship


class ViewpointTemplate:
    """Template for ArchiMate viewpoints."""
    
    def __init__(
        self,
        name: str,
        description: str,
        elements: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        layout: Dict[str, Any] = None
    ):
        self.name = name
        self.description = description
        self.elements = elements
        self.relationships = relationships
        self.layout = layout or {}


# ArchiMate viewpoint templates
ARCHIMATE_VIEWPOINTS = {
    "layered": ViewpointTemplate(
        name="Layered Viewpoint",
        description="Shows the layers and their relationships in enterprise architecture",
        elements=[
            {
                "id": "business_service",
                "name": "Business Service",
                "element_type": "Business_Service",
                "layer": "Business"
            },
            {
                "id": "application_service", 
                "name": "Application Service",
                "element_type": "Application_Service",
                "layer": "Application"
            },
            {
                "id": "technology_service",
                "name": "Technology Service", 
                "element_type": "Technology_Service",
                "layer": "Technology"
            }
        ],
        relationships=[
            {
                "id": "app_realizes_business",
                "from_element": "application_service",
                "to_element": "business_service",
                "relationship_type": "Realization"
            },
            {
                "id": "tech_realizes_app",
                "from_element": "technology_service",
                "to_element": "application_service", 
                "relationship_type": "Realization"
            }
        ],
        layout={"direction": "vertical", "group_by_layer": True}
    ),
    
    "service_realization": ViewpointTemplate(
        name="Service Realization Viewpoint",
        description="Shows how services are realized by underlying components",
        elements=[
            {
                "id": "business_actor",
                "name": "Business Actor",
                "element_type": "Business_Actor",
                "layer": "Business"
            },
            {
                "id": "business_service",
                "name": "Business Service",
                "element_type": "Business_Service", 
                "layer": "Business"
            },
            {
                "id": "application_component",
                "name": "Application Component",
                "element_type": "Application_Component",
                "layer": "Application"
            },
            {
                "id": "application_service",
                "name": "Application Service",
                "element_type": "Application_Service",
                "layer": "Application"
            }
        ],
        relationships=[
            {
                "id": "actor_uses_service",
                "from_element": "business_actor",
                "to_element": "business_service",
                "relationship_type": "Serving"
            },
            {
                "id": "app_realizes_business",
                "from_element": "application_service",
                "to_element": "business_service",
                "relationship_type": "Realization"
            },
            {
                "id": "component_provides_service",
                "from_element": "application_component",
                "to_element": "application_service",
                "relationship_type": "Assignment"
            }
        ]
    ),
    
    "application_cooperation": ViewpointTemplate(
        name="Application Cooperation Viewpoint",
        description="Shows application components and their interactions",
        elements=[
            {
                "id": "app_component_1",
                "name": "Application Component A",
                "element_type": "Application_Component",
                "layer": "Application"
            },
            {
                "id": "app_component_2", 
                "name": "Application Component B",
                "element_type": "Application_Component",
                "layer": "Application"
            },
            {
                "id": "app_interface_1",
                "name": "Interface A",
                "element_type": "Application_Interface",
                "layer": "Application"
            },
            {
                "id": "app_interface_2",
                "name": "Interface B", 
                "element_type": "Application_Interface",
                "layer": "Application"
            },
            {
                "id": "data_object",
                "name": "Shared Data",
                "element_type": "Data_Object",
                "layer": "Application"
            }
        ],
        relationships=[
            {
                "id": "comp_a_interface",
                "from_element": "app_component_1",
                "to_element": "app_interface_1",
                "relationship_type": "Composition"
            },
            {
                "id": "comp_b_interface",
                "from_element": "app_component_2", 
                "to_element": "app_interface_2",
                "relationship_type": "Composition"
            },
            {
                "id": "interface_flow",
                "from_element": "app_interface_1",
                "to_element": "app_interface_2",
                "relationship_type": "Flow"
            },
            {
                "id": "comp_a_data",
                "from_element": "app_component_1",
                "to_element": "data_object",
                "relationship_type": "Access"
            },
            {
                "id": "comp_b_data",
                "from_element": "app_component_2",
                "to_element": "data_object", 
                "relationship_type": "Access"
            }
        ]
    ),
    
    "technology_usage": ViewpointTemplate(
        name="Technology Usage Viewpoint",
        description="Shows technology infrastructure and its usage",
        elements=[
            {
                "id": "node_1",
                "name": "Application Server",
                "element_type": "Node",
                "layer": "Technology"
            },
            {
                "id": "node_2",
                "name": "Database Server",
                "element_type": "Node", 
                "layer": "Technology"
            },
            {
                "id": "system_software_1",
                "name": "Application Runtime",
                "element_type": "System_Software",
                "layer": "Technology"
            },
            {
                "id": "system_software_2",
                "name": "Database System",
                "element_type": "System_Software",
                "layer": "Technology"
            },
            {
                "id": "communication_network",
                "name": "Network",
                "element_type": "Communication_Network",
                "layer": "Technology"
            }
        ],
        relationships=[
            {
                "id": "node1_software1",
                "from_element": "node_1",
                "to_element": "system_software_1",
                "relationship_type": "Assignment"
            },
            {
                "id": "node2_software2",
                "from_element": "node_2",
                "to_element": "system_software_2",
                "relationship_type": "Assignment"
            },
            {
                "id": "nodes_network",
                "from_element": "node_1",
                "to_element": "communication_network",
                "relationship_type": "Access"
            },
            {
                "id": "network_node2",
                "from_element": "communication_network",
                "to_element": "node_2",
                "relationship_type": "Access"
            }
        ]
    ),
    
    "motivation": ViewpointTemplate(
        name="Motivation Viewpoint",
        description="Shows stakeholders, drivers, goals and requirements",
        elements=[
            {
                "id": "stakeholder_1",
                "name": "Business Stakeholder",
                "element_type": "Stakeholder",
                "layer": "Motivation"
            },
            {
                "id": "driver_1",
                "name": "Business Driver",
                "element_type": "Driver",
                "layer": "Motivation"
            },
            {
                "id": "goal_1",
                "name": "Strategic Goal",
                "element_type": "Goal",
                "layer": "Motivation"
            },
            {
                "id": "requirement_1",
                "name": "Business Requirement",
                "element_type": "Requirement",
                "layer": "Motivation"
            },
            {
                "id": "principle_1",
                "name": "Architecture Principle",
                "element_type": "Principle",
                "layer": "Motivation"
            }
        ],
        relationships=[
            {
                "id": "stakeholder_driver",
                "from_element": "stakeholder_1",
                "to_element": "driver_1",
                "relationship_type": "Association"
            },
            {
                "id": "driver_goal",
                "from_element": "driver_1",
                "to_element": "goal_1",
                "relationship_type": "Influence"
            },
            {
                "id": "goal_requirement",
                "from_element": "goal_1",
                "to_element": "requirement_1",
                "relationship_type": "Realization"
            },
            {
                "id": "principle_requirement",
                "from_element": "principle_1",
                "to_element": "requirement_1",
                "relationship_type": "Influence"
            }
        ]
    )
}


def get_viewpoint_template(viewpoint_name: str) -> Optional[ViewpointTemplate]:
    """Get viewpoint template by name.
    
    Args:
        viewpoint_name: Name of the viewpoint
        
    Returns:
        ViewpointTemplate if found, None otherwise
    """
    return ARCHIMATE_VIEWPOINTS.get(viewpoint_name)


def list_available_viewpoints() -> List[str]:
    """Get list of available viewpoint names.
    
    Returns:
        List of viewpoint names
    """
    return list(ARCHIMATE_VIEWPOINTS.keys())