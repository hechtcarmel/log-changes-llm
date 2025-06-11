# Campaign Changes Analyzer

A Python application that analyzes MySQL campaign change logs and provides AI-powered insights about modifications, risks, and recommendations using OpenAI.

## Features

- **Database Integration**: Connects to MySQL database with runtime credentials
- **Campaign Analysis**: Retrieves and analyzes campaign modification history
- **AI Insights**: Uses OpenAI to generate strategic insights and recommendations
- **Data Visualization**: Groups changes by time and provides summary statistics
- **Gradio Interface**: User-friendly web interface for analysis

## Requirements

- Python 3.11+
- Conda
- MySQL database access
- OpenAI API key

## Installation

### Quick Setup (Recommended)
```bash
git clone <repository-url>
cd campaign-changes-analyzer
chmod +x setup.sh
./setup.sh
```

### Manual Setup
1. Clone this repository:
```bash
git clone <repository-url>
cd campaign-changes-analyzer
```

2. Create and activate the Conda environment:
```bash
conda env create -f environment.yml
conda activate log_changes
```

3. Set up environment variables:
```bash
cp env.example .env
```

4. Edit the `.env` file and add your OpenAI API key:
```bash
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open the web interface in your browser (usually at http://127.0.0.1:7860)

3. Enter the following:
   - **MySQL Username**: Your database username
   - **MySQL Password**: Your database password  
   - **Campaign ID**: The campaign ID to analyze (numeric)
   - **Max Records**: Number of recent changes to retrieve (5-50)

4. Click "🔍 Analyze Campaign Changes" to get results

## Database Configuration

The application connects to:
- **Host**: proxysql-office.taboolasyndication.com:6033
- **Database**: trc
- **Table**: sp_campaign_details_v2_changes_log

Database credentials are entered via the GUI for security (not stored in files).

## What You Get

### AI Analysis
- **Summary**: Overview of changes and their significance
- **Key Insights**: Strategic observations about campaign modifications
- **Risk Factors**: Potential concerns or issues identified
- **Recommendations**: Actionable suggestions for campaign management

### Data Views
- **Grouped Changes**: Changes organized by update time and user
- **All Changes**: Complete chronological change history
- **Statistics**: Summary metrics about change patterns
- **Raw Data**: Formatted data sent to AI (for transparency)

## Example Output

```json
{
  "summary": "Campaign received 8 changes across 3 sessions over 2 days, focusing on budget optimization and targeting refinements.",
  "key_insights": [
    "Budget increases suggest positive performance trends",
    "Geographic targeting expansion indicates market testing",
    "Bid strategy changes show move toward automation"
  ],
  "risk_factors": [
    "Multiple simultaneous changes may complicate performance attribution",
    "Rapid geographic expansion requires careful monitoring"
  ],
  "recommendations": [
    "Monitor performance in new geographic regions closely",
    "Allow 7-14 day learning period for automated bidding",
    "Establish baseline metrics before further optimizations"
  ]
}
```

## Architecture

- **Database Layer**: MySQL connection and query management
- **AI Layer**: OpenAI integration for campaign analysis
- **Data Processing**: Pandas-based data formatting and grouping
- **Interface**: Gradio web application with tabbed results

## Troubleshooting

### "ModuleNotFoundError: No module named 'gradio'"
Make sure you're in the correct conda environment:
```bash
conda activate log_changes
python app.py
```

### Environment Setup Issues
If the environment creation fails, try:
```bash
conda clean --all
conda env create -f environment.yml --force
```

### MySQL Connection Issues
- Ensure you have the correct database credentials
- Check VPN connection if required
- Verify the hostname: `proxysql-office.taboolasyndication.com:6033`

### OpenAI API Issues
- Verify your API key is valid: https://platform.openai.com/api-keys
- Check your API quota and billing settings
- Ensure the key starts with `sk-`

## Security

- Database credentials entered via GUI (not stored)
- Secure password input fields
- No credential persistence or caching
- Connection testing before queries
- .env file ignored by git (contains API keys)

## License

MIT 