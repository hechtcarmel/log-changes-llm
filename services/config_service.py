"""Configuration service for application settings and environment management."""

import os
from typing import Dict, Any
from dotenv import load_dotenv
from constants import DATABASE_CONFIG, AI_MODEL_CONFIG

class ConfigService:
    """Manages application configuration and environment settings."""
    
    def __init__(self):
        """Initialize configuration service and load environment variables."""
        load_dotenv()
        self._config = self._load_configuration()
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load and validate configuration from environment and constants."""
        config = {
            "database": DATABASE_CONFIG.copy(),
            "ai_model": {
                **AI_MODEL_CONFIG,
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model_name": os.getenv("OPENAI_MODEL", AI_MODEL_CONFIG["default_model"])
            },
            "app": {
                "title": "Campaign Changes Analyzer",
                "description": "AI-powered campaign modification analysis tool",
                "version": "2.0.0"
            }
        }
        return config
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return self._config["database"].copy()
    
    def get_ai_model_config(self) -> Dict[str, Any]:
        """Get AI model configuration."""
        return self._config["ai_model"].copy()
    
    def get_app_config(self) -> Dict[str, Any]:
        """Get application configuration."""
        return self._config["app"].copy()
    
    def has_openai_api_key(self) -> bool:
        """Check if OpenAI API key is configured in environment."""
        return bool(self._config["ai_model"]["api_key"])
    
    def get_openai_api_key(self) -> str:
        """Get OpenAI API key from environment."""
        return self._config["ai_model"]["api_key"] or ""
    
    def get_openai_model_name(self) -> str:
        """Get OpenAI model name."""
        return self._config["ai_model"]["model_name"] 