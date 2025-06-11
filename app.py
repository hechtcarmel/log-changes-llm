import os
import gradio as gr
import asyncio
import logging
from datetime import datetime, date
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional, Tuple

from models import OpenAIModel
from database import DatabaseConnection, CampaignChangesQuery
from utils.data_formatter import (
    format_changes_table, 
    format_grouped_changes_table,
    format_connection_status,
    format_summary_stats
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize OpenAI model
openai_model = None
if os.getenv("OPENAI_API_KEY"):
    openai_model = OpenAIModel(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name=os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    )

async def analyze_campaign(
    username: str,
    password: str,
    campaign_id: str,
    from_date: str,
    to_date: str
) -> Tuple[str, any, any, str, str, str]:
    """Analyze campaign changes and generate AI insights."""
    
    # Input validation
    if not username or not password:
        return "❌ Please provide database username and password", None, None, "", "", ""
    
    if not campaign_id:
        return "❌ Please provide a campaign ID", None, None, "", "", ""
    
    if not from_date or not to_date:
        return "❌ Please provide both from and to dates", None, None, "", "", ""
    
    try:
        campaign_id_int = int(campaign_id)
    except ValueError:
        return "❌ Campaign ID must be a number", None, None, "", "", ""
    
    # Date validation
    def validate_date(date_str: str, field_name: str) -> bool:
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    if not validate_date(from_date, "From Date"):
        return "❌ From Date must be in YYYY-MM-DD format", None, None, "", "", ""
    
    if not validate_date(to_date, "To Date"):
        return "❌ To Date must be in YYYY-MM-DD format", None, None, "", "", ""
    
    try:
        from_dt = datetime.strptime(from_date, '%Y-%m-%d')
        to_dt = datetime.strptime(to_date, '%Y-%m-%d')
        if from_dt > to_dt:
            return "❌ From Date must be before To Date", None, None, "", "", ""
    except ValueError:
        pass
    
    if not openai_model:
        return "❌ OpenAI API key not configured", None, None, "", "", ""
    
    # Database operations
    db = DatabaseConnection()
    query_handler = CampaignChangesQuery(db)
    
    try:
        # Test connection
        connection_status = db.test_connection(username, password)
        status_message = format_connection_status(connection_status)
        
        if not connection_status['success']:
            return status_message, None, None, "", "", ""
        
        # Connect and query
        if not db.connect(username, password):
            return "❌ Failed to connect to database", None, None, "", "", ""
        
        # Get campaign changes
        changes = query_handler.get_campaign_changes(campaign_id_int, from_date, to_date)
        
        if not changes:
            db.disconnect()
            return status_message, None, None, "No changes found for this campaign ID in the specified date range", "", ""
        
        # Group changes by time
        grouped_changes = query_handler.group_changes_by_time(changes)
        
        # Generate summary statistics
        stats = query_handler.get_campaign_summary_stats(changes)
        stats_text = format_summary_stats(stats, from_date, to_date)
        
        # Format data for AI analysis
        ai_input_text = query_handler.format_changes_for_ai(grouped_changes)
        
        # Generate AI analysis
        try:
            ai_response = await openai_model.analyze_campaign_changes(ai_input_text, campaign_id_int)
            ai_summary = ai_response.to_formatted_text()
        except Exception as e:
            ai_summary = f"❌ AI analysis failed: {str(e)}"
        
        # Format tables for display
        changes_table = format_changes_table(changes)
        grouped_table = format_grouped_changes_table(grouped_changes)
        
        db.disconnect()
        
        return (
            status_message,
            changes_table,
            grouped_table, 
            ai_summary,
            stats_text,
            ai_input_text
        )
        
    except Exception as e:
        if db.is_connected():
            db.disconnect()
        return f"❌ Error: {str(e)}", None, None, "", "", ""

# Get today's date as default
today = date.today().strftime('%Y-%m-%d')

# Create Gradio interface
with gr.Blocks(title="Campaign Changes Analyzer", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 📊 Campaign Changes Analyzer")
    gr.Markdown("Analyze campaign modifications and get AI-powered insights about changes and strategic implications.")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Database Connection")
            username_input = gr.Textbox(
                label="MySQL Username",
                placeholder="Enter database username",
                type="text"
            )
            
            password_input = gr.Textbox(
                label="MySQL Password", 
                placeholder="Enter database password",
                type="password"
            )
            
            campaign_id_input = gr.Textbox(
                label="Campaign ID",
                placeholder="Enter campaign ID (numeric)",
                type="text"
            )
            
            with gr.Row():
                from_date_input = gr.Textbox(
                    label="From Date (Required)",
                    placeholder="YYYY-MM-DD",
                    value=today,
                    type="text",
                    info="Start date for filtering changes"
                )
                
                to_date_input = gr.Textbox(
                    label="To Date (Required)", 
                    placeholder="YYYY-MM-DD",
                    value=today,
                    type="text",
                    info="End date for filtering changes"
                )
            
            analyze_button = gr.Button("🔍 Analyze Campaign Changes", variant="primary", size="lg")
        
        with gr.Column(scale=2):
            connection_status = gr.Textbox(
                label="Connection Status",
                placeholder="Connection status will appear here...",
                interactive=False,
                max_lines=2
            )
            
            ai_analysis = gr.Textbox(
                label="🤖 AI Analysis & Insights",
                placeholder="AI-generated insights will appear here...",
                lines=15,
                interactive=False
            )
    
    with gr.Tabs():
        with gr.TabItem("📋 Grouped Changes"):
            grouped_changes_table = gr.Dataframe(
                label="Changes Grouped by Update Time",
                interactive=False,
                wrap=True
            )
        
        with gr.TabItem("📑 All Changes"):
            all_changes_table = gr.Dataframe(
                label="Complete Change History",
                interactive=False,
                wrap=True
            )
        
        with gr.TabItem("📈 Statistics"):
            stats_output = gr.Textbox(
                label="Campaign Change Statistics",
                placeholder="Summary statistics will appear here...",
                lines=15,
                interactive=False
            )
        
        with gr.TabItem("🔧 Raw Data"):
            raw_ai_input = gr.Textbox(
                label="Raw Data Sent to AI",
                placeholder="Formatted data sent to AI for analysis...",
                lines=20,
                interactive=False
            )
    
    # Event handlers
    analyze_button.click(
        fn=lambda username, password, campaign_id, from_date, to_date: asyncio.run(
            analyze_campaign(username, password, campaign_id, from_date, to_date)
        ),
        inputs=[
            username_input,
            password_input, 
            campaign_id_input,
            from_date_input,
            to_date_input
        ],
        outputs=[
            connection_status,
            all_changes_table,
            grouped_changes_table,
            ai_analysis,
            stats_output,
            raw_ai_input
        ]
    )

if __name__ == "__main__":
    app.launch() 