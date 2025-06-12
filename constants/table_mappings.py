"""Table mappings and display configurations."""

# Available tables for campaign changes
AVAILABLE_TABLES = [
    "sp_campaign_details_v2_changes_log",
    "sp_campaign_targeting_v2_changes_log", 
    "sp_campaign_creative_v2_changes_log",
    "sp_campaign_budget_v2_changes_log"
]

# Table display name mappings
TABLE_DISPLAY_NAMES = {
    "sp_campaign_details_v2_changes_log": "Campaign Details",
    "sp_campaign_targeting_v2_changes_log": "Campaign Targeting",
    "sp_campaign_creative_v2_changes_log": "Campaign Creative", 
    "sp_campaign_budget_v2_changes_log": "Campaign Budget"
}

def get_display_name(table_name: str) -> str:
    """Get display name for a table."""
    if table_name in TABLE_DISPLAY_NAMES:
        return TABLE_DISPLAY_NAMES[table_name]
    
    # Fallback: clean up table name automatically
    return table_name.replace('_changes_log', '').replace('_', ' ').title()

def get_table_choices() -> list:
    """Get list of table choices for UI selection."""
    return [(get_display_name(table), table) for table in AVAILABLE_TABLES] 