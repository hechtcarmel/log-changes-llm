from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from .connection import DatabaseConnection

class CampaignChangesQuery:
    """Handles campaign changes queries and data processing."""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        
    def get_campaign_changes(self, campaign_id: int, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve campaign changes for a specific campaign ID.
        
        Args:
            campaign_id: The campaign ID to query
            limit: Maximum number of records to return
            
        Returns:
            List of change records or None if error
        """
        query = """
        SELECT id, campaign_id, field_name, old_value, new_value, 
               update_time, update_user
        FROM sp_campaign_details_v2_changes_log 
        WHERE campaign_id = %s 
        ORDER BY update_time DESC 
        LIMIT %s
        """
        
        try:
            results = self.db.execute_query(query, (campaign_id, limit))
            if results:
                # Convert datetime objects to strings for JSON serialization
                for record in results:
                    if isinstance(record.get('update_time'), datetime):
                        record['update_time'] = record['update_time'].isoformat()
            return results
        except Exception as e:
            print(f"Error retrieving campaign changes: {e}")
            return None
    
    def group_changes_by_time(self, changes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Group changes by update_time for better analysis.
        
        Args:
            changes: List of individual change records
            
        Returns:
            List of grouped change records by update_time
        """
        if not changes:
            return []
            
        # Convert to DataFrame for easier grouping
        df = pd.DataFrame(changes)
        
        # Group by update_time and update_user
        grouped_changes = []
        
        for (update_time, update_user), group in df.groupby(['update_time', 'update_user']):
            change_group = {
                'update_time': update_time,
                'update_user': update_user,
                'campaign_id': group['campaign_id'].iloc[0],
                'changes_count': len(group),
                'changes': []
            }
            
            # Add individual field changes
            for _, row in group.iterrows():
                change_group['changes'].append({
                    'field_name': row['field_name'],
                    'old_value': row['old_value'],
                    'new_value': row['new_value']
                })
            
            grouped_changes.append(change_group)
        
        # Sort by update_time descending
        grouped_changes.sort(key=lambda x: x['update_time'], reverse=True)
        
        return grouped_changes
    
    def format_changes_for_ai(self, grouped_changes: List[Dict[str, Any]]) -> str:
        """
        Format grouped changes into a readable text for AI analysis.
        
        Args:
            grouped_changes: List of grouped change records
            
        Returns:
            Formatted string representation of changes
        """
        if not grouped_changes:
            return "No changes found for this campaign."
        
        formatted_text = f"Campaign Changes Analysis:\n"
        formatted_text += f"Total change sessions: {len(grouped_changes)}\n\n"
        
        for i, change_group in enumerate(grouped_changes, 1):
            formatted_text += f"Session {i}:\n"
            formatted_text += f"  Time: {change_group['update_time']}\n"
            formatted_text += f"  User: {change_group['update_user']}\n"
            formatted_text += f"  Changes: {change_group['changes_count']} fields modified\n"
            
            for change in change_group['changes']:
                old_val = change['old_value'] or '[empty]'
                new_val = change['new_value'] or '[empty]'
                formatted_text += f"    - {change['field_name']}: '{old_val}' → '{new_val}'\n"
            
            formatted_text += "\n"
        
        return formatted_text
    
    def get_campaign_summary_stats(self, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for campaign changes.
        
        Args:
            changes: List of change records
            
        Returns:
            Dictionary with summary statistics
        """
        if not changes:
            return {
                "total_changes": 0,
                "unique_fields": 0,
                "unique_users": 0,
                "date_range": None
            }
        
        df = pd.DataFrame(changes)
        
        # Convert update_time to datetime if it's a string
        if df['update_time'].dtype == 'object':
            df['update_time'] = pd.to_datetime(df['update_time'])
        
        stats = {
            "total_changes": len(changes),
            "unique_fields": df['field_name'].nunique(),
            "unique_users": df['update_user'].nunique(),
            "date_range": {
                "earliest": df['update_time'].min().isoformat() if not df.empty else None,
                "latest": df['update_time'].max().isoformat() if not df.empty else None
            },
            "most_changed_fields": df['field_name'].value_counts().head(5).to_dict(),
            "users_activity": df['update_user'].value_counts().to_dict()
        }
        
        return stats 