# Campaign Changes Analyzer - Project Plan

## Project Overview
Create a web application that analyzes MySQL campaign change logs and provides AI-powered summaries using OpenAI. The application will allow users to input a campaign ID, retrieve change history, and get intelligent summaries of recent modifications.

## Current State Analysis
**Existing Project Structure (Value LLM Experiment):**
- Uses Gradio for web interface
- Multi-LLM support (Ollama, OpenAI, Anthropic)
- Modular architecture with base classes
- Environment-based configuration
- HTML processing utilities
- Structured prompts with examples

**Key Components to Adapt:**
- ✅ Models directory (base.py, openai.py) - adapt for campaign summarization
- ✅ Prompts system - create campaign change prompts
- ✅ Environment configuration - OpenAI API key (MySQL credentials via GUI)
- ✅ Conda environment setup
- ✅ Gradio interface - adapt for campaign ID input and results display
- ❌ HTML parsing utilities - not needed

## Technical Requirements

### Database Integration
- **MySQL Connection**: `jdbc:mysql://proxysql-office.taboolasyndication.com:6033/trc`
- **Authentication**: Username/password provided via GUI input fields
- **Target Table**: `trc.sp_campaign_details_v2_changes_log`
- **Query**: `SELECT * FROM trc.sp_campaign_details_v2_changes_log WHERE campaign_id = ? ORDER BY update_time LIMIT 10`
- **Grouping**: Group changes by `update_time` for better analysis

### GUI Requirements (Gradio Interface)
- **Database Connection Inputs**:
  - Username field (text input)
  - Password field (password input, masked)
  - Campaign ID field (text input)
- **Display Areas**: 
  - Raw change data (formatted table/JSON)
  - AI-generated summary (text area)
  - Query execution status and metadata
  - Connection status indicator
- **Interactive Elements**: Analyze button, clear/reset functionality
- **Data Visualization**: Tabular display of grouped changes by update_time

### AI Integration
- **OpenAI Integration**: Use existing OpenAI model structure
- **Prompt Engineering**: Create specialized prompts for campaign change summarization
- **Response Format**: Structured summary of changes with key insights

## Implementation Plan

### Phase 1: Project Setup & Cleanup ✅
- [x] Analyze existing project structure
- [x] Delete unnecessary files (HTML parsing, Ollama, Anthropic models)
- [x] Update environment.yml with MySQL dependencies
- [x] Update .env template (keep OpenAI, remove others)
- [x] Update README.md with project documentation

### Phase 2: Database Integration ✅
- [x] Create dynamic database connection utility (with runtime credentials)
- [x] Implement MySQL connection to proxysql-office.taboolasyndication.com:6033
- [x] Implement campaign changes query functionality
- [x] Add data grouping by update_time
- [x] Create data models for campaign changes
- [x] Add error handling for database operations and authentication

### Phase 3: AI Integration ✅
- [x] Adapt OpenAI model for campaign summarization
- [x] Create campaign change analysis prompts
- [x] Implement structured response handling
- [x] Add prompt examples for different change scenarios

### Phase 4: Gradio Interface Development ✅
- [x] Adapt existing Gradio interface for campaign analysis
- [x] Create database credential input fields (username/password)
- [x] Create campaign ID input field
- [x] Add connection status indicator
- [x] Add tabular data display components
- [x] Implement AI summary display area
- [x] Add status/metadata display
- [x] Integrate database and AI functionality

### Phase 5: Testing & Refinement 🔄
- [ ] Test with sample campaign IDs
- [ ] Refine AI prompts based on results
- [ ] Add error handling and validation
- [ ] Performance optimization
- [ ] Documentation updates

## File Structure Plan

```
campaign-changes-analyzer/
├── models/
│   ├── __init__.py
│   ├── base.py (adapted)
│   └── openai.py (adapted)
├── database/
│   ├── __init__.py
│   ├── connection.py
│   └── queries.py
├── prompts/
│   ├── __init__.py
│   └── campaign_changes.py
├── utils/
│   ├── __init__.py
│   └── data_formatter.py
├── app.py (Gradio interface + main entry point)
├── environment.yml
├── env.example
├── README.md
└── table_ddl.txt
```

## Database Schema Analysis
Based on `table_ddl.txt`:
- **Primary Key**: (id, update_time) with partitioning
- **Key Fields**: campaign_id, field_name, old_value, new_value, update_time, update_user
- **Indexes**: Available on (campaign_id, update_time) and (update_time, field_name)
- **Data Types**: Values stored as varchar(5000), allowing for large content changes

## AI Analysis Strategy
1. **Group Changes**: Combine changes from same update_time
2. **Categorize Changes**: Identify field types and change patterns
3. **Summarize Impact**: Provide business-friendly interpretation
4. **Highlight Anomalies**: Flag unusual patterns or frequent changes

## Dependencies to Update
- **Add**: `mysql-connector-python` or `PyMySQL`, `pandas` for data manipulation
- **Keep**: `gradio` (for web interface), `openai`, `python-dotenv`
- **Remove**: `ollama`, `anthropic`, `beautifulsoup4`

## Next Steps
1. **Approval Required**: Please review and approve this updated plan
2. **✅ Database Connection**: Confirmed - `proxysql-office.taboolasyndication.com:6033/trc`
3. **Sample Data**: Any test campaign IDs for development?
4. **Gradio Layout**: Confirm preferred layout (single column vs multi-column)
5. **OpenAI API**: Confirm OpenAI API key will be in environment or also GUI input?

## Progress Tracking
- ✅ = Completed
- 🔄 = In Progress  
- ❌ = Not Started
- 🚫 = Removed/Not Needed

---
*Plan created on: $(date)*
*Status: IMPLEMENTATION COMPLETE - Ready for Testing* 