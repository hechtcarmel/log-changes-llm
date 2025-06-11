from typing import Dict, List, Optional, Any, AsyncGenerator
import json
from openai import AsyncOpenAI
from .base import BaseModel, CampaignAnalysisResponse
from prompts.campaign_changes import get_system_prompt, get_user_prompt

class OpenAIModel(BaseModel):
    """Interface for OpenAI models for campaign analysis."""
    
    def __init__(
        self, 
        api_key: str,
        model_name: str = "gpt-4o-mini", 
    ):
        self.model_name = model_name
        self.client = AsyncOpenAI(api_key=api_key, timeout=600.0)
    
    async def analyze_campaign_changes(
        self, 
        changes_text: str,
        campaign_id: int
    ) -> AsyncGenerator[str, None]:
        """Analyze campaign changes and provide insights using OpenAI model."""
        system_prompt = get_system_prompt()
        user_prompt = get_user_prompt(changes_text, campaign_id)
        
        try:
            stream = await self.client.chat.completions.create(
                model=self.model_name,
                response_format={"type": "json_object"},
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
    
 