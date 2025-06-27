# ArchiMate Diagram Viewing Guide

## 📊 Available Architecture Diagrams

This repository contains 8 comprehensive ArchiMate diagrams showcasing the complete architecture of the ArchiMate MCP Server across all 7 ArchiMate layers.

## 🖼️ Diagram Formats

Each architectural view is available in multiple formats:

### PlantUML Source Files (`.puml`)
- **Purpose**: Human-readable PlantUML source code
- **Usage**: Edit, modify, or regenerate diagrams
- **Tool Support**: PlantUML IDE, VS Code PlantUML extension

### SVG Vector Graphics (`.svg`)
- **Purpose**: High-quality scalable vector graphics
- **Usage**: Web viewing, documentation, presentations
- **Browser Support**: All modern browsers (Chrome, Firefox, Safari, Edge)

## 📋 Complete Diagram Catalog

### 1. 🎯 Motivation Layer
- **File**: `archi_mcp_motivation.puml` / `archi_mcp_motivation.svg`
- **Content**: Stakeholders, drivers, goals, and requirements
- **Focus**: WHY the system exists and what it aims to achieve

### 2. 📋 Strategy Layer  
- **File**: `archi_mcp_strategy_layer.puml` / `archi_mcp_strategy_layer.svg`
- **Content**: Resources, capabilities, and courses of action
- **Focus**: HOW strategic goals will be achieved

### 3. 🏗️ Layered Architecture
- **File**: `archi_mcp_layered_architecture.puml` / `archi_mcp_layered_architecture.svg`
- **Content**: Business, application, and technology layers
- **Focus**: Cross-layer relationships and dependencies

### 4. 💻 Application Structure
- **File**: `archi_mcp_application_structure.puml` / `archi_mcp_application_structure.svg`
- **Content**: Detailed application components and data flow
- **Focus**: Internal application architecture and component interactions

### 5. ⚙️ Technology Infrastructure
- **File**: `archi_mcp_technology_layer.puml` / `archi_mcp_technology_layer.svg`
- **Content**: Technology services, nodes, and infrastructure
- **Focus**: Technical platform and runtime environment

### 6. 🏗️ Physical Infrastructure
- **File**: `archi_mcp_physical_layer.puml` / `archi_mcp_physical_layer.svg`
- **Content**: Equipment, facilities, and distribution networks
- **Focus**: Physical deployment and infrastructure

### 7. 🚀 Implementation & Migration
- **File**: `archi_mcp_implementation_migration.puml` / `archi_mcp_implementation_migration.svg`
- **Content**: Project phases, deliverables, and timeline
- **Focus**: Implementation roadmap and change management

### 8. 🔗 Multi-Layer Integration
- **File**: `archi_mcp_multi_layer_integration.puml` / `archi_mcp_multi_layer_integration.svg`
- **Content**: Cross-layer relationships and traceability
- **Focus**: End-to-end architectural connections

## 🌐 Viewing Methods

### Method 1: Web Browser (Recommended)
```bash
# Open SVG files directly in any web browser
open archi_mcp_motivation.svg                    # macOS
start archi_mcp_motivation.svg                   # Windows  
xdg-open archi_mcp_motivation.svg                # Linux

# Or drag and drop SVG files into browser window
```

### Method 2: VS Code with PlantUML Extension
1. Install the PlantUML extension
2. Open any `.puml` file
3. Press `Alt+D` to preview
4. Install Java and Graphviz if prompted

### Method 3: PlantUML Server (Online)
1. Visit: http://www.plantuml.com/plantuml/uml/
2. Copy content from any `.puml` file
3. Paste into the text area
4. View rendered diagram

### Method 4: Local PlantUML Rendering
```bash
# Generate SVG from PlantUML source (requires Java + Graphviz)
java -jar plantuml.jar -tsvg archi_mcp_motivation.puml

# Generate PNG 
java -jar plantuml.jar -tpng archi_mcp_motivation.puml

# Generate all formats
java -jar plantuml.jar -tsvg -tpng *.puml
```

### Method 5: GitHub Integration
- SVG files render directly in GitHub repositories
- View any diagram by clicking the SVG file in the repository
- Perfect for documentation and sharing

## 🎨 Diagram Features

### ArchiMate Visual Elements
- **Color Coding**: Each layer has distinct colors following ArchiMate conventions
- **Shape Variety**: Different shapes for different element types
- **Icons**: Standard ArchiMate icons for element identification
- **Relationships**: Various line styles for different relationship types

### Interactive Elements
- **Tooltips**: Hover over elements to see descriptions (in compatible viewers)
- **Zoom**: SVG format supports infinite zoom without quality loss
- **Links**: Some elements may contain clickable links (viewer dependent)

### Layout Optimization
- **Direction**: Diagrams use optimal layout direction (horizontal/vertical)
- **Spacing**: Professional spacing and alignment
- **Legends**: Each diagram includes layer identification
- **Titles**: Clear, descriptive titles for each view

## 🔧 Technical Requirements

### For SVG Viewing
- **Browser**: Any modern web browser (Chrome, Firefox, Safari, Edge)
- **Image Viewer**: Any SVG-compatible image viewer
- **No Installation**: No additional software required

### For PlantUML Editing
- **Java**: Java 8 or higher
- **Graphviz**: For advanced diagram rendering
- **PlantUML JAR**: Available in this repository
- **Editor**: VS Code with PlantUML extension (recommended)

### For Local Rendering
```bash
# Install dependencies (macOS with Homebrew)
brew install java graphviz

# Install dependencies (Ubuntu/Debian)
sudo apt-get install default-jre graphviz

# Install dependencies (Windows)
# Download and install Java and Graphviz manually
```

## 📱 Mobile and Tablet Viewing

### Mobile Optimization
- SVG files scale perfectly on mobile devices
- Pinch-to-zoom supported on touch devices
- Diagrams remain readable on small screens

### Recommended Mobile Apps
- **iOS**: Any web browser, Files app
- **Android**: Chrome, Files by Google
- **Cross-platform**: Dropbox, Google Drive apps

## 🎯 Best Viewing Practices

### For Analysis
1. **Start with Motivation**: Understand the WHY
2. **Move to Strategy**: See the HOW
3. **Examine Layered**: Understand overall structure
4. **Dive into Details**: Application and Technology layers
5. **Check Implementation**: See the delivery plan
6. **Review Integration**: Understand connections

### For Presentation
1. **Use SVG Format**: Best quality for projectors
2. **Zoom to Details**: Highlight specific areas
3. **Follow Narrative**: Present layers in logical order
4. **Explain Relationships**: Point out key connections
5. **Reference Standards**: Note ArchiMate compliance

### For Development
1. **Focus on Application Structure**: Understand components
2. **Study Technology Layer**: Know the tech stack
3. **Review Implementation**: Follow development phases
4. **Check Integration**: Understand dependencies

## 🔍 Troubleshooting

### SVG Not Displaying
- **Issue**: Browser doesn't show SVG
- **Solution**: Try different browser or update current one
- **Alternative**: Use PNG versions (regenerate if needed)

### PlantUML Won't Render
- **Issue**: PlantUML source doesn't compile
- **Check**: Java and Graphviz installation
- **Verify**: PlantUML JAR file present
- **Test**: Use online PlantUML server first

### Poor Quality Display
- **Issue**: Diagrams appear blurry
- **Cause**: Using raster format instead of vector
- **Solution**: Use SVG format for best quality
- **Alternative**: Generate high-DPI PNG versions

### File Access Issues
- **Issue**: Cannot open files
- **Check**: File permissions and location
- **Verify**: Correct file extension associations
- **Try**: Different application or viewer

## 📞 Support

For viewing issues or questions:
- **GitHub Issues**: Report technical problems
- **Documentation**: Check PlantUML and ArchiMate documentation
- **Community**: ArchiMate and PlantUML communities

---

**Note**: All diagrams in this repository are generated using the ArchiMate MCP Server itself, demonstrating real-world application of the tool's capabilities.