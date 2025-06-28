"""Conversation logger for MCP tool calls and results."""

import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path


class ConversationLogger:
    """Logger for MCP tool calls and conversation history."""
    
    def __init__(self, log_dir: str = "/tmp"):
        """Initialize conversation logger.
        
        Args:
            log_dir: Directory to save conversation logs (default: /tmp)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.conversation_log: List[Dict[str, Any]] = []
        self.session_id = f"archi_mcp_{int(time.time())}"
        
    def log_tool_call(self, tool_name: str, parameters: Dict[str, Any], result: Any, success: bool = True, error: Optional[str] = None) -> None:
        """Log MCP tool call with parameters and result.
        
        Args:
            tool_name: Name of the MCP tool called
            parameters: Tool parameters
            result: Tool result/output
            success: Whether the call was successful
            error: Error message if failed
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "mcp_tool_call",
            "tool_name": tool_name,
            "parameters": parameters,
            "success": success,
            "result": str(result)[:1000] if result else None,  # Truncate long results
            "error": error
        }
        
        self.conversation_log.append(log_entry)
    
    def log_user_message(self, message: str) -> None:
        """Log user message.
        
        Args:
            message: User's message
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "user_message", 
            "content": message[:500]  # Truncate long messages
        }
        
        self.conversation_log.append(log_entry)
    
    def log_assistant_response(self, response: str) -> None:
        """Log assistant response.
        
        Args:
            response: Assistant's response
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "assistant_response",
            "content": response[:500]  # Truncate long responses
        }
        
        self.conversation_log.append(log_entry)
    
    def generate_markdown_summary(self) -> str:
        """Generate markdown summary of the conversation.
        
        Returns:
            Markdown formatted conversation summary
        """
        md_lines = []
        
        # Header
        md_lines.append(f"# ArchiMate MCP Conversation Log")
        md_lines.append(f"**Session ID:** `{self.session_id}`")
        md_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md_lines.append(f"**Total Entries:** {len(self.conversation_log)}")
        md_lines.append("")
        
        # Statistics
        tool_calls = [entry for entry in self.conversation_log if entry["type"] == "mcp_tool_call"]
        successful_calls = [call for call in tool_calls if call["success"]]
        failed_calls = [call for call in tool_calls if not call["success"]]
        
        md_lines.append("## 📊 Session Statistics")
        md_lines.append(f"- **MCP Tool Calls:** {len(tool_calls)}")
        md_lines.append(f"- **Successful:** {len(successful_calls)} ✅")
        md_lines.append(f"- **Failed:** {len(failed_calls)} ❌")
        
        if tool_calls:
            tool_counts = {}
            for call in tool_calls:
                tool_name = call["tool_name"]
                tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
            
            md_lines.append("")
            md_lines.append("### 🔧 Tools Used")
            for tool_name, count in sorted(tool_counts.items()):
                md_lines.append(f"- `{tool_name}`: {count} calls")
        
        md_lines.append("")
        
        # Conversation timeline
        md_lines.append("## 💬 Conversation Timeline")
        md_lines.append("")
        
        for i, entry in enumerate(self.conversation_log):
            timestamp = entry["timestamp"]
            entry_type = entry["type"]
            
            if entry_type == "user_message":
                md_lines.append(f"### {i+1}. 👤 User Message")
                md_lines.append(f"**Time:** {timestamp}")
                md_lines.append(f"```")
                md_lines.append(entry["content"])
                md_lines.append(f"```")
                
            elif entry_type == "assistant_response":
                md_lines.append(f"### {i+1}. 🤖 Assistant Response")
                md_lines.append(f"**Time:** {timestamp}")
                md_lines.append(f"```")
                md_lines.append(entry["content"])
                md_lines.append(f"```")
                
            elif entry_type == "mcp_tool_call":
                status_icon = "✅" if entry["success"] else "❌"
                md_lines.append(f"### {i+1}. 🔧 MCP Tool Call {status_icon}")
                md_lines.append(f"**Tool:** `{entry['tool_name']}`")
                md_lines.append(f"**Time:** {timestamp}")
                md_lines.append(f"**Success:** {entry['success']}")
                
                if entry["parameters"]:
                    md_lines.append("")
                    md_lines.append("**Parameters:**")
                    md_lines.append("```json")
                    md_lines.append(json.dumps(entry["parameters"], indent=2))
                    md_lines.append("```")
                
                if entry["success"] and entry["result"]:
                    md_lines.append("")
                    md_lines.append("**Result:**")
                    md_lines.append("```")
                    md_lines.append(entry["result"])
                    md_lines.append("```")
                
                if not entry["success"] and entry["error"]:
                    md_lines.append("")
                    md_lines.append("**Error:**")
                    md_lines.append("```")
                    md_lines.append(entry["error"])
                    md_lines.append("```")
            
            md_lines.append("")
        
        # Footer
        md_lines.append("---")
        md_lines.append("*Generated by ArchiMate MCP Server conversation logger*")
        
        return "\n".join(md_lines)
    
    def save_to_file(self, filename: Optional[str] = None) -> str:
        """Save conversation log to markdown file.
        
        Args:
            filename: Optional custom filename (default: auto-generated)
            
        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"archi_mcp_conversation_{timestamp}.md"
        
        filepath = self.log_dir / filename
        
        # Generate markdown content
        markdown_content = self.generate_markdown_summary()
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return str(filepath)
    
    def clear_log(self) -> None:
        """Clear the conversation log."""
        self.conversation_log.clear()
    
    def get_log_count(self) -> int:
        """Get number of log entries."""
        return len(self.conversation_log)


# Global conversation logger instance
conversation_logger = ConversationLogger()


def log_mcp_tool_call(tool_name: str, parameters: Dict[str, Any], result: Any, success: bool = True, error: Optional[str] = None) -> None:
    """Convenience function to log MCP tool calls.
    
    Args:
        tool_name: Name of the MCP tool
        parameters: Tool parameters
        result: Tool result
        success: Whether call was successful
        error: Error message if failed
    """
    conversation_logger.log_tool_call(tool_name, parameters, result, success, error)


def save_conversation_log() -> str:
    """Save current conversation log to file.
    
    Returns:
        Path to saved file
    """
    return conversation_logger.save_to_file()