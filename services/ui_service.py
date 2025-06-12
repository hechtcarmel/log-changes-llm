"""UI service for creating and managing the Gradio interface."""

import os
from datetime import date
import gradio as gr

from database import CampaignChangesQuery
from constants import get_table_choices
from .campaign_service import CampaignService

class UIService:
    """Service for creating and managing the Gradio user interface."""
    
    def __init__(self, config_service):
        """Initialize UI service with configuration."""
        self.config = config_service
        self.campaign_service = CampaignService(config_service)
        
    def create_interface(self) -> gr.Blocks:
        """Create and configure the Gradio interface."""
        
        # Get available tables for selection
        query_handler = CampaignChangesQuery(None)
        available_tables = query_handler.get_available_tables()
        
        # Prepare table choices for checkboxes
        table_choices = [f"{name} - {info['description']}" for name, info in available_tables.items()]
        table_names = list(available_tables.keys())
        
        today = date.today().strftime('%Y-%m-%d')
        app_config = self.config.get_app_config()
        
        with gr.Blocks(
            title=app_config["title"],
            theme=gr.themes.Ocean(),
            css=self._get_custom_css()
        ) as app:
            
            # Header
            gr.Markdown(f"""
            # 🔍 {app_config["title"]}
            
            {app_config["description"]}
            """)
            
            with gr.Row():
                # Left column - inputs
                with gr.Column(scale=3):
                    # Credentials section
                    gr.Markdown("### 🔐 API & Database Credentials")
                    
                    openai_api_key = self._create_api_key_input()
                    username_input, password_input = self._create_database_inputs()
                    
                    # Analysis parameters
                    gr.Markdown("### 📊 Analysis Parameters")
                    campaign_id_input = self._create_campaign_id_input()
                    from_date_input, to_date_input = self._create_date_inputs(today)
                    
                    # Table selection
                    gr.Markdown("### 🗂️ Data Sources")
                    table_selection = self._create_table_selection(table_choices)
                    
                    connection_status = gr.Markdown("🔄 Ready to connect...")
                    analyze_button = self._create_analyze_button()
                
                # Right column - AI analysis
                with gr.Column(scale=4):
                    ai_analysis = self._create_ai_analysis_section()
            
            # Results tabs
            results_tabs_components = self._create_results_tabs()
            
            # Event handlers
            self._setup_event_handlers(
                analyze_button, 
                [username_input, password_input, campaign_id_input, 
                 from_date_input, to_date_input, table_selection, openai_api_key],
                [connection_status, results_tabs_components[0], ai_analysis, results_tabs_components[1], results_tabs_components[2]],
                table_choices, table_names
            )
        
        return app
    
    def _get_custom_css(self) -> str:
        """Get custom CSS for the interface."""
        return """
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
        .centered-header th { text-align: center !important; }
        """
    
    def _create_api_key_input(self) -> gr.Textbox:
        """Create OpenAI API key input."""
        api_key_from_env = self.config.get_openai_api_key()
        
        return gr.Textbox(
            label="OpenAI API Key",
            placeholder="Enter your OpenAI API key if not in .env",
            value=api_key_from_env,
            type="password",
            visible=True,
            info="Required. Loaded from .env if available."
        )
    
    def _create_database_inputs(self) -> tuple:
        """Create database credential inputs."""
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
        return username_input, password_input
    
    def _create_campaign_id_input(self) -> gr.Textbox:
        """Create campaign ID input."""
        return gr.Textbox(
            label="Campaign ID (Required)",
            placeholder="Enter campaign ID",
            info="The campaign ID to analyze"
        )
    
    def _create_date_inputs(self, today: str) -> tuple:
        """Create date input components."""
        from gradio_calendar import Calendar
        
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
        
        return from_date_input, to_date_input
    
    def _create_table_selection(self, table_choices: list) -> gr.CheckboxGroup:
        """Create table selection component."""
        with gr.Accordion("Select Tables to Query", open=False):
            gr.Markdown("Choose which change log tables to include in the analysis:")
            return gr.CheckboxGroup(
                choices=table_choices,
                value=table_choices,
                label="Available Tables",
                info=f"Select from {len(table_choices)} available change log tables"
            )
    
    def _create_analyze_button(self) -> gr.Button:
        """Create the main analyze button."""
        return gr.Button(
            "🔍 Analyze Campaign Changes",
            variant="primary",
            size="lg"
        )
    
    def _create_ai_analysis_section(self) -> gr.Markdown:
        """Create AI analysis display section."""
        gr.Markdown("### 🤖 AI Analysis")
        with gr.Column(elem_id="ai_analysis_wrapper"):
            return gr.Markdown(
                label="AI-Generated Analysis",
                value="Click 'Analyze Campaign Changes' to generate AI insights...",
                elem_classes=["markdown-content"]
            )
    
    def _create_results_tabs(self) -> list:
        """Create results tabs and return output components."""
        with gr.Tabs():
            with gr.Tab("🗓️ Change History"):
                all_changes_table = gr.Dataframe(
                    label="All Campaign Changes Grouped by Session",
                    interactive=False,
                    wrap=True,
                    headers=['Date', 'Time', 'Performer/User', 'Table', 'Field', 'Old Value', 'New Value'],
                    datatype=["markdown"] * 7,
                    column_widths=["auto"] * 7,
                    elem_classes=["centered-header"]
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
        
        return [all_changes_table, stats_output, raw_ai_input]
    
    def _setup_event_handlers(self, analyze_button, input_components, output_components, table_choices, table_names):
        """Setup event handlers for the interface."""
        
        async def analysis_wrapper(*inputs):
            """Wrapper for campaign analysis with table name mapping."""
            username, password, campaign_id, from_date, to_date, table_selection_choices, openai_api_key_input = inputs[:7]
            progress = gr.Progress(track_tqdm=True)
            
            # Map table choices back to actual table names
            table_names_list = [table_names[table_choices.index(choice)] for choice in table_selection_choices]
            
            # Stream results from campaign service
            async for outputs in self.campaign_service.analyze_campaign_stream(
                username, password, campaign_id, from_date, to_date, table_names_list, openai_api_key_input, progress
            ):
                yield outputs
        
        # Bind the analysis function to the button
        analyze_button.click(
            fn=analysis_wrapper,
            inputs=input_components,
            outputs=output_components
        ) 