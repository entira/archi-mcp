"""Enhanced MCP Debug Logger for server-client communication tracking."""

import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import traceback


class MCPDebugLogger:
    """Enhanced debug logger for MCP server-client communication."""
    
    def __init__(self, log_dir: str = "/tmp"):
        """Initialize MCP debug logger.
        
        Args:
            log_dir: Directory to save debug logs (default: /tmp)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.session_id = f"mcp_debug_{int(time.time())}"
        self.call_counter = 0
        self.debug_entries: List[Dict[str, Any]] = []
        
        # Create session log file
        self.log_file_path = self.log_dir / f"{self.session_id}.md"
        self._initialize_log_file()
    
    def _initialize_log_file(self) -> None:
        """Initialize the debug log file with header."""
        header = f"""# 🐛 MCP Server Debug Log
        
**Session ID:** `{self.session_id}`  
**Started:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Server:** ArchiMate MCP Server  
**Purpose:** Debug communication between MCP server and client

---

"""
        with open(self.log_file_path, 'w', encoding='utf-8') as f:
            f.write(header)
    
    def log_tool_call(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any], 
        start_time: Optional[float] = None
    ) -> str:
        """Log the start of an MCP tool call and return call ID.
        
        Args:
            tool_name: Name of the MCP tool being called
            parameters: Tool parameters from client
            start_time: Optional start timestamp
            
        Returns:
            Unique call ID for tracking this call
        """
        self.call_counter += 1
        call_id = f"call_{self.call_counter:03d}"
        
        if start_time is None:
            start_time = time.time()
        
        debug_entry = {
            "call_id": call_id,
            "tool_name": tool_name,
            "parameters": parameters,
            "start_time": start_time,
            "start_timestamp": datetime.fromtimestamp(start_time).isoformat(),
            "status": "in_progress"
        }
        
        self.debug_entries.append(debug_entry)
        self._write_call_start(debug_entry)
        
        return call_id
    
    def log_tool_result(
        self, 
        call_id: str, 
        result: Any, 
        success: bool = True, 
        error: Optional[str] = None,
        end_time: Optional[float] = None
    ) -> None:
        """Log the result of an MCP tool call.
        
        Args:
            call_id: Call ID from log_tool_call
            result: Tool result/output
            success: Whether the call was successful
            error: Error message if failed
            end_time: Optional end timestamp
        """
        if end_time is None:
            end_time = time.time()
        
        # Find the matching debug entry
        debug_entry = None
        for entry in self.debug_entries:
            if entry["call_id"] == call_id:
                debug_entry = entry
                break
        
        if debug_entry is None:
            # Create a new entry if not found (shouldn't happen)
            debug_entry = {
                "call_id": call_id,
                "tool_name": "unknown",
                "parameters": {},
                "start_time": end_time - 0.1,
                "start_timestamp": datetime.fromtimestamp(end_time - 0.1).isoformat()
            }
            self.debug_entries.append(debug_entry)
        
        # Update the entry with results
        debug_entry.update({
            "end_time": end_time,
            "end_timestamp": datetime.fromtimestamp(end_time).isoformat(),
            "duration": end_time - debug_entry["start_time"],
            "success": success,
            "result": self._sanitize_result(result),
            "error": error,
            "status": "completed" if success else "failed"
        })
        
        self._write_call_result(debug_entry)
        self._update_summary()
    
    def log_client_message(self, message: str, message_type: str = "info") -> None:
        """Log a message from the client perspective.
        
        Args:
            message: Message content
            message_type: Type of message (info, warning, error)
        """
        timestamp = datetime.now().isoformat()
        
        entry = {
            "timestamp": timestamp,
            "type": "client_message",
            "message_type": message_type,
            "content": message[:1000]  # Truncate long messages
        }
        
        self.debug_entries.append(entry)
        self._write_client_message(entry)
    
    def log_server_event(self, event: str, details: Dict[str, Any] = None) -> None:
        """Log a server-side event.
        
        Args:
            event: Event description
            details: Additional event details
        """
        timestamp = datetime.now().isoformat()
        
        entry = {
            "timestamp": timestamp,
            "type": "server_event",
            "event": event,
            "details": details or {}
        }
        
        self.debug_entries.append(entry)
        self._write_server_event(entry)
    
    def log_error(self, error: Exception, context: str = "") -> None:
        """Log an error with full traceback.
        
        Args:
            error: Exception that occurred
            context: Additional context about where the error occurred
        """
        timestamp = datetime.now().isoformat()
        
        entry = {
            "timestamp": timestamp,
            "type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "traceback": traceback.format_exc()
        }
        
        self.debug_entries.append(entry)
        self._write_error(entry)
    
    def _sanitize_result(self, result: Any) -> str:
        """Sanitize result for logging (truncate if too long).
        
        Args:
            result: Tool result to sanitize
            
        Returns:
            Sanitized result string
        """
        result_str = str(result)
        
        # Truncate very long results
        if len(result_str) > 2000:
            return result_str[:2000] + f"... [TRUNCATED - {len(result_str)} total chars]"
        
        return result_str
    
    def _write_call_start(self, entry: Dict[str, Any]) -> None:
        """Write tool call start to log file."""
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n## 🔧 [{entry['call_id']}] {entry['tool_name']} - STARTED\n")
            f.write(f"**Time:** {entry['start_timestamp']}  \n")
            f.write(f"**Status:** {entry['status']}  \n\n")
            
            if entry['parameters']:
                f.write("**Parameters:**\n")
                f.write("```json\n")
                f.write(json.dumps(entry['parameters'], indent=2, ensure_ascii=False))
                f.write("\n```\n\n")
            else:
                f.write("**Parameters:** None\n\n")
    
    def _write_call_result(self, entry: Dict[str, Any]) -> None:
        """Write tool call result to log file."""
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            status_icon = "✅" if entry['success'] else "❌"
            f.write(f"### {status_icon} [{entry['call_id']}] {entry['tool_name']} - COMPLETED\n")
            f.write(f"**End Time:** {entry['end_timestamp']}  \n")
            f.write(f"**Duration:** {entry['duration']:.3f}s  \n")
            f.write(f"**Success:** {entry['success']}  \n\n")
            
            if entry['success'] and entry['result']:
                f.write("**Result:**\n")
                f.write("```\n")
                f.write(entry['result'])
                f.write("\n```\n\n")
            
            if not entry['success'] and entry['error']:
                f.write("**Error:**\n")
                f.write("```\n")
                f.write(entry['error'])
                f.write("\n```\n\n")
            
            f.write("---\n\n")
    
    def _write_client_message(self, entry: Dict[str, Any]) -> None:
        """Write client message to log file."""
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            icon = "💬" if entry['message_type'] == "info" else "⚠️" if entry['message_type'] == "warning" else "🚨"
            f.write(f"\n## {icon} Client Message ({entry['message_type'].upper()})\n")
            f.write(f"**Time:** {entry['timestamp']}  \n\n")
            f.write("```\n")
            f.write(entry['content'])
            f.write("\n```\n\n")
    
    def _write_server_event(self, entry: Dict[str, Any]) -> None:
        """Write server event to log file."""
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n## 🖥️ Server Event\n")
            f.write(f"**Time:** {entry['timestamp']}  \n")
            f.write(f"**Event:** {entry['event']}  \n\n")
            
            if entry['details']:
                f.write("**Details:**\n")
                f.write("```json\n")
                f.write(json.dumps(entry['details'], indent=2, ensure_ascii=False))
                f.write("\n```\n\n")
    
    def _write_error(self, entry: Dict[str, Any]) -> None:
        """Write error to log file."""
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n## 🚨 ERROR: {entry['error_type']}\n")
            f.write(f"**Time:** {entry['timestamp']}  \n")
            f.write(f"**Context:** {entry['context']}  \n\n")
            f.write(f"**Error Message:**\n")
            f.write("```\n")
            f.write(entry['error_message'])
            f.write("\n```\n\n")
            f.write(f"**Traceback:**\n")
            f.write("```python\n")
            f.write(entry['traceback'])
            f.write("\n```\n\n")
    
    def _update_summary(self) -> None:
        """Update the summary statistics in the log file."""
        # Count statistics
        tool_calls = [e for e in self.debug_entries if e.get('call_id')]
        successful_calls = [e for e in tool_calls if e.get('success') == True]
        failed_calls = [e for e in tool_calls if e.get('success') == False]
        errors = [e for e in self.debug_entries if e.get('type') == 'error']
        
        # Read the current file and update the header
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find where to insert summary (after the header)
            header_end = content.find("---\n") + 4
            
            summary = f"""
## 📊 Session Summary (Live Updated)

- **Total Tool Calls:** {len(tool_calls)}
- **Successful:** {len(successful_calls)} ✅
- **Failed:** {len(failed_calls)} ❌
- **Errors Logged:** {len(errors)} 🚨
- **Last Updated:** {datetime.now().strftime('%H:%M:%S')}

### 🔧 Most Used Tools
"""
            
            # Count tool usage
            tool_usage = {}
            for call in tool_calls:
                tool_name = call.get('tool_name', 'unknown')
                tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
            
            for tool_name, count in sorted(tool_usage.items(), key=lambda x: x[1], reverse=True):
                summary += f"- `{tool_name}`: {count} calls\n"
            
            summary += "\n---\n"
            
            # Replace the content after header
            new_content = content[:header_end] + summary + content[header_end:]
            
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
        except Exception as e:
            # If summary update fails, just log it and continue
            pass
    
    def get_log_file_path(self) -> str:
        """Get the path to the current log file.
        
        Returns:
            Path to the log file
        """
        return str(self.log_file_path)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics.
        
        Returns:
            Dictionary with session statistics
        """
        tool_calls = [e for e in self.debug_entries if e.get('call_id')]
        successful_calls = [e for e in tool_calls if e.get('success') == True]
        failed_calls = [e for e in tool_calls if e.get('success') == False]
        
        return {
            "session_id": self.session_id,
            "total_calls": len(tool_calls),
            "successful_calls": len(successful_calls),
            "failed_calls": len(failed_calls),
            "total_entries": len(self.debug_entries),
            "log_file": str(self.log_file_path)
        }


# Global debug logger instance
mcp_debug_logger = MCPDebugLogger()


def log_mcp_call_start(tool_name: str, parameters: Dict[str, Any]) -> str:
    """Convenience function to log MCP tool call start.
    
    Args:
        tool_name: Name of the MCP tool
        parameters: Tool parameters
        
    Returns:
        Call ID for tracking
    """
    return mcp_debug_logger.log_tool_call(tool_name, parameters)


def log_mcp_call_result(call_id: str, result: Any, success: bool = True, error: Optional[str] = None) -> None:
    """Convenience function to log MCP tool call result.
    
    Args:
        call_id: Call ID from log_mcp_call_start
        result: Tool result
        success: Whether call was successful
        error: Error message if failed
    """
    mcp_debug_logger.log_tool_result(call_id, result, success, error)


def log_mcp_error(error: Exception, context: str = "") -> None:
    """Convenience function to log MCP errors.
    
    Args:
        error: Exception that occurred
        context: Additional context
    """
    mcp_debug_logger.log_error(error, context)


def get_debug_log_path() -> str:
    """Get the current debug log file path.
    
    Returns:
        Path to the debug log file
    """
    return mcp_debug_logger.get_log_file_path()