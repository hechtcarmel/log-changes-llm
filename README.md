# Campaign Changes Analyzer

A modular Python application that analyzes MySQL campaign change logs and provides AI-powered insights about modifications, risks, and recommendations using OpenAI. Built with clean architecture principles for maintainability and extensibility.

## 🏗️ Architecture

The application follows clean architecture principles with clear separation of concerns:

### **Service Layer**
- **ConfigService**: Centralized configuration and environment management
- **ValidationService**: Input validation and data integrity checks
- **CampaignService**: Main business logic coordination for campaign analysis
- **UIService**: Gradio interface creation and event handling

### **Data Layer**
- **DatabaseConnection**: MySQL connection management with runtime credentials
- **CampaignChangesQuery**: Database query operations and data retrieval

### **Models**
- **OpenAIModel**: AI integration for campaign analysis
- **BaseModel**: Abstract base for AI models
- **Data Models**: ChangeEntry, ChangeSession, CampaignAnalysisResponse

### **Constants & Configuration**
- **Constants**: Centralized application constants and configurations
- **Table Mappings**: Database table definitions and display names

## 📁 Project Structure

```
campaign-changes-analyzer/
├── app.py                          # Main application entry point (15 lines)
├── constants/                      # Application constants
│   ├── __init__.py                 # Package exports
│   ├── app_constants.py            # Core application constants
│   └── table_mappings.py           # Database table configurations
├── services/                       # Business logic layer
│   ├── __init__.py                 # Package exports
│   ├── config_service.py           # Configuration management
│   ├── validation_service.py       # Input validation logic
│   ├── campaign_service.py         # Main business logic coordinator
│   └── ui_service.py               # UI creation and management
├── database/                       # Data access layer
│   ├── __init__.py
│   ├── connection.py               # Database connection management
│   └── queries.py                  # Query operations
├── models/                         # Data models and AI integration
│   ├── __init__.py
│   ├── base.py                     # Base models and data structures
│   └── openai.py                   # OpenAI integration
├── utils/                          # Utility functions
│   ├── __init__.py
│   └── data_formatter.py           # Data formatting utilities
├── prompts/                        # AI prompt templates
│   ├── __init__.py
│   └── campaign_changes.py         # Campaign analysis prompts
└── ui/                             # UI components (if needed)
```

## ✨ Features

- **🏗️ Clean Architecture**: Service-oriented design with clear separation of concerns
- **🔧 Configurable**: Centralized configuration management with environment support
- **✅ Robust Validation**: Comprehensive input validation and error handling
- **🗄️ Database Integration**: Secure MySQL connection with runtime credentials
- **🤖 AI-Powered Analysis**: OpenAI integration for intelligent campaign insights
- **📊 Rich Data Visualization**: Grouped changes, statistics, and formatted displays
- **🖥️ Modern UI**: Responsive Gradio interface with tabbed results
- **🛡️ Security**: Secure credential handling and validation

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Conda
- MySQL database access
- OpenAI API key

### Installation

1. **Clone and setup**:
```bash
git clone <repository-url>
cd campaign-changes-analyzer
chmod +x setup.sh
./setup.sh
```

2. **Configure environment**:
```bash
cp env.example .env
# Edit .env with your OpenAI API key
```

3. **Run the application**:
```bash
python app.py
```

## 🔧 Configuration

The application uses a centralized configuration system:

### Environment Variables (.env)
```bash
OPENAI_API_KEY=sk-your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

### Database Configuration
Configured in `constants/app_constants.py`:
- Host: proxysql-office.taboolasyndication.com:6033
- Database: trc
- Tables: Multiple campaign change log tables

### Application Constants
All constants are centralized in the `constants/` directory:
- UI messages and labels
- Validation rules and limits
- Display configurations
- Progress step mappings

## 📋 Usage

1. **Start the application**: `python app.py`
2. **Access the web interface**: Usually at http://127.0.0.1:7861
3. **Enter credentials and parameters**:
   - MySQL username and password
   - Campaign ID (numeric)
   - Date range for analysis
   - Select tables to query
   - OpenAI API key (if not in environment)
4. **Analyze**: Click "🔍 Analyze Campaign Changes"

## 📊 Analysis Results

### AI-Generated Insights
- **📋 Summary**: Overview of changes and their significance
- **💡 Key Insights**: Strategic observations about modifications
- **⚠️ Risk Assessment**: Potential concerns identified
- **🎯 Recommendations**: Actionable suggestions

### Data Views
- **🗓️ Change History**: Chronological change sessions
- **📈 Statistics**: Summary metrics and patterns
- **🔍 Raw Data**: Formatted data sent to AI (transparency)

## 🛠️ Development

### Design Principles
- **SOLID Principles**: Single responsibility, open/closed, dependency inversion
- **DRY (Don't Repeat Yourself)**: Centralized constants and reusable components
- **KISS (Keep It Simple, Stupid)**: Clean, focused interfaces
- **Separation of Concerns**: Clear boundaries between layers

### Adding New Features

1. **Business Logic**: Add to appropriate service in `services/`
2. **Configuration**: Add constants to `constants/`
3. **Validation**: Extend `ValidationService`
4. **UI Components**: Extend `UIService`
5. **Database Operations**: Extend query classes in `database/`

### Testing
```bash
# Run tests (when implemented)
python -m pytest tests/

# Check code style
black .
flake8 .
```

## 🐛 Troubleshooting

### Common Issues

**Environment Issues**:
```bash
conda activate log_changes
pip install -r requirements.txt  # if conda fails
```

**Database Connection**:
- Verify credentials and network access
- Check VPN connection if required
- Ensure database host is accessible

**OpenAI API**:
- Verify API key format (starts with `sk-`)
- Check API quota and billing
- Ensure model availability

**Import Errors**:
```bash
# Ensure you're in the project directory
cd campaign-changes-analyzer
python app.py
```

## 🔐 Security

- **Credential Safety**: No credential storage or persistence
- **Secure Input**: Password fields and validation
- **Environment Protection**: .env files ignored by git
- **Connection Testing**: Validation before operations
- **Input Sanitization**: Comprehensive validation service

## 🚦 Performance

- **Efficient Architecture**: Service layer for optimal resource usage
- **Streaming Results**: Real-time AI analysis updates
- **Connection Management**: Proper database connection lifecycle
- **Memory Optimization**: Pandas for efficient data processing

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Follow the established architecture patterns
2. Add constants to appropriate files
3. Include comprehensive validation
4. Update documentation for new features
5. Maintain clean separation of concerns

## 🔄 Version History

- **v2.0.0**: Refactored architecture with service layer
- **v1.0.0**: Initial monolithic implementation 