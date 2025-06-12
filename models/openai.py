from typing import Dict, List, Optional, Any, AsyncGenerator
import json
from openai import AsyncOpenAI
from .base import BaseModel, CampaignAnalysisResponse
from campaign_analyzer.prompts.campaign_changes import get_system_prompt, get_user_prompt
from campaign_analyzer.constants import AI_MODEL_CONFIG

class OpenAIModel(BaseModel):
    """Interface for OpenAI models for campaign analysis."""
    
    def __init__(
        self, 
        api_key: str,
        model_name: str = AI_MODEL_CONFIG["default_model"], 
    ):
        self.model_name = model_name
        self.client = AsyncOpenAI(api_key=api_key, timeout=AI_MODEL_CONFIG["timeout"])
    
    async def analyze_campaign_changes(
        self, 
        changes_text: str,
        campaign_id: int,
        net_changes_text: str
    ) -> AsyncGenerator[str, None]:
        """Analyze campaign changes and provide insights using OpenAI model."""
        system_prompt = get_system_prompt()
        user_prompt = get_user_prompt(changes_text, campaign_id, net_changes_text)
        
        try:
            stream = await self.client.chat.completions.create(
                model=self.model_name,
                response_format=AI_MODEL_CONFIG["response_format"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=True
            )
            
            async for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
                
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            yield json.dumps({"error": f"Error calling OpenAI API: {str(e)}"})
    
 