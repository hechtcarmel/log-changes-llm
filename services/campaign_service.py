"""Campaign analysis service for coordinating the main business logic."""

import asyncio
import json
import logging
from typing import List, AsyncGenerator, Tuple, Any
import gradio as gr

from campaign_analyzer.models import OpenAIModel, CampaignAnalysisResponse, ChangeEntry, ChangeSession
from campaign_analyzer.database import DatabaseConnection, CampaignChangesQuery
from campaign_analyzer.utils.data_formatter import (
    format_grouped_changes_for_display,
    format_connection_status,
    format_summary_stats,
    get_performer_or_user
)
from campaign_analyzer.constants import UI_MESSAGES, PROGRESS_STEPS
from .validation_service import ValidationService

class CampaignService:
    """Main service for coordinating campaign analysis workflow."""
    
    def __init__(self, config_service):
        """Initialize campaign service with configuration."""
        self.config = config_service
        self.db = DatabaseConnection()
        self.validation = ValidationService()
        
    async def analyze_campaign_stream(
        self,
        username: str,
        password: str,
        campaign_id: str,
        from_date: str,
        to_date: str,
        selected_tables: List[str],
        openai_api_key: str,
        progress: gr.Progress = gr.Progress()
    ) -> AsyncGenerator[Tuple[str, Any, str, str, str], None]:
        """Analyze campaign changes and stream AI insights."""
        
        progress(0, desc=UI_MESSAGES["starting_analysis"])
        yield UI_MESSAGES["starting_analysis"], None, UI_MESSAGES["ai_generating"], "", ""
        
        # Input validation
        is_valid, error_msg, campaign_id_int = self.validation.validate_campaign_inputs(
            username, password, campaign_id, from_date, to_date, selected_tables, openai_api_key
        )
        
        if not is_valid:
            yield error_msg, None, "", "", ""
            return
        
        progress(PROGRESS_STEPS["validation"], desc=UI_MESSAGES["input_validation"])
        
        # Initialize OpenAI model
        try:
            openai_model = OpenAIModel(
                api_key=openai_api_key,
                model_name=self.config.get_openai_model_name()
            )
        except Exception as e:
            yield UI_MESSAGES["ai_init_failed"].format(e), None, "", "", ""
            return
        
        # Database operations
        query_handler = CampaignChangesQuery(self.db)
        
        try:
            # Test database connection
            progress(PROGRESS_STEPS["db_test"], desc=UI_MESSAGES["db_connection"])
            connection_status = self.db.test_connection(username, password)
            status_message = format_connection_status(connection_status)
            
            if not connection_status['success']:
                yield status_message, None, "", "", ""
                return
                
            progress(PROGRESS_STEPS["db_connect"], desc=UI_MESSAGES["db_success"])
            if not self.db.connect(username, password):
                yield UI_MESSAGES["db_connection_failed"], None, "", "", ""
                return
                
            # Query campaign changes
            progress(PROGRESS_STEPS["query_data"], desc=UI_MESSAGES["querying_tables"].format(len(selected_tables)))
            changes = query_handler.get_campaign_changes(campaign_id_int, from_date, to_date, selected_tables)
            
            if not changes:
                self.db.disconnect()
                yield status_message, None, UI_MESSAGES["no_changes_found"].format(campaign_id), "", ""
                return
                
            progress(PROGRESS_STEPS["data_retrieved"], desc=UI_MESSAGES["data_retrieved"])
            
            # Process and format data
            user_grouped_changes = query_handler.group_changes_by_user_and_date(changes)
            changes_display_table = format_grouped_changes_for_display(user_grouped_changes)
            
            # Build change session objects
            change_session_objects = self._build_change_sessions(user_grouped_changes)
            
            # Prepare data for AI analysis
            time_grouped_changes = query_handler.group_changes_by_time(changes)
            stats = query_handler.get_campaign_summary_stats(changes)
            stats_text = format_summary_stats(stats, from_date, to_date, selected_tables)
            
            progress(PROGRESS_STEPS["format_data"], desc=UI_MESSAGES["formatting_data"])
            ai_input_text = query_handler.format_changes_for_ai(time_grouped_changes)
            net_changes = query_handler.calculate_net_changes(changes)
            net_changes_text = query_handler.format_net_changes_for_ai(net_changes)
            
            # Yield pre-AI results
            yield status_message, changes_display_table, UI_MESSAGES["ai_generating"], stats_text, ai_input_text
            
            # Stream AI analysis
            progress(PROGRESS_STEPS["ai_analysis"], desc=UI_MESSAGES["ai_analysis"])
            
            ai_full_response = ""
            async for chunk in openai_model.analyze_campaign_changes(ai_input_text, campaign_id_int, net_changes_text):
                ai_full_response += chunk
                # Format partial response nicely using the new method
                display_text = CampaignAnalysisResponse.format_partial_response(ai_full_response)
                
                yield status_message, changes_display_table, display_text, stats_text, ai_input_text
                await asyncio.sleep(0.05)
            
            # Finalize results
            progress(0.9, desc="📋 Finalizing results...")
            try:
                final_data = json.loads(ai_full_response)
                final_response = CampaignAnalysisResponse(
                    summary=final_data.get("summary", "No summary available"),
                    change_sessions=change_session_objects,
                    key_insights=final_data.get("key_insights", []),
                    raw_response=json.dumps(final_data)
                )
                final_summary = final_response.to_formatted_text()
            except (json.JSONDecodeError, KeyError) as e:
                final_summary = f"❌ AI analysis post-processing failed: {e}\n\nRaw response:\n{ai_full_response}"
            
            yield status_message, changes_display_table, final_summary, stats_text, ai_input_text
            
            self.db.disconnect()
            progress(1.0, desc="✅ Analysis complete")
            
        except Exception as e:
            if self.db.is_connected():
                self.db.disconnect()
            progress(0, desc="❌ Error occurred")
            yield f"❌ Error: {str(e)}", None, "", "", ""
    
    def _build_change_sessions(self, sessions_raw):
        """Build ChangeSession objects from raw session data."""
        session_objs = []
        skip_fields = {'performer', 'update_user', 'update_time'}
        
        for sess in sessions_raw:
            timestamp = f"{sess['date']} {sess['time']}:00"
            user = sess['user']
            entry_objs = []
            
            for ch in sess.get('changes', []):
                field_name = ch.get('field_name') or ch.get('field') or 'unknown_field'
                if field_name in skip_fields:
                    continue
                
                performer_user = get_performer_or_user(ch)
                if not performer_user:
                    performer_user = user
                    
                entry_objs.append(
                    ChangeEntry(
                        timestamp=timestamp,
                        user=performer_user,
                        field=field_name,
                        old_value=str(ch.get('old_value', '')),
                        new_value=str(ch.get('new_value', ''))
                    )
                )
                
            if entry_objs:
                session_objs.append(ChangeSession(timestamp, user, entry_objs))
                
        return session_objs 