# ArchiMate MCP Server - Business Logic Analysis (Simplified API)

## Overview
The ArchiMate MCP server provides 4 essential tools for AI-powered enterprise architecture modeling using ArchiMate 3.2 standard. The API has been optimized to focus on core diagram creation with intelligent error analysis and troubleshooting guidance.

---

## Core Architecture Creation Tools

### 1. `create_archimate_diagram`
**Business Purpose:** Primary tool for generating complete ArchiMate diagrams from structured input.

**Business Logic:**
- **Input Processing:** Accepts structured diagram data (elements, relationships, layout preferences)
- **Element Creation:** Creates ArchiMate elements with proper normalization and layer assignment
- **Relationship Management:** Establishes connections between elements with validation
- **Layout Configuration:** Applies visual layout preferences (vertical/horizontal, grouping, legends)
- **Validation Pipeline:** Mandatory PlantUML syntax validation before returning results
- **Output Generation:** Produces validated PlantUML code with statistics and PNG file generation

**Inputs:**
- `DiagramInput`: Structured data containing elements, relationships, layout, title, description
- Elements with id, name, element_type, layer, optional description/stereotype
- Relationships with id, from_element, to_element, relationship_type

**Outputs:**
- Validated PlantUML source code
- PNG file path in /tmp directory
- Diagram statistics (elements, relationships, layers)
- Validation status

**Business Value:** Enables complete architecture documentation from high-level descriptions.

**Workflow Integration:** Entry point for most architecture creation workflows.

---

## Architecture Generation Tools

### 2. `generate_full_architecture`
**Business Purpose:** Generate complete enterprise architectures following ArchiMate methodology.

**Business Logic:**
- **Methodology Compliance:** Follows ArchiMate Cookbook best practices
- **Multiple View Generation:** Creates coordinated views across architecture layers
- **Domain Contextualization:** Adapts element naming based on business domain
- **Scope Management:** Scales architecture based on enterprise/system/application scope
- **Phase Planning:** Generates implementation roadmaps with configurable phases
- **Cross-View Consistency:** Ensures element reuse across related views

**Inputs:**
- `system_description`: Description of target system or business problem
- `business_domain`: Domain context (banking, healthcare, e-commerce, manufacturing)
- `architecture_scope`: Scope level (enterprise, system, application, component)
- `include_views`: List of views to generate
- `implementation_phases`: Number of implementation phases (1-6)

**Outputs:**
- Multiple coordinated ArchiMate views with PlantUML code
- Implementation guidance and methodology notes
- Architecture statistics and validation status
- Comprehensive view documentation

**Supported Views:**
- Motivation View (stakeholders, goals, drivers)
- Layered View (business, application, technology)
- Application Structure (detailed component breakdown)
- Implementation Roadmap (phased delivery planning)
- Business Model Canvas, Value Stream, Strategy & Capability views

**Business Value:** Comprehensive architecture generation for strategic planning.

---


## Validation and Quality Assurance Tools

### 3. `validate_archimate_model`
**Business Purpose:** Ensure architecture compliance with ArchiMate 3.2 specification.

**Business Logic:**
- **Element Validation:** Checks element type correctness and naming conventions
- **Relationship Validation:** Verifies relationship types against ArchiMate metamodel
- **Model Consistency:** Ensures referential integrity between elements and relationships
- **Layer Compliance:** Validates proper layer usage and cross-layer relationships
- **Strict Mode:** Optional enhanced validation with additional rule checking

**Inputs:**
- `strict`: Boolean flag for enhanced validation (default: false)

**Outputs:**
- Comprehensive validation report
- Error and warning summaries
- Compliance assessment
- Detailed issue descriptions with remediation suggestions

**Business Value:** Ensures architecture quality and standard compliance.

**Validation Levels:**
- **Standard:** Basic ArchiMate compliance checking
- **Strict:** Enhanced validation with advanced rule checking

---


## Debug and Analysis Tools

### 4. `analyze_current_architecture`
**Business Purpose:** Comprehensive analysis of current architecture state and health.

**Business Logic:**
- **State Analysis:** Examines current elements, relationships, and layers
- **Health Assessment:** Identifies critical issues and warnings
- **Element Review:** Detailed inspection of element properties and PlantUML output
- **Relationship Audit:** Validates relationship endpoints and types
- **Problem Identification:** Automated detection of common architecture issues

**Inputs:** None (analyzes current generator state)

**Outputs:**
- Architecture health assessment
- Element and relationship summaries
- Issue identification and severity assessment
- Improvement recommendations
- Detailed state analysis

**Business Value:** Architecture quality assurance and issue identification.

---

### 5. `test_element_normalization`
**Business Purpose:** Test and validate element type normalization across all layers.

**Business Logic:**
- **Cross-Layer Testing:** Tests element normalization for all ArchiMate layers
- **Error Detection:** Identifies normalization failures and inconsistencies
- **Mapping Verification:** Validates element type mappings
- **Success Rate Calculation:** Provides normalization success metrics

**Inputs:** None (tests predefined element types)

**Outputs:**
- Normalization test results for all layers
- Success/failure rates by layer
- Detailed error reports for failed normalizations
- Element type mapping verification

**Business Value:** Ensures reliable element processing and PlantUML generation.

---

### 6. `extract_problems_from_latest_attempt`
**Business Purpose:** Analyze problems from the most recent architecture creation attempt.

**Business Logic:**
- **Temporal Analysis:** Focuses on latest session errors
- **Error Categorization:** Groups errors by type and severity
- **Pattern Detection:** Identifies recurring issues
- **Critical Issue Flagging:** Highlights urgent problems requiring attention
- **Actionable Recommendations:** Provides specific remediation steps

**Inputs:** None (analyzes recent error logs)

**Outputs:**
- Latest attempt problem summary
- Categorized error analysis
- Critical issue identification
- Specific remediation recommendations
- Problem timeline and context

**Business Value:** Rapid problem diagnosis for troubleshooting.

---

### 7. `extract_problems_from_recent_attempts`
**Business Purpose:** Broader analysis of problems from recent architecture attempts.

**Business Logic:**
- **Time Window Analysis:** Configurable lookback period (default 10 minutes)
- **Trend Analysis:** Identifies error patterns over time
- **Tool-Specific Issues:** Tracks which tools are experiencing problems
- **Severity Assessment:** Prioritizes issues by impact and frequency
- **Stability Monitoring:** Provides overall system health assessment

**Inputs:**
- `lookback_minutes`: Time window for analysis (default: 10)

**Outputs:**
- Multi-attempt problem analysis
- Error trend identification
- Tool-specific issue tracking
- System stability assessment
- Comprehensive remediation roadmap

**Business Value:** System monitoring and trend analysis for quality improvement.

---

## Utility and Support Tools

### 8. `get_debug_log_info`
**Business Purpose:** Provide access to detailed MCP session logging information.

**Business Logic:**
- **Session Tracking:** Shows current session statistics
- **Call Monitoring:** Tracks successful and failed tool calls
- **Performance Metrics:** Provides timing and usage information
- **Log Path Information:** Directs users to detailed log files

**Inputs:** None

**Outputs:**
- Current session statistics
- Tool call success/failure rates
- Performance metrics and timing data
- Log file locations and access information
- Session activity summary

**Business Value:** Transparency and debugging support for development.

---

### 9. `save_conversation_to_tmp`
**Business Purpose:** Export conversation and debug logs for external analysis.

**Business Logic:**
- **Conversation Export:** Saves complete MCP interaction history
- **Debug Log Export:** Includes detailed debug information
- **File Management:** Creates timestamped files in /tmp directory
- **Session Documentation:** Preserves complete audit trail

**Inputs:**
- `session_name`: Optional session identifier (default: auto-generated)

**Outputs:**
- Conversation log file path
- Debug log export location
- Session documentation summary
- File size and export confirmation

**Business Value:** Documentation and audit capabilities for architecture sessions.

---

## Business Rules and Validation

### Cross-Tool Business Rules:
1. **ArchiMate Compliance:** All tools enforce ArchiMate 3.2 specification
2. **PlantUML Validation:** Mandatory syntax checking before output
3. **Element Normalization:** Automatic element type normalization for consistency
4. **Layer Integrity:** Proper layer assignment and cross-layer relationship validation
5. **Referential Integrity:** Relationship endpoints must exist
6. **Progress Tracking:** All tools provide operation status and statistics

### Quality Assurance:
- Comprehensive error logging and analysis
- Real-time validation and feedback
- Pattern-based problem detection
- Automated remediation recommendations

### Integration Points:
- PNG generation to /tmp directory for visual verification
- JSON-based logging for programmatic analysis
- Template library for rapid development
- Debug tools for troubleshooting and optimization

### Workflow Patterns:

#### Single Diagram Creation:
1. `create_archimate_diagram` - Generate complete diagram in one step
2. `validate_archimate_model` - Ensure compliance and quality

#### Enterprise Architecture Development:
1. `generate_full_architecture` - Generate comprehensive architecture
2. `analyze_current_architecture` - Review and validate

#### Troubleshooting and Debugging:
1. `extract_problems_from_latest_attempt` - Identify immediate issues
2. `test_element_normalization` - Verify element processing
3. `get_debug_log_info` - Access detailed logging
4. `save_conversation_to_tmp` - Export for external analysis

This simplified architecture provides a focused ecosystem for AI-powered enterprise architecture modeling with 2 core tools for architecture creation and 7 supporting tools for debugging, analysis, and quality assurance.