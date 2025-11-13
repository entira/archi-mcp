---
name: archimate-diagrams
description: Generate ArchiMate 3.2 enterprise architecture diagrams from natural language with full spec compliance and auto-validation
---

# ArchiMate Diagram Generation Skill

Generate production-ready ArchiMate 3.2 enterprise architecture diagrams directly in Claude Code sessions. Supports all 55+ elements across 7 layers, 12 relationship types, with automatic validation and PlantUML rendering.

## When to Activate

Trigger this skill when the user mentions:
- "archimate" or "ArchiMate"
- "architecture diagram" or "enterprise architecture"
- "business/application/technology layer"
- Layer names: Business, Application, Technology, Physical, Strategy, Motivation, Implementation
- "draw/create/generate architecture"

## Prerequisites

**Required:**
- Python 3.11+
- Java 8+ (for PlantUML rendering)
- uv package manager

**First-time setup:**
Run once to download PlantUML JAR and create output directory:
```bash
uv run python .claude/skills/archimate-diagrams/skill_runner.py setup
```

This creates `.archimate-diagrams/` in project root and downloads PlantUML automatically.

## Workflow Steps

### 1. Parse User's Architecture Description

Identify from natural language:

**Elements** (architectural components):
- **Business Layer** - What the organization does
  - Business_Actor, Business_Role, Business_Process, Business_Service
  - Business_Function, Business_Object, Business_Event, Product

- **Application Layer** - Software and data
  - Application_Component, Application_Service, Application_Interface
  - Application_Function, Application_Process, Data_Object

- **Technology Layer** - Infrastructure and platforms
  - Node, Device, System_Software, Technology_Service
  - Artifact, Communication_Path, Network

- **Physical Layer** - Tangible resources
  - Equipment, Facility, Distribution_Network, Material

- **Strategy Layer** - Strategic direction
  - Resource, Capability, Course_of_Action, Value_Stream

- **Motivation Layer** - Why we do things
  - Stakeholder, Driver, Goal, Outcome, Requirement, Constraint

- **Implementation Layer** - How we realize change
  - Work_Package, Deliverable, Implementation_Event, Plateau

**Relationships** (how components connect):
- **Structural**: Composition, Aggregation, Assignment, Realization
- **Dependency**: Serving, Access, Influence, Association
- **Dynamic**: Flow, Triggering
- **Other**: Specialization

### 2. Create JSON Input

Transform parsed elements and relationships into JSON format:

```json
{
  "title": "Service Architecture",
  "elements": [
    {
      "id": "customer",
      "name": "Customer",
      "element_type": "Business_Actor",
      "layer": "BUSINESS",
      "description": "End user"
    },
    {
      "id": "portal",
      "name": "Web Portal",
      "element_type": "Application_Component",
      "layer": "APPLICATION"
    }
  ],
  "relationships": [
    {
      "id": "r1",
      "from_element": "portal",
      "to_element": "customer",
      "relationship_type": "Serving"
    }
  ],
  "options": {
    "direction": "top-bottom",
    "spacing": "comfortable",
    "generate_svg": false
  }
}
```

**Key Rules:**
- Element types use underscores: `Business_Actor` (not BusinessActor)
- Layer must be uppercase: `BUSINESS`, `APPLICATION`, `TECHNOLOGY`, etc.
- All IDs must be unique
- Relationships reference element IDs

### 3. Generate Diagram

Save JSON to temporary file and invoke skill runner:

```bash
# Create input file
cat > /tmp/archimate_input.json << 'EOF'
{
  "title": "Architecture View",
  "elements": [...],
  "relationships": [...]
}
EOF

# Generate diagram
uv run python .claude/skills/archimate-diagrams/skill_runner.py generate --input /tmp/archimate_input.json
```

The runner:
1. Validates ArchiMate 3.2 compliance
2. Generates PlantUML code
3. Renders PNG image
4. Saves to `.archimate-diagrams/YYYYMMDD_HHMMSS/`

### 4. Display Results

After generation completes:

**Parse JSON output** - contains file paths and status:
```json
{
  "success": true,
  "files": {
    "puml": ".archimate-diagrams/20251112_220500/diagram.puml",
    "png": ".archimate-diagrams/20251112_220500/diagram.png",
    "metadata": ".archimate-diagrams/20251112_220500/metadata.json"
  },
  "export_dir": ".archimate-diagrams/20251112_220500"
}
```

**Display the PNG** using Read tool:
```
Read the generated PNG file and display it in the conversation
```

**Show file locations** to user:
```markdown
✅ ArchiMate diagram generated successfully!

**Output files:**
- 📄 PlantUML source: `.archimate-diagrams/20251112_220500/diagram.puml`
- 🖼️ PNG image: `.archimate-diagrams/20251112_220500/diagram.png`
- 📊 Metadata: `.archimate-diagrams/20251112_220500/metadata.json`

[PNG image displayed above]
```

### 5. Handle Errors

If `success: false` in output:

**Validation errors** - suggest fixes:
```
❌ Validation failed:
- "Unknown element type: BusinessActor"
  → Use underscore format: Business_Actor

- "Invalid relationship: Serving from Node to Business_Actor"
  → Technology elements cannot serve business elements directly
```

**Rendering errors** - check setup:
```
❌ PNG generation failed
→ Ensure Java is installed: java -version
→ Verify PlantUML JAR: ls .archimate-diagrams/plantuml.jar
```

### 6. Iterative Refinement

Support modifications:

**User**: "Add a database to that diagram"

**Your actions:**
1. Load previous JSON from `.archimate-diagrams/{timestamp}/metadata.json`
2. Add new Data_Object element
3. Add Access relationships
4. Regenerate with updated JSON
5. Display new diagram
6. Note: Previous version preserved in timestamped directory

## Common Patterns

### Pattern 1: Layered View
```json
{
  "title": "Layered Architecture",
  "elements": [
    {"id": "user", "element_type": "Business_Actor", "layer": "BUSINESS"},
    {"id": "app", "element_type": "Application_Component", "layer": "APPLICATION"},
    {"id": "server", "element_type": "Node", "layer": "TECHNOLOGY"}
  ],
  "relationships": [
    {"id": "r1", "from_element": "app", "to_element": "user", "relationship_type": "Serving"},
    {"id": "r2", "from_element": "server", "to_element": "app", "relationship_type": "Assignment"}
  ],
  "options": {"direction": "top-bottom"}
}
```

### Pattern 2: Service Realization
```json
{
  "elements": [
    {"id": "svc", "element_type": "Application_Service", "layer": "APPLICATION"},
    {"id": "comp", "element_type": "Application_Component", "layer": "APPLICATION"}
  ],
  "relationships": [
    {"id": "r1", "from_element": "comp", "to_element": "svc", "relationship_type": "Realization"}
  ]
}
```

### Pattern 3: Data Flow
```json
{
  "elements": [
    {"id": "proc1", "element_type": "Business_Process", "layer": "BUSINESS"},
    {"id": "proc2", "element_type": "Business_Process", "layer": "BUSINESS"},
    {"id": "data", "element_type": "Business_Object", "layer": "BUSINESS"}
  ],
  "relationships": [
    {"id": "r1", "from_element": "proc1", "to_element": "proc2", "relationship_type": "Flow"},
    {"id": "r2", "from_element": "proc1", "to_element": "data", "relationship_type": "Access"}
  ]
}
```

## Layout Options

**Direction:**
- `top-bottom` (default) - vertical layout, good for layers
- `left-right` - horizontal layout, good for flows
- `bottom-top` - inverted vertical
- `right-left` - inverted horizontal

**Spacing:**
- `compact` - minimal whitespace
- `comfortable` (default) - balanced spacing
- `spacious` - maximum readability

**SVG Generation:**
- `generate_svg: false` (default) - PNG only
- `generate_svg: true` - generate both PNG and SVG

## Validation Rules

The skill automatically validates:

✓ **Element types** - must be valid ArchiMate 3.2 types
✓ **Layer assignment** - element type must match layer
✓ **Relationship validity** - checked against ArchiMate matrix
✓ **ID uniqueness** - no duplicate IDs
✓ **Reference integrity** - all relationship endpoints exist

## Error Messages and Fixes

| Error | Fix |
|-------|-----|
| "Unknown element type" | Check spelling, use underscores |
| "Layer mismatch" | Use correct layer for element type |
| "Invalid relationship" | Consult relationship matrix |
| "Duplicate ID" | Ensure all IDs are unique |
| "Missing element" | Verify relationship endpoints exist |
| "Java not found" | Install Java 8+: https://www.java.com/ |
| "PlantUML failed" | Re-run setup to download JAR |

## Performance

- Small diagrams (< 10 elements): ~2-5 seconds
- Medium diagrams (10-30 elements): ~5-10 seconds
- Large diagrams (> 30 elements): ~10-20 seconds

Includes validation, PlantUML generation, and PNG rendering.

## Files and Locations

**Skill location:**
`.claude/skills/archimate-diagrams/`

**Output directory:**
`.archimate-diagrams/` (project root)

**Generated files per diagram:**
- `diagram.puml` - PlantUML source (editable)
- `diagram.png` - Rendered image
- `diagram.svg` - Vector image (if requested)
- `metadata.json` - Generation details

**PlantUML JAR:**
`.archimate-diagrams/plantuml.jar` (auto-downloaded)

## Tips for Best Results

1. **Start simple** - Begin with 3-5 elements, add complexity iteratively
2. **Use layers** - Group related elements by architectural layer
3. **Name clearly** - Use business-friendly names, not technical IDs
4. **Label relationships** - Add descriptive labels for clarity
5. **Choose direction** - top-bottom for layers, left-right for processes
6. **Validate early** - Let ArchiMate validation catch errors before rendering
7. **Preserve history** - Timestamped directories keep all versions

## Example Conversation

**User:** "Create an archimate diagram showing a customer using a web portal to access a database"

**Your response:**
```
I'll create an ArchiMate diagram with three layers showing that architecture.

[Creates JSON with Business_Actor (customer), Application_Component (portal),
Data_Object (database), and appropriate Serving/Access relationships]

[Generates diagram]

✅ Diagram generated!

The architecture shows:
- **Business Layer**: Customer actor
- **Application Layer**: Web Portal component accessing Customer Database
- **Relationships**: Portal serves Customer, Portal accesses Database

Files saved to: `.archimate-diagrams/20251112_220500/`

[Displays PNG image]

Would you like me to add more components or modify the layout?
```

## Advanced Usage

**Multiple views:**
Generate separate diagrams for each concern (business processes, application landscape, infrastructure) and reference them together.

**Complex relationships:**
Use junction elements (And/Or junctions) for complex splits and merges in flows.

**Nested structures:**
Use Composition for strong containment (component contains sub-components) or Aggregation for loose grouping.

**Motivation layer:**
Add goals, requirements, and drivers to show why architecture exists, not just what it is.

---

**Remember**: This skill runs within Claude Code session with full access to conversation context. Users can iteratively refine diagrams, compare versions, and build comprehensive architecture documentation through natural conversation.
