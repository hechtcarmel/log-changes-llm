"""Campaign Changes Analyzer - Main Application Entry Point."""

import logging
import multiprocessing

from campaign_analyzer.services import ConfigService, UIService

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    """Main application entry point."""
    # Initialize configuration service
    config = ConfigService()
    
    # Initialize UI service
    ui_service = UIService(config)
    
    # Create and launch the interface
    app = ui_service.create_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7861,
        show_error=True,
        share=False,
        inbrowser=True
    ) 

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main() 
    