# Claude Desktop Setup for ArchiMate MCP Server

## 🚀 Quick Setup

### Step 1: Locate Claude Desktop Configuration

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

### Step 2: Add ArchiMate MCP Server Configuration

Add the following **optimized configuration** to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "archi-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/Users/patrik/Projects/archi-mcp", "python", "-m", "archi_mcp.server"],
      "cwd": "/Users/patrik/Projects/archi-mcp",
      "env": {
        "ARCHI_MCP_LOG_LEVEL": "INFO",
        
        "ARCHI_MCP_DEFAULT_DIRECTION": "vertical",
        "ARCHI_MCP_DEFAULT_SHOW_LEGEND": "false",
        "ARCHI_MCP_DEFAULT_SHOW_TITLE": "false",
        "ARCHI_MCP_DEFAULT_GROUP_BY_LAYER": "true",
        "ARCHI_MCP_DEFAULT_SPACING": "compact"
      }
    }
  }
}
```

**Important:** 
- Update the `cwd` path to match your actual project location!
- This configuration **enforces your layout preferences** - Claude cannot override these settings

### Step 3: Restart Claude Desktop

Close and restart Claude Desktop to load the new MCP server configuration.

## 🔧 Configuration Options

### Minimal Configuration (Uses Defaults)
```json
{
  "mcpServers": {
    "archi-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/your/archi-mcp", "python", "-m", "archi_mcp.server"],
      "cwd": "/path/to/your/archi-mcp"
    }
  }
}
```

### **Recommended: Layout-Optimized Configuration**
```json
{
  "mcpServers": {
    "archi-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/your/archi-mcp", "python", "-m", "archi_mcp.server"],
      "cwd": "/path/to/your/archi-mcp",
      "env": {
        "ARCHI_MCP_LOG_LEVEL": "INFO",
        
        "ARCHI_MCP_DEFAULT_DIRECTION": "vertical",
        "ARCHI_MCP_DEFAULT_SHOW_LEGEND": "false",
        "ARCHI_MCP_DEFAULT_SHOW_TITLE": "false", 
        "ARCHI_MCP_DEFAULT_GROUP_BY_LAYER": "true",
        "ARCHI_MCP_DEFAULT_SPACING": "compact",
        
        "ARCHI_MCP_DEFAULT_SHOW_ELEMENT_TYPES": "false",
        "ARCHI_MCP_DEFAULT_SHOW_RELATIONSHIP_LABELS": "true"
      }
    }
  }
}
```

### Debug Configuration
```json
{
  "mcpServers": {
    "archi-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/your/archi-mcp", "python", "-m", "archi_mcp.server"],
      "cwd": "/path/to/your/archi-mcp",
      "env": {
        "ARCHI_MCP_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Alternative Python Configuration
If you don't have `uv` installed, you can use Python directly:

```json
{
  "mcpServers": {
    "archi-mcp": {
      "command": "python",
      "args": ["-m", "archi_mcp.server"],
      "cwd": "/path/to/your/archi-mcp"
    }
  }
}
```

## 🛠️ Environment Variables

### Essential Configuration Parameters

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `ARCHI_MCP_LOG_LEVEL` | Logging verbosity | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

### Layout Configuration Parameters (Config-First Priority)

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `ARCHI_MCP_DEFAULT_DIRECTION` | Diagram layout direction | `vertical` | `horizontal`, `vertical` |
| `ARCHI_MCP_DEFAULT_SHOW_LEGEND` | Show diagram legend | `false` | `true`, `false` |
| `ARCHI_MCP_DEFAULT_SHOW_TITLE` | Show diagram title | `false` | `true`, `false` |
| `ARCHI_MCP_DEFAULT_GROUP_BY_LAYER` | Group elements by layer | `true` | `true`, `false` |
| `ARCHI_MCP_DEFAULT_SPACING` | Element spacing | `compact` | `compact`, `normal`, `wide` |
| `ARCHI_MCP_DEFAULT_SHOW_ELEMENT_TYPES` | Show element type names | `false` | `true`, `false` |
| `ARCHI_MCP_DEFAULT_SHOW_RELATIONSHIP_LABELS` | Show relationship labels | `true` | `true`, `false` |

**🔒 Important:** Layout parameters configured here **cannot be overridden** by Claude requests. Your settings are enforced consistently.

### Automatically Configured (No Configuration Needed)
- **Language Detection**: Automatic (always enabled)
- **PNG/SVG Generation**: Always enabled with high quality
- **Validation**: Always strict validation
- **Export Cleanup**: Always enabled

### Custom Relationship Names
The server supports custom relationship names with intelligent validation:
- **Maximum length**: 3 words or 30 characters
- **Language-aware**: Validates synonyms in Slovak and English
- **Semantic validation**: Ensures custom names are appropriate synonyms of formal relationship types
- **Examples**: 
  - "Realization" → "implements", "fulfills", "delivers" (EN) or "realizuje", "plní" (SK)
  - "Serving" → "supports", "provides" (EN) or "podporuje", "poskytuje" (SK)

## ✅ Verification

### Test MCP Server Connection

1. **Open Claude Desktop**
2. **Start a new conversation**
3. **Type:** "What ArchiMate tools are available?"
4. **Expected Response:** Claude should list the 5 available ArchiMate MCP tools:
   - `create_archimate_diagram`
   - `analyze_current_architecture`
   - `test_element_normalization`
   - `create_architecture_views_summary`
   - `analyze_recent_errors`

### Test Basic Functionality

**Create a simple diagram:**
```
Create an ArchiMate diagram showing:
- A business service called "Customer Service"
- An application component called "CRM System" 
- A relationship showing the CRM System realizes the Customer Service
```

**Expected Output:** 
- PlantUML code with proper ArchiMate syntax
- Layout follows your configured preferences (vertical, compact spacing, etc.)
- Element types shown/hidden based on configuration
- Relationship labels shown/hidden based on configuration  
- PNG/SVG files automatically generated

### Test Full Architecture Generation

**Generate complete architecture:**
```
Generate a complete enterprise architecture for an online banking system including motivation view, layered view, application structure, and implementation roadmap.
```

**Expected Output:** Multiple coordinated ArchiMate views with cross-layer relationships

## 🔍 Troubleshooting

### MCP Server Not Loading

**Check 1: Verify uv installation**
```bash
uv --version
```

**Check 2: Test server manually**
```bash
cd /path/to/archi-mcp
uv run python -m archi_mcp.server
```

**Check 3: Check Claude Desktop logs**
- Look for MCP server connection errors
- Verify path configuration is correct

### Command Not Found Errors

**Solution 1: Use full path to uv**
```json
{
  "command": "/usr/local/bin/uv",
  "args": ["run", "--directory", "/path/to/archi-mcp", "python", "-m", "archi_mcp.server"]
}
```

**Solution 2: Use Python directly**
```json
{
  "command": "python",
  "args": ["-m", "archi_mcp.server"],
  "cwd": "/path/to/archi-mcp"
}
```

### Permission Errors

**macOS/Linux:**
```bash
chmod +x /path/to/archi-mcp
```

**Windows:**
- Run Claude Desktop as Administrator
- Check folder permissions

### Layout Issues

**If your layout preferences aren't working:**

1. **Check configuration spelling** - ensure exact variable names
2. **Restart Claude Desktop** after config changes
3. **Use analyze_recent_errors tool** to check for configuration issues

**Test layout enforcement:**
```
Create a simple ArchiMate diagram with horizontal layout and show legend
```
Even though you request horizontal layout, it should use your configured vertical layout.

## 📊 Performance Optimization

### For Large Diagrams (Reduce Logging)
```json
{
  "env": {
    "ARCHI_MCP_LOG_LEVEL": "WARNING"
  }
}
```

### For Development (Detailed Logging)
```json
{
  "env": {
    "ARCHI_MCP_LOG_LEVEL": "DEBUG"
  }
}
```

## 🔄 Multiple Configuration Example

You can configure multiple MCP servers:

```json
{
  "mcpServers": {
    "archi-mcp-production": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/archi-mcp", "python", "-m", "archi_mcp.server"],
      "cwd": "/path/to/archi-mcp",
      "env": {
        "ARCHI_MCP_LOG_LEVEL": "INFO",
        "ARCHI_MCP_DEFAULT_DIRECTION": "vertical",
        "ARCHI_MCP_DEFAULT_SPACING": "compact"
      }
    },
    "archi-mcp-dev": {
      "command": "uv", 
      "args": ["run", "--directory", "/path/to/archi-mcp-dev", "python", "-m", "archi_mcp.server"],
      "cwd": "/path/to/archi-mcp-dev",
      "env": {
        "ARCHI_MCP_LOG_LEVEL": "DEBUG",
        "ARCHI_MCP_DEFAULT_DIRECTION": "horizontal",
        "ARCHI_MCP_DEFAULT_SPACING": "wide"
      }
    }
  }
}
```

## 📞 Support

### Configuration Issues
- Check path spelling and permissions
- Verify uv/Python installation
- Test server manually before configuring Claude Desktop

### Functionality Issues
- Enable debug logging to see detailed operations
- Check ArchiMate validation messages
- Review generated PlantUML syntax

### Getting Help
- GitHub Issues: Report configuration problems
- Documentation: Review CLAUDE.md for development guidance
- Examples: Check generated diagrams in repository

---

## 🎯 **New in This Version: Optimized Configuration**

### ✅ What's Improved:
- **Config-First Priority**: Your layout settings cannot be overridden by Claude requests
- **Enhanced Display Control**: Show/hide element types and relationship labels
- **Custom Relationship Names**: Intelligent validation of client-provided relationship synonyms
- **Simplified Configuration**: Only essential parameters with smart defaults
- **Always-On Features**: Language detection, PNG/SVG generation, validation - no configuration needed
- **Better Performance**: Streamlined parameter handling

### 🔒 Layout Enforcement:
When you configure layout parameters, they are **enforced consistently**:
- Claude requests for different layouts are **ignored**
- Your preferences (vertical, compact, no legend) are **always applied**
- Reliable, predictable diagram generation

---

**Ready to use ArchiMate MCP Server with Claude Desktop!** 🎉

After setup, you can generate professional ArchiMate diagrams through natural conversation with Claude Desktop, with your layout preferences consistently enforced.