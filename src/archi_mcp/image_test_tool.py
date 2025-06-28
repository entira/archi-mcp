"""Test tool for image display in Claude Desktop - rôzne prístupy."""

import base64
import tempfile
import subprocess
import os
from pathlib import Path
from typing import Union, Optional

try:
    from fastmcp import Image
    MCP_IMAGE_AVAILABLE = True
except ImportError:
    MCP_IMAGE_AVAILABLE = False
    Image = None

def create_simple_test_image() -> bytes:
    """Vytvorí jednoduchý test PNG obrázok pomocou PlantUML."""
    simple_plantuml = """@startuml
rectangle "Test Image" as test #lightblue
note right of test
  This is a test image
  for Claude Desktop
end note
@enduml"""
    
    # Vytvor dočasný PlantUML súbor
    with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False, encoding='utf-8') as f:
        f.write(simple_plantuml)
        temp_puml = f.name
    
    try:
        # Nájdi PlantUML jar
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
            raise Exception("PlantUML jar not found")
        
        # Generuj PNG
        cmd = ["java", "-jar", plantuml_jar, "-tpng", temp_puml]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise Exception(f"PlantUML error: {result.stderr}")
        
        # Načítaj vygenerovaný obrázok
        generated_image = Path(temp_puml).parent / f"{Path(temp_puml).stem}.png"
        if generated_image.exists():
            with open(generated_image, 'rb') as img_file:
                image_data = img_file.read()
            
            # Vyčisti dočasné súbory
            generated_image.unlink()
            os.unlink(temp_puml)
            
            return image_data
        else:
            raise Exception("PNG file was not generated")
            
    except Exception as e:
        # Vyčisti temp súbor aj pri chybe
        if os.path.exists(temp_puml):
            os.unlink(temp_puml)
        raise e

def test_approach_1_mcp_image() -> Union[Image, str]:
    """Test 1: FastMCP Image object - direct return."""
    if not MCP_IMAGE_AVAILABLE:
        return "❌ FastMCP Image class not available"
    
    try:
        image_data = create_simple_test_image()
        image_obj = Image(data=image_data, format="png")
        return image_obj
    except Exception as e:
        return f"❌ FastMCP Image approach failed: {str(e)}"

def test_approach_2_base64_markdown() -> str:
    """Test 2: Base64 encoded image v Markdown."""
    try:
        image_data = create_simple_test_image()
        base64_data = base64.b64encode(image_data).decode('utf-8')
        
        markdown_image = f"""## 🖼️ Test Approach 2: Base64 Markdown Image

![Test Image](data:image/png;base64,{base64_data})

**Image size:** {len(image_data)} bytes  
**Base64 size:** {len(base64_data)} characters

This should display as an inline image if Claude Desktop supports base64 data URLs in markdown.
"""
        return markdown_image
        
    except Exception as e:
        return f"❌ Base64 Markdown approach failed: {str(e)}"

def test_approach_3_file_path() -> str:
    """Test 3: Uloženie do temporary súboru a vrátenie cesty."""
    try:
        image_data = create_simple_test_image()
        
        # Ulož do /tmp s unique názvom
        import time
        timestamp = int(time.time())
        temp_path = f"/tmp/claude_image_test_{timestamp}.png"
        
        with open(temp_path, 'wb') as f:
            f.write(image_data)
        
        return f"""## 🖼️ Test Approach 3: File Path

**File saved to:** `{temp_path}`  
**File size:** {len(image_data)} bytes  
**File exists:** {os.path.exists(temp_path)}

Try opening this file path directly in Claude Desktop or your system image viewer.

**Instructions:**
1. Copy the file path: `{temp_path}`
2. Open it in Finder (macOS) or File Explorer 
3. Or drag & drop into Claude Desktop chat

This tests if Claude Desktop can handle local file references.
"""
    except Exception as e:
        return f"❌ File path approach failed: {str(e)}"

def test_approach_4_multiple_formats() -> str:
    """Test 4: Kombinácia viacerých formátov naraz."""
    try:
        image_data = create_simple_test_image()
        base64_data = base64.b64encode(image_data).decode('utf-8')
        
        # Ulož aj do súboru
        import time
        timestamp = int(time.time())
        temp_path = f"/tmp/claude_multiformat_test_{timestamp}.png"
        
        with open(temp_path, 'wb') as f:
            f.write(image_data)
        
        return f"""## 🖼️ Test Approach 4: Multiple Formats

### Format 1: Markdown Base64 Image
![Test Image](data:image/png;base64,{base64_data[:100]}...)

### Format 2: File Path Reference
**Local file:** `{temp_path}`

### Format 3: Data URL (copy-paste to browser)
```
data:image/png;base64,{base64_data[:100]}...
```

### Format 4: Online Preview URL
**PlantUML Server:** http://www.plantuml.com/plantuml/png/SoWkIImgAStDuN8goKnELKWkuWrAoE5Igi5L9EPcMcK_sTl_kOgG9yMKbEe7

**Stats:**
- Image size: {len(image_data)} bytes
- Base64 length: {len(base64_data)} characters  
- Temp file: {temp_path}

This tests which format works best in Claude Desktop.
"""
        
    except Exception as e:
        return f"❌ Multiple formats approach failed: {str(e)}"

def test_approach_5_text_visualization() -> str:
    """Test 5: ASCII/text reprezentácia ako fallback."""
    return """## 🖼️ Test Approach 5: Text Visualization

```
┌─────────────────────────────────┐
│        ArchiMate Diagram        │
├─────────────────────────────────┤
│                                 │
│  📊 Business Layer              │
│  ├── Actor: User               │
│  ├── Process: Login            │
│  └── Service: Authentication   │
│                                 │
│  💻 Application Layer           │
│  ├── Component: Web App        │
│  ├── Interface: REST API       │
│  └── Data: User Database       │
│                                 │
│  🔧 Technology Layer            │
│  ├── Node: Web Server          │
│  ├── Device: Load Balancer     │
│  └── Network: Internal LAN     │
│                                 │
└─────────────────────────────────┘
```

**Relationships:**
- User → Login Process (Assignment)
- Login Process → Authentication Service (Realization)  
- Web App → REST API (Serving)
- REST API → User Database (Access)
- Web Server → Web App (Assignment)

This is a text-based fallback visualization that always works in any chat interface.
"""

def test_all_approaches() -> str:
    """Test všetkých prístupov naraz."""
    results = []
    
    results.append("# 🧪 Claude Desktop Image Display Test Suite")
    results.append("Testing different approaches to display images in Claude Desktop chat.\n")
    
    # Test 1
    results.append("## Test 1: FastMCP Image Object")
    if MCP_IMAGE_AVAILABLE:
        results.append("✅ FastMCP Image class available - testing object return...")
        # Note: This would return an Image object, not text
        results.append("⚠️ Image object will be returned separately")
    else:
        results.append("❌ FastMCP Image class not available")
    
    # Test 2
    results.append("\n## Test 2: Base64 Markdown")
    try:
        image_data = create_simple_test_image()
        base64_data = base64.b64encode(image_data).decode('utf-8')
        results.append(f"✅ Base64 generated ({len(base64_data)} chars)")
        results.append(f"![Test](data:image/png;base64,{base64_data[:50]}...)")
    except Exception as e:
        results.append(f"❌ Failed: {e}")
    
    # Test 3  
    results.append("\n## Test 3: File Path")
    try:
        image_data = create_simple_test_image()
        import time
        timestamp = int(time.time())
        temp_path = f"/tmp/claude_test_all_{timestamp}.png"
        with open(temp_path, 'wb') as f:
            f.write(image_data)
        results.append(f"✅ File saved: {temp_path}")
    except Exception as e:
        results.append(f"❌ Failed: {e}")
    
    # Test 4
    results.append("\n## Test 4: Text Visualization")
    results.append("✅ Always available as fallback")
    
    results.append("\n## 📋 Results Summary")
    results.append("Check which approach displays images correctly in Claude Desktop.")
    results.append("Expected behavior: Images should appear inline in the chat.")
    
    return "\n".join(results)