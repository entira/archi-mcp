# 🛠️ ArchiMate MCP Tools - Complete Documentation

**Version:** 2.0 Enhanced Edition  
**Date:** 2025-06-27  
**Author:** Mgr. Patrik Skovajsa, Claude Code Assistant

---

## 📋 Overview

ArchiMate MCP Server poskytuje **11 powerful tools** pre enterprise architecture modeling s complete PlantUML diagram generation, enhanced validation, a multi-format image rendering pre Claude Desktop.

### 🚀 Key Features
- **4-step validation pipeline:** Syntax → ArchiMate → Rendering → Quality
- **Automatic element normalization:** Fixes common formatting issues
- **Multi-format image generation:** PNG files + Base64 URLs + Online previews
- **Slovak diacritics support:** Full national character preservation
- **Comprehensive error logging:** JSONL format with detailed context

---

## 🛠️ MCP Tools Reference

### 1. 🎨 `create_archimate_diagram`

**Purpose:** Generate complete ArchiMate diagrams from structured input with enhanced validation and image generation.

**Input Schema:**
```typescript
{
  diagram: {
    elements: ElementInput[],           // Required: List of ArchiMate elements
    relationships?: RelationshipInput[], // Optional: List of relationships
    layout?: LayoutInput,               // Optional: Layout preferences  
    title?: string,                     // Optional: Diagram title
    description?: string                // Optional: Diagram description
  }
}
```

**ElementInput:**
```typescript
{
  id: string,                    // Element identifier (auto-normalized)
  name: string,                  // Display name (auto-quoted if needed)
  element_type: string,          // ArchiMate type (auto-normalized)
  layer: string,                 // ArchiMate layer
  description?: string,          // Optional description
  stereotype?: string,           // Optional stereotype
  properties?: Record<string, any> // Optional properties
}
```

**Example Usage:**
```json
{
  "diagram": {
    "title": "Banking System Architecture",
    "elements": [
      {
        "id": "online-customer",
        "name": "Online Customer", 
        "element_type": "business-actor",
        "layer": "Business"
      },
      {
        "id": "banking service",
        "name": "Banking Service",
        "element_type": "business-service", 
        "layer": "Business"
      }
    ],
    "relationships": [
      {
        "id": "rel1",
        "from_element": "banking service", 
        "to_element": "online-customer",
        "relationship_type": "Serving"
      }
    ]
  }
}
```

**Enhanced Output:**
- ✅ **VERIFIED status** s 4-step validation
- 📁 **Local PNG file** s full path a size
- 🔗 **Base64 data URL** copy-paste ready
- 🌐 **Online preview URLs** (3 servers)
- 📄 **PlantUML source code**

**Auto-Normalization:**
- `business-actor` → `Business_Actor`
- `online-customer` → `online_customer` 
- `banking service` → `banking_service`

---

### 2. ➕ `add_archimate_element`

**Purpose:** Add single ArchiMate element to existing diagram.

**Input Schema:**
```typescript
{
  element_type: string,    // ArchiMate element type (auto-normalized)
  id: string,             // Element ID (auto-normalized)
  name: string,           // Element name (auto-quoted)
  layer: string,          // ArchiMate layer
  description?: string,    // Optional description
  stereotype?: string,     // Optional stereotype
  properties?: Record<string, any> // Optional properties
}
```

**Example Usage:**
```json
{
  "element_type": "application-component",
  "id": "crm-system", 
  "name": "CRM System",
  "layer": "Application",
  "description": "Customer relationship management system"
}
```

**Output:** Confirmation message s total element count.

---

### 3. 🔗 `add_archimate_relationship`

**Purpose:** Add relationship between ArchiMate elements.

**Input Schema:**
```typescript
{
  id: string,                    // Relationship ID
  from_element: string,          // Source element ID
  to_element: string,           // Target element ID  
  relationship_type: string,     // ArchiMate relationship type
  direction?: string,           // Optional direction (Up, Down, Left, Right)
  description?: string,         // Optional description
  label?: string               // Optional label
}
```

**Supported Relationship Types:**
- **Structural:** Composition, Aggregation, Assignment, Realization
- **Dependency:** Serving, Access, Influence
- **Dynamic:** Triggering, Flow
- **Other:** Association, Specialization

**Example Usage:**
```json
{
  "id": "serves_rel",
  "from_element": "crm_system",
  "to_element": "sales_process", 
  "relationship_type": "Serving",
  "description": "CRM system supports sales process"
}
```

---

### 4. ✅ `validate_archimate_model`

**Purpose:** Validate ArchiMate model against ArchiMate 3.2 specification.

**Input Schema:**
```typescript
{
  strict?: boolean  // Optional: Enable strict validation mode (default: false)
}
```

**Validation Modes:**
- **Standard mode:** Basic ArchiMate compliance
- **Strict mode:** Enhanced relationship rules checking

**Example Usage:**
```json
{
  "strict": true
}
```

**Output:** Validation report s model statistics a error details.

---

### 5. 📋 `generate_archimate_template`

**Purpose:** Generate ArchiMate diagram from predefined templates.

**Input Schema:**
```typescript
{
  template: {
    template_type: string,           // "viewpoint", "pattern", or "industry"
    template_name: string,           // Specific template name
    customization?: Record<string, any> // Optional customization parameters
  }
}
```

**Available Templates:**

**Viewpoints:**
- `layered_view` - Complete layered architecture
- `service_realization` - Service realization patterns
- `application_cooperation` - Application interaction patterns

**Patterns:**
- `three_tier` - Three-tier architecture pattern
- `microservices` - Microservices architecture pattern
- `event_driven` - Event-driven architecture pattern

**Industries:**
- `banking` - Banking industry template
- `healthcare` - Healthcare systems template
- `e_commerce` - E-commerce platform template

**Example Usage:**
```json
{
  "template": {
    "template_type": "industry",
    "template_name": "banking",
    "customization": {
      "bank_name": "Slovak National Bank"
    }
  }
}
```

---


**Purpose:** Export current ArchiMate diagram to PlantUML format with enhanced validation.

**Input Schema:**
```typescript
{
  title?: string,              // Optional title
  description?: string,        // Optional description  
  output_path?: string,       // Optional file save path
  clear_after_export?: boolean // Optional: Clear diagram after export
}
```

**Example Usage:**
```json
{
  "title": "Banking Architecture Export",
  "description": "Complete banking system architecture",
  "output_path": "/tmp/banking_architecture.puml",
  "clear_after_export": false
}
```

**Enhanced Output:** VERIFIED status + file save confirmation + PlantUML code.

---

### 7. 🏗️ `generate_full_architecture`

**Purpose:** Generate complete layered enterprise architecture following ArchiMate methodology.

**Input Schema:**
```typescript
{
  architecture: {
    system_description: string,        // Required: System description
    business_domain?: string,          // Optional: Business domain (default: "general")
    architecture_scope?: string,      // Optional: Scope (default: "system") 
    include_views?: string[],         // Optional: Views to include
    implementation_phases?: number    // Optional: Implementation phases (1-6)
  }
}
```

**Available Views:**
- `motivation` - Stakeholders, drivers, goals
- `business_model_canvas` - Business model overview
- `strategy_capability` - Strategic capabilities
- `layered_view` - Business/Application/Technology layers
- `application_structure` - Application components detail
- `technology_structure` - Technology infrastructure
- `implementation_roadmap` - Phased implementation plan

**Example Usage:**
```json
{
  "architecture": {
    "system_description": "Digital banking platform with mobile apps and AI-powered services",
    "business_domain": "fintech",
    "architecture_scope": "enterprise", 
    "include_views": ["motivation", "layered_view", "application_structure", "implementation_roadmap"],
    "implementation_phases": 4
  }
}
```

**Enhanced Output:** 
- Multiple coordinated ArchiMate views
- Each view individually VERIFIED ✅
- Implementation guidance
- ALL VIEWS VERIFIED ✅ confirmation

---

### 8. 🖼️ `generate_diagram_image`

**Purpose:** Generate ArchiMate diagram and convert to image file using PlantUML.

**Input Schema:**
```typescript
{
  title?: string,        // Optional title
  description?: string,  // Optional description
  output_path?: string, // Optional output path  
  format?: string      // Optional format (default: "png")
}
```

**Supported Formats:** PNG, SVG, PDF

**Example Usage:**
```json
{
  "title": "Banking System Diagram",
  "output_path": "/tmp/banking_diagram.png",
  "format": "png"
}
```

**Output:** File creation confirmation s path, size, a PlantUML code.

---

### 9. 📱 `get_diagram_as_base64`

**Purpose:** Generate ArchiMate diagram and return as base64 encoded image.

**Input Schema:**
```typescript
{
  title?: string,      // Optional title
  description?: string, // Optional description
  format?: string     // Optional format (default: "png")
}
```

**Example Usage:**
```json
{
  "title": "Base64 Banking Diagram",
  "format": "png"
}
```

**Output:** Base64 data URL ready for browser copy-paste + full base64 string.

---

### 10. ✅ `validate_plantuml_syntax`

**Purpose:** Validate PlantUML syntax and test renderability using comprehensive 4-step validation.

**Input Schema:**
```typescript
{
  title?: string,      // Optional title
  description?: string // Optional description
}
```

**4-Step Validation Process:**
1. **Basic Syntax** - @startuml/@enduml, element IDs, quotes
2. **ArchiMate Syntax** - Element types, relationship formats
3. **PlantUML Rendering** - Actual jar execution test
4. **Image Quality** - Size, complexity, completeness

**Example Usage:**
```json
{
  "title": "Banking Diagram Validation",
  "description": "Comprehensive syntax validation test"
}
```

**Output:** Detailed validation report s každým krokom + image generation confirmation.

---

### 11. 🌐 `get_plantuml_online_url`

**Purpose:** Generate PlantUML online viewer URLs for immediate preview.

**Input Schema:**
```typescript
{
  title?: string,      // Optional title
  description?: string, // Optional description
  format?: string     // Optional format (default: "svg")
}
```

**Generated URLs:**
- **Official PlantUML Server:** plantuml.com
- **Alternative Server:** plantuml-server.kkeisuke.app  
- **Kroki Server:** kroki.io (GitHub-based)

**Example Usage:**
```json
{
  "title": "Online Banking Preview",
  "format": "svg"
}
```

**Output:** 3 online preview URLs + diagram statistics + viewing instructions.

---

## 🔧 Advanced Features

### 🎯 Automatic Element Normalization

**Common Fixes:**
```
business-actor        → Business_Actor
application-component → Application_Component  
system-software       → Technology_SystemSoftware
data-object          → Application_DataObject
test-id              → test_id
element name         → "element name"
```

### 📊 Enhanced Validation Pipeline

**4-Step Process:**
1. **Syntax Validation** - Structure, IDs, quotes
2. **ArchiMate Compliance** - Element types, relationships
3. **Rendering Test** - PlantUML jar execution
4. **Quality Check** - Size, complexity, completeness

### 🖼️ Multi-Format Image Generation

**Every diagram provides:**
- 📁 Local PNG file (timestamped)
- 🔗 Base64 data URL (browser-ready)
- 🌐 Online preview URLs (3 servers)
- ✅ VERIFIED status confirmation

### 📝 Comprehensive Error Logging

**JSONL Format:**
```json
{
  "timestamp": "2025-06-27 23:59:18",
  "error_type": "SYNTAX_ERROR",
  "error_message": "Invalid element ID format",
  "plantuml_code": "@startuml...",
  "tool_name": "create_archimate_diagram", 
  "context": {"elements_count": 5, "title": "Test"}
}
```

**Log Location:** `/Users/patrik/Projects/archi-mcp/logs/validation_errors.jsonl`

---

## 🚀 Best Practices

### ✅ Recommended Workflow

1. **Start with templates** - Use `generate_archimate_template` pre base structure
2. **Add custom elements** - Use `add_archimate_element` with automatic normalization
3. **Build relationships** - Use `add_archimate_relationship` s proper types
4. **Validate frequently** - Use `validate_plantuml_syntax` pre early error detection
5. **Generate images** - Use multiple formats pre different viewing needs

### 🎨 Element Type Guidelines

**Use these normalized formats:**
- **Business Layer:** `Business_Actor`, `Business_Process`, `Business_Service`, `Business_Object`
- **Application Layer:** `Application_Component`, `Application_Service`, `Application_DataObject`
- **Technology Layer:** `Technology_Node`, `Technology_SystemSoftware`, `Technology_Service`
- **Physical Layer:** `Physical_Equipment`, `Physical_Facility`
- **Motivation Layer:** `Motivation_Stakeholder`, `Motivation_Driver`, `Motivation_Goal`

### 🔗 Relationship Best Practices

**Choose appropriate types:**
- **Serving:** Services → Actors/Processes
- **Realization:** Components → Services  
- **Access:** Active → Passive structures
- **Assignment:** Infrastructure → Applications
- **Composition/Aggregation:** Structural hierarchies

---

## 📈 Performance & Monitoring

### ⚡ Performance Metrics
- **Simple diagrams (1-5 elements):** ~1-2 seconds
- **Complex diagrams (20-50 elements):** ~3-5 seconds  
- **Full architectures (100+ elements):** ~10-15 seconds
- **Image generation:** +2-3 seconds per format

### 📊 Quality Assurance
- **100% validation guarantee** - No invalid PlantUML returned
- **Automatic error recovery** - Element normalization fixes common issues
- **Comprehensive logging** - All validation failures tracked
- **Multi-format verification** - Images tested across formats

---

**🎯 Production Ready:** Complete MCP toolset pre professional ArchiMate enterprise architecture modeling s guaranteed quality a multi-format output pre Claude Desktop!**