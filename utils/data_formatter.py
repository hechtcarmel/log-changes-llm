from typing import List, Dict, Any
import pandas as pd
from campaign_analyzer.constants import SKIP_FIELDS, DISPLAY_CONFIG

def get_performer_or_user(data: Dict[str, Any]) -> str:
    """
    Gets the performer if it exists, otherwise the update_user.
    Returns empty string if neither exist.
    
    Args:
        data: Dictionary containing potential performer or update_user keys
        
    Returns:
        String with performer, update_user, or empty string
    """
    if 'performer' in data and data['performer']:
        return data['performer']
    elif 'update_user' in data and data['update_user']:
        return data['update_user']
    return ''

def format_grouped_changes_for_display(sessions: List[Dict[str, Any]]) -> any:
    """Formats sessions into a table with a header row for each session."""
    if not sessions:
        return None
    
    display_rows = []
    skip_fields = SKIP_FIELDS
    
    # Each item in `sessions` is now a discrete session.
    for session in sessions:
        # Filter changes for this session
        filtered_changes = [change for change in session['changes'] if change.get('field_name') not in skip_fields]
        if not filtered_changes:
            continue  # Skip this session if no changes remain after filtering

        display_table_name = session['source_table'].replace('_changes_log', '').replace('_', ' ').title()
        date_style = DISPLAY_CONFIG["date_style"]
        summary_text = f"_{session['change_count']} changes in this session_"

        display_rows.append({
            'Date': f"<div {date_style}><b>{session['date']}</b></div>",
            'Time': f"<b>{session['time']}</b>",
            'Performer/User': f"<b>{session['user']}</b>",
            'Table': f"<b>{display_table_name}</b>",
            'Field': '', 
            'Old Value': '', 
            'New Value': f"<b>{summary_text}</b>"
        })

        for change in filtered_changes:
            display_rows.append({
                'Date': '',
                'Time': '',  # Do not display time in non-header rows
                'Performer/User': '',
                'Table': '',
                'Field': change.get('field_name'),
                'Old Value': str(change.get('old_value', ''))[:DISPLAY_CONFIG["max_value_length"]],
                'New Value': str(change.get('new_value', ''))[:DISPLAY_CONFIG["max_value_length"]]
            })
    
    if not display_rows:
        return None
        
    df = pd.DataFrame(display_rows)
    # Define the final column order
    df = df[DISPLAY_CONFIG["table_columns"]]
    return df

def format_summary_stats(stats: Dict[str, Any], from_date: str, to_date: str, selected_tables: List[str]) -> str:
    """Format summary statistics as markdown text."""
    
    # Calculate table-specific stats
    table_stats = {}
    if 'changes' in stats:
        for change in stats['changes']:
            table = change.get('source_table', 'Unknown')
            if table not in table_stats:
                table_stats[table] = 0
            table_stats[table] += 1
    
    # Sort tables by change count
    sorted_tables = sorted(table_stats.items(), key=lambda x: x[1], reverse=True)
    
    stats_text = f"""
## 📊 Analysis Summary

### 🗓️ Date Range
- **From:** {from_date}
- **To:** {to_date}
- **Selected Tables:** {len(selected_tables)} out of {len(selected_tables)} available

### 📈 Overall Statistics
- **Total Changes:** {stats.get('total_changes', 0):,}
- **Unique Fields Modified:** {stats.get('unique_fields', 0)}
- **Date Range (Days):** {stats.get('date_range_days', 0)}
- **Average Changes/Day:** {stats.get('changes_per_day', 0):.1f}

### 🗂️ Changes by Data Source
"""
    
    if sorted_tables:
        for table, count in sorted_tables:
            # Clean up table name for display
            display_name = table.replace('_changes_log', '').replace('_', ' ').title()
            percentage = (count / stats.get('total_changes', 1)) * 100
            stats_text += f"- **{display_name}:** {count:,} changes ({percentage:.1f}%)\n"
    else:
        stats_text += "- No changes found in selected tables\n"
    
    stats_text += f"""

### 👥 Performer/User Activity
- **Active Performers/Users:** {stats.get('unique_users', 0)}
- **Most Active Performer/User:** {stats.get('most_active_user', 'N/A')} ({stats.get('most_active_user_changes', 0)} changes)

### 🏆 Top Modified Fields
"""
    
    top_fields = stats.get('top_fields', [])
    for field, count in top_fields[:DISPLAY_CONFIG["top_fields_limit"]]:
        stats_text += f"- **{field}:** {count} changes\n"
    
    if not top_fields:
        stats_text += "- No field data available\n"
    
    return stats_text

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

def format_connection_status(connection_info: Dict[str, Any]) -> str:
    """Format database connection status message."""
    if connection_info['success']:
        if connection_info.get('version'):
            return f"✅ Connected to {connection_info['version']}"
        else:
            return "✅ Database connection successful"
    else:
        return f"❌ Connection failed: {connection_info.get('error', 'Unknown error')}"

 