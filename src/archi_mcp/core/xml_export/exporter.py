"""ArchiMate XML Exchange Format Exporter

Exports ArchiMate models to Open Group XML Exchange format.
Supports ArchiMate 3.2 elements using 3.0 XML schema namespace for backward compatibility.
"""

import uuid
import os
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
from .xml_validator import validate_archimate_export, log_validation_results
from .universal_relationship_fixer import apply_universal_fix, get_fix_summary
from .liberal_validator import analyze_model_relationships, generate_liberal_validation_report

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
            
            # Apply universal relationship fixing (safe - preserves PlantUML generation)
            try:
                # Universal fixing enabled by default for maximum Archi compatibility
                enable_universal_fix = os.getenv("ARCHI_MCP_ENABLE_UNIVERSAL_FIX", "true").lower() in ("true", "1", "yes")
                
                if enable_universal_fix:
                    xml_string, fix_stats = apply_universal_fix(xml_string)
                    
                    # Log results
                    if fix_stats["fixes_applied"] > 0:
                        logger.info(f"Universal relationship fixer: {fix_stats['fixes_applied']} relationships optimized for Archi compatibility")
                        logger.info(f"Preservation rate: {(fix_stats['preserved_relationships'] / fix_stats['total_relationships'] * 100):.1f}%")
                    else:
                        logger.info(f"Universal fixer: All {fix_stats['total_relationships']} relationships already optimal")
                else:
                    logger.debug("Universal relationship fixing disabled")
                    
            except Exception as e:
                logger.warning(f"Universal relationship fixing failed (non-blocking): {e}")
            
            # Save to file if path provided
            if output_path:
                if isinstance(output_path, str):
                    output_path = Path(output_path)
                output_path.write_text(xml_string, encoding='utf-8')
                logger.info(f"XML exported to {output_path}")
                
                # Liberal validation and analysis (safe - never blocks export)
                try:
                    # Use liberal validator for informational purposes only
                    analysis = analyze_model_relationships(xml_string)
                    
                    # Log the analysis results (informational only - no fixing)
                    problematic_count = len(analysis["problematic"])
                    total_count = analysis["total_relationships"]
                    
                    logger.info(f"📊 ArchiMate analysis: {total_count} relationships, {problematic_count} flagged for review")
                    
                    # Log cross-layer relationship statistics
                    cross_layer_count = len(analysis["cross_layer"])
                    same_layer_count = len(analysis["same_layer"])
                    logger.info(f"📈 Distribution: {same_layer_count} same-layer, {cross_layer_count} cross-layer relationships")
                    
                    # Note: Liberal validator allows most relationships as valid for practical use
                    logger.info("ℹ️  ArchiMate relationships may show warnings in Archi validation but are functionally valid")
                        
                except Exception as e:
                    logger.warning(f"Model analysis failed (non-blocking): {e}")
            
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
            
            # Calculate intelligent layout positions
            element_positions = self._calculate_intelligent_layout(elements, relationships)
            
            # Add elements to the view with intelligent positioning
            for i, element in enumerate(elements):
                child = etree.SubElement(view, "child")
                child.set(f"{{{self.XSI_NAMESPACE}}}type", "archimate:DiagramObject")
                child.set("id", f"id-obj-{i}")
                child.set("archimateElement", element.id)
                
                # Add targetConnections attribute if this element is a target
                target_connections = connection_map.get(f"id-obj-{i}", [])
                if target_connections:
                    child.set("targetConnections", " ".join(target_connections))
                
                # Use intelligent layout positions
                position = element_positions.get(element.id, {"x": 50, "y": 50})
                bounds = etree.SubElement(child, "bounds")
                bounds.set("x", str(position["x"]))
                bounds.set("y", str(position["y"]))
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
                            
                            # Add connection routing for better visual clarity
                            source_pos = element_positions.get(element.id, {"x": 50, "y": 50})
                            target_element = elements[target_idx]
                            target_pos = element_positions.get(target_element.id, {"x": 50, "y": 50})
                            
                            # Add bendpoints for cross-layer connections to avoid overlap
                            if abs(source_pos["y"] - target_pos["y"]) > 80:  # Different layers
                                bendpoints = self._calculate_connection_bendpoints(source_pos, target_pos)
                                if bendpoints:
                                    for bp_idx, (bx, by) in enumerate(bendpoints):
                                        bendpoint = etree.SubElement(source_connection, "bendpoint")
                                        bendpoint.set("startX", str(bx - source_pos["x"] - 100))  # Relative to source center
                                        bendpoint.set("startY", str(by - source_pos["y"] - 30))
                                        bendpoint.set("endX", str(bx - target_pos["x"] - 100))    # Relative to target center  
                                        bendpoint.set("endY", str(by - target_pos["y"] - 30))
            
            # Set viewpoint property
            viewpoint_prop = etree.SubElement(view, "property")
            viewpoint_prop.set("key", "viewpoint")
            viewpoint_prop.set("value", "layered")
    
    def _calculate_intelligent_layout(self, elements: List[ArchiMateElement], relationships: List[ArchiMateRelationship]):
        """Calculate intelligent layout positions for elements based on ArchiMate layer hierarchy."""
        positions = {}
        
        # ArchiMate layer hierarchy (top to bottom) - FIXED ORDER
        layer_hierarchy = [
            "Motivation",
            "Strategy", 
            "Business",
            "Application",
            "Technology",
            "Physical",
            "Implementation"
        ]
        
        # Group elements by their actual ArchiMate layer
        layer_groups = {layer: [] for layer in layer_hierarchy}
        
        # Categorize elements by their actual layer
        for element in elements:
            layer = element.layer.value if hasattr(element.layer, 'value') else str(element.layer)
            if layer in layer_groups:
                layer_groups[layer].append(element)
            else:
                # If unknown layer, add to Business as fallback
                layer_groups["Business"].append(element)
        
        # Build relationship graph for positioning within layers
        element_connections = {}
        for element in elements:
            element_connections[element.id] = {"outgoing": [], "incoming": []}
        
        for relationship in relationships:
            if relationship.from_element in element_connections:
                element_connections[relationship.from_element]["outgoing"].append(relationship.to_element)
            if relationship.to_element in element_connections:
                element_connections[relationship.to_element]["incoming"].append(relationship.from_element)
        
        # Layout configuration - optimized for visual clarity
        layer_height = 160  # Vertical space between layers (increased for group padding)
        element_width = 300   # Horizontal space between elements (increased for readability)
        start_x = 80          # More margin from left
        start_y = 80          # More margin from top
        max_elements_per_row = 3  # Fewer elements per row for better readability
        
        current_y = start_y
        
        # Position elements layer by layer following ArchiMate hierarchy
        for layer_name in layer_hierarchy:
            layer_elements = layer_groups[layer_name]
            if not layer_elements:
                continue
                
            # Sort elements within layer by relationship importance
            # Elements with more connections should be more central
            layer_elements.sort(key=lambda e: len(element_connections[e.id]["outgoing"]) + 
                                            len(element_connections[e.id]["incoming"]), reverse=True)
            
            # Calculate positions for this layer
            layer_positions = self._calculate_layer_positions(
                layer_elements, element_connections, start_x, current_y, 
                element_width, max_elements_per_row
            )
            
            # Add to overall positions
            positions.update(layer_positions)
            
            # Move to next layer position
            current_y += layer_height
        
        return positions
    
    def _calculate_layer_positions(self, layer_elements, element_connections, start_x, start_y, 
                                  element_width, max_elements_per_row):
        """Calculate positions for elements within a single layer with relationship awareness."""
        positions = {}
        
        if not layer_elements:
            return positions
        
        # Try to group related elements together
        if len(layer_elements) <= max_elements_per_row:
            # Single row layout - arrange by relationship importance
            # Central elements (with most connections) in the middle
            sorted_elements = self._sort_elements_by_centrality(layer_elements, element_connections)
            
            # Calculate optimal spacing to center the elements on the canvas
            canvas_width = 1200  # Assume canvas width for centering
            total_elements_width = len(sorted_elements) * element_width
            center_offset = (canvas_width - total_elements_width) // 2
            current_x = max(start_x, center_offset)
            
            for element in sorted_elements:
                positions[element.id] = {"x": current_x, "y": start_y}
                current_x += element_width
        else:
            # Multi-row layout with relationship-aware clustering
            element_clusters = self._cluster_related_elements(layer_elements, element_connections, max_elements_per_row)
            
            current_x = start_x
            current_y = start_y
            elements_in_current_row = 0
            
            for cluster in element_clusters:
                for element in cluster:
                    positions[element.id] = {"x": current_x, "y": current_y}
                    current_x += element_width
                    elements_in_current_row += 1
                    
                    # Move to next row if needed
                    if elements_in_current_row >= max_elements_per_row:
                        current_x = start_x
                        current_y += 100  # Move down
                        elements_in_current_row = 0
        
        return positions
    
    def _sort_elements_by_centrality(self, elements, element_connections):
        """Sort elements by their centrality (connection count) for better visual impact."""
        def centrality_score(element):
            return len(element_connections[element.id]["outgoing"]) + len(element_connections[element.id]["incoming"])
        
        return sorted(elements, key=centrality_score, reverse=True)
    
    def _cluster_related_elements(self, elements, element_connections, max_per_row):
        """Group related elements into clusters for better visual organization."""
        clusters = []
        remaining_elements = elements.copy()
        
        while remaining_elements:
            # Start a new cluster with the most connected element
            cluster_seed = max(remaining_elements, key=lambda e: 
                             len(element_connections[e.id]["outgoing"]) + len(element_connections[e.id]["incoming"]))
            
            current_cluster = [cluster_seed]
            remaining_elements.remove(cluster_seed)
            
            # Add related elements to the cluster (up to max_per_row)
            while len(current_cluster) < max_per_row and remaining_elements:
                best_candidate = None
                best_score = -1
                
                for candidate in remaining_elements:
                    # Score based on connections to elements already in cluster
                    score = 0
                    for cluster_element in current_cluster:
                        if candidate.id in element_connections[cluster_element.id]["outgoing"]:
                            score += 2  # Outgoing connection
                        if candidate.id in element_connections[cluster_element.id]["incoming"]:
                            score += 2  # Incoming connection
                        if cluster_element.id in element_connections[candidate.id]["outgoing"]:
                            score += 1  # Connected element
                        if cluster_element.id in element_connections[candidate.id]["incoming"]:
                            score += 1  # Connected element
                    
                    if score > best_score:
                        best_score = score
                        best_candidate = candidate
                
                if best_candidate and best_score > 0:
                    current_cluster.append(best_candidate)
                    remaining_elements.remove(best_candidate)
                else:
                    # No more related elements, move to next available
                    if remaining_elements:
                        current_cluster.append(remaining_elements.pop(0))
            
            clusters.append(current_cluster)
        
        return clusters
    
    def _calculate_connection_bendpoints(self, source_pos, target_pos):
        """Calculate bendpoints for connections to improve visual clarity."""
        bendpoints = []
        
        # Calculate the distance and direction
        dx = target_pos["x"] - source_pos["x"]
        dy = target_pos["y"] - source_pos["y"]
        
        # For cross-layer connections (vertical), add a bendpoint to make nice curves
        if abs(dy) > 80:  # Different layers
            # Add a midpoint for smooth routing
            mid_y = source_pos["y"] + dy // 2
            
            # If horizontal distance is small, create a straight vertical path
            if abs(dx) < 100:
                # Simple vertical connection
                bendpoints.append((source_pos["x"] + 100, mid_y))  # Element center + offset
            else:
                # Create an L-shaped or curved path
                if dx > 0:  # Target is to the right
                    bendpoints.append((source_pos["x"] + 150, source_pos["y"] + 30))  # Exit right
                    bendpoints.append((target_pos["x"] - 50, target_pos["y"] - 30))   # Enter left
                else:  # Target is to the left
                    bendpoints.append((source_pos["x"] - 50, source_pos["y"] + 30))   # Exit left  
                    bendpoints.append((target_pos["x"] + 150, target_pos["y"] - 30))  # Enter right
        
        return bendpoints
    
    def _group_elements_by_layer(self, elements: List[ArchiMateElement]):
        """Group elements by their ArchiMate layer."""
        layer_hierarchy = [
            "Motivation", "Strategy", "Business", "Application", 
            "Technology", "Physical", "Implementation"
        ]
        
        layer_groups = {layer: [] for layer in layer_hierarchy}
        
        for element in elements:
            layer = element.layer.value if hasattr(element.layer, 'value') else str(element.layer)
            if layer in layer_groups:
                layer_groups[layer].append(element)
            else:
                layer_groups["Business"].append(element)  # Fallback
                
        return layer_groups
    
    def _calculate_group_bounds(self, layer_elements, element_positions):
        """Calculate bounds for a layer group based on its elements."""
        if not layer_elements:
            return {"x": 0, "y": 0, "width": 100, "height": 100}
        
        # Find min/max positions
        x_positions = []
        y_positions = []
        
        for element in layer_elements:
            pos = element_positions.get(element.id, {"x": 50, "y": 50})
            x_positions.append(pos["x"])
            y_positions.append(pos["y"])
        
        if not x_positions:
            return {"x": 0, "y": 0, "width": 100, "height": 100}
        
        min_x = min(x_positions)
        max_x = max(x_positions)
        min_y = min(y_positions)
        max_y = max(y_positions)
        
        # Add padding around elements
        padding = 20
        element_width = 200
        element_height = 60
        
        return {
            "x": min_x - padding,
            "y": min_y - padding,
            "width": (max_x - min_x) + element_width + (2 * padding),
            "height": (max_y - min_y) + element_height + (2 * padding)
        }
    
    def _get_layer_color(self, layer_name):
        """Get distinctive color for each ArchiMate layer."""
        layer_colors = {
            "Motivation": "#FFE6E6",    # Light pink
            "Strategy": "#E6F3FF",      # Light blue  
            "Business": "#FFF4E6",      # Light orange
            "Application": "#E6FFE6",   # Light green
            "Technology": "#F0E6FF",    # Light purple
            "Physical": "#FFFFE6",      # Light yellow
            "Implementation": "#E6E6E6"  # Light gray
        }
        return layer_colors.get(layer_name, "#F5F5F5")