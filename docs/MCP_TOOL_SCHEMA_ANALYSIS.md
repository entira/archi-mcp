# 🔧 ArchiMate MCP Server - Tool Schema Analysis

## Overview

This document provides a comprehensive analysis of all MCP tools exposed by the ArchiMate MCP Server, including their JSON schemas, capabilities, and usage patterns. The server implements 4 essential tools via FastMCP 2.8+ protocol for complete enterprise architecture modeling.

## Tool Schemas

### 1. `create_archimate_diagram`

**Purpose**: Generate complete ArchiMate diagrams from structured input with comprehensive enterprise architecture modeling support.

**Key Features**:
- Supports all 7 ArchiMate 3.2 layers with 55+ element types
- All 12 relationship types with directional support
- Automatic language detection (Slovak/English)
- Intelligent layout optimization
- PNG/SVG generation with live HTTP server URLs

**Schema Structure**:
```json
{
  "name": "create_archimate_diagram",
  "inputSchema": {
    "type": "object",
    "properties": {
      "diagram": {
        "$ref": "#/$defs/DiagramInput",
        "title": "Diagram",
        "description": "Complete ArchiMate diagram specification"
      }
    },
    "required": ["diagram"]
  }
}
```

**DiagramInput Properties**:
- `elements`: Array of ArchiMate elements (required)
- `relationships`: Array of relationships between elements
- `title`: Diagram title
- `description`: Diagram description
- `layout`: Layout configuration object
- `language`: Language code (auto-detected if not specified)

**ElementInput Properties**:
- `id`: Unique element identifier (required)
- `name`: Element display name (required)
- `element_type`: ArchiMate element type (required)
- `layer`: ArchiMate layer (required)
- `description`: Optional element description
- `stereotype`: Optional stereotype for specialized notation
- `properties`: Additional key-value properties

**RelationshipInput Properties**:
- `id`: Unique relationship identifier (required)
- `from_element`: Source element ID (required)
- `to_element`: Target element ID (required)
- `relationship_type`: ArchiMate relationship type (required)
- `description`: Optional relationship description
- `direction`: Layout direction hint
- `label`: Custom relationship label (max 3 words, 30 chars)

**Supported Element Types by Layer**:

**Business Layer** (12 types):
- Business_Actor, Business_Role, Business_Collaboration
- Business_Interface, Business_Function, Business_Process
- Business_Event, Business_Service, Business_Object
- Business_Contract, Business_Representation, Location

**Application Layer** (9 types):
- Application_Component, Application_Collaboration, Application_Interface
- Application_Function, Application_Interaction, Application_Process
- Application_Event, Application_Service, Data_Object

**Technology Layer** (13 types):
- Node, Device, System_Software, Technology_Collaboration
- Technology_Interface, Path, Communication_Network
- Technology_Function, Technology_Process, Technology_Interaction
- Technology_Event, Technology_Service, Artifact

**Physical Layer** (4 types):
- Equipment, Facility, Distribution_Network, Material

**Motivation Layer** (10 types):
- Stakeholder, Driver, Assessment, Goal, Outcome
- Principle, Requirement, Constraint, Meaning, Value

**Strategy Layer** (4 types):
- Resource, Capability, Course_of_Action, Value_Stream

**Implementation Layer** (5 types):
- Work_Package, Deliverable, Implementation_Event, Plateau, Gap

**Supported Relationship Types** (12 types):
- Access, Aggregation, Assignment, Association
- Composition, Flow, Influence, Realization
- Serving, Specialization, Triggering

**Layout Options**:
- `direction`: top-bottom, left-right, bottom-top, right-left
- `spacing`: compact, normal, wide
- `show_title`: true/false
- `show_legend`: true/false
- `group_by_layer`: true/false
- `show_element_types`: true/false
- `show_relationship_labels`: true/false

### 2. `analyze_current_architecture`

**Purpose**: Analyze the current in-memory architecture model and generate comprehensive insights.

**Schema**:
```json
{
  "name": "analyze_current_architecture",
  "inputSchema": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  }
}
```

**Returns**:
- Element and relationship statistics by layer
- Architecture completeness assessment (% of layers used)
- Layer distribution analysis with percentages
- Model health indicators
- Element type breakdown
- Relationship type usage statistics
- Markdown-formatted report

**Example Output Structure**:
```markdown
# Architecture Analysis Report

## Architecture Overview
- Total Elements: 25
- Total Relationships: 18
- Layers Used: 5/7
- Model Completeness: 85%

## Elements by Layer
### Business Layer (8 elements - 32.0%)
- Business Actor: Customer
- Business Service: Customer Service
...

## Architecture Insights
### Layer Distribution
- Business: 8 elements (32.0%)
- Application: 6 elements (24.0%)
...

### Element Types
- Business Actor: 2
- Application Component: 4
...
```

### 3. `test_element_normalization`

**Purpose**: Test and validate element type normalization across all ArchiMate layers.

**Schema**:
```json
{
  "name": "test_element_normalization",
  "inputSchema": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  }
}
```

**Tests**:
- Case-insensitive element type handling
- Common naming variations and abbreviations
- Layer-specific element prefixes
- Relationship type normalization
- Edge cases and error scenarios

**Normalization Examples**:
- "function" → "Business_Function"
- "STAKEHOLDER" → "Stakeholder"
- "business-actor" → "Business_Actor"
- "workpackage" → "Work_Package"
- "data object" → "Data_Object"

**Returns**: Comprehensive test results showing all normalization rules and examples.

### 4. `analyze_recent_errors`

**Purpose**: Analyze recent diagram generation errors with actionable troubleshooting guidance.

**Schema**:
```json
{
  "name": "analyze_recent_errors",
  "inputSchema": {
    "type": "object",
    "properties": {
      "minutes": {
        "type": "integer",
        "minimum": 1,
        "maximum": 60,
        "default": 10,
        "description": "Time window in minutes to analyze errors"
      }
    },
    "additionalProperties": false
  }
}
```

**Features**:
- Real-time error detection from validation logs
- Pattern recognition and error categorization
- Contextual troubleshooting recommendations
- Configurable time window (1-60 minutes)

**Error Categories**:
1. **Empty Model**: No elements defined
2. **Orphaned Relationships**: References to non-existent elements
3. **Validation Errors**: ArchiMate compliance issues
4. **System Errors**: PlantUML generation failures

**Example Output**:
```markdown
# Recent Error Analysis (Last 10 minutes)

## Summary
- Total Errors: 3
- Time Range: 2025-07-02 15:30 - 15:40
- Most Common: Orphaned Relationships (2)

## Error Categories

### Orphaned Relationships (2 errors)
**Pattern**: Relationships referencing non-existent elements
**Examples**:
- Relationship 'r1' references missing element 'customer'
- Relationship 'r2' references missing element 'service'

**How to Fix**:
1. Ensure all element IDs in relationships exist
2. Check for typos in from_element/to_element
3. Define elements before relationships

### System Errors (1 error)
**Pattern**: PlantUML generation failed
**Example**: Exit code 200 - Invalid element type

**How to Fix**:
1. Check element_type spelling
2. Use supported ArchiMate types
3. Verify layer compatibility
```

## Environment Variable Configuration

The server supports extensive configuration through environment variables:

### Language Settings
- `ARCHI_MCP_LANGUAGE`: auto|en|sk (default: auto)

### Layout Defaults
- `ARCHI_MCP_DEFAULT_DIRECTION`: vertical|horizontal (default: vertical)
- `ARCHI_MCP_DEFAULT_SPACING`: compact|normal|wide (default: compact)
- `ARCHI_MCP_DEFAULT_SHOW_TITLE`: true|false (default: false)
- `ARCHI_MCP_DEFAULT_SHOW_LEGEND`: true|false (default: false)
- `ARCHI_MCP_DEFAULT_GROUP_BY_LAYER`: true|false (default: true)
- `ARCHI_MCP_DEFAULT_SHOW_ELEMENT_TYPES`: true|false (default: false)
- `ARCHI_MCP_DEFAULT_SHOW_RELATIONSHIP_LABELS`: true|false (default: true)

### Configuration Locking
When environment variables are set, they override client-provided values. This allows administrators to enforce consistent diagram styles across an organization.

## Schema Evolution

### Version 2.0 (Current)
- Added comprehensive element type enums
- Enhanced relationship type documentation
- Improved layout parameter discovery
- Added language detection support

### Version 1.0
- Basic element and relationship support
- Simple layout configuration
- English-only support

## Integration Guidelines

### Client Discovery
Clients can discover available capabilities by examining the schema:
1. Query available element types per layer
2. Check supported relationship types
3. Review layout configuration options
4. Understand validation constraints

### Error Handling
The comprehensive schemas enable:
1. Client-side validation before submission
2. Clear error messages with specific field references
3. Suggested fixes based on common patterns
4. Real-time error analysis tool for debugging

### Best Practices
1. Always provide element IDs for reliable relationship creation
2. Use proper ArchiMate element types from the enums
3. Leverage layout parameters for consistent diagrams
4. Monitor validation errors during development
5. Use analyze_recent_errors for troubleshooting

## Conclusion

The ArchiMate MCP Server provides a comprehensive, well-documented API through these 4 tools. The detailed schemas enable:
- Full capability discovery by clients
- Type-safe integration
- Comprehensive validation
- Professional diagram generation
- Effective troubleshooting

The combination of strict schemas with intelligent normalization provides both reliability and ease of use, making it suitable for both manual and automated architecture modeling workflows.