import os
import gradio as gr
import asyncio
import logging
import json
from datetime import datetime, date
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional, Tuple, AsyncGenerator
from gradio_calendar import Calendar

from models import OpenAIModel, CampaignAnalysisResponse
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

async def analyze_campaign_stream(
    username: str,
    password: str,
    campaign_id: str,
    from_date: str,
    to_date: str,
    selected_tables: List[str],
    progress: gr.Progress = gr.Progress()
) -> AsyncGenerator[Tuple[str, Any, Any, str, str, str], None]:
    """Analyze campaign changes and stream AI insights."""
    
    # This function now acts as a generator, yielding updates.
    
    progress(0, desc="🔄 Starting analysis...")
    yield "🔄 Starting analysis...", None, None, "🤖 AI analysis will appear here...", "", ""
    
    # Input validation
    if not username or not password:
        yield "❌ Please provide database username and password", None, None, "", "", ""
        return
    if not campaign_id:
        yield "❌ Please provide a campaign ID", None, None, "", "", ""
        return
    if not from_date or not to_date:
        yield "❌ Please provide both from and to dates", None, None, "", "", ""
        return
    if not selected_tables:
        yield "❌ Please select at least one table to query", None, None, "", "", ""
        return
    
    try:
        campaign_id_int = int(campaign_id)
    except ValueError:
        yield "❌ Campaign ID must be a number", None, None, "", "", ""
        return
    
    progress(0.1, desc="✅ Input validation completed")
    
    # Date validation can remain synchronous as it's quick
    def validate_date(date_str: str) -> bool:
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    if not validate_date(from_date) or not validate_date(to_date):
        yield "❌ Dates must be in YYYY-MM-DD format", None, None, "", "", ""
        return
        
    if datetime.strptime(from_date, '%Y-%m-%d') > datetime.strptime(to_date, '%Y-%m-%d'):
        yield "❌ From Date must be before To Date", None, None, "", "", ""
        return

    if not openai_model:
        yield "❌ OpenAI API key not configured", None, None, "", "", ""
        return
    
    progress(0.2, desc="✅ Date validation completed")
    
    db = DatabaseConnection()
    query_handler = CampaignChangesQuery(db)
    
    try:
        # DB connection and initial query
        progress(0.3, desc="🔌 Testing database connection...")
        connection_status = db.test_connection(username, password)
        status_message = format_connection_status(connection_status)
        
        if not connection_status['success']:
            yield status_message, None, None, "", "", ""
            return
            
        progress(0.4, desc="✅ Database connection successful")
        if not db.connect(username, password):
            yield "❌ Failed to connect to database", None, None, "", "", ""
            return
            
        progress(0.5, desc=f"🔍 Querying {len(selected_tables)} tables...")
        changes = query_handler.get_campaign_changes(campaign_id_int, from_date, to_date, selected_tables)
        
        if not changes:
            db.disconnect()
            yield status_message, None, None, f"No changes found for campaign ID {campaign_id}", "", ""
            return
            
        progress(0.6, desc="✅ Data retrieved")
        
        # Prepare data and tables for display
        grouped_changes = query_handler.group_changes_by_time(changes)
        stats = query_handler.get_campaign_summary_stats(changes)
        stats_text = format_summary_stats(stats, from_date, to_date, selected_tables)
        changes_table = format_changes_table(changes)
        grouped_table = format_grouped_changes_table(grouped_changes)
        
        progress(0.7, desc="📊 Formatting data for AI...")
        ai_input_text = query_handler.format_changes_for_ai(grouped_changes)
        net_changes = query_handler.calculate_net_changes(changes)
        net_changes_text = query_handler.format_net_changes_for_ai(net_changes)

        # Yield pre-AI results first
        yield status_message, changes_table, grouped_table, "🤖 Generating AI analysis...", stats_text, ai_input_text
        
        progress(0.8, desc="🤖 Streaming AI analysis...")
        
        # Stream AI analysis
        ai_full_response = ""
        async for chunk in openai_model.analyze_campaign_changes(ai_input_text, campaign_id_int, net_changes_text):
            ai_full_response += chunk
            # Attempt to pretty-print the partial JSON
            try:
                # This helps in formatting the streaming JSON nicely
                parsed_json = json.loads(ai_full_response)
                display_text = CampaignAnalysisResponse.from_dict(parsed_json).to_formatted_text()
            except json.JSONDecodeError:
                # Handle cases where the JSON is not yet complete
                display_text = ai_full_response.replace("{", "{\n").replace("}", "\n}").replace(",", ",\n")

            yield status_message, changes_table, grouped_table, display_text, stats_text, ai_input_text
            await asyncio.sleep(0.05) # Small delay to allow UI to update smoothly

        # Final update with fully formatted response
        progress(0.9, desc="📋 Finalizing results...")
        try:
            final_data = json.loads(ai_full_response)
            final_response = CampaignAnalysisResponse.from_dict(final_data)
            final_summary = final_response.to_formatted_text()
        except (json.JSONDecodeError, KeyError) as e:
            final_summary = f"❌ AI analysis post-processing failed: {e}\n\nRaw response:\n{ai_full_response}"

        yield status_message, changes_table, grouped_table, final_summary, stats_text, ai_input_text
        
        db.disconnect()
        progress(1.0, desc="✅ Analysis complete")

    except Exception as e:
        if db.is_connected():
            db.disconnect()
        progress(0, desc="❌ Error occurred")
        yield f"❌ Error: {str(e)}", None, None, "", "", ""

def create_interface():
    """Create and configure the Gradio interface."""
    
    # Get available tables for selection
    query_handler = CampaignChangesQuery(None)  # Just for table info
    available_tables = query_handler.get_available_tables()
    
    # Prepare table choices for checkboxes
    table_choices = [f"{name} - {info['description']}" for name, info in available_tables.items()]
    table_names = list(available_tables.keys())
    
    today = date.today().strftime('%Y-%m-%d')
    
    with gr.Blocks(
        title="Campaign Changes Analyzer",
        theme=gr.themes.Soft(),
        css="""
        .tab-nav { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); }
        .tab-nav button { color: white !important; }
        #ai_analysis_wrapper {
            height: 60vh;
            overflow-y: auto;
            border: 1px solid #E5E7EB; 
            border-radius: 8px; 
            padding: 1rem;
        }
        .markdown-content {
            white-space: pre-wrap;
            line-height: 1.6;
        }
        .markdown-content ul {
            list-style-type: none;
            padding-left: 0;
        }
        .markdown-content li {
            margin-bottom: 0.5em;
        }
        """
    ) as app:
        
        gr.Markdown("""
        # 🔍 Campaign Changes Analyzer
        
        Analyze campaign changes across multiple database tables with AI-powered insights.
        """)
        
        with gr.Row():
            with gr.Column(scale=3):
                gr.Markdown("### 🔐 Database Connection")
                with gr.Row():
                    username_input = gr.Textbox(
                        label="Username",
                        placeholder="Enter database username",
                        info="Your database username"
                    )
                    password_input = gr.Textbox(
                        label="Password",
                        type="password",
                        placeholder="Enter database password",
                        info="Your database password"
                    )
                
                gr.Markdown("### 📊 Analysis Parameters")
                campaign_id_input = gr.Textbox(
                    label="Campaign ID (Required)",
                    placeholder="Enter campaign ID",
                    info="The campaign ID to analyze"
                )
                
                with gr.Row():
                    from_date_input = Calendar(
                        label="From Date (Required)",
                        value=today,
                        type="string",
                        info="Start date for filtering changes"
                    )
                    
                    to_date_input = Calendar(
                        label="To Date (Required)", 
                        value=today,
                        type="string",
                        info="End date for filtering changes"
                    )

                # Table selection section
                gr.Markdown("### 🗂️ Data Sources")
                with gr.Accordion("Select Tables to Query", open=False):
                    gr.Markdown("Choose which change log tables to include in the analysis:")
                    table_selection = gr.CheckboxGroup(
                        choices=table_choices,
                        value=table_choices,  # All selected by default
                        label="Available Tables",
                        info=f"Select from {len(table_choices)} available change log tables"
                    )
                
                connection_status = gr.Markdown("🔄 Ready to connect...")
                
                analyze_button = gr.Button(
                    "🔍 Analyze Campaign Changes",
                    variant="primary",
                    size="lg"
                )
            
            with gr.Column(scale=4):
                gr.Markdown("### 🤖 AI Analysis")
                with gr.Column(elem_id="ai_analysis_wrapper"):
                    ai_analysis = gr.Markdown(
                        label="AI-Generated Analysis",
                        value="Click 'Analyze Campaign Changes' to generate AI insights...",
                        elem_classes=["markdown-content"]
                    )
        
        # Results tabs
        with gr.Tabs():
            with gr.Tab("📋 Grouped Changes"):
                grouped_changes_table = gr.Dataframe(
                    label="Changes Grouped by Time",
                    interactive=False,
                    wrap=True
                )
                
            with gr.Tab("📊 All Changes"):
                all_changes_table = gr.Dataframe(
                    label="All Campaign Changes",
                    interactive=False,
                    wrap=True
                )
                
            with gr.Tab("📈 Statistics"):
                stats_output = gr.Markdown(
                    label="Summary Statistics",
                    value="Statistics will appear here after analysis..."
                )
                
            with gr.Tab("🔍 Raw Data for AI"):
                raw_ai_input = gr.Textbox(
                    label="Formatted Data Sent to AI",
                    lines=10,
                    max_lines=20,
                    value="Raw data will appear here after analysis..."
                )

        async def analysis_wrapper(username, password, campaign_id, from_date, to_date, table_selection_choices, progress=gr.Progress(track_tqdm=True)):
            # Get the actual table names from the choices
            table_names_list = [table_names[table_choices.index(choice)] for choice in table_selection_choices]
            
            # Use an async for loop to iterate through the generator
            async for outputs in analyze_campaign_stream(
                username, password, campaign_id, from_date, to_date, table_names_list, progress
            ):
                yield outputs

        # Event handlers
        analyze_button.click(
            fn=analysis_wrapper,
            inputs=[
                username_input,
                password_input, 
                campaign_id_input,
                from_date_input,
                to_date_input,
                table_selection
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
    
    return app

if __name__ == "__main__":
    app = create_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7861,
        show_error=True,
        share=False
    ) 
    