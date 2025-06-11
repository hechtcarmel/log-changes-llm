from typing import List, Dict, Any
import pandas as pd

def format_grouped_changes_for_display(sessions: List[Dict[str, Any]]) -> any:
    """Formats sessions into a table with a header row for each session."""
    if not sessions:
        return None
    
    display_rows = []
    skip_fields = {'update_time', 'performer', 'update_user'}
    
    # Each item in `sessions` is now a discrete session.
    for session in sessions:
        # Filter changes for this session
        filtered_changes = [change for change in session['changes'] if change.get('field_name') not in skip_fields]
        if not filtered_changes:
            continue  # Skip this session if no changes remain after filtering

        display_table_name = session['source_table'].replace('_changes_log', '').replace('_', ' ').title()
        date_style = "style='border-bottom:2px solid #bdbdbd; display:block;'"
        summary_text = f"_{session['change_count']} changes in this session_"

        display_rows.append({
            'Date': f"<div {date_style}><b>{session['date']}</b></div>",
            'Time': f"<b>{session['time']}</b>",
            'User': f"<b>{session['user']}</b>",
            'Table': f"<b>{display_table_name}</b>",
            'Field': '', 
            'Old Value': '', 
            'New Value': f"<b>{summary_text}</b>"
        })

        for change in filtered_changes:
            display_rows.append({
                'Date': '',
                'Time': '',  # Do not display time in non-header rows
                'User': '',
                'Table': '',
                'Field': change.get('field_name'),
                'Old Value': str(change.get('old_value', ''))[:100],
                'New Value': str(change.get('new_value', ''))[:100]
            })
    
    if not display_rows:
        return None
        
    df = pd.DataFrame(display_rows)
    # Define the final column order: Date, Time, User, Table, Field, Old Value, New Value
    df = df[['Date', 'Time', 'User', 'Table', 'Field', 'Old Value', 'New Value']]
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

### 👥 User Activity
- **Active Users:** {stats.get('unique_users', 0)}
- **Most Active User:** {stats.get('most_active_user', 'N/A')} ({stats.get('most_active_user_changes', 0)} changes)

### 🏆 Top Modified Fields
"""
    
    top_fields = stats.get('top_fields', [])
    for field, count in top_fields[:10]:  # Show top 10
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

 