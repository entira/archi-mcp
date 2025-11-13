#!/usr/bin/env python3
"""
ArchiMate Diagram Skill Runner

This script handles diagram generation for the Claude Agent Skill.
It manages setup, PlantUML rendering, and file output.

Author: Mgr. Patrik Skovajsa
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import urllib.request

# Detect paths automatically for portability
SKILL_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SKILL_DIR.parent.parent.parent  # .claude/skills/archimate-diagrams -> project root

# Add lib directory to path - this makes lib/ the root package
sys.path.insert(0, str(SKILL_DIR / "lib"))

# Now import from lib - archimate, utils, etc. are top-level packages
from archimate.generator import ArchiMateGenerator
from archimate.validator import ArchiMateValidator
from archimate.elements import ArchiMateElement, ArchiMateLayer, ArchiMateAspect
from archimate.relationships import ArchiMateRelationship


def get_element_aspect(element_type: str) -> ArchiMateAspect:
    """Determine ArchiMate aspect based on element type."""

    # Behavior elements
    behavior_types = {
        "Business_Process", "Business_Function", "Business_Interaction", "Business_Event", "Business_Service",
        "Application_Function", "Application_Interaction", "Application_Process", "Application_Event", "Application_Service",
        "Technology_Function", "Technology_Process", "Technology_Interaction", "Technology_Event", "Technology_Service",
    }

    # Passive structure elements
    passive_types = {
        "Business_Object", "Business_Contract", "Business_Representation", "Product",
        "Data_Object",
        "Artifact",
        "Material",
    }

    if element_type in behavior_types:
        return ArchiMateAspect.BEHAVIOR
    elif element_type in passive_types:
        return ArchiMateAspect.PASSIVE_STRUCTURE
    else:
        # Default to active structure (actors, roles, components, nodes, etc.)
        return ArchiMateAspect.ACTIVE_STRUCTURE


class SkillConfig:
    """Configuration for the skill - project-relative paths"""

    # Output directory: project-relative for easy access
    OUTPUT_DIR = PROJECT_ROOT / ".archimate-diagrams"

    # PlantUML JAR: stored in output directory
    PLANTUML_JAR = OUTPUT_DIR / "plantuml.jar"
    PLANTUML_URL = "https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar"


def setup_environment() -> Dict[str, Any]:
    """
    Setup the skill environment:
    - Create output directory
    - Download PlantUML JAR if needed
    - Verify Java is installed

    Returns:
        Status dictionary with setup results
    """
    status = {"success": True, "messages": []}

    # Create output directory
    SkillConfig.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    status["messages"].append(f"✓ Created directory: {SkillConfig.OUTPUT_DIR}")

    # Check for PlantUML JAR
    if not SkillConfig.PLANTUML_JAR.exists():
        status["messages"].append("⚠ PlantUML JAR not found, downloading...")
        try:
            urllib.request.urlretrieve(SkillConfig.PLANTUML_URL, SkillConfig.PLANTUML_JAR)
            status["messages"].append(f"✓ Downloaded PlantUML JAR to {SkillConfig.PLANTUML_JAR}")
        except Exception as e:
            status["success"] = False
            status["messages"].append(f"✗ Failed to download PlantUML: {e}")
            return status
    else:
        status["messages"].append(f"✓ PlantUML JAR found: {SkillConfig.PLANTUML_JAR}")

    # Verify Java
    try:
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            java_version = result.stderr.split('\n')[0] if result.stderr else "Unknown"
            status["messages"].append(f"✓ Java found: {java_version}")
        else:
            status["success"] = False
            status["messages"].append("✗ Java not working properly")
    except Exception as e:
        status["success"] = False
        status["messages"].append(f"✗ Java not found: {e}")
        status["messages"].append("  Please install Java 8+ from https://www.java.com/")

    return status


def render_plantuml(puml_file: Path, output_format: str = "png") -> Optional[Path]:
    """
    Render PlantUML file to PNG or SVG

    Args:
        puml_file: Path to .puml file
        output_format: 'png' or 'svg'

    Returns:
        Path to generated image file, or None on error
    """
    if not SkillConfig.PLANTUML_JAR.exists():
        print(f"✗ PlantUML JAR not found: {SkillConfig.PLANTUML_JAR}", file=sys.stderr)
        return None

    try:
        cmd = [
            "java",
            "-Djava.awt.headless=true",  # CRITICAL for macOS
            "-jar", str(SkillConfig.PLANTUML_JAR),
            f"-t{output_format}",
            str(puml_file)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            output_file = puml_file.with_suffix(f".{output_format}")
            if output_file.exists():
                return output_file
            else:
                print(f"✗ Output file not created: {output_file}", file=sys.stderr)
                return None
        else:
            print(f"✗ PlantUML error: {result.stderr}", file=sys.stderr)
            return None

    except Exception as e:
        print(f"✗ Rendering failed: {e}", file=sys.stderr)
        return None


def generate_diagram(
    title: str,
    elements: list,
    relationships: list,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate ArchiMate diagram

    Args:
        title: Diagram title
        elements: List of element dictionaries
        relationships: List of relationship dictionaries
        options: Generation options (direction, spacing, etc.)

    Returns:
        Result dictionary with file paths and status
    """
    result = {"success": True, "files": {}, "errors": []}

    # Create timestamped export directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = SkillConfig.OUTPUT_DIR / timestamp
    export_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Initialize generator
        generator = ArchiMateGenerator()
        validator = ArchiMateValidator()

        # Add elements
        for elem_data in elements:
            element_type = elem_data["element_type"]
            element = ArchiMateElement(
                id=elem_data["id"],
                name=elem_data["name"],
                element_type=element_type,
                layer=ArchiMateLayer[elem_data.get("layer", "APPLICATION").upper()],
                aspect=get_element_aspect(element_type),
                description=elem_data.get("description")
            )
            generator.add_element(element)

        # Add relationships
        for rel_data in relationships:
            relationship = ArchiMateRelationship(
                id=rel_data["id"],
                from_element=rel_data["from_element"],
                to_element=rel_data["to_element"],
                relationship_type=rel_data["relationship_type"],
                label=rel_data.get("label")
            )
            generator.add_relationship(relationship)

        # Validate
        try:
            elements_list = list(generator.elements.values())
            relationships_list = list(generator.relationships.values())
            validation_errors = validator.validate_model(elements_list, relationships_list)
        except AttributeError as e:
            result["success"] = False
            result["errors"].append(f"Validation error: {str(e)}. Generator elements type: {type(generator.elements)}")
            return result

        if validation_errors:
            result["success"] = False
            result["errors"] = validation_errors
            return result

        # Generate PlantUML code
        puml_code = generator.generate_plantuml(
            title=title,
            direction=options.get("direction", "top-bottom") if options else "top-bottom",
            spacing=options.get("spacing", "comfortable") if options else "comfortable"
        )

        # Save PlantUML file
        puml_file = export_dir / "diagram.puml"
        puml_file.write_text(puml_code, encoding="utf-8")
        result["files"]["puml"] = str(puml_file)

        # Render PNG
        png_file = render_plantuml(puml_file, "png")
        if png_file:
            result["files"]["png"] = str(png_file)
        else:
            result["errors"].append("PNG rendering failed")

        # Optionally render SVG
        if options and options.get("generate_svg"):
            svg_file = render_plantuml(puml_file, "svg")
            if svg_file:
                result["files"]["svg"] = str(svg_file)

        # Save metadata
        metadata = {
            "title": title,
            "timestamp": timestamp,
            "element_count": len(elements),
            "relationship_count": len(relationships),
            "options": options or {}
        }
        metadata_file = export_dir / "metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        result["files"]["metadata"] = str(metadata_file)

        result["export_dir"] = str(export_dir)

    except Exception as e:
        result["success"] = False
        result["errors"].append(f"Generation failed: {str(e)}")

    return result


def main():
    """Main entry point for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(description="ArchiMate Diagram Skill Runner")
    parser.add_argument("command", choices=["setup", "generate"], help="Command to run")
    parser.add_argument("--input", help="JSON input file for generate command")

    args = parser.parse_args()

    if args.command == "setup":
        status = setup_environment()
        for msg in status["messages"]:
            print(msg)
        sys.exit(0 if status["success"] else 1)

    elif args.command == "generate":
        if not args.input:
            print("Error: --input required for generate command", file=sys.stderr)
            sys.exit(1)

        with open(args.input, 'r') as f:
            data = json.load(f)

        result = generate_diagram(
            title=data["title"],
            elements=data["elements"],
            relationships=data["relationships"],
            options=data.get("options")
        )

        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
