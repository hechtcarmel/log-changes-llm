"""Validation service for input validation and data integrity checks."""

from datetime import datetime
from typing import List, Dict, Any, Tuple
from campaign_analyzer.constants import VALIDATION_RULES, UI_MESSAGES

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class ValidationService:
    """Centralized validation service for all application inputs."""
    
    @staticmethod
    def validate_campaign_inputs(
        username: str,
        password: str, 
        campaign_id: str,
        from_date: str,
        to_date: str,
        selected_tables: List[str],
        openai_api_key: str
    ) -> Tuple[bool, str, int]:
        """
        Validate all campaign analysis inputs.
        
        Returns:
            Tuple of (is_valid, error_message, campaign_id_int)
        """
        # Basic required field validation
        if not username or not password:
            return False, UI_MESSAGES["no_username_password"], 0
            
        if not campaign_id:
            return False, UI_MESSAGES["no_campaign_id"], 0
            
        if not from_date or not to_date:
            return False, UI_MESSAGES["no_dates"], 0
            
        if not selected_tables:
            return False, UI_MESSAGES["no_tables"], 0
            
        if not openai_api_key:
            return False, UI_MESSAGES["no_api_key"], 0
        
        # Campaign ID validation
        try:
            campaign_id_int = int(campaign_id)
            if campaign_id_int < VALIDATION_RULES["campaign_id_min"]:
                return False, UI_MESSAGES["invalid_campaign_id"], 0
        except ValueError:
            return False, UI_MESSAGES["invalid_campaign_id"], 0
        
        # Date validation
        if not ValidationService.validate_date_format(from_date):
            return False, UI_MESSAGES["invalid_date_format"], 0
            
        if not ValidationService.validate_date_format(to_date):
            return False, UI_MESSAGES["invalid_date_format"], 0
        
        # Date range validation
        if not ValidationService.validate_date_range(from_date, to_date):
            return False, UI_MESSAGES["invalid_date_range"], 0
        
        return True, "", campaign_id_int
    
    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """
        Validate date string format.
        
        Args:
            date_str: Date string to validate
            
        Returns:
            True if valid format, False otherwise
        """
        try:
            datetime.strptime(date_str, VALIDATION_RULES["date_format"])
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_date_range(from_date: str, to_date: str) -> bool:
        """
        Validate that from_date is before to_date.
        
        Args:
            from_date: Start date string
            to_date: End date string
            
        Returns:
            True if valid range, False otherwise
        """
        try:
            from_dt = datetime.strptime(from_date, VALIDATION_RULES["date_format"])
            to_dt = datetime.strptime(to_date, VALIDATION_RULES["date_format"])
            return from_dt <= to_dt
        except ValueError:
            return False
    
    @staticmethod
    def validate_openai_api_key(api_key: str) -> bool:
        """
        Basic validation for OpenAI API key format.
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if basic format is valid
        """
        return bool(api_key and api_key.startswith('sk-') and len(api_key) > 20)
    
    @staticmethod
    def validate_records_limit(max_records: int) -> bool:
        """
        Validate max records limit.
        
        Args:
            max_records: Maximum number of records
            
        Returns:
            True if within valid range
        """
        return (VALIDATION_RULES["min_records"] <= 
                max_records <= 
                VALIDATION_RULES["max_records"]) 