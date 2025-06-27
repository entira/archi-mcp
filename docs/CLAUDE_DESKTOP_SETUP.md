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

Add the following configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "archi-mcp": {
      "command": "uv",
      "args": ["run", "archi-mcp"],
      "cwd": "/Users/patrik/Projects/archi-mcp",
      "env": {
        "ARCHI_MCP_LOG_LEVEL": "INFO",
        "ARCHI_MCP_STRICT_VALIDATION": "true"
      }
    }
  }
}
```

**Important:** Update the `cwd` path to match your actual project location!

### Step 3: Restart Claude Desktop

Close and restart Claude Desktop to load the new MCP server configuration.

## 🔧 Configuration Options

### Basic Configuration
```json
{
  "mcpServers": {
    "archi-mcp": {
      "command": "uv",
      "args": ["run", "archi-mcp"],
      "cwd": "/path/to/your/archi-mcp"
    }
  }
}
```

### Advanced Configuration with Environment Variables
```json
{
  "mcpServers": {
    "archi-mcp": {
      "command": "uv",
      "args": ["run", "archi-mcp"],
      "cwd": "/path/to/your/archi-mcp",
      "env": {
        "ARCHI_MCP_LOG_LEVEL": "DEBUG",
        "ARCHI_MCP_LOG_FILE": "/tmp/archi-mcp.log",
        "ARCHI_MCP_STRICT_VALIDATION": "true"
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

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `ARCHI_MCP_LOG_LEVEL` | Logging verbosity | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `ARCHI_MCP_LOG_FILE` | Log file path | None (stdout) | Any valid file path |
| `ARCHI_MCP_STRICT_VALIDATION` | Enable strict ArchiMate validation | `false` | `true`, `false` |

## ✅ Verification

### Test MCP Server Connection

1. **Open Claude Desktop**
2. **Start a new conversation**
3. **Type:** "What ArchiMate tools are available?"
4. **Expected Response:** Claude should list the 7 available ArchiMate MCP tools

### Test Basic Functionality

**Create a simple diagram:**
```
Create an ArchiMate diagram showing:
- A business service called "Customer Service"
- An application component called "CRM System" 
- A relationship showing the CRM System realizes the Customer Service
```

**Expected Output:** PlantUML code with proper ArchiMate syntax

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
uv run archi-mcp
```

**Check 3: Check Claude Desktop logs**
- Look for MCP server connection errors
- Verify path configuration is correct

### Command Not Found Errors

**Solution 1: Use full path to uv**
```json
{
  "command": "/usr/local/bin/uv",
  "args": ["run", "archi-mcp"]
}
```

**Solution 2: Use Python directly**
```json
{
  "command": "python",
  "args": ["-m", "archi_mcp.server"]
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

### Validation Errors

**Disable strict validation temporarily:**
```json
{
  "env": {
    "ARCHI_MCP_STRICT_VALIDATION": "false"
  }
}
```

## 📊 Performance Optimization

### For Large Diagrams
```json
{
  "env": {
    "ARCHI_MCP_LOG_LEVEL": "WARNING",
    "ARCHI_MCP_TIMEOUT": "60"
  }
}
```

### For Development
```json
{
  "env": {
    "ARCHI_MCP_LOG_LEVEL": "DEBUG",
    "ARCHI_MCP_LOG_FILE": "/tmp/archi-mcp-debug.log"
  }
}
```

## 🔄 Multiple Configuration Example

You can configure multiple MCP servers:

```json
{
  "mcpServers": {
    "archi-mcp": {
      "command": "uv",
      "args": ["run", "archi-mcp"],
      "cwd": "/path/to/archi-mcp"
    },
    "archi-mcp-dev": {
      "command": "uv", 
      "args": ["run", "archi-mcp"],
      "cwd": "/path/to/archi-mcp-dev",
      "env": {
        "ARCHI_MCP_LOG_LEVEL": "DEBUG"
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

**Ready to use ArchiMate MCP Server with Claude Desktop!** 🎉

After setup, you can generate professional ArchiMate diagrams through natural conversation with Claude Desktop.