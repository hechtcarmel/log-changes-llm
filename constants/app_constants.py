"""Application constants and configuration values."""

# Database Configuration
DATABASE_CONFIG = {
    "host": "proxysql-office.taboolasyndication.com",
    "port": 6033,
    "database": "trc",
    "connect_timeout": 10,
    "charset": "utf8mb4"
}

# AI Model Configuration
AI_MODEL_CONFIG = {
    "default_model": "gpt-4o-mini",
    "timeout": 600.0,
    "response_format": {"type": "json_object"}
}

# Field Configuration
SKIP_FIELDS = {'update_time', 'performer', 'update_user'}

# Validation Constants
VALIDATION_RULES = {
    "min_records": 1,
    "max_records": 1000,
    "date_format": "%Y-%m-%d",
    "campaign_id_min": 1
}

# UI Constants
UI_MESSAGES = {
    "starting_analysis": "🔄 Starting analysis...",
    "input_validation": "✅ Input validation completed",
    "db_connection": "🔌 Testing database connection...",
    "db_success": "✅ Database connection successful",
    "querying_tables": "🔍 Querying {} tables...",
    "data_retrieved": "✅ Data retrieved",
    "formatting_data": "📊 Formatting data for AI...",
    "ai_analysis": "🤖 Streaming AI analysis...",
    "ai_generating": "🤖 Generating AI analysis...",
    "no_username_password": "❌ Please provide database username and password",
    "no_campaign_id": "❌ Please provide a campaign ID",
    "no_dates": "❌ Please provide both from and to dates",
    "no_tables": "❌ Please select at least one table to query",
    "no_api_key": "❌ Please provide an OpenAI API key",
    "invalid_campaign_id": "❌ Campaign ID must be a number",
    "invalid_date_format": "❌ Dates must be in YYYY-MM-DD format",
    "invalid_date_range": "❌ From Date must be before To Date",
    "db_connection_failed": "❌ Failed to connect to database",
    "ai_init_failed": "❌ Failed to initialize OpenAI model: {}",
    "no_changes_found": "No changes found for campaign ID {}"
}

# Progress Steps
PROGRESS_STEPS = {
    "validation": 0.2,
    "db_test": 0.3,
    "db_connect": 0.4,
    "query_data": 0.5,
    "data_retrieved": 0.6,
    "format_data": 0.7,
    "ai_analysis": 0.8
}

# Display Configuration  
DISPLAY_CONFIG = {
    "max_value_length": 100,
    "date_style": "style='border-bottom:2px solid #bdbdbd; display:block;'",
    "table_columns": ['Date', 'Time', 'Performer/User', 'Table', 'Field', 'Old Value', 'New Value'],
    "top_fields_limit": 10
} 