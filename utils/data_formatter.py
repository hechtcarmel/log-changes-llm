from typing import List, Dict, Any
import pandas as pd

def format_changes_table(changes: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Format campaign changes into a pandas DataFrame for Gradio display.
    
    Args:
        changes: List of change records from database
        
    Returns:
        pandas DataFrame formatted for display
    """
    if not changes:
        return pd.DataFrame(columns=['ID', 'Field', 'Old Value', 'New Value', 'Update Time', 'User'])
    
    # Convert to DataFrame
    df = pd.DataFrame(changes)
    
    # Select and rename columns for display
    display_columns = {
        'id': 'ID',
        'field_name': 'Field',
        'old_value': 'Old Value',
        'new_value': 'New Value',
        'update_time': 'Update Time',
        'update_user': 'User'
    }
    
    # Select relevant columns and rename
    df_display = df[list(display_columns.keys())].rename(columns=display_columns)
    
    # Truncate long values for display
    df_display['Old Value'] = df_display['Old Value'].apply(lambda x: truncate_text(str(x) if x else '', 50))
    df_display['New Value'] = df_display['New Value'].apply(lambda x: truncate_text(str(x) if x else '', 50))
    
    # Format datetime
    df_display['Update Time'] = pd.to_datetime(df_display['Update Time']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return df_display

def format_grouped_changes_table(grouped_changes: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Format grouped campaign changes into a DataFrame for display.
    
    Args:
        grouped_changes: List of grouped change records
        
    Returns:
        pandas DataFrame with grouped changes
    """
    if not grouped_changes:
        return pd.DataFrame(columns=['Update Time', 'User', 'Changes Count', 'Fields Modified'])
    
    rows = []
    for group in grouped_changes:
        fields_modified = ', '.join([change['field_name'] for change in group['changes']])
        rows.append({
            'Update Time': group['update_time'],
            'User': group['update_user'],
            'Changes Count': group['changes_count'],
            'Fields Modified': truncate_text(fields_modified, 100)
        })
    
    df = pd.DataFrame(rows)
    
    # Format datetime
    if not df.empty:
        df['Update Time'] = pd.to_datetime(df['Update Time']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return df

def truncate_text(text: str, max_length: int) -> str:
    """
    Truncate text to specified length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def format_connection_status(status: Dict[str, Any]) -> str:
    """
    Format database connection status for display.
    
    Args:
        status: Connection status dictionary
        
    Returns:
        Formatted status string
    """
    if status.get('success'):
        return f"✅ Connected to {status['host']}:{status['port']}/{status['database']}"
    else:
        return f"❌ Connection failed: {status.get('message', 'Unknown error')}"

def format_summary_stats(stats: Dict[str, Any], from_date: str = None, to_date: str = None) -> str:
    """
    Format campaign summary statistics for display.
    
    Args:
        stats: Summary statistics dictionary
        from_date: Filter start date (optional)
        to_date: Filter end date (optional)
        
    Returns:
        Formatted statistics string
    """
    if stats['total_changes'] == 0:
        return "No changes found for this campaign in the specified date range."
    
    # Build filter info
    filter_info = ""
    if from_date or to_date:
        filter_info = "\n**Applied Filters:**\n"
        if from_date:
            filter_info += f"📅 From Date: {from_date}\n"
        if to_date:
            filter_info += f"📅 To Date: {to_date}\n"
    
    text = f"""**Campaign Change Summary:**
📊 Total Changes: {stats['total_changes']}
🔧 Unique Fields: {stats['unique_fields']}
👥 Unique Users: {stats['unique_users']}{filter_info}

**Actual Date Range in Results:**
📅 Earliest: {stats['date_range']['earliest'][:19] if stats['date_range']['earliest'] else 'N/A'}
📅 Latest: {stats['date_range']['latest'][:19] if stats['date_range']['latest'] else 'N/A'}

**Most Changed Fields:**
"""
    
    for field, count in list(stats['most_changed_fields'].items())[:5]:
        text += f"• {field}: {count} changes\n"
    
    text += "\n**User Activity:**\n"
    for user, count in list(stats['users_activity'].items())[:5]:
        text += f"👤 {user}: {count} changes\n"
    
    return text 