"""ArchiMate XML Exchange Format Templates

Provides XML templates and examples for ArchiMate Exchange format.
Helps with understanding the expected XML structure.
"""

from typing import Dict, Any


class XMLTemplates:
    """
    ArchiMate XML Exchange Format Templates
    
    Provides example XML structures and templates for reference.
    """
    
    @staticmethod
    def get_minimal_model_template() -> str:
        """
        Get minimal ArchiMate XML model template.
        
        Returns:
            Minimal valid ArchiMate XML model string
        """
        return '''<?xml version="1.0" encoding="UTF-8"?>
<model xmlns="http://www.opengroup.org/xsd/archimate/3.0/"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.opengroup.org/xsd/archimate/3.0/ http://www.opengroup.org/xsd/archimate/3.0/archimate3_Model.xsd"
       identifier="model-minimal">
    
    <name>Minimal ArchiMate Model</name>
    
    <metadata>
        <schema>3.0</schema>
        <created>2025-07-05T00:00:00</created>
        <creator>ArchiMate MCP Server</creator>
        <version>1.0</version>
    </metadata>
    
    <elements>
        <!-- Elements will be added here -->
    </elements>
    
    <relationships>
        <!-- Relationships will be added here -->
    </relationships>
    
</model>'''
    
    @staticmethod 
    def get_sample_business_model() -> str:
        """
        Get sample business model with basic elements and relationships.
        
        Returns:
            Sample ArchiMate XML with business elements
        """
        return '''<?xml version="1.0" encoding="UTF-8"?>
<model xmlns="http://www.opengroup.org/xsd/archimate/3.0/"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.opengroup.org/xsd/archimate/3.0/ http://www.opengroup.org/xsd/archimate/3.0/archimate3_Model.xsd"
       identifier="model-business-sample">
    
    <name>Sample Business Model</name>
    
    <metadata>
        <schema>3.0</schema>
        <created>2025-07-05T00:00:00</created>
        <creator>ArchiMate MCP Server</creator>
        <version>1.0</version>
    </metadata>
    
    <elements>
        <element identifier="customer" xsi:type="BusinessActor">
            <name>Customer</name>
            <documentation>External customer actor</documentation>
        </element>
        
        <element identifier="order-process" xsi:type="BusinessProcess">
            <name>Order Management Process</name>
            <documentation>Main business process for handling orders</documentation>
        </element>
        
        <element identifier="order-service" xsi:type="BusinessService">
            <name>Order Service</name>
            <documentation>Service provided to customers for placing orders</documentation>
        </element>
    </elements>
    
    <relationships>
        <relationship identifier="rel-1" xsi:type="ServingRelationship" 
                     source="order-service" target="customer">
            <name>serves</name>
        </relationship>
        
        <relationship identifier="rel-2" xsi:type="RealizationRelationship"
                     source="order-process" target="order-service">
            <name>realizes</name>
        </relationship>
    </relationships>
    
</model>'''
    
    @staticmethod
    def get_element_template(element_type: str) -> str:
        """
        Get XML template for specific element type.
        
        Args:
            element_type: ArchiMate element type
            
        Returns:
            XML template string for the element
        """
        return f'''<element identifier="element-id" xsi:type="{element_type}">
    <name>Element Name</name>
    <documentation>Element description</documentation>
    <properties>
        <property propertyDefinitionRef="custom-property">
            <value>Custom Value</value>
        </property>
    </properties>
</element>'''
    
    @staticmethod
    def get_relationship_template(relationship_type: str) -> str:
        """
        Get XML template for specific relationship type.
        
        Args:
            relationship_type: ArchiMate relationship type
            
        Returns:
            XML template string for the relationship
        """
        return f'''<relationship identifier="rel-id" xsi:type="{relationship_type}Relationship"
             source="source-element-id" target="target-element-id">
    <name>Relationship Label</name>
    <documentation>Relationship description</documentation>
</relationship>'''
    
    @staticmethod
    def get_supported_element_types() -> Dict[str, list]:
        """
        Get supported ArchiMate element types by layer.
        
        Returns:
            Dictionary mapping layers to element types
        """
        return {
            "Business": [
                "BusinessActor", "BusinessRole", "BusinessCollaboration", 
                "BusinessInterface", "BusinessFunction", "BusinessProcess",
                "BusinessEvent", "BusinessService", "BusinessObject",
                "Contract", "Representation", "Location"
            ],
            "Application": [
                "ApplicationComponent", "ApplicationCollaboration", 
                "ApplicationInterface", "ApplicationFunction", 
                "ApplicationInteraction", "ApplicationProcess",
                "ApplicationEvent", "ApplicationService", "DataObject"
            ],
            "Technology": [
                "Node", "Device", "SystemSoftware", "TechnologyCollaboration",
                "TechnologyInterface", "Path", "CommunicationNetwork",
                "TechnologyFunction", "TechnologyProcess", "TechnologyInteraction",
                "TechnologyEvent", "TechnologyService", "Artifact"
            ],
            "Physical": [
                "Equipment", "Facility", "DistributionNetwork", "Material"
            ],
            "Motivation": [
                "Stakeholder", "Driver", "Assessment", "Goal", "Outcome",
                "Principle", "Requirement", "Constraint", "Meaning", "Value"
            ],
            "Strategy": [
                "Resource", "Capability", "CourseOfAction", "ValueStream"
            ],
            "Implementation": [
                "WorkPackage", "Deliverable", "ImplementationEvent", 
                "Plateau", "Gap"
            ]
        }
    
    @staticmethod
    def get_supported_relationship_types() -> list:
        """
        Get supported ArchiMate relationship types.
        
        Returns:
            List of relationship type names
        """
        return [
            "AccessRelationship", "AggregationRelationship", "AssignmentRelationship",
            "AssociationRelationship", "CompositionRelationship", "FlowRelationship",
            "InfluenceRelationship", "RealizationRelationship", "ServingRelationship",
            "SpecializationRelationship", "TriggeringRelationship"
        ]