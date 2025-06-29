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
