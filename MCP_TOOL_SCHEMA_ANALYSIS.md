# MCP Tool Schema Analysis - `create_archimate_diagram`

## Overview

This document provides the exact MCP tool schema that gets sent to clients for the `create_archimate_diagram` tool in the ArchiMate MCP Server. The schema was extracted by analyzing how FastMCP generates and exposes tool definitions through the MCP protocol.

## How FastMCP Generates Tool Schemas

### 1. Tool Registration Process

```python
@mcp.tool()
def create_archimate_diagram(diagram: DiagramInput) -> str:
    """Tool function with Pydantic model parameter"""
```

### 2. Schema Generation Pipeline

1. **Function Introspection**: FastMCP uses `inspect.signature()` to analyze the function
2. **Pydantic Type Adapter**: Creates a `TypeAdapter` from the function signature 
3. **JSON Schema Generation**: Calls `type_adapter.json_schema()` to generate JSON Schema
4. **Schema Compression**: Uses `compress_schema()` to optimize the schema (removes excluded parameters)
5. **MCP Tool Creation**: Converts to `mcp.types.Tool` object with `inputSchema` field

### 3. Key Components

- **FastMCP Tool Class**: Internal representation with function reference
- **MCP Tool Object**: Protocol-compliant tool without function references
- **Input Schema**: JSON Schema describing expected parameters

## Complete MCP Tool Schema

The exact schema that MCP clients receive via `tools/list`:

```json
{
  "name": "create_archimate_diagram",
  "description": "Generate complete ArchiMate diagrams from structured input with elements and relationships.\n\nAutomatically detects language from content and translates layer names and relationship labels.\nSupports Slovak language detection via Slovak text patterns and diacritics.\nWhen Slovak content detected: layer names and relationship labels are translated to Slovak.\n\nAvailable languages: en (English), sk (Slovak) - detected automatically\n\nOutputs are saved to CWD/exports/YYYYMMDD_HHMMSS/ directory with:\n- diagram.puml: Validated PlantUML code\n- diagram.png: Generated PNG (mandatory)\n- architecture.md: Extended textual architecture representation with PNG link\n- generation.log: Debug log with detailed generation info\n- metadata.json: Diagram metadata and statistics",
  "inputSchema": {
    "$defs": {
      "DiagramInput": {
        "properties": {
          "elements": {
            "description": "List of ArchiMate elements",
            "items": {
              "$ref": "#/$defs/ElementInput"
            },
            "title": "Elements",
            "type": "array"
          },
          "relationships": {
            "description": "List of relationships",
            "items": {
              "$ref": "#/$defs/RelationshipInput"
            },
            "title": "Relationships",
            "type": "array"
          },
          "title": {
            "anyOf": [
              {"type": "string"},
              {"type": "null"}
            ],
            "default": null,
            "description": "Diagram title",
            "title": "Title"
          },
          "description": {
            "anyOf": [
              {"type": "string"},
              {"type": "null"}
            ],
            "default": null,
            "description": "Diagram description",
            "title": "Description"
          },
          "layout": {
            "anyOf": [
              {
                "additionalProperties": true,
                "type": "object"
              },
              {"type": "null"}
            ],
            "description": "Layout configuration",
            "title": "Layout"
          },
          "language": {
            "anyOf": [
              {"type": "string"},
              {"type": "null"}
            ],
            "default": "en",
            "description": "Language code for translations (en, sk)",
            "title": "Language"
          }
        },
        "required": ["elements"],
        "title": "DiagramInput",
        "type": "object"
      },
      "ElementInput": {
        "properties": {
          "id": {
            "description": "Unique element identifier",
            "title": "Id",
            "type": "string"
          },
          "name": {
            "description": "Element display name",
            "title": "Name",
            "type": "string"
          },
          "element_type": {
            "description": "ArchiMate element type",
            "title": "Element Type",
            "type": "string"
          },
          "layer": {
            "description": "ArchiMate layer",
            "title": "Layer",
            "type": "string"
          },
          "description": {
            "anyOf": [
              {"type": "string"},
              {"type": "null"}
            ],
            "default": null,
            "description": "Element description",
            "title": "Description"
          },
          "stereotype": {
            "anyOf": [
              {"type": "string"},
              {"type": "null"}
            ],
            "default": null,
            "description": "Element stereotype",
            "title": "Stereotype"
          },
          "properties": {
            "anyOf": [
              {
                "additionalProperties": true,
                "type": "object"
              },
              {"type": "null"}
            ],
            "title": "Properties"
          }
        },
        "required": ["id", "name", "element_type", "layer"],
        "title": "ElementInput",
        "type": "object"
      },
      "RelationshipInput": {
        "properties": {
          "id": {
            "description": "Unique relationship identifier",
            "title": "Id",
            "type": "string"
          },
          "from_element": {
            "description": "Source element ID",
            "title": "From Element",
            "type": "string"
          },
          "to_element": {
            "description": "Target element ID",
            "title": "To Element",
            "type": "string"
          },
          "relationship_type": {
            "description": "ArchiMate relationship type",
            "title": "Relationship Type",
            "type": "string"
          },
          "description": {
            "anyOf": [
              {"type": "string"},
              {"type": "null"}
            ],
            "default": null,
            "description": "Relationship description",
            "title": "Description"
          },
          "direction": {
            "anyOf": [
              {"type": "string"},
              {"type": "null"}
            ],
            "default": null,
            "description": "Direction hint for layout",
            "title": "Direction"
          },
          "label": {
            "anyOf": [
              {"type": "string"},
              {"type": "null"}
            ],
            "default": null,
            "description": "Relationship label",
            "title": "Label"
          }
        },
        "required": ["id", "from_element", "to_element", "relationship_type"],
        "title": "RelationshipInput",
        "type": "object"
      }
    },
    "properties": {
      "diagram": {
        "$ref": "#/$defs/DiagramInput",
        "title": "Diagram"
      }
    },
    "required": ["diagram"],
    "type": "object"
  },
  "annotations": null
}
```

## Schema Structure Analysis

### Top-Level Tool Properties

- **name**: `"create_archimate_diagram"`
- **description**: 762-character detailed description
- **inputSchema**: JSON Schema defining expected parameters
- **annotations**: `null` (no additional metadata)

### Input Schema Structure

#### Root Parameters
- **Required**: `["diagram"]`
- **Properties**: Single `diagram` parameter referencing `DiagramInput`

#### DiagramInput Schema
- **Required**: `["elements"]`
- **Properties**:
  - `elements`: Array of `ElementInput` objects (required)
  - `relationships`: Array of `RelationshipInput` objects (optional)
  - `title`: String or null (optional, default: null)
  - `description`: String or null (optional, default: null)
  - `layout`: Object with additional properties or null (optional)
  - `language`: String or null (optional, default: "en")

#### ElementInput Schema
- **Required**: `["id", "name", "element_type", "layer"]`
- **Properties**:
  - `id`: String (unique identifier)
  - `name`: String (display name)
  - `element_type`: String (ArchiMate element type)
  - `layer`: String (ArchiMate layer)
  - `description`: String or null (optional)
  - `stereotype`: String or null (optional)
  - `properties`: Object with additional properties or null (optional)

#### RelationshipInput Schema
- **Required**: `["id", "from_element", "to_element", "relationship_type"]`
- **Properties**:
  - `id`: String (unique identifier)
  - `from_element`: String (source element ID)
  - `to_element`: String (target element ID)
  - `relationship_type`: String (ArchiMate relationship type)
  - `description`: String or null (optional)
  - `direction`: String or null (optional, layout hint)
  - `label`: String or null (optional, custom label)

## Key Findings

### 1. Pydantic Integration
- FastMCP automatically generates JSON Schema from Pydantic models
- Uses JSON Schema Draft 7 format with `$defs` for reusable components
- Handles optional fields with `anyOf` union types

### 2. Type Safety
- All required fields are properly marked in the schema
- Optional fields have explicit `null` types and default values
- String fields have appropriate descriptions

### 3. Nested Object Support
- Complex nested structures are supported via `$ref` references
- Reusable components defined in `$defs` section
- Arrays of objects properly typed with `items` schemas

### 4. MCP Protocol Compliance
- Tool schema follows MCP protocol specification exactly
- `inputSchema` is valid JSON Schema
- No function references in serialized form

## Files Generated

1. **create_archimate_diagram_mcp_protocol.json**: Individual tool schema
2. **tools_list_response.json**: Complete MCP `tools/list` response
3. **create_archimate_diagram_schema.json**: FastMCP internal schema

## Usage for Clients

MCP clients receive this schema via the `tools/list` request and can use it to:

1. **Validate Input**: Ensure tool calls match expected schema
2. **Generate UI**: Create forms or interfaces based on schema
3. **Type Safety**: Provide IDE completion and validation
4. **Documentation**: Auto-generate tool documentation

## Technical Implementation

The schema generation process in FastMCP:

```python
# 1. Function decorated with @mcp.tool()
@mcp.tool()
def create_archimate_diagram(diagram: DiagramInput) -> str:
    ...

# 2. FastMCP creates FunctionTool
tool = FunctionTool.from_function(fn=create_archimate_diagram)

# 3. Generates JSON Schema from function signature
type_adapter = get_cached_typeadapter(fn)
schema = type_adapter.json_schema()

# 4. Compresses schema (removes context parameters)
schema = compress_schema(schema, prune_params=prune_params)

# 5. Creates MCP Tool object
mcp_tool = tool.to_mcp_tool()
```

This provides a complete view of how FastMCP generates and exposes tool schemas through the MCP protocol.