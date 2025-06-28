"""Enhanced image display functionality for Claude Desktop."""

import base64
import tempfile
import subprocess
import os
from pathlib import Path
from typing import Tuple, Optional, Union

try:
    from mcp.server.fastmcp import Image
    MCP_IMAGE_AVAILABLE = True
except ImportError:
    MCP_IMAGE_AVAILABLE = False
    Image = None

def generate_mcp_image_object(plantuml_code: str, title: str = None) -> Union[Image, None]:
    """
    Generate FastMCP Image object for direct display in Claude Desktop.
    Returns Image object if successful, None if failed.
    """
    if not MCP_IMAGE_AVAILABLE:
        return None
        
    try:
        # Find PlantUML jar
        plantuml_jar = _find_plantuml_jar()
        if not plantuml_jar:
            return None
            
        # Create temporary PlantUML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False, encoding='utf-8') as f:
            f.write(plantuml_code)
            temp_puml = f.name
        
        try:
            # Generate PNG image using PlantUML
            cmd = [
                "java", "-jar", plantuml_jar,
                "-tpng",
                temp_puml
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return None
            
            # Find generated image file
            generated_image = Path(temp_puml).parent / f"{Path(temp_puml).stem}.png"
            
            if generated_image.exists():
                # Read image bytes and create MCP Image object
                with open(generated_image, 'rb') as img_file:
                    image_data = img_file.read()
                
                # Clean up generated image
                generated_image.unlink()
                
                # Return FastMCP Image object
                return Image(data=image_data, format="png")
            else:
                return None
                
        finally:
            # Clean up temporary files
            if os.path.exists(temp_puml):
                os.unlink(temp_puml)
                    
    except Exception as e:
        return None

def generate_claude_desktop_image(plantuml_code: str, title: str = None) -> Tuple[bool, str]:
    """
    Generate image optimized for Claude Desktop display.
    Returns (success: bool, result_message: str)
    """
    try:
        # 1. Generate PNG image
        png_success, png_result = _generate_png_image(plantuml_code, title)
        if not png_success:
            return False, f"PNG generation failed: {png_result}"
        
        # 2. Generate base64 data URL
        base64_success, base64_result = _generate_base64_data_url(plantuml_code, title)
        if not base64_success:
            return False, f"Base64 generation failed: {base64_result}"
        
        # 3. Generate online preview URLs
        urls_success, urls_result = _generate_online_urls(plantuml_code, title)
        
        # Format comprehensive response
        result = f"🖼️ **Image Generated Successfully for Claude Desktop**\\n\\n"
        result += f"**Title:** {title or 'ArchiMate Diagram'}\\n\\n"
        
        # Add PNG file info
        result += "### 📁 Local PNG File\\n"
        result += f"{png_result}\\n\\n"
        
        # Add base64 data URL (shortened for display)
        result += "### 🔗 Base64 Data URL\\n"
        if "data:image" in base64_result:
            data_url_line = [line for line in base64_result.split('\\n') if line.startswith('data:image')]
            if data_url_line:
                data_url = data_url_line[0]
                result += f"```\\n{data_url[:100]}...\\n```\\n"
                result += f"*Copy and paste this URL directly into your browser address bar to view the image.*\\n\\n"
        
        # Add online URLs if available
        if urls_success:
            result += "### 🌐 Online Preview URLs\\n"
            result += f"{urls_result}\\n\\n"
        
        # Add viewing instructions
        result += "### 📋 How to View in Claude Desktop\\n"
        result += "1. **Local File:** Open the saved PNG file with any image viewer\\n"
        result += "2. **Browser Preview:** Copy the data URL above and paste it in your browser\\n"
        result += "3. **Online Preview:** Click any of the online URLs above\\n\\n"
        
        result += "✅ **All image formats generated successfully!**"
        
        return True, result
        
    except Exception as e:
        return False, f"Image generation error: {str(e)}"

def _generate_png_image(plantuml_code: str, title: str = None) -> Tuple[bool, str]:
    """Generate PNG image file."""
    try:
        # Create output path
        timestamp = int(__import__('time').time())
        safe_title = _sanitize_filename(title or "diagram")
        output_path = f"/tmp/archimate_{safe_title}_{timestamp}.png"
        
        # Create temporary PlantUML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False) as f:
            f.write(plantuml_code)
            temp_puml = f.name
        
        try:
            # Find PlantUML jar
            plantuml_jar = _find_plantuml_jar()
            if not plantuml_jar:
                return False, "PlantUML jar not found"
            
            # Generate PNG
            cmd = [
                "java", "-jar", plantuml_jar,
                "-tpng",
                "-o", str(Path(output_path).parent),
                temp_puml
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return False, f"PlantUML error: {result.stderr}"
            
            # Check if file was created
            expected_output = Path(temp_puml).parent / f"{Path(temp_puml).stem}.png"
            if expected_output.exists():
                # Move to desired location
                expected_output.rename(output_path)
                file_size = Path(output_path).stat().st_size
                return True, f"📁 **File:** {output_path}\\n📊 **Size:** {file_size} bytes"
            else:
                return False, "PNG file was not generated"
                
        finally:
            if os.path.exists(temp_puml):
                os.unlink(temp_puml)
                
    except Exception as e:
        return False, f"PNG generation error: {str(e)}"

def _generate_base64_data_url(plantuml_code: str, title: str = None) -> Tuple[bool, str]:
    """Generate base64 data URL."""
    try:
        # Create temporary PlantUML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False) as f:
            f.write(plantuml_code)
            temp_puml = f.name
        
        try:
            plantuml_jar = _find_plantuml_jar()
            if not plantuml_jar:
                return False, "PlantUML jar not found"
            
            # Generate PNG
            cmd = [
                "java", "-jar", plantuml_jar,
                "-tpng",
                temp_puml
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return False, f"PlantUML error: {result.stderr}"
            
            # Find generated image
            generated_image = Path(temp_puml).parent / f"{Path(temp_puml).stem}.png"
            if generated_image.exists():
                # Read and encode as base64
                with open(generated_image, 'rb') as img_file:
                    image_data = img_file.read()
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                
                data_url = f"data:image/png;base64,{base64_data}"
                file_size = len(image_data)
                
                # Clean up
                generated_image.unlink()
                
                return True, f"🔗 **Data URL:** {data_url}\\n📏 **Size:** {file_size} bytes"
            else:
                return False, "Base64 image generation failed"
                
        finally:
            if os.path.exists(temp_puml):
                os.unlink(temp_puml)
                
    except Exception as e:
        return False, f"Base64 generation error: {str(e)}"

def _generate_online_urls(plantuml_code: str, title: str = None) -> Tuple[bool, str]:
    """Generate online preview URLs."""
    try:
        # Simple PlantUML URL encoding (basic version)
        import zlib
        
        compressed = zlib.compress(plantuml_code.encode('utf-8'))
        
        # PlantUML base64 encoding
        def encode6bit(b):
            if b < 10:
                return chr(48 + b)
            b -= 10
            if b < 26:
                return chr(65 + b)
            b -= 26
            if b < 26:
                return chr(97 + b)
            b -= 26
            if b == 0:
                return '-'
            if b == 1:
                return '_'
            return '?'
        
        result = ""
        for i in range(0, len(compressed), 3):
            b1 = compressed[i] if i < len(compressed) else 0
            b2 = compressed[i + 1] if i + 1 < len(compressed) else 0
            b3 = compressed[i + 2] if i + 2 < len(compressed) else 0
            
            result += encode6bit(b1 >> 2)
            result += encode6bit(((b1 & 0x3) << 4) | (b2 >> 4))
            result += encode6bit(((b2 & 0xF) << 2) | (b3 >> 6))
            result += encode6bit(b3 & 0x3F)
        
        encoded = result
        
        # Generate URLs
        urls = {
            "Official PlantUML": f"http://www.plantuml.com/plantuml/png/{encoded}",
            "Alternative Server": f"https://plantuml-server.kkeisuke.app/png/{encoded}",
            "Kroki Server": f"https://kroki.io/plantuml/png/{base64.urlsafe_b64encode(plantuml_code.encode()).decode()}"
        }
        
        result_text = ""
        for server_name, url in urls.items():
            result_text += f"**{server_name}:** {url}\\n"
        
        return True, result_text
        
    except Exception as e:
        return False, f"URL generation error: {str(e)}"

def _find_plantuml_jar() -> Optional[str]:
    """Find PlantUML jar in common locations."""
    possible_locations = [
        "/Users/patrik/Projects/archi-mcp/plantuml.jar",
        "./plantuml.jar", 
        "/usr/local/bin/plantuml.jar",
        "/opt/homebrew/bin/plantuml.jar"
    ]
    
    for jar_path in possible_locations:
        if os.path.exists(jar_path):
            return jar_path
    
    return None

def _sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file creation."""
    import re
    # Remove or replace problematic characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove extra spaces and limit length
    sanitized = '_'.join(sanitized.split())[:50]
    return sanitized