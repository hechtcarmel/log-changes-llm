from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
from .connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class CampaignChangesQuery:
    """Handle campaign changes queries across multiple change log tables."""
    
    # Configuration for all change log tables
    TABLE_CONFIGS = {
        'sp_campaign_details_v2_changes_log': {
            'campaign_id_column': 'campaign_id',
            'campaign_id_type': 'int',
            'has_update_user': True,
            'field_name_column': 'field_name',
            'update_user_column': 'update_user',
            'description': 'Campaign Details Changes',
            'owner': 'Media - arik.f'
        },
        'campaign_exploration_config_changes_log': {
            'campaign_id_column': 'campaign_id',
            'campaign_id_type': 'bigint',
            'has_update_user': True,
            'field_name_column': 'field_name',
            'update_user_column': 'update_user',
            'description': 'Campaign Exploration Config',
            'owner': 'Aviad Shiber'
        },
        'campaigns_progress_changes_log': {
            'campaign_id_column': 'campaign_id',
            'campaign_id_type': 'bigint',
            'has_update_user': False,
            'field_name_column': 'field_name',
            'update_user_column': None,
            'description': 'Campaign Progress Changes',
            'owner': 'Media - guy.b'
        },
        'cra_campaign_assignments_changes_log': {
            'campaign_id_column': 'campaign_id',
            'campaign_id_type': 'bigint',
            'has_update_user': True,
            'field_name_column': 'field_name',
            'update_user_column': 'update_user',
            'description': 'CRA Campaign Assignments',
            'owner': 'Internal Apps - david.c'
        },
        'dco_campaigns_changes_log': {
            'campaign_id_column': 'sp_campaign_id',
            'campaign_id_type': 'int',
            'has_update_user': True,
            'field_name_column': 'field_name',
            'update_user_column': 'update_user',
            'description': 'DCO Campaigns Changes',
            'owner': 'Emerging Demand - ofer.c'
        },
        'max_conversions_campaigns_performance_data_changes_log': {
            'campaign_id_column': 'campaign_id',
            'campaign_id_type': 'bigint',
            'has_update_user': False,
            'field_name_column': 'field_name',
            'update_user_column': None,
            'description': 'Max Conversions Performance Data',
            'owner': 'Media - nir.l'
        },
        'sp_campaign_context_cpc_modification_configuration_changes_log': {
            'campaign_id_column': 'campaign_id',
            'campaign_id_type': 'bigint',
            'has_update_user': False,
            'field_name_column': 'field_name',
            'update_user_column': None,
            'description': 'Context CPC Modification Config',
            'owner': 'Media - boris.l'
        },
        'sp_campaign_day_parting_changes_log': {
            'campaign_id_column': 'campaign_id',
            'campaign_id_type': 'int',
            'has_update_user': False,
            'field_name_column': 'field_name',
            'update_user_column': None,
            'description': 'Campaign Day Parting',
            'owner': 'Media'
        },
        'sp_campaign_features_changes_log': {
            'campaign_id_column': 'campaign_id',
            'campaign_id_type': 'int',
            'has_update_user': True,
            'field_name_column': 'feature',  # Different column name
            'update_user_column': 'performer',  # Different column name
            'description': 'Campaign Features',
            'owner': 'Media'
        },
        'sp_campaign_restrictions_changes_log': {
            'campaign_id_column': 'campaign_id',
            'campaign_id_type': 'bigint',
            'has_update_user': False,
            'field_name_column': 'field_name',
            'update_user_column': None,
            'description': 'Campaign Restrictions',
            'owner': 'Media'
        },
        'sp_campaign_targeting_changes_log': {
            'campaign_id_column': 'campaign_id',
            'campaign_id_type': 'int',
            'has_update_user': True,
            'field_name_column': 'rule_type',  # Different structure
            'update_user_column': 'performer',  # Different column name
            'special_handling': 'targeting',  # Special case
            'description': 'Campaign Targeting',
            'owner': 'Media'
        },
        'sp_campaigns_changes_log': {
            'campaign_id_column': 'campaigns_id',  # Different column name
            'campaign_id_type': 'int',
            'has_update_user': False,
            'field_name_column': 'field_name',
            'update_user_column': None,
            'description': 'SP Campaigns Changes',
            'owner': 'Media - matan.t'
        },
        'sp_campaigns_spent_plan_config_changes_log': {
            'campaign_id_column': 'campaign_id',
            'campaign_id_type': 'bigint',
            'has_update_user': True,
            'field_name_column': 'field_name',
            'update_user_column': 'update_user',
            'description': 'Campaign Spent Plan Config',
            'owner': 'Media - nir.l'
        },
        'target_cpa_campaigns_configurations_changes_log': {
            'campaign_id_column': 'campaign_id',
            'campaign_id_type': 'bigint',
            'has_update_user': True,
            'field_name_column': 'field_name',
            'update_user_column': 'update_user',
            'description': 'Target CPA Configurations',
            'owner': 'Media - chen.a'
        },
        'target_cpa_feedback_loop_campaigns_settings_changes_log': {
            'campaign_id_column': 'campaign_id',
            'campaign_id_type': 'bigint',
            'has_update_user': True,
            'field_name_column': 'field_name',
            'update_user_column': 'update_user',
            'description': 'Target CPA Feedback Loop Settings',
            'owner': 'Media - dotan.b'
        },
        'temp_sp_campaign_details_v2_changes_log': {
            'campaign_id_column': 'campaign_id',
            'campaign_id_type': 'int',
            'has_update_user': True,
            'field_name_column': 'field_name',
            'update_user_column': 'update_user',
            'description': 'Temp Campaign Details Changes',
            'owner': 'Media - arik.f'
        },
        'unip_funnel_campaign_changes_log': {
            'campaign_id_column': 'unip_funnel_campaign_id',  # Different column name
            'campaign_id_type': 'bigint',
            'has_update_user': True,
            'field_name_column': 'field_name',
            'update_user_column': 'update_user',
            'description': 'Unip Funnel Campaign Changes',
            'owner': 'Media - zoe.e',
            'note': 'Uses unip_funnel_campaign_id instead of campaign_id'
        }
    }

    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        
    def get_available_tables(self) -> Dict[str, Dict[str, str]]:
        """Get list of available tables with their descriptions."""
        return {
            table_name: {
                'description': config['description'],
                'owner': config['owner'],
                'note': config.get('note', '')
            }
            for table_name, config in self.TABLE_CONFIGS.items()
        }

    def _build_table_query(self, table_name: str, campaign_id: int, from_date: str, to_date: str) -> Tuple[str, list]:
        """Build query for a specific table."""
        config = self.TABLE_CONFIGS[table_name]
        
        # Handle special cases
        if config.get('special_handling') == 'targeting':
            # Special handling for targeting table
            query = f"""
            SELECT 
                '{table_name}' as source_table,
                {config['campaign_id_column']} as campaign_id,
                {config['field_name_column']} as field_name,
                action as old_value,
                'TARGETING_CHANGE' as new_value,
                update_time,
                {config['update_user_column']} as update_user
            FROM {table_name}
            WHERE {config['campaign_id_column']} = %s 
                AND update_time >= %s 
                AND update_time < DATE_ADD(%s, INTERVAL 1 DAY)
            """
        else:
            # Standard query structure
            user_column = config['update_user_column'] if config['has_update_user'] else 'NULL'
            query = f"""
            SELECT 
                '{table_name}' as source_table,
                {config['campaign_id_column']} as campaign_id,
                {config['field_name_column']} as field_name,
                old_value,
                new_value,
                update_time,
                {user_column} as update_user
            FROM {table_name}
            WHERE {config['campaign_id_column']} = %s 
                AND update_time >= %s 
                AND update_time < DATE_ADD(%s, INTERVAL 1 DAY)
            """
        
        params = [campaign_id, from_date, to_date]
        return query, params

    def get_campaign_changes(self, campaign_id: int, from_date: str, to_date: str, 
                           selected_tables: Optional[List[str]] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve campaign changes from selected tables.
        
        Args:
            campaign_id: The campaign ID to query
            from_date: Start date for filtering (YYYY-MM-DD format)
            to_date: End date for filtering (YYYY-MM-DD format)
            selected_tables: List of table names to query (all if None)
            
        Returns:
            List of change records or None if error
        """
        if selected_tables is None:
            selected_tables = list(self.TABLE_CONFIGS.keys())
        
        all_changes = []
        
        for table_name in selected_tables:
            if table_name not in self.TABLE_CONFIGS:
                logger.warning(f"Unknown table: {table_name}")
                continue
                
            try:
                query, params = self._build_table_query(table_name, campaign_id, from_date, to_date)
                results = self.db.execute_query(query, tuple(params))
                
                if results:
                    all_changes.extend(results)
                    logger.info(f"Found {len(results)} changes in {table_name}")
                    
            except Exception as e:
                logger.error(f"Error querying {table_name}: {str(e)}")
                continue
        
        if not all_changes:
            return None
            
        # Sort by update_time
        all_changes.sort(key=lambda x: x['update_time'], reverse=True)
        
        logger.info(f"Total changes found: {len(all_changes)} from {len(selected_tables)} tables")
        return all_changes
    
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
        
        # Ensure update_time is datetime
        if df['update_time'].dtype == 'object':
            df['update_time'] = pd.to_datetime(df['update_time'])
        
        # Group by update_time (rounded to minute for grouping similar times)
        df['time_group'] = df['update_time'].dt.floor('min')
        
        grouped_changes = []
        
        for time_group, group in df.groupby('time_group'):
            change_group = {
                'update_time': time_group.isoformat(),
                'change_count': len(group),
                'changes': []
            }
            
            # Add individual field changes with source table info
            for _, row in group.iterrows():
                change_group['changes'].append({
                    'source_table': row.get('source_table', 'Unknown'),
                    'field_name': row['field_name'],
                    'old_value': row.get('old_value'),
                    'new_value': row.get('new_value'),
                    'update_user': row.get('update_user')
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
            formatted_text += f"  Changes: {change_group['change_count']} fields modified\n"
            
            # Group changes by table
            tables_in_session = {}
            for change in change_group['changes']:
                table = change.get('source_table', 'Unknown')
                if table not in tables_in_session:
                    tables_in_session[table] = []
                tables_in_session[table].append(change)
            
            for table, table_changes in tables_in_session.items():
                formatted_text += f"  Table: {table}\n"
                for change in table_changes:
                    old_val = change.get('old_value') or '[empty]'
                    new_val = change.get('new_value') or '[empty]'
                    user = change.get('update_user', 'Unknown')
                    formatted_text += f"    - {change['field_name']}: '{old_val}' → '{new_val}' (by {user})\n"
            
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
                "date_range_days": 0,
                "changes_per_day": 0,
                "changes": [],
                "top_fields": [],
                "most_active_user": "N/A",
                "most_active_user_changes": 0
            }
        
        df = pd.DataFrame(changes)
        
        # Convert update_time to datetime if it's a string
        if df['update_time'].dtype == 'object':
            df['update_time'] = pd.to_datetime(df['update_time'])
        
        # Calculate date range
        min_date = df['update_time'].min()
        max_date = df['update_time'].max()
        date_range_days = (max_date - min_date).days + 1 if min_date != max_date else 1
        
        # Get user statistics
        user_counts = df['update_user'].value_counts()
        most_active_user = user_counts.index[0] if not user_counts.empty else "N/A"
        most_active_user_changes = user_counts.iloc[0] if not user_counts.empty else 0
        
        # Get field statistics
        field_counts = df['field_name'].value_counts()
        top_fields = list(field_counts.head(10).items())
        
        stats = {
            "total_changes": len(changes),
            "unique_fields": df['field_name'].nunique(),
            "unique_users": df['update_user'].nunique(),
            "date_range_days": date_range_days,
            "changes_per_day": len(changes) / date_range_days,
            "changes": changes,  # Include raw changes for table-specific stats
            "top_fields": top_fields,
            "most_active_user": most_active_user,
            "most_active_user_changes": most_active_user_changes,
            "date_range": {
                "earliest": min_date.isoformat() if not df.empty else None,
                "latest": max_date.isoformat() if not df.empty else None
            }
        }
        
        return stats 