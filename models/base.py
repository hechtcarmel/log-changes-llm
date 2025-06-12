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
        
        header = f"On {self.timestamp}\n{self.user} changed:"
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
        
        if self.key_insights:
            text += "**💡 Key Insights:**\n"
            for insight in self.key_insights:
                text += f"• {insight}\n"
            text += "\n"
        
        if self.change_sessions:
            text += "**📋 Change History:**\n"
            text += f"{self.format_change_history()}\n\n"
        
        return text

    @staticmethod
    def format_partial_response(partial_json: str) -> str:
        """Format partial JSON response for streaming display."""
        try:
            # Try to parse complete JSON first
            parsed = json.loads(partial_json)
            response = CampaignAnalysisResponse.from_dict(parsed)
            return response.to_formatted_text()
        except json.JSONDecodeError:
            # Parse partial content for streaming display
            display_text = ""
            
            # Try to extract summary if present
            if '"summary"' in partial_json:
                summary_start = partial_json.find('"summary"')
                if summary_start != -1:
                    # Find the start of the summary value
                    colon_pos = partial_json.find(':', summary_start)
                    if colon_pos != -1:
                        # Find the opening quote
                        quote_start = partial_json.find('"', colon_pos)
                        if quote_start != -1:
                            # Try to find the closing quote (but it might be incomplete)
                            quote_end = partial_json.find('"', quote_start + 1)
                            if quote_end != -1:
                                summary_content = partial_json[quote_start + 1:quote_end]
                            else:
                                # Incomplete summary - show what we have
                                summary_content = partial_json[quote_start + 1:] + "..."
                            
                            # Clean up escape sequences
                            summary_content = summary_content.replace('\\n', '\n').replace('\\"', '"')
                            display_text += f"**Summary:**\n{summary_content}\n\n"
            
            # Try to extract key insights if present
            if '"key_insights"' in partial_json:
                insights_start = partial_json.find('"key_insights"')
                if insights_start != -1:
                    # Look for the array start
                    bracket_start = partial_json.find('[', insights_start)
                    if bracket_start != -1:
                        # Try to extract insights from the array
                        insights_section = partial_json[bracket_start:]
                        display_text += "**💡 Key Insights:**\n"
                        
                        # Simple extraction of quoted strings in the array
                        import re
                        insight_matches = re.findall(r'"([^"]*)"', insights_section)
                        for insight in insight_matches:
                            if insight and not insight in ['key_insights', 'summary']:
                                display_text += f"• {insight}\n"
                        
                        if not insight_matches:
                            display_text += "Generating insights...\n"
                        display_text += "\n"
            
            # If we couldn't parse anything meaningful, show generating message
            if not display_text:
                display_text = "🤖 Generating AI analysis..."
            
            return display_text

class BaseModel(ABC):
    """Base class for all LLM models."""
    
    @abstractmethod
    async def analyze_campaign_changes(
        self, 
        changes_text: str,
        campaign_id: int,
        net_changes_text: str
    ) -> CampaignAnalysisResponse:
        """Analyze campaign changes and provide insights."""
        pass 