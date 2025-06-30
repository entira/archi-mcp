# ArchiMate MCP Server - Tools Overview

## Overview
The simplified ArchiMate MCP server exposes four MCP tools focused on diagram creation and troubleshooting. These tools provide essential capabilities for generating PlantUML diagrams, inspecting the current architecture state and diagnosing recent errors.

---

## 1. `create_archimate_diagram`
**Business Purpose:** Generate a complete ArchiMate diagram from structured input.

**Business Logic:**
- **Input Processing:** Accept structured diagram data with elements, relationships and layout preferences.
- **Element Creation:** Create ArchiMate elements with normalization and proper layer assignment.
- **Relationship Management:** Establish connections between elements with validation.
- **Layout Configuration:** Apply visual layout options such as direction and grouping.
- **Validation Pipeline:** Validate generated PlantUML before returning results.

**Inputs:**
- `DiagramInput` containing elements, relationships, title and description

**Outputs:**
- Validated PlantUML code
- Optional PNG file path in `/tmp`
- Diagram statistics and validation status

**Business Value:** Enables complete architecture documentation from a single structured request.

### Real-World MCP Example

**User Request:** "Create an ArchiMate diagram showing a three-tier web application with business services, application components, and infrastructure."

**MCP Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "create_archimate_diagram",
    "arguments": {
      "diagram": {
        "title": "Three-Tier Web Application Architecture",
        "description": "Complete stack from business services to infrastructure",
        "elements": [
          {
            "id": "bs1",
            "type": "business-service",
            "name": "Customer Portal Service",
            "layer": "Business"
          },
          {
            "id": "app1",
            "type": "application-component",
            "name": "Web Application",
            "layer": "Application"
          },
          {
            "id": "app2",
            "type": "application-component",
            "name": "API Gateway",
            "layer": "Application"
          },
          {
            "id": "app3",
            "type": "application-component",
            "name": "Business Logic Server",
            "layer": "Application"
          },
          {
            "id": "tech1",
            "type": "node",
            "name": "Web Server",
            "layer": "Technology"
          },
          {
            "id": "tech2",
            "type": "node",
            "name": "Application Server",
            "layer": "Technology"
          },
          {
            "id": "tech3",
            "type": "system-software",
            "name": "PostgreSQL Database",
            "layer": "Technology"
          }
        ],
        "relationships": [
          {
            "source": "bs1",
            "target": "app1",
            "type": "serving"
          },
          {
            "source": "app1",
            "target": "app2",
            "type": "flow"
          },
          {
            "source": "app2",
            "target": "app3",
            "type": "flow"
          },
          {
            "source": "app1",
            "target": "tech1",
            "type": "assignment"
          },
          {
            "source": "app3",
            "target": "tech2",
            "type": "assignment"
          },
          {
            "source": "app3",
            "target": "tech3",
            "type": "access"
          }
        ],
        "layout": {
          "direction": "top-down",
          "groupByLayer": true
        }
      }
    }
  },
  "id": "call-001"
}
```

**MCP Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "✅ Successfully generated ArchiMate diagram: Three-Tier Web Application Architecture\n\nDiagram Statistics:\n- Elements: 7 (Business: 1, Application: 3, Technology: 3)\n- Relationships: 6\n- Validation: PASSED\n\nGenerated PlantUML:\n@startuml\n!theme archimate\ntitle Three-Tier Web Application Architecture\n\n' Business Layer\narchimate #Business <<business-service>> bs1 as \"Customer Portal Service\"\n\n' Application Layer\narchimate #Application <<application-component>> app1 as \"Web Application\"\narchimate #Application <<application-component>> app2 as \"API Gateway\"\narchimate #Application <<application-component>> app3 as \"Business Logic Server\"\n\n' Technology Layer\narchimate #Technology <<node>> tech1 as \"Web Server\"\narchimate #Technology <<node>> tech2 as \"Application Server\"\narchimate #Technology <<system-software>> tech3 as \"PostgreSQL Database\"\n\n' Relationships\nbs1 --|> app1 : serving\napp1 --> app2 : flow\napp2 --> app3 : flow\napp1 ..> tech1 : assignment\napp3 ..> tech2 : assignment\napp3 --> tech3 : access\n@enduml\n\nPNG file generated: /tmp/archimate_20241230_143527_three_tier_web_application.png"
      }
    ]
  },
  "id": "call-001"
}
```

---

## 2. `analyze_current_architecture`
**Business Purpose:** Provide a health assessment of the current in-memory architecture.

**Business Logic:**
- **State Analysis:** Examine existing elements and relationships.
- **Layer Breakdown:** Summarize elements by layer.
- **Health Assessment:** Detect common issues before validation.

**Inputs:** None

**Outputs:**
- Architecture statistics and element breakdown
- Status message indicating readiness for validation

**Business Value:** Helps verify diagram completeness and spot potential problems early.

### Real-World MCP Example

**User Request:** "Analyze the current architecture state and check if it's ready for validation."

**MCP Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "analyze_current_architecture",
    "arguments": {}
  },
  "id": "call-002"
}
```

**MCP Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "🏗️ Current Architecture Analysis\n\n📊 Architecture Statistics:\n- Total Elements: 7\n- Total Relationships: 6\n\n📋 Elements by Layer:\n- Business (1): Customer Portal Service\n- Application (3): Web Application, API Gateway, Business Logic Server\n- Technology (3): Web Server, Application Server, PostgreSQL Database\n- Strategy: 0 elements\n- Physical: 0 elements\n- Motivation: 0 elements\n- Implementation & Migration: 0 elements\n\n🔗 Relationships by Type:\n- serving: 1\n- flow: 2\n- assignment: 2\n- access: 1\n\n✅ Architecture Status: Ready for validation\n- Has elements: Yes (7)\n- Has relationships: Yes (6)\n- Cross-layer connections: Yes\n- Model appears complete for basic three-tier architecture\n\n💡 Recommendations:\n- Consider adding motivation elements (goals, requirements)\n- Add stakeholders to show business context\n- Include principles or constraints for governance"
      }
    ]
  },
  "id": "call-002"
}
```

---

## 3. `test_element_normalization`
**Business Purpose:** Verify element type normalization across all layers.

**Business Logic:**
- **Cross-Layer Testing:** Test normalization for representative element types.
- **Error Detection:** Highlight normalization failures or inconsistencies.

**Inputs:** None (uses predefined test elements)

**Outputs:**
- Normalization results with success or failure indicators

**Business Value:** Ensures reliable element processing and PlantUML generation.

### Real-World MCP Example

**User Request:** "Test if element types are being normalized correctly across all ArchiMate layers."

**MCP Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "test_element_normalization",
    "arguments": {}
  },
  "id": "call-003"
}
```

**MCP Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "🧪 Element Normalization Test Results\n\n✅ Business Layer Tests:\n- 'business-actor' → 'Business_Actor' ✓\n- 'business_actor' → 'Business_Actor' ✓\n- 'Business Actor' → 'Business_Actor' ✓\n- 'BUSINESS-ACTOR' → 'Business_Actor' ✓\n- 'business-service' → 'Business_Service' ✓\n- 'business-process' → 'Business_Process' ✓\n\n✅ Application Layer Tests:\n- 'application-component' → 'Application_Component' ✓\n- 'application_component' → 'Application_Component' ✓\n- 'Application Component' → 'Application_Component' ✓\n- 'application-service' → 'Application_Service' ✓\n- 'application-interface' → 'Application_Interface' ✓\n\n✅ Technology Layer Tests:\n- 'node' → 'Node' ✓\n- 'NODE' → 'Node' ✓\n- 'device' → 'Device' ✓\n- 'system-software' → 'System_Software' ✓\n- 'technology-service' → 'Technology_Service' ✓\n\n✅ Motivation Layer Tests:\n- 'goal' → 'Goal' ✓\n- 'GOAL' → 'Goal' ✓\n- 'requirement' → 'Requirement' ✓\n- 'constraint' → 'Constraint' ✓\n\n✅ Strategy Layer Tests:\n- 'capability' → 'Capability' ✓\n- 'resource' → 'Resource' ✓\n- 'course-of-action' → 'Course_of_Action' ✓\n\n✅ Physical Layer Tests:\n- 'equipment' → 'Equipment' ✓\n- 'facility' → 'Facility' ✓\n- 'distribution-network' → 'Distribution_Network' ✓\n\n✅ Implementation Layer Tests:\n- 'work-package' → 'Work_Package' ✓\n- 'deliverable' → 'Deliverable' ✓\n- 'implementation-event' → 'Implementation_Event' ✓\n\n📊 Summary:\n- Total tests: 30\n- Passed: 30\n- Failed: 0\n- Success rate: 100%\n\n✨ All element type normalizations working correctly!"
      }
    ]
  },
  "id": "call-003"
}
```

---

## 4. `analyze_recent_errors`
**Business Purpose:** Inspect recent generation errors and provide troubleshooting guidance.

**Business Logic:**
- **Time Window Analysis:** Review errors within a configurable lookback period.
- **Pattern Detection:** Identify recurring problems and error categories.
- **Actionable Recommendations:** Suggest remediation steps based on findings.

**Inputs:**
- `minutes` – lookback period for analysis (default: 10)

**Outputs:**
- Error summary with categories and common patterns
- Recommended troubleshooting steps

**Business Value:** Rapid problem diagnosis and continuous improvement of architecture generation.

### Real-World MCP Example

**User Request:** "Check for any errors in the last 15 minutes and provide troubleshooting guidance."

**MCP Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "analyze_recent_errors",
    "arguments": {
      "minutes": 15
    }
  },
  "id": "call-004"
}
```

**MCP Response (when errors exist):**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "🔍 Recent Error Analysis (Last 15 minutes)\n\n📊 Error Summary:\n- Total errors found: 3\n- Time range: 2024-12-30 14:20:00 - 14:35:00\n\n⚠️ Error Categories:\n\n1. 🔗 Orphaned Relationships (2 occurrences)\n   - Missing element 'app4' referenced in relationship\n   - Missing element 'tech5' referenced in relationship\n   \n2. 📝 Invalid Element Types (1 occurrence)\n   - Unknown element type: 'business-widget' in Business layer\n\n📈 Error Timeline:\n- 14:22:15: Orphaned relationship error (missing 'app4')\n- 14:28:42: Invalid element type error ('business-widget')\n- 14:31:09: Orphaned relationship error (missing 'tech5')\n\n🛠️ Troubleshooting Recommendations:\n\n1. For Orphaned Relationships:\n   ✓ Verify all element IDs in relationships exist in the elements array\n   ✓ Check for typos in source/target IDs\n   ✓ Ensure elements are created before relationships\n   \n2. For Invalid Element Types:\n   ✓ Use 'test_element_normalization' to see valid element types\n   ✓ Common Business layer types: business-actor, business-service, business-process\n   ✓ Check ArchiMate 3.2 specification for complete element list\n\n💡 Prevention Tips:\n- Always validate element IDs before creating relationships\n- Use the normalization test tool to verify element types\n- Consider using the architecture analyzer before diagram generation"
      }
    ]
  },
  "id": "call-004"
}
```

**MCP Response (when no errors):**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "🔍 Recent Error Analysis (Last 15 minutes)\n\n✅ No errors found in the specified time period!\n\n📊 Summary:\n- Time range analyzed: Last 15 minutes\n- Total errors: 0\n- System status: All operations successful\n\n💡 Tips for maintaining error-free operations:\n- Continue using proper element type names\n- Verify relationships reference existing elements\n- Use 'analyze_current_architecture' to validate before generation\n- Run 'test_element_normalization' to verify input formats"
      }
    ]
  },
  "id": "call-004"
}
```

---

## Business Rules and Validation
### Cross-Tool Business Rules
1. **ArchiMate Compliance:** All tools enforce ArchiMate 3.2 specification.
2. **PlantUML Validation:** Mandatory syntax checking before output.
3. **Element Normalization:** Automatic element type normalization for consistency.
4. **Layer Integrity:** Proper layer assignment and cross-layer relationship validation.
5. **Referential Integrity:** Relationship endpoints must exist.
6. **Progress Tracking:** All tools provide operation status and statistics.

### Quality Assurance
- Comprehensive error logging and analysis
- Real-time validation and feedback
- Pattern-based problem detection
- Automated remediation recommendations

### Integration Points
- PNG generation to `/tmp` for visual verification
- JSON-based logging for programmatic analysis

### Workflow Patterns
1. `create_archimate_diagram` – generate a new diagram
2. `analyze_current_architecture` – review the generated diagram
3. `test_element_normalization` – verify element processing
4. `analyze_recent_errors` – troubleshoot issues

This simplified toolset provides a focused ecosystem for AI-powered enterprise architecture modeling with four key tools covering creation, analysis and troubleshooting.
