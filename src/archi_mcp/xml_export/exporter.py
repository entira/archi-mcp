"""ArchiMate XML Exchange Format Exporter

Exports ArchiMate models to Open Group XML Exchange format.
Supports ArchiMate 3.2 elements using 3.0 XML schema namespace for backward compatibility.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

try:
    from lxml import etree
    LXML_AVAILABLE = True
except ImportError:
    import xml.etree.ElementTree as etree
    LXML_AVAILABLE = False

from ..archimate import ArchiMateElement, ArchiMateRelationship
from ..archimate.elements.base import ArchiMateLayer, ArchiMateAspect

logger = logging.getLogger(__name__)


class ArchiMateXMLExporter:
    """
    ArchiMate XML Exchange Format Exporter
    
    Exports ArchiMate models to Open Group XML Exchange format.
    This is a modular component that can be easily removed or relocated.
    """
    
    # Archi tool namespace for compatibility with Archi import
    ARCHIMATE_NAMESPACE = "http://www.archimatetool.com/archimate"
    XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
    
    def __init__(self):
        """Initialize the ArchiMate XML exporter."""
        self.nsmap = {
            None: self.ARCHIMATE_NAMESPACE,
            'xsi': self.XSI_NAMESPACE
        }
        
    def export_to_xml(
        self,
        elements: List[ArchiMateElement],
        relationships: List[ArchiMateRelationship],
        model_name: str = "ArchiMate Model",
        model_id: Optional[str] = None,
        output_path: Optional[Path] = None
    ) -> str:
        """
        Export ArchiMate model to XML Exchange format.
        
        Args:
            elements: List of ArchiMate elements
            relationships: List of ArchiMate relationships
            model_name: Name of the model
            model_id: Optional model ID (generated if not provided)
            output_path: Optional file path to save XML
            
        Returns:
            XML string in ArchiMate Exchange format
            
        Raises:
            Exception: If XML generation fails
        """
        try:
            logger.info(f"Starting XML export for {len(elements)} elements, {len(relationships)} relationships")
            
            # Generate model ID if not provided
            if not model_id:
                model_id = f"id-{uuid.uuid4()}"
            
            # Create root element with Archi namespace structure
            if LXML_AVAILABLE:
                nsmap = {
                    'xsi': self.XSI_NAMESPACE,
                    'archimate': self.ARCHIMATE_NAMESPACE
                }
                root = etree.Element(f"{{{self.ARCHIMATE_NAMESPACE}}}model", nsmap=nsmap)
            else:
                # Register namespaces for ElementTree
                etree.register_namespace('archimate', self.ARCHIMATE_NAMESPACE)
                etree.register_namespace('xsi', self.XSI_NAMESPACE)
                root = etree.Element(f"{{{self.ARCHIMATE_NAMESPACE}}}model")
            
            # Set root attributes
            root.set("name", model_name)
            root.set("id", model_id)
            root.set("version", "4.9.0")  # Archi version
            
            # Add folders and elements using Archi structure
            self._add_archi_folders_and_elements(root, elements)
            
            # Add relationships folder
            self._add_archi_relationships(root, relationships)
            
            # Add Views folder with diagrams
            self._add_archi_views(root, elements, relationships, model_name)
            
            # Convert to string (single line format like Archi)
            if LXML_AVAILABLE:
                xml_string = etree.tostring(
                    root, 
                    pretty_print=False,  # No pretty printing for Archi compatibility
                    xml_declaration=False, 
                    encoding='UTF-8'
                ).decode('utf-8')
                xml_string = '<?xml version="1.0" encoding="UTF-8"?>' + xml_string
            else:
                xml_string = etree.tostring(root, encoding='unicode')
                xml_string = '<?xml version="1.0" encoding="UTF-8"?>' + xml_string
            
            # Save to file if path provided
            if output_path:
                if isinstance(output_path, str):
                    output_path = Path(output_path)
                output_path.write_text(xml_string, encoding='utf-8')
                logger.info(f"XML exported to {output_path}")
            
            logger.info("XML export completed successfully")
            return xml_string
            
        except Exception as e:
            logger.error(f"XML export failed: {e}")
            raise
    
    
    def _get_xml_element_type(self, element_type: str) -> str:
        """
        Convert internal element type to XML schema type.
        
        ArchiMate 3.2 element types are exported using ArchiMate 3.0 XML schema.
        This maintains backward compatibility while supporting newer elements.
        """
        # Map internal types to XML schema types
        type_mappings = {
            # Business Layer
            "Business_Actor": "BusinessActor",
            "Business_Role": "BusinessRole", 
            "Business_Collaboration": "BusinessCollaboration",
            "Business_Interface": "BusinessInterface",
            "Business_Function": "BusinessFunction",
            "Business_Process": "BusinessProcess",
            "Business_Event": "BusinessEvent",
            "Business_Service": "BusinessService",
            "Business_Object": "BusinessObject",
            "Business_Contract": "Contract",
            "Business_Representation": "Representation",
            "Location": "Location",
            
            # Application Layer
            "Application_Component": "ApplicationComponent",
            "Application_Collaboration": "ApplicationCollaboration",
            "Application_Interface": "ApplicationInterface", 
            "Application_Function": "ApplicationFunction",
            "Application_Interaction": "ApplicationInteraction",
            "Application_Process": "ApplicationProcess",
            "Application_Event": "ApplicationEvent",
            "Application_Service": "ApplicationService",
            "Data_Object": "DataObject",
            
            # Technology Layer
            "Node": "Node",
            "Device": "Device",
            "System_Software": "SystemSoftware",
            "Technology_Collaboration": "TechnologyCollaboration",
            "Technology_Interface": "TechnologyInterface",
            "Path": "Path",
            "Communication_Network": "CommunicationNetwork",
            "Technology_Function": "TechnologyFunction",
            "Technology_Process": "TechnologyProcess",
            "Technology_Interaction": "TechnologyInteraction", 
            "Technology_Event": "TechnologyEvent",
            "Technology_Service": "TechnologyService",
            "Artifact": "Artifact",
            
            # Physical Layer
            "Equipment": "Equipment",
            "Facility": "Facility", 
            "Distribution_Network": "DistributionNetwork",
            "Material": "Material",
            
            # Motivation Layer
            "Stakeholder": "Stakeholder",
            "Driver": "Driver",
            "Assessment": "Assessment",
            "Goal": "Goal",
            "Outcome": "Outcome", 
            "Principle": "Principle",
            "Requirement": "Requirement",
            "Constraint": "Constraint",
            "Meaning": "Meaning",
            "Value": "Value",
            
            # Strategy Layer
            "Resource": "Resource",
            "Capability": "Capability",
            "Course_of_Action": "CourseOfAction",
            "Value_Stream": "ValueStream",
            
            # Implementation Layer
            "Work_Package": "WorkPackage",
            "Deliverable": "Deliverable",
            "Implementation_Event": "ImplementationEvent",
            "Plateau": "Plateau",
            "Gap": "Gap"
        }
        
        return type_mappings.get(element_type, element_type)
    
    def _get_xml_relationship_type(self, relationship_type: str) -> str:
        """Convert internal relationship type to XML schema type."""
        # ArchiMate relationship types are typically the same
        type_mappings = {
            "Access": "AccessRelationship",
            "Aggregation": "AggregationRelationship", 
            "Assignment": "AssignmentRelationship",
            "Association": "AssociationRelationship",
            "Composition": "CompositionRelationship",
            "Flow": "FlowRelationship",
            "Influence": "InfluenceRelationship",
            "Realization": "RealizationRelationship",
            "Serving": "ServingRelationship",
            "Specialization": "SpecializationRelationship",
            "Triggering": "TriggeringRelationship"
        }
        
        return type_mappings.get(relationship_type, f"{relationship_type}Relationship")
    
    def _add_archi_folders_and_elements(self, root, elements: List[ArchiMateElement]):
        """Add folders and elements using Archi's structure."""
        # Group elements by layer
        elements_by_layer = {}
        for element in elements:
            layer = element.layer.value if hasattr(element.layer, 'value') else str(element.layer)
            if layer not in elements_by_layer:
                elements_by_layer[layer] = []
            elements_by_layer[layer].append(element)
        
        # Create folders for each layer
        layer_folders = {
            "Strategy": "strategy",
            "Business": "business", 
            "Application": "application",
            "Technology": "technology",
            "Physical": "technology",  # Physical elements often go in technology folder
            "Motivation": "motivation",
            "Implementation": "implementation_migration"
        }
        
        # Add folders in order
        for layer_name, folder_type in layer_folders.items():
            folder = etree.SubElement(root, "folder")
            folder.set("name", layer_name)
            folder.set("id", f"id-{uuid.uuid4()}")
            folder.set("type", folder_type)
            
            # Add elements to folder if they exist for this layer
            if layer_name in elements_by_layer:
                for element in elements_by_layer[layer_name]:
                    self._add_archi_element(folder, element)
        
        # Add empty "Other" folder
        other_folder = etree.SubElement(root, "folder")
        other_folder.set("name", "Other")
        other_folder.set("id", f"id-{uuid.uuid4()}")
        other_folder.set("type", "other")
    
    def _add_archi_element(self, parent, element: ArchiMateElement):
        """Add element in Archi format."""
        elem = etree.SubElement(parent, "element")
        
        # Set element type with archimate namespace
        element_type = self._get_xml_element_type(element.element_type)
        elem.set(f"{{{self.XSI_NAMESPACE}}}type", f"archimate:{element_type}")
        
        # Set attributes
        elem.set("id", element.id)
        elem.set("name", element.name)
        
        # Add documentation as property
        if element.description:
            prop = etree.SubElement(elem, "property")
            prop.set("key", "documentation")
            prop.set("value", element.description)
        
        # Add custom properties
        if hasattr(element, 'properties') and element.properties:
            for key, value in element.properties.items():
                prop = etree.SubElement(elem, "property")
                prop.set("key", key)
                prop.set("value", str(value))
    
    def _add_archi_relationships(self, root, relationships: List[ArchiMateRelationship]):
        """Add relationships folder in Archi format."""
        relations_folder = etree.SubElement(root, "folder")
        relations_folder.set("name", "Relations")
        relations_folder.set("id", f"id-{uuid.uuid4()}")
        relations_folder.set("type", "relations")
        
        for relationship in relationships:
            elem = etree.SubElement(relations_folder, "element")
            
            # Set relationship type with archimate namespace
            rel_type = self._get_xml_relationship_type(relationship.relationship_type)
            elem.set(f"{{{self.XSI_NAMESPACE}}}type", f"archimate:{rel_type}")
            
            # Set attributes
            elem.set("id", relationship.id)
            elem.set("source", relationship.from_element)
            elem.set("target", relationship.to_element)
            
            # Add label and description if available
            if hasattr(relationship, 'label') and relationship.label:
                elem.set("name", relationship.label)
            
            if hasattr(relationship, 'description') and relationship.description:
                prop = etree.SubElement(elem, "property") 
                prop.set("key", "documentation")
                prop.set("value", relationship.description)
    
    def _add_archi_views(self, root, elements: List[ArchiMateElement], relationships: List[ArchiMateRelationship], model_name: str):
        """Add Views folder with diagrams in Archi format."""
        views_folder = etree.SubElement(root, "folder")
        views_folder.set("name", "Views")
        views_folder.set("id", f"id-{uuid.uuid4()}")
        views_folder.set("type", "diagrams")
        
        # Create a default view that shows all elements
        if elements:
            view = etree.SubElement(views_folder, "element")
            view.set(f"{{{self.XSI_NAMESPACE}}}type", "archimate:ArchimateDiagramModel")
            view.set("name", f"{model_name} - Overview")
            view.set("id", f"id-{uuid.uuid4()}")
            view.set("connectionRouterType", "2")  # Important for Archi
            
            # Build connection mapping for targetConnections
            connection_map = {}
            connection_id_map = {}
            
            # Pre-generate connection IDs and map relationships
            for relationship in relationships:
                connection_id = f"id-{uuid.uuid4()}"
                connection_id_map[relationship.id] = connection_id
                
                # Find source and target object indices
                source_idx = None
                target_idx = None
                for i, element in enumerate(elements):
                    if element.id == relationship.from_element:
                        source_idx = i
                    elif element.id == relationship.to_element:
                        target_idx = i
                
                if source_idx is not None and target_idx is not None:
                    target_obj_id = f"id-obj-{target_idx}"
                    if target_obj_id not in connection_map:
                        connection_map[target_obj_id] = []
                    connection_map[target_obj_id].append(connection_id)
            
            # Add elements to the view with proper connection attributes
            x_pos = 50
            y_pos = 50
            for i, element in enumerate(elements):
                child = etree.SubElement(view, "child")
                child.set(f"{{{self.XSI_NAMESPACE}}}type", "archimate:DiagramObject")
                child.set("id", f"id-obj-{i}")
                child.set("archimateElement", element.id)
                
                # Add targetConnections attribute if this element is a target
                target_connections = connection_map.get(f"id-obj-{i}", [])
                if target_connections:
                    child.set("targetConnections", " ".join(target_connections))
                
                # Simple grid layout
                bounds = etree.SubElement(child, "bounds")
                bounds.set("x", str(x_pos))
                bounds.set("y", str(y_pos))
                bounds.set("width", "200")
                bounds.set("height", "60")
                
                # Add sourceConnection elements as children
                for relationship in relationships:
                    if relationship.from_element == element.id:
                        # Find target object ID
                        target_idx = None
                        for j, target_element in enumerate(elements):
                            if target_element.id == relationship.to_element:
                                target_idx = j
                                break
                        
                        if target_idx is not None:
                            source_connection = etree.SubElement(child, "sourceConnection")
                            source_connection.set(f"{{{self.XSI_NAMESPACE}}}type", "archimate:Connection")
                            source_connection.set("id", connection_id_map[relationship.id])
                            source_connection.set("source", f"id-obj-{i}")
                            source_connection.set("target", f"id-obj-{target_idx}")
                            source_connection.set("archimateRelationship", relationship.id)
                
                # Move to next position
                x_pos += 220
                if x_pos > 800:  # New row
                    x_pos = 50
                    y_pos += 100
            
            # Set viewpoint property
            viewpoint_prop = etree.SubElement(view, "property")
            viewpoint_prop.set("key", "viewpoint")
            viewpoint_prop.set("value", "layered")