import os
import gradio as gr
import asyncio
import logging
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
    limit: int = 10
) -> Tuple[str, any, any, str, str, str]:
    """Analyze campaign changes and generate AI insights."""
    
    # Input validation
    if not username or not password:
        return "❌ Please provide database username and password", None, None, "", "", ""
    
    if not campaign_id:
        return "❌ Please provide a campaign ID", None, None, "", "", ""
    
    try:
        campaign_id_int = int(campaign_id)
    except ValueError:
        return "❌ Campaign ID must be a number", None, None, "", "", ""
    
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
        changes = query_handler.get_campaign_changes(campaign_id_int, limit)
        
        if not changes:
            db.disconnect()
            return status_message, None, None, "No changes found for this campaign ID", "", ""
        
        # Group changes by time
        grouped_changes = query_handler.group_changes_by_time(changes)
        
        # Generate summary statistics
        stats = query_handler.get_campaign_summary_stats(changes)
        stats_text = format_summary_stats(stats)
        
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

# Create Gradio interface
with gr.Blocks(title="Campaign Changes Analyzer", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 📊 Campaign Changes Analyzer")
    gr.Markdown("Analyze campaign modifications and get AI-powered insights about changes, risks, and recommendations.")
    
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
                placeholder="Enter campaign ID (e.g., 12345)",
                type="text"
            )
            
            limit_input = gr.Slider(
                label="Max Records",
                minimum=5,
                maximum=50,
                value=10,
                step=5,
                info="Maximum number of change records to retrieve"
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
                label="🤖 AI Analysis & Recommendations",
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
        fn=lambda username, password, campaign_id, limit: asyncio.run(
            analyze_campaign(username, password, campaign_id, limit)
        ),
        inputs=[username_input, password_input, campaign_id_input, limit_input],
        outputs=[
            connection_status,
            all_changes_table,
            grouped_changes_table,
            ai_analysis,
            stats_output,
            raw_ai_input
        ]
    )
    
    # Add example section
    with gr.Accordion("💡 Usage Instructions", open=False):
        gr.Markdown("""
        ### How to Use:
        1. **Database Credentials**: Enter your MySQL username and password
        2. **Campaign ID**: Enter the numeric campaign ID to analyze  
        3. **Max Records**: Choose how many recent changes to retrieve (5-50)
        4. **Analyze**: Click the button to retrieve data and generate insights
        
        ### What You'll Get:
        - **AI Analysis**: Strategic insights, risk factors, and recommendations
        - **Grouped Changes**: Changes organized by update time for better understanding
        - **All Changes**: Complete chronological list of modifications
        - **Statistics**: Summary metrics about change patterns and user activity
        - **Raw Data**: The formatted data sent to AI for transparency
        
        ### Database Details:
        - **Host**: proxysql-office.taboolasyndication.com:6033
        - **Database**: trc
        - **Table**: sp_campaign_details_v2_changes_log
        """)

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_api=True
    ) 