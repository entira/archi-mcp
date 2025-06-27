#!/usr/bin/env python3
"""PlantUML validation tool for ArchiMate diagrams."""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from archi_mcp.server import ArchiMCPServer
import asyncio


class PlantUMLValidator:
    """Validates PlantUML ArchiMate diagrams by attempting to render them."""
    
    def __init__(self, plantuml_jar_path: str = None):
        """Initialize the validator."""
        if plantuml_jar_path is None:
            # Look for plantuml.jar in current directory or common locations
            possible_paths = [
                "plantuml.jar",
                "../plantuml.jar", 
                "/usr/local/bin/plantuml.jar",
                "/opt/plantuml/plantuml.jar"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    plantuml_jar_path = path
                    break
            
            if plantuml_jar_path is None:
                raise FileNotFoundError("PlantUML JAR not found. Please install PlantUML or specify path.")
        
        self.plantuml_jar = plantuml_jar_path
        
    def validate_puml_syntax(self, puml_content: str) -> Tuple[bool, str]:
        """Validate PlantUML syntax by attempting to compile it."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False) as f:
                f.write(puml_content)
                temp_file = f.name
            
            # Try to compile the PlantUML file - run headless to avoid window focus issues
            result = subprocess.run([
                'java', '-Djava.awt.headless=true', '-jar', self.plantuml_jar, 
                '-checkonly', temp_file
            ], capture_output=True, text=True, timeout=30, 
               creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
            
            # Clean up
            os.unlink(temp_file)
            
            if result.returncode == 0:
                return True, "Valid PlantUML syntax"
            else:
                return False, f"PlantUML validation error: {result.stderr or result.stdout}"
                
        except subprocess.TimeoutExpired:
            return False, "PlantUML validation timeout"
        except Exception as e:
            return False, f"PlantUML validation failed: {str(e)}"
    
    def render_to_svg(self, puml_content: str, output_path: str = None) -> Tuple[bool, str]:
        """Render PlantUML to SVG format."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False) as f:
                f.write(puml_content)
                temp_file = f.name
            
            if output_path is None:
                output_path = temp_file.replace('.puml', '.svg')
            
            # Render to SVG - run headless
            result = subprocess.run([
                'java', '-Djava.awt.headless=true', '-jar', self.plantuml_jar,
                '-tsvg', temp_file, '-o', str(Path(output_path).parent)
            ], capture_output=True, text=True, timeout=60,
               creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
            
            # Clean up temp file
            os.unlink(temp_file)
            
            if result.returncode == 0:
                return True, f"Successfully rendered to {output_path}"
            else:
                return False, f"Rendering failed: {result.stderr or result.stdout}"
                
        except subprocess.TimeoutExpired:
            return False, "PlantUML rendering timeout"
        except Exception as e:
            return False, f"PlantUML rendering failed: {str(e)}"
    
    def render_to_png(self, puml_content: str, output_path: str = None) -> Tuple[bool, str]:
        """Render PlantUML to PNG format."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False) as f:
                f.write(puml_content)
                temp_file = f.name
            
            if output_path is None:
                output_path = temp_file.replace('.puml', '.png')
            
            # Render to PNG - run headless
            result = subprocess.run([
                'java', '-Djava.awt.headless=true', '-jar', self.plantuml_jar,
                '-tpng', temp_file, '-o', str(Path(output_path).parent)
            ], capture_output=True, text=True, timeout=60,
               creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
            
            # Clean up temp file
            os.unlink(temp_file)
            
            if result.returncode == 0:
                return True, f"Successfully rendered to {output_path}"
            else:
                return False, f"Rendering failed: {result.stderr or result.stdout}"
                
        except subprocess.TimeoutExpired:
            return False, "PlantUML rendering timeout"
        except Exception as e:
            return False, f"PlantUML rendering failed: {str(e)}"


def fix_archimate_diagram(puml_content: str) -> str:
    """Fix common issues in ArchiMate PlantUML diagrams."""
    lines = puml_content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Fix empty relationship parameters - add labels
        if line.strip().startswith('Rel_') and line.strip().endswith(', )'):
            # Extract relationship info
            parts = line.strip().split('(', 1)[1].rsplit(',', 1)[0].split(', ')
            if len(parts) >= 3:
                rel_type = line.strip().split('_', 1)[1].split('(')[0]
                source = parts[0]
                target = parts[1]
                # Add meaningful label
                line = line.replace(', )', f', "{rel_type.lower()}")')
        
        # Fix direction definition
        if '!define DIRECTION' in line:
            line = 'left to right direction'
        
        # Fix legend syntax
        if line.strip() == 'legend':
            line = 'legend right'
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


async def test_all_generated_architectures():
    """Test all architecture generation examples with PlantUML validation."""
    validator = PlantUMLValidator('plantuml.jar')
    server = ArchiMCPServer()
    
    test_cases = [
        {
            "name": "Banking Portal",
            "args": {
                "system_description": "Online Banking Portal",
                "business_domain": "banking",
                "architecture_scope": "system",
                "include_views": ["motivation", "layered_view"],
                "implementation_phases": 3
            }
        },
        {
            "name": "E-commerce Platform", 
            "args": {
                "system_description": "E-commerce Platform",
                "business_domain": "e-commerce",
                "architecture_scope": "enterprise",
                "include_views": ["layered_view", "application_structure"],
                "implementation_phases": 3
            }
        },
        {
            "name": "Healthcare System",
            "args": {
                "system_description": "Healthcare Management System",
                "business_domain": "healthcare", 
                "architecture_scope": "system",
                "include_views": ["motivation", "interaction_view"],
                "implementation_phases": 4
            }
        }
    ]
    
    results = {}
    
    for test_case in test_cases:
        print(f"\n🧪 Testing {test_case['name']}...")
        print("=" * 50)
        
        try:
            # Generate architecture
            result = await server._generate_full_architecture(test_case['args'])
            content = result.content[0].text
            
            # Extract PlantUML diagrams
            diagrams = extract_plantuml_diagrams(content)
            
            test_results = []
            for i, (view_name, diagram) in enumerate(diagrams.items()):
                print(f"\n📊 Validating {view_name}...")
                
                # Fix common issues
                fixed_diagram = fix_archimate_diagram(diagram)
                
                # Validate syntax
                is_valid, message = validator.validate_puml_syntax(fixed_diagram)
                
                if is_valid:
                    print(f"✅ {view_name}: Valid syntax")
                    
                    # Try to render
                    output_path = f"test_output_{test_case['name'].lower().replace(' ', '_')}_{view_name}.svg"
                    rendered, render_msg = validator.render_to_svg(fixed_diagram, output_path)
                    
                    if rendered:
                        print(f"🎨 {view_name}: Successfully rendered to {output_path}")
                        test_results.append((view_name, True, "Valid and rendered"))
                    else:
                        print(f"⚠️  {view_name}: Valid syntax but render failed: {render_msg}")
                        test_results.append((view_name, False, f"Render failed: {render_msg}"))
                else:
                    print(f"❌ {view_name}: Invalid syntax: {message}")
                    test_results.append((view_name, False, f"Invalid syntax: {message}"))
                    
                    # Save the problematic diagram for debugging
                    debug_path = f"debug_{test_case['name'].lower().replace(' ', '_')}_{view_name}.puml"
                    with open(debug_path, 'w') as f:
                        f.write(fixed_diagram)
                    print(f"🐛 Saved debug diagram to {debug_path}")
            
            results[test_case['name']] = test_results
            
        except Exception as e:
            print(f"❌ Failed to generate {test_case['name']}: {e}")
            results[test_case['name']] = [("error", False, str(e))]
    
    # Summary
    print("\n" + "=" * 70)
    print("🏁 VALIDATION SUMMARY")
    print("=" * 70)
    
    total_tests = 0
    passed_tests = 0
    
    for test_name, test_results in results.items():
        print(f"\n📋 {test_name}:")
        for view_name, passed, message in test_results:
            status = "✅" if passed else "❌"
            print(f"  {status} {view_name}: {message}")
            total_tests += 1
            if passed:
                passed_tests += 1
    
    print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    return results


def extract_plantuml_diagrams(content: str) -> Dict[str, str]:
    """Extract PlantUML diagrams from MCP server output."""
    diagrams = {}
    lines = content.split('\n')
    
    current_diagram = []
    current_view = None
    in_plantuml = False
    
    for line in lines:
        if line.startswith('## ') and not line.startswith('## 📋'):
            current_view = line[3:].strip().lower().replace(' ', '_')
        elif '```plantuml' in line:
            in_plantuml = True
            current_diagram = []
        elif in_plantuml and '```' in line:
            in_plantuml = False
            if current_view and current_diagram:
                diagrams[current_view] = '\n'.join(current_diagram)
            current_diagram = []
        elif in_plantuml:
            current_diagram.append(line)
    
    return diagrams


def test_existing_diagram():
    """Test and fix the existing archi_mcp_architecture.puml file."""
    print("🔍 Testing existing ArchiMate MCP Server diagram...")
    
    validator = PlantUMLValidator('plantuml.jar')
    
    # Read existing diagram
    try:
        with open('archi_mcp_architecture.puml', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ archi_mcp_architecture.puml not found")
        return
    
    print("Original diagram:")
    is_valid, message = validator.validate_puml_syntax(content)
    print(f"  {'✅' if is_valid else '❌'} {message}")
    
    if not is_valid:
        print("\n🔧 Attempting to fix issues...")
        fixed_content = fix_archimate_diagram(content)
        
        is_valid_fixed, message_fixed = validator.validate_puml_syntax(fixed_content)
        print(f"  {'✅' if is_valid_fixed else '❌'} After fixes: {message_fixed}")
        
        if is_valid_fixed:
            # Save fixed version
            with open('archi_mcp_architecture_fixed.puml', 'w') as f:
                f.write(fixed_content)
            print("💾 Saved fixed version to archi_mcp_architecture_fixed.puml")
            
            # Try to render
            rendered, render_msg = validator.render_to_svg(fixed_content, 'archi_mcp_architecture.svg')
            if rendered:
                print(f"🎨 Successfully rendered to archi_mcp_architecture.svg")
            else:
                print(f"⚠️  Failed to render: {render_msg}")


if __name__ == "__main__":
    print("🧪 PlantUML ArchiMate Validation Tool")
    print("=" * 50)
    
    # Test existing diagram first
    test_existing_diagram()
    
    print("\n" + "=" * 50)
    
    # Test generated architectures
    asyncio.run(test_all_generated_architectures())