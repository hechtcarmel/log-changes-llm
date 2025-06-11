from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Any
import json

class ChangeEntry:
    """Represents a single field change."""
    
    def __init__(self, timestamp: str, user: str, field: str, old_value: str, new_value: str):
        self.timestamp = timestamp
        self.user = user
        self.field = field
        self.old_value = old_value
        self.new_value = new_value
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChangeEntry':
        """Create a ChangeEntry from a dictionary."""
        return cls(
            timestamp=data.get("timestamp", ""),
            user=data.get("user", ""),
            field=data.get("field", ""),
            old_value=data.get("old_value", ""),
            new_value=data.get("new_value", "")
        )
    
    def to_formatted_line(self) -> str:
        """Format the change as a single line."""
        return f"• {self.field}: \"{self.old_value}\" → \"{self.new_value}\""

class ChangeSession:
    """Represents a group of changes made at the same time by the same user."""
    
    def __init__(self, timestamp: str, user: str, changes: List[ChangeEntry]):
        self.timestamp = timestamp
        self.user = user
        self.changes = changes
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChangeSession':
        """Create a ChangeSession from a dictionary."""
        changes = [ChangeEntry.from_dict(change) for change in data.get("changes", [])]
        return cls(
            timestamp=data.get("timestamp", ""),
            user=data.get("user", ""),
            changes=changes
        )
    
    def to_formatted_block(self) -> str:
        """Format the session as a formatted block."""
        header = f"On {self.timestamp}, user {self.user} changed:"
        change_lines = [change.to_formatted_line() for change in self.changes]
        return header + "\n" + "\n".join(change_lines)

class CampaignAnalysisResponse:
    """Structured response from campaign analysis LLM models."""
    
    def __init__(
        self, 
        summary: Optional[str] = None,
        change_sessions: Optional[List[ChangeSession]] = None,
        key_insights: Optional[List[str]] = None,
        raw_response: Optional[str] = None
    ):
        self.summary = summary or "No summary available"
        self.change_sessions = change_sessions or []
        self.key_insights = key_insights or []
        self.raw_response = raw_response
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CampaignAnalysisResponse':
        """Create a response object from a dictionary."""
        change_sessions = []
        if "change_sessions" in data:
            change_sessions = [ChangeSession.from_dict(session) for session in data["change_sessions"]]
        
        return cls(
            summary=data.get("summary"),
            change_sessions=change_sessions,
            key_insights=data.get("key_insights", []),
            raw_response=json.dumps(data)
        )
    
    def to_json(self) -> str:
        """Convert response to JSON string."""
        return json.dumps({
            "summary": self.summary,
            "change_sessions": [session.__dict__ for session in self.change_sessions],
            "key_insights": self.key_insights,
            "raw_response": self.raw_response
        })
    
    def to_dict(self) -> Dict:
        """Convert response to dictionary."""
        return {
            "summary": self.summary,
            "change_sessions": [session.__dict__ for session in self.change_sessions],
            "key_insights": self.key_insights,
            "raw_response": self.raw_response
        }
    
    def format_change_history(self) -> str:
        """Format change sessions into readable change history."""
        if not self.change_sessions:
            return "No changes found"
        
        formatted_blocks = []
        for session in self.change_sessions:
            formatted_blocks.append(session.to_formatted_block())
        
        return "\n\n----\n\n".join(formatted_blocks)
    
    def to_formatted_text(self) -> str:
        """Convert response to formatted text for display."""
        text = f"**Summary:**\n{self.summary}\n\n"
        
        if self.change_sessions:
            text += "**📋 Change History:**\n"
            text += f"{self.format_change_history()}\n\n"
        
        if self.key_insights:
            text += "**💡 Key Insights:**\n"
            for insight in self.key_insights:
                text += f"• {insight}\n"
            text += "\n"
        
        return text

class BaseModel(ABC):
    """Base class for all LLM models."""
    
    @abstractmethod
    async def analyze_campaign_changes(
        self, 
        changes_text: str,
        campaign_id: int
    ) -> CampaignAnalysisResponse:
        """Analyze campaign changes and provide insights."""
        pass 