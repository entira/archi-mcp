"""PlantUML ArchiMate diagram generator."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from .elements.base import ArchiMateElement
from .relationships import ArchiMateRelationship
from ..utils.exceptions import ArchiMateGenerationError
from ..i18n import ArchiMateTranslator


class DiagramLayout(BaseModel):
    """Diagram layout configuration."""
    direction: str = "horizontal"  # horizontal, vertical, layered
    show_legend: bool = True
    show_title: bool = True
    group_by_layer: bool = False
    spacing: str = "normal"  # compact, normal, wide
    show_element_types: bool = False  # show element type names (e.g. Business_Actor)
    show_relationship_labels: bool = True  # show relationship labels and custom names


class ArchiMateGenerator:
    """Generator for PlantUML ArchiMate diagrams."""
    
    def __init__(self, translator: Optional[ArchiMateTranslator] = None):
        """Initialize the ArchiMate generator.
        
        Args:
            translator: Optional translator for multilingual support
        """
        self.elements: Dict[str, ArchiMateElement] = {}
        self.relationships: List[ArchiMateRelationship] = []
        self.layout: DiagramLayout = DiagramLayout()
        self.translator = translator or ArchiMateTranslator("en")
        
    def add_element(self, element: ArchiMateElement) -> None:
        """Add an ArchiMate element to the diagram.
        
        Args:
            element: ArchiMateElement to add
            
        Raises:
            ArchiMateGenerationError: If element ID already exists
        """
        if element.id in self.elements:
            raise ArchiMateGenerationError(
                f"Element with ID '{element.id}' already exists",
                details={"existing_element": str(self.elements[element.id])}
            )
        
        self.elements[element.id] = element
    
    def add_relationship(self, relationship: ArchiMateRelationship) -> None:
        """Add an ArchiMate relationship to the diagram.
        
        Args:
            relationship: ArchiMateRelationship to add
            
        Raises:
            ArchiMateGenerationError: If relationship validation fails
        """
        # Validate relationship
        errors = relationship.validate_relationship(self.elements)
        if errors:
            raise ArchiMateGenerationError(
                f"Relationship validation failed: {'; '.join(errors)}",
                details={"relationship": str(relationship), "errors": errors}
            )
        
        self.relationships.append(relationship)
    
    def set_layout(self, layout: DiagramLayout) -> None:
        """Set diagram layout configuration.
        
        Args:
            layout: DiagramLayout configuration
        """
        self.layout = layout
    
    def generate_plantuml(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> str:
        """Generate complete PlantUML ArchiMate diagram code.
        
        Args:
            title: Optional diagram title
            description: Optional diagram description
            
        Returns:
            Complete PlantUML code string
            
        Raises:
            ArchiMateGenerationError: If generation fails
        """
        if not self.elements:
            raise ArchiMateGenerationError("No elements defined for diagram generation")
        
        # Start building PlantUML code
        lines = []
        
        # Add PlantUML header
        lines.append("@startuml")
        lines.append("!include <archimate/Archimate>")
        lines.append("")
        
        # Add title if provided
        if title and self.layout.show_title:
            lines.append(f"title {title}")
            lines.append("")
        
        # Add description if provided (as a comment since note syntax may cause issues)
        if description:
            lines.append(f"' Description: {description}")
            lines.append("")
        
        # Set direction
        if self.layout.direction == "vertical":
            lines.append("top to bottom direction")
        elif self.layout.direction == "horizontal":
            lines.append("left to right direction")
        
        lines.append("")
        
        # Generate elements - use layout setting for grouping
        if self.layout.group_by_layer:
            self._generate_elements_by_layer(lines)
        else:
            self._generate_elements_sequential(lines)
        
        lines.append("")
        
        # Generate relationships
        self._generate_relationships(lines)
        
        # Add legend if requested
        if self.layout.show_legend:
            lines.append("")
            self._generate_legend(lines)
        
        # End PlantUML
        lines.append("")
        lines.append("@enduml")
        
        return "\n".join(lines)
    
    def _generate_elements_sequential(self, lines: List[str]) -> None:
        """Generate elements in sequential order."""
        lines.append("' Elements")
        for element in self.elements.values():
            lines.append(element.to_plantuml(show_element_type=self.layout.show_element_types))
    
    def _generate_elements_by_layer(self, lines: List[str]) -> None:
        """Generate elements grouped by layer."""
        # Group elements by layer
        layers = {}
        for element in self.elements.values():
            layer = element.layer.value
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(element)
        
        # Generate each layer with grouping for multi-layer diagrams
        if len(layers) > 1:
            for layer_name, layer_elements in layers.items():
                translated_layer = self.translator.translate_layer(layer_name)
                lines.append(f"package \"{translated_layer}\" {{")
                for element in layer_elements:
                    lines.append("  " + element.to_plantuml(show_element_type=self.layout.show_element_types))
                lines.append("}")
                lines.append("")
        else:
            # Single layer - no grouping needed
            for layer_name, layer_elements in layers.items():
                translated_layer = self.translator.translate_layer(layer_name)
                lines.append(f"' {translated_layer}")
                for element in layer_elements:
                    lines.append(element.to_plantuml(show_element_type=self.layout.show_element_types))
                lines.append("")
    
    def _generate_relationships(self, lines: List[str]) -> None:
        """Generate relationships."""
        if not self.relationships:
            return
            
        lines.append("' Relationships")
        for relationship in self.relationships:
            lines.append(relationship.to_plantuml(self.translator, show_labels=self.layout.show_relationship_labels))
    
    def _generate_legend(self, lines: List[str]) -> None:
        """Generate diagram legend."""
        lines.append("' Legend")
        lines.append("legend right")
        
        # Show layers present in diagram
        layers_used = set(element.layer.value for element in self.elements.values())
        for layer in sorted(layers_used):
            translated_layer = self.translator.translate_layer(layer)
            lines.append(f"  {translated_layer}")
        
        lines.append("end legend")
    
    def clear(self) -> None:
        """Clear all elements and relationships."""
        self.elements.clear()
        self.relationships.clear()
    
    def get_element_count(self) -> int:
        """Get number of elements in diagram."""
        return len(self.elements)
    
    def get_relationship_count(self) -> int:
        """Get number of relationships in diagram."""
        return len(self.relationships)
    
    def get_layers_used(self) -> List[str]:
        """Get list of layers used in diagram."""
        return list(set(element.layer.value for element in self.elements.values()))
    
    def validate_diagram(self) -> List[str]:
        """Validate the complete diagram.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate all elements
        for element in self.elements.values():
            element_errors = element.validate_element()
            if element_errors:
                errors.extend([f"Element {element.id}: {error}" for error in element_errors])
        
        # Validate all relationships
        for relationship in self.relationships:
            rel_errors = relationship.validate_relationship(self.elements)
            if rel_errors:
                errors.extend([f"Relationship {relationship.id}: {error}" for error in rel_errors])
        
        return errors
    
    def export_to_file(self, filepath: str, title: Optional[str] = None) -> None:
        """Export diagram to PlantUML file.
        
        Args:
            filepath: Output file path
            title: Optional diagram title
            
        Raises:
            ArchiMateGenerationError: If export fails
        """
        try:
            plantuml_code = self.generate_plantuml(title=title)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(plantuml_code)
        except Exception as e:
            raise ArchiMateGenerationError(
                f"Failed to export diagram to file: {str(e)}",
                details={"filepath": filepath, "error": str(e)}
            )
    
    def generate_png_to_tmp(self, title: Optional[str] = None) -> str:
        """Generate PNG image to /tmp directory and return file path.
        
        Args:
            title: Optional diagram title for filename
            
        Returns:
            File path to generated PNG image
            
        Raises:
            ArchiMateGenerationError: If PNG generation fails
        """
        import tempfile
        import subprocess
        import os
        import time
        from pathlib import Path
        
        try:
            # Generate PlantUML code
            plantuml_code = self.generate_plantuml(title=title)
            
            # Create temporary PlantUML file
            timestamp = int(time.time())
            temp_filename = f"archimate_diagram_{timestamp}"
            if title:
                # Clean title for filename
                clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                clean_title = clean_title.replace(' ', '_')[:50]  # Limit length
                temp_filename = f"archimate_{clean_title}_{timestamp}"
            
            temp_puml_path = f"/tmp/{temp_filename}.puml"
            temp_png_path = f"/tmp/{temp_filename}.png"
            
            # Write PlantUML code
            with open(temp_puml_path, 'w', encoding='utf-8') as f:
                f.write(plantuml_code)
            
            # Find PlantUML jar
            possible_jars = [
                "/Users/patrik/Projects/archi-mcp/plantuml.jar",
                "./plantuml.jar",
                "/usr/local/bin/plantuml.jar",
                "/opt/homebrew/bin/plantuml.jar"
            ]
            
            plantuml_jar = None
            for jar_path in possible_jars:
                if os.path.exists(jar_path):
                    plantuml_jar = jar_path
                    break
            
            if not plantuml_jar:
                error_msg = """PlantUML jar not found. Download it by running:
curl -L https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar -o plantuml.jar

The jar should be placed in the project root directory or one of these locations:
- ./plantuml.jar (current directory)
- /usr/local/bin/plantuml.jar
- /opt/homebrew/bin/plantuml.jar"""
                raise ArchiMateGenerationError(error_msg)
            
            # Generate PNG (with headless mode to prevent focus stealing)
            cmd = ["java", "-Djava.awt.headless=true", "-jar", plantuml_jar, "-tpng", temp_puml_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                raise ArchiMateGenerationError(f"PlantUML generation failed: {result.stderr}")
            
            # Verify PNG was created
            if not os.path.exists(temp_png_path):
                raise ArchiMateGenerationError("PNG file was not generated")
            
            # Clean up temporary PlantUML file
            try:
                os.unlink(temp_puml_path)
            except:
                pass  # Don't fail if cleanup fails
            
            return temp_png_path
            
        except subprocess.TimeoutExpired:
            raise ArchiMateGenerationError("PlantUML generation timed out")
        except Exception as e:
            raise ArchiMateGenerationError(f"Failed to generate PNG: {str(e)}")
    
