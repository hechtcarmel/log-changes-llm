"""Configuration service for application settings and environment management."""

import os
from typing import Dict, Any
from campaign_analyzer.constants import DATABASE_CONFIG, AI_MODEL_CONFIG


class ConfigService:
    """Manages application configuration and environment settings integrated with PyToolbox config system."""
    
    def __init__(self, config_loader=None, logger=None):
        """Initialize configuration service with PyToolbox config loader.
        
        Args:
            config_loader: PyToolbox ConfigLoader instance
            logger: PyToolbox logger instance
        """
        self.config_loader = config_loader
        self.logger = logger
        self._config = self._load_configuration()
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load and validate configuration from PyToolbox config system and constants."""
        config = {
            "database": DATABASE_CONFIG.copy(),
            "ai_model": {
                **AI_MODEL_CONFIG,
                "api_key": self._get_openai_api_key(),
                "model_name": self._get_openai_model_name()
            },
            "app": {
                "title": "Campaign Changes Analyzer",
                "description": "AI-powered campaign modification analysis tool",
                "version": "2.0.0"
            }
        }
        
        # Override database config from PyToolbox config if available
        if self.config_loader:
            # Try to get campaign analyzer specific database config
            db_config = self.config_loader.get('com.taboola.campaign_analyzer.database', {})
            if db_config:
                config["database"].update(db_config)
                if self.logger:
                    self.logger.info("Updated database config from PyToolbox configuration")
            
            # Get app configuration
            app_config = self.config_loader.get('com.taboola.campaign_analyzer.app', {})
            if app_config:
                config["app"].update(app_config)
        
        return config
    
    def _get_openai_api_key(self) -> str:
        """Get OpenAI API key from PyToolbox config or environment."""
        if self.config_loader:
            # Try PyToolbox config first
            api_key = self.config_loader.get('com.taboola.openai.api_key')
            if api_key:
                return api_key
        
        # Fallback to environment variable
        return os.getenv("OPENAI_API_KEY", "")
    
    def _get_openai_model_name(self) -> str:
        """Get OpenAI model name from PyToolbox config or environment."""
        if self.config_loader:
            # Try PyToolbox config first
            model_name = self.config_loader.get('com.taboola.campaign_analyzer.ai_model.model_name') or \
                        self.config_loader.get('com.taboola.openai.model')
            if model_name:
                return model_name
        
        # Fallback to environment variable or default
        return os.getenv("OPENAI_MODEL", AI_MODEL_CONFIG["default_model"])
    
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
        """Check if OpenAI API key is configured."""
        return bool(self._config["ai_model"]["api_key"])
    
    def get_openai_api_key(self) -> str:
        """Get OpenAI API key."""
        return self._config["ai_model"]["api_key"] or ""
    
    def get_openai_model_name(self) -> str:
        """Get OpenAI model name."""
        return self._config["ai_model"]["model_name"] 