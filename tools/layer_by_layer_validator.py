#!/usr/bin/env python3
"""Layer-by-layer ArchiMate architecture validator and generator."""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from archi_mcp.server import ArchiMCPServer
from plantuml_validator import PlantUMLValidator


class LayerByLayerValidator:
    """Validates and generates ArchiMate diagrams layer by layer."""
    
    def __init__(self):
        """Initialize the validator."""
        self.validator = PlantUMLValidator('plantuml.jar')
        self.server = ArchiMCPServer()
        self.output_dir = Path("architecture_diagrams")
        self.output_dir.mkdir(exist_ok=True)
    
    async def generate_all_layers(self, system_description: str, business_domain: str = "general") -> Dict[str, Tuple[bool, str]]:
        """Generate and validate all architecture layers."""
        print(f"🏗️ Generating all architecture layers for: {system_description}")
        print("=" * 80)
        
        # Define layers to test individually
        layers = [
            ("motivation", "Stakeholders, drivers, goals and requirements"),
            ("business_model_canvas", "Business model and value propositions"),
            ("value_stream", "Value creation flow via capabilities"),
            ("strategy_capability", "Strategic goals and capabilities"),
            ("layered_view", "Business, application, technology structure"),
            ("interaction_view", "Actor and process interactions"),
            ("application_structure", "Detailed application components"),
            ("technology_structure", "Infrastructure components"),
            ("implementation_roadmap", "Phased delivery timeline")
        ]
        
        results = {}
        
        for layer_name, description in layers:
            print(f"\n📋 Layer: {layer_name.replace('_', ' ').title()}")
            print(f"   Description: {description}")
            print("-" * 60)
            
            try:
                # Generate single layer
                args = {
                    "system_description": system_description,
                    "business_domain": business_domain,
                    "architecture_scope": "system",
                    "include_views": [layer_name],
                    "implementation_phases": 3
                }
                
                result = await self.server._generate_full_architecture(args)
                content = result.content[0].text
                
                # Extract PlantUML diagram
                plantuml_diagram = self._extract_plantuml(content)
                
                if plantuml_diagram:
                    # Validate syntax
                    is_valid, message = self.validator.validate_puml_syntax(plantuml_diagram)
                    
                    if is_valid:
                        print("   ✅ Syntax validation: PASSED")
                        
                        # Save diagram file
                        diagram_file = self.output_dir / f"{layer_name}.puml"
                        with open(diagram_file, 'w') as f:
                            f.write(plantuml_diagram)
                        print(f"   💾 Saved: {diagram_file}")
                        
                        # Render to SVG and PNG
                        svg_success = self._render_diagram(plantuml_diagram, layer_name, "svg")
                        png_success = self._render_diagram(plantuml_diagram, layer_name, "png")
                        
                        render_status = []
                        if svg_success:
                            render_status.append("SVG")
                        if png_success:
                            render_status.append("PNG")
                        
                        if render_status:
                            print(f"   🎨 Rendered: {', '.join(render_status)}")
                        else:
                            print("   ⚠️  Rendering failed (but syntax is valid)")
                        
                        results[layer_name] = (True, f"Valid - {', '.join(render_status) if render_status else 'Validation only'}")
                    else:
                        print(f"   ❌ Syntax validation: FAILED - {message}")
                        
                        # Save debug version
                        debug_file = self.output_dir / f"{layer_name}_debug.puml"
                        with open(debug_file, 'w') as f:
                            f.write(plantuml_diagram)
                        print(f"   🐛 Debug saved: {debug_file}")
                        
                        results[layer_name] = (False, f"Invalid syntax: {message}")
                else:
                    print("   ❌ No PlantUML diagram found in output")
                    results[layer_name] = (False, "No diagram generated")
                    
            except Exception as e:
                print(f"   ❌ Generation failed: {e}")
                results[layer_name] = (False, f"Generation error: {str(e)}")
        
        return results
    
    def _extract_plantuml(self, content: str) -> str:
        """Extract PlantUML diagram from MCP server output."""
        lines = content.split('\n')
        in_plantuml = False
        diagram_lines = []
        
        for line in lines:
            if '```plantuml' in line:
                in_plantuml = True
                continue
            elif in_plantuml and '```' in line:
                break
            elif in_plantuml:
                diagram_lines.append(line)
        
        return '\n'.join(diagram_lines) if diagram_lines else ""
    
    def _render_diagram(self, plantuml_content: str, layer_name: str, format: str) -> bool:
        """Render diagram to specified format."""
        try:
            output_path = self.output_dir / f"{layer_name}.{format}"
            
            if format == "svg":
                success, message = self.validator.render_to_svg(plantuml_content, str(output_path))
            elif format == "png":
                success, message = self.validator.render_to_png(plantuml_content, str(output_path))
            else:
                return False
            
            return success
        except Exception:
            return False
    
    def generate_summary_report(self, results: Dict[str, Tuple[bool, str]]) -> None:
        """Generate summary report of all layer validations."""
        print("\n" + "=" * 80)
        print("📊 LAYER-BY-LAYER VALIDATION SUMMARY")
        print("=" * 80)
        
        total_layers = len(results)
        valid_layers = sum(1 for valid, _ in results.values() if valid)
        
        print(f"📈 Overall Results: {valid_layers}/{total_layers} layers valid ({valid_layers/total_layers*100:.1f}%)")
        print()
        
        # Group by status
        valid_results = []
        invalid_results = []
        
        for layer_name, (is_valid, message) in results.items():
            layer_display = layer_name.replace('_', ' ').title()
            if is_valid:
                valid_results.append((layer_display, message))
            else:
                invalid_results.append((layer_display, message))
        
        if valid_results:
            print("✅ WORKING LAYERS:")
            for layer, message in valid_results:
                print(f"   • {layer}: {message}")
            print()
        
        if invalid_results:
            print("❌ PROBLEMATIC LAYERS:")
            for layer, message in invalid_results:
                print(f"   • {layer}: {message}")
            print()
        
        # File locations
        print("📁 Generated Files:")
        if self.output_dir.exists():
            puml_files = list(self.output_dir.glob("*.puml"))
            svg_files = list(self.output_dir.glob("*.svg"))
            png_files = list(self.output_dir.glob("*.png"))
            
            print(f"   📄 PlantUML files: {len(puml_files)} in {self.output_dir}/")
            print(f"   🖼️  SVG files: {len(svg_files)} in {self.output_dir}/")
            print(f"   🎨 PNG files: {len(png_files)} in {self.output_dir}/")
        
        print("\n💡 Local Viewing Instructions:")
        print("   1. PlantUML files (.puml): Open with PlantUML editor/plugin")
        print("   2. SVG files (.svg): Open in web browser or vector graphics editor")
        print("   3. PNG files (.png): Open with any image viewer")
        print("   4. Online: Upload .puml to https://www.plantuml.com/plantuml/uml/")


async def main():
    """Main function to run layer-by-layer validation."""
    print("🧪 ArchiMate Layer-by-Layer Validator")
    print("Running in background mode - no window focus interruptions")
    print("=" * 80)
    
    validator = LayerByLayerValidator()
    
    # Test with ArchiMate MCP Server itself
    system_description = "ArchiMate MCP Server - Enterprise architecture modeling tool with Claude Desktop integration"
    business_domain = "general"
    
    try:
        results = await validator.generate_all_layers(system_description, business_domain)
        validator.generate_summary_report(results)
        
        print("\n🎉 Layer-by-layer validation completed!")
        print("All files saved to architecture_diagrams/ directory")
        
    except KeyboardInterrupt:
        print("\n⏹️  Validation interrupted by user")
    except Exception as e:
        print(f"\n💥 Validation failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())