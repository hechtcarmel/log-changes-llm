from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Any
import json

class CampaignAnalysisResponse:
    """Structured response from campaign analysis LLM models."""
    
    def __init__(
        self, 
        summary: Optional[str] = None,
        change_history: Optional[str] = None,
        key_insights: Optional[List[str]] = None,
        raw_response: Optional[str] = None
    ):
        self.summary = summary or "No summary available"
        self.change_history = change_history or "No change history available"
        self.key_insights = key_insights or []
        self.raw_response = raw_response
    
    def to_json(self) -> str:
        """Convert response to JSON string."""
        return json.dumps({
            "summary": self.summary,
            "change_history": self.change_history,
            "key_insights": self.key_insights,
            "raw_response": self.raw_response
        })
    
    def to_dict(self) -> Dict:
        """Convert response to dictionary."""
        return {
            "summary": self.summary,
            "change_history": self.change_history,
            "key_insights": self.key_insights,
            "raw_response": self.raw_response
        }
    
    def to_formatted_text(self) -> str:
        """Convert response to formatted text for display."""
        text = f"**Summary:**\n{self.summary}\n\n"
        
        if self.change_history and self.change_history != "No change history available":
            text += "**📋 Change History:**\n"
            text += f"{self.change_history}\n\n"
        
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