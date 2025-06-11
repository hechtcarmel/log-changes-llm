#!/bin/bash

# Campaign Changes Analyzer - Setup Script
echo "🚀 Campaign Changes Analyzer Setup"
echo "=================================="

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed. Please install Anaconda or Miniconda first."
    echo "   Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✅ Conda found"

# Create conda environment
echo "📦 Creating conda environment 'log_changes'..."
conda env create -f environment.yml

if [ $? -eq 0 ]; then
    echo "✅ Environment created successfully"
else
    echo "❌ Failed to create environment"
    exit 1
fi

# Copy environment file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp env.example .env
    echo "✅ .env file created from template"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your OpenAI API key!"
    echo "   Get your API key from: https://platform.openai.com/api-keys"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the environment: conda activate log_changes"
echo "2. Edit .env file and add your OpenAI API key"
echo "3. Run the application: python app.py"
echo "4. Open http://0.0.0.0:7860 in your browser"
echo ""
echo "💡 Make sure you have your MySQL credentials ready!" 