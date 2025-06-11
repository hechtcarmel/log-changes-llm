from typing import List, Dict, Any
import pandas as pd

def format_changes_table(changes: List[Dict[str, Any]]) -> any:
    """Format campaign changes data for Gradio DataFrame display."""
    if not changes:
        return None
    
    # Convert to DataFrame with source table information
    df_data = []
    for change in changes:
        df_data.append({
            'Source Table': change.get('source_table', 'Unknown'),
            'Campaign ID': change.get('campaign_id'),
            'Field': change.get('field_name'),
            'Old Value': str(change.get('old_value', ''))[:100] + ('...' if len(str(change.get('old_value', ''))) > 100 else ''),
            'New Value': str(change.get('new_value', ''))[:100] + ('...' if len(str(change.get('new_value', ''))) > 100 else ''),
            'Update Time': change.get('update_time'),
            'User': change.get('update_user', 'N/A')
        })
    
    return pd.DataFrame(df_data)

def format_grouped_changes_table(grouped_changes: List[Dict[str, Any]]) -> any:
    """Format grouped campaign changes for Gradio DataFrame display."""
    if not grouped_changes:
        return None
    
    df_data = []
    for group in grouped_changes:
        tables_involved = set()
        fields_changed = []
        users_involved = set()
        
        for change in group['changes']:
            if change.get('source_table'):
                tables_involved.add(change['source_table'])
            if change.get('field_name'):
                fields_changed.append(change['field_name'])
            if change.get('update_user'):
                users_involved.add(change['update_user'])
        
        df_data.append({
            'Update Time': group['update_time'],
            'Tables': ', '.join(sorted(tables_involved)) if tables_involved else 'N/A',
            'Changes Count': group['change_count'],
            'Fields Changed': ', '.join(fields_changed[:5]) + ('...' if len(fields_changed) > 5 else ''),
            'Users': ', '.join(sorted(users_involved)) if users_involved else 'N/A',
            'Summary': f"{group['change_count']} changes across {len(tables_involved)} table(s)"
        })
    
    return pd.DataFrame(df_data)

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

 