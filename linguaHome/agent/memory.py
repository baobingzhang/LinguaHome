"""
LinguaHome Memory System
Simplified from NanoBot, focused on smart home context.
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional


def today_date() -> str:
    """Get today's date string."""
    return datetime.now().strftime("%Y-%m-%d")


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    return path


class MemoryStore:
    """
    Memory system for LinguaHome.
    
    Supports:
    - Daily notes (memory/YYYY-MM-DD.md) for session context
    - Long-term memory (MEMORY.md) for user preferences
    - Sensor event logging
    """
    
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.memory_dir = ensure_dir(workspace / "memory")
        self.memory_file = self.memory_dir / "MEMORY.md"
    
    def get_today_file(self) -> Path:
        """Get path to today's memory file."""
        return self.memory_dir / f"{today_date()}.md"
    
    def read_today(self) -> str:
        """Read today's memory notes."""
        today_file = self.get_today_file()
        if today_file.exists():
            return today_file.read_text(encoding="utf-8")
        return ""
    
    def append_today(self, content: str) -> None:
        """Append content to today's memory notes."""
        today_file = self.get_today_file()
        
        if today_file.exists():
            existing = today_file.read_text(encoding="utf-8")
            content = existing + "\n" + content
        else:
            header = f"# LinguaHome Log - {today_date()}\n\n"
            content = header + content
        
        today_file.write_text(content, encoding="utf-8")
    
    def read_long_term(self) -> str:
        """Read long-term memory (MEMORY.md)."""
        if self.memory_file.exists():
            return self.memory_file.read_text(encoding="utf-8")
        return ""
    
    def write_long_term(self, content: str) -> None:
        """Write to long-term memory (MEMORY.md)."""
        self.memory_file.write_text(content, encoding="utf-8")
    
    def append_long_term(self, content: str) -> None:
        """Append to long-term memory."""
        existing = self.read_long_term()
        if existing:
            content = existing + "\n" + content
        else:
            content = "# LinguaHome User Preferences\n\n" + content
        self.write_long_term(content)
    
    def get_recent_memories(self, days: int = 3) -> str:
        """Get memories from the last N days."""
        memories = []
        today = datetime.now().date()
        
        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            file_path = self.memory_dir / f"{date_str}.md"
            
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                memories.append(content)
        
        return "\n\n---\n\n".join(memories)
    
    def remember_sensor_event(self, sensor_name: str, value: str, status: str) -> None:
        """Record a significant sensor event."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"- [{timestamp}] {sensor_name}: {value} ({status})"
        self.append_today(entry)
    
    def remember_user_command(self, command: str, result: str) -> None:
        """Record a user command and its result."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"- [{timestamp}] Command: {command}\n  Result: {result}"
        self.append_today(entry)
    
    def remember_preference(self, preference: str) -> None:
        """Record a user preference to long-term memory."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"- [{timestamp}] {preference}"
        self.append_long_term(entry)
    
    def get_memory_context(self) -> str:
        """Get memory context for LLM."""
        parts = []
        
        # Long-term memory (preferences)
        long_term = self.read_long_term()
        if long_term:
            parts.append("## User Preferences\n" + long_term)
        
        # Recent activity
        recent = self.get_recent_memories(days=1)
        if recent:
            parts.append("## Recent Activity\n" + recent)
        
        return "\n\n".join(parts) if parts else ""
