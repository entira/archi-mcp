#!/usr/bin/env python3
"""
Backfill input.json files for old diagrams that don't have them.
Parses diagram.puml and metadata.json to reconstruct the input data.
"""

import json
import re
from pathlib import Path

def parse_plantuml_element(line):
    """Parse a PlantUML element definition line."""
    # Match: ElementType(id, "name")
    match = re.match(r'\s*(\w+)\((\w+),\s*"([^"]+)"\)', line)
    if match:
        element_type, elem_id, name = match.groups()
        return {
            "id": elem_id,
            "name": name,
            "type": element_type.lower().replace('_', '-')
        }
    return None

def parse_plantuml_relationship(line):
    """Parse a PlantUML relationship line."""
    # Match: Rel_Type(source, target, "label")
    match = re.match(r'\s*Rel_(\w+)\((\w+),\s*(\w+),\s*"([^"]+)"\)', line)
    if match:
        rel_type, source, target, label = match.groups()
        return {
            "source": source,
            "target": target,
            "type": rel_type.lower().replace('_', '-'),
            "label": label
        }
    return None

def parse_plantuml_file(puml_path):
    """Parse PlantUML file to extract elements and relationships."""
    elements = []
    relationships = []
    title = ""
    description = ""

    with open(puml_path, 'r', encoding='utf-8') as f:
        content = f.read()

        # Extract title
        title_match = re.search(r'^title\s+(.+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1)

        # Extract description from comment
        desc_match = re.search(r"^'\s*Description:\s*(.+)$", content, re.MULTILINE)
        if desc_match:
            description = desc_match.group(1)

        # Parse lines
        for line in content.split('\n'):
            # Try to parse as element
            elem = parse_plantuml_element(line)
            if elem:
                elements.append(elem)
                continue

            # Try to parse as relationship
            rel = parse_plantuml_relationship(line)
            if rel:
                relationships.append(rel)

    return {
        "title": title,
        "description": description,
        "elements": elements,
        "relationships": relationships
    }

def extract_layout_from_plantuml(puml_path):
    """Extract layout settings from PlantUML file."""
    layout = {
        "direction": "top-bottom",  # Default
        "spacing": "comfortable",   # Default
        "show_legend": True,
        "show_title": True,
        "group_by_layer": False,
        "show_element_types": False,
        "show_relationship_labels": True
    }

    with open(puml_path, 'r', encoding='utf-8') as f:
        content = f.read()

        # Check for left to right layout
        if re.search(r'left to right direction', content, re.IGNORECASE):
            layout["direction"] = "left-right"

        # Check if legend exists
        if 'legend' in content.lower():
            layout["show_legend"] = True

        # Check if packages exist (grouping by layer)
        if 'package' in content.lower():
            layout["group_by_layer"] = True

    return layout

def backfill_export_directory(export_dir):
    """Create input.json for an export directory if it doesn't exist."""
    input_json_path = export_dir / "input.json"

    # Skip if input.json already exists
    if input_json_path.exists():
        return False, "already exists"

    puml_path = export_dir / "diagram.puml"
    metadata_path = export_dir / "metadata.json"

    # Skip if required files don't exist
    if not puml_path.exists() or not metadata_path.exists():
        return False, "missing puml or metadata"

    try:
        # Parse PlantUML file
        parsed_data = parse_plantuml_file(puml_path)

        # Extract layout settings
        layout = extract_layout_from_plantuml(puml_path)

        # Load metadata for language detection
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # Detect language (Slovak if any Slovak characters found)
        language = "sk" if any(c in parsed_data["title"] + parsed_data["description"]
                              for c in "áäčďéíľĺňóôŕšťúýžÁÄČĎÉÍĽĹŇÓÔŔŠŤÚÝŽ") else "en"

        # Create input.json structure
        input_data = {
            "title": parsed_data["title"],
            "description": parsed_data["description"],
            "elements": parsed_data["elements"],
            "relationships": parsed_data["relationships"],
            "layout": layout,
            "language": language
        }

        # Write input.json
        with open(input_json_path, 'w', encoding='utf-8') as f:
            json.dump(input_data, f, indent=2, ensure_ascii=False)

        return True, f"{len(parsed_data['elements'])} elements, {len(parsed_data['relationships'])} relationships"

    except Exception as e:
        return False, f"error: {str(e)}"

def main():
    """Main function to backfill all export directories."""
    exports_dir = Path("/Users/patrik/Projects/archi-mcp/exports")

    if not exports_dir.exists():
        print(f"❌ Exports directory not found: {exports_dir}")
        return

    print(f"🔍 Scanning {exports_dir} for export directories without input.json...")
    print()

    total = 0
    created = 0
    skipped = 0
    failed = 0

    # Process each export directory
    for export_dir in sorted(exports_dir.iterdir()):
        if not export_dir.is_dir() or export_dir.name == "latest":
            continue

        total += 1
        success, message = backfill_export_directory(export_dir)

        if success:
            created += 1
            print(f"✅ {export_dir.name}: Created input.json ({message})")
        elif "already exists" in message:
            skipped += 1
            print(f"⏭️  {export_dir.name}: Skipped ({message})")
        else:
            failed += 1
            print(f"❌ {export_dir.name}: Failed ({message})")

    print()
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   Total directories: {total}")
    print(f"   Created: {created}")
    print(f"   Skipped: {skipped}")
    print(f"   Failed: {failed}")
    print("=" * 60)

if __name__ == "__main__":
    main()
