# ArchiMate Diagrams - Claude Agent Skill

**Standalone Claude Code skill for generating ArchiMate 3.2 enterprise architecture diagrams with full specification compliance.**

## Overview

This skill enables Claude Code to generate production-ready ArchiMate diagrams directly in chat sessions. Unlike the MCP server approach, this skill runs within your Claude Code session with full context awareness, allowing iterative refinement and natural language interaction.

### Key Features

✨ **Standalone Operation** - No MCP server configuration required
💬 **Conversational** - Natural language → architecture diagrams
🎨 **Inline Display** - Diagrams appear directly in Claude chat
📦 **Auto-Setup** - Downloads PlantUML automatically on first use
🔄 **Iterative** - Refine diagrams through conversation
📚 **Full ArchiMate 3.2** - All 55+ elements, 12 relationships, 7 layers
✅ **Auto-Validation** - Real-time ArchiMate compliance checking
🌍 **Portable** - Works in any Claude Code session

## Installation

### Prerequisites

- **Python 3.11+** - Check: `python3 --version`
- **Java 8+** - Check: `java -version` (required for PlantUML)
- **uv** - Check: `uv --version` ([install guide](https://github.com/astral-sh/uv))

### Quick Install

**Option 1: From archi-mcp repository**

```bash
# Clone the repository
git clone https://github.com/entira/archi-mcp.git

# Copy skill to your project
cd your-project
mkdir -p .claude/skills
cp -r path/to/archi-mcp/.claude/skills/archimate-diagrams .claude/skills/

# First-time setup
uv run python .claude/skills/archimate-diagrams/skill_runner.py setup
```

**Option 2: Direct download**

```bash
# Download skill directory
cd your-project/.claude/skills
git clone https://github.com/entira/archi-mcp.git temp
mv temp/.claude/skills/archimate-diagrams ./
rm -rf temp

# Setup
uv run python .claude/skills/archimate-diagrams/skill_runner.py setup
```

### What Setup Does

The setup command:
1. Creates `.archimate-diagrams/` directory in project root
2. Downloads PlantUML JAR (~20MB) automatically
3. Verifies Java installation
4. Displays status messages

Output files will be saved to: `.archimate-diagrams/YYYYMMDD_HHMMSS/`

## Usage

### Basic Workflow

1. **Ask Claude to generate a diagram:**
   ```
   "Create an archimate diagram showing a customer using a web portal to access a database"
   ```

2. **Claude automatically:**
   - Activates the skill
   - Parses your description
   - Creates JSON representation
   - Generates and validates the diagram
   - Displays the PNG image

3. **Refine iteratively:**
   ```
   "Add an API gateway between the portal and database"
   "Change to left-right layout"
   "Add a mobile app that also uses the API"
   ```

### Example Conversation

**You:** "Generate an ArchiMate diagram for a three-tier web application"

**Claude:**
```
I'll create an ArchiMate diagram showing the three-tier architecture.

[Generates diagram with:
- Business Layer: User actor
- Application Layer: Web UI, Business Logic, Data Access components
- Technology Layer: Web Server, App Server, Database Server nodes]

✅ Diagram generated!

**Architecture:**
- Business tier: Users
- Application tier: Web UI → Business Logic → Data Access
- Technology tier: Web/App/DB Servers

Files: `.archimate-diagrams/20251112_220500/`

[PNG displayed in conversation]

Would you like to add more components or modify the layout?
```

## Supported Elements

### Business Layer (13 types)
- Business_Actor, Business_Role, Business_Collaboration, Business_Interface
- Business_Process, Business_Function, Business_Interaction, Business_Event
- Business_Service, Business_Object, Contract, Representation, Product

### Application Layer (8 types)
- Application_Component, Application_Collaboration, Application_Interface
- Application_Function, Application_Interaction, Application_Process
- Application_Event, Application_Service, Data_Object

### Technology Layer (13 types)
- Node, Device, System_Software, Technology_Collaboration, Technology_Interface
- Path, Communication_Network, Technology_Function, Technology_Process
- Technology_Interaction, Technology_Event, Technology_Service, Artifact

### Physical Layer (4 types)
- Equipment, Facility, Distribution_Network, Material

### Strategy Layer (4 types)
- Resource, Capability, Value_Stream, Course_of_Action

### Motivation Layer (10 types)
- Stakeholder, Driver, Assessment, Goal, Outcome
- Principle, Requirement, Constraint, Meaning, Value

### Implementation Layer (4 types)
- Work_Package, Deliverable, Implementation_Event, Plateau

**Total: 55+ ArchiMate 3.2 elements**

## Supported Relationships (12 types)

- **Structural:** Composition, Aggregation, Assignment, Realization
- **Dependency:** Serving, Access, Influence, Association
- **Dynamic:** Flow, Triggering
- **Other:** Specialization, Junction

See `references/RELATIONSHIPS.md` for detailed relationship rules.

## Project Structure

```
.claude/skills/archimate-diagrams/
├── SKILL.md                    # Claude instructions
├── README.md                   # This file
├── skill_runner.py             # Main script
├── pyproject.toml              # Dependencies
├── lib/                        # Standalone ArchiMate core
│   ├── archimate/              # Element & relationship definitions
│   ├── i18n/                   # Multi-language support
│   ├── utils/                  # Utilities
│   └── xml_export/             # XML export (experimental)
└── references/
    ├── ELEMENTS.md             # All element types
    ├── RELATIONSHIPS.md        # Relationship matrix
    └── TEMPLATES.md            # Common patterns

.archimate-diagrams/            # Output directory (created by setup)
├── plantuml.jar                # Auto-downloaded
└── YYYYMMDD_HHMMSS/            # Timestamped exports
    ├── diagram.puml            # PlantUML source
    ├── diagram.png             # PNG image
    ├── diagram.svg             # SVG (optional)
    └── metadata.json           # Generation metadata
```

## Configuration

### Layout Options

**Direction:**
- `top-bottom` (default) - Vertical, good for layers
- `left-right` - Horizontal, good for flows
- `bottom-top` - Inverted vertical
- `right-left` - Inverted horizontal

**Spacing:**
- `compact` - Minimal whitespace
- `comfortable` (default) - Balanced
- `spacious` - Maximum readability

**Output Formats:**
- PNG (always generated)
- SVG (on request: `"generate_svg": true`)

### Environment Variables

None required - skill auto-detects paths based on its location.

## Troubleshooting

### "Java not found"

**Solution:** Install Java 8+
- macOS: `brew install openjdk@11`
- Windows: Download from https://www.java.com/
- Linux: `sudo apt install default-jre`

Verify: `java -version`

### "PlantUML download failed"

**Solution:** Manual download
```bash
cd .archimate-diagrams
curl -L https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar -o plantuml.jar
```

### "PNG not displaying in Claude"

**Solution:** Check file was created
```bash
ls -la .archimate-diagrams/latest/diagram.png
```

If file exists, Claude should display it automatically. Try regenerating.

### "Invalid element type: BusinessActor"

**Solution:** Use underscore format
- ✗ Wrong: `BusinessActor`, `business-actor`, `business_actor`
- ✓ Correct: `Business_Actor`

### "Relationship not allowed between X and Y"

**Solution:** Check ArchiMate relationship matrix
- Consult `references/RELATIONSHIPS.md`
- Some cross-layer relationships are restricted
- Use appropriate relationship types

### "Module not found: archimate"

**Solution:** Re-run setup or check lib/ directory exists
```bash
uv run python .claude/skills/archimate-diagrams/skill_runner.py setup
ls .claude/skills/archimate-diagrams/lib/
```

## Comparison: Skill vs MCP Server

| Feature | Claude Agent Skill | MCP Server |
|---------|-------------------|------------|
| **Installation** | Copy directory | Configure claude_desktop_config.json |
| **Setup** | One command | Manual config + uv setup |
| **Usage** | Natural language | JSON schema |
| **Context** | Full conversation | Single requests |
| **Display** | Inline images | File paths + HTTP server |
| **Iteration** | Conversational | New tool calls |
| **Platform** | Claude Code only | Claude Desktop + Code |
| **Portability** | Very high | Medium |
| **Best For** | Interactive design | Automation, CI/CD |

**Recommendation:** Use skill for interactive diagram design in Claude Code, MCP server for Claude Desktop or production automation.

## Advanced Usage

### Multiple Views

Generate separate diagrams for different concerns:
```
"Create a business layer view showing customer interactions"
"Now create an application layer view showing the supporting systems"
"Finally, show the technology infrastructure"
```

Each diagram saved with timestamp - easy to compare versions.

### Complex Architectures

Build incrementally:
```
"Start with core business services"
→ Generate initial diagram

"Add supporting application components"
→ Regenerate with additions

"Show the complete stack including infrastructure"
→ Final comprehensive view
```

### Export for Documentation

All outputs saved to `.archimate-diagrams/` - ready for:
- Embedding in architecture documents
- Presentations (use SVG for scaling)
- Version control (PlantUML source is text)
- Archi tool import (XML export - experimental)

## Performance

- Small diagrams (< 10 elements): ~2-5 seconds
- Medium diagrams (10-30 elements): ~5-10 seconds
- Large diagrams (> 30 elements): ~10-20 seconds

Time includes validation, PlantUML generation, and PNG rendering.

## Contributing

This skill is part of the [archi-mcp](https://github.com/entira/archi-mcp) project.

**Report issues:**
https://github.com/entira/archi-mcp/issues

**Contribute:**
- Fork the repository
- Create feature branch: `git checkout -b feature/skill-enhancement`
- Submit pull request

## License

MIT License - See [LICENSE](https://github.com/entira/archi-mcp/blob/main/LICENSE)

## Author

**Mgr. Patrik Skovajsa**

## Resources

- **ArchiMate 3.2 Specification:** https://pubs.opengroup.org/architecture/archimate32-doc/
- **PlantUML ArchiMate:** https://plantuml.com/archimate-diagram
- **Claude Code Documentation:** https://docs.claude.com/en/docs/claude-code
- **Project Repository:** https://github.com/entira/archi-mcp

---

**🎯 Ready to Use:** Copy the skill directory, run setup, and start generating enterprise architecture diagrams in Claude Code!
