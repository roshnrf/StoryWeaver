#!/bin/bash

# StoryWeaver Speech Therapy - Setup Script
# This script automates the initial setup process

echo "🎯 StoryWeaver Speech Therapy - Setup"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo -e "${GREEN}✓${NC} Python $python_version detected"
else
    echo -e "${RED}✗${NC} Python 3.8+ required. Current: $python_version"
    exit 1
fi

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠${NC} Virtual environment already exists"
else
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🚀 Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓${NC} Pip upgraded"

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
echo "   This may take a few minutes..."
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} All dependencies installed"
else
    echo -e "${RED}✗${NC} Error installing dependencies"
    exit 1
fi

# Create necessary directories
echo ""
echo "📁 Creating project directories..."
mkdir -p pictures
mkdir -p docs/screenshots
mkdir -p outputs
echo -e "${GREEN}✓${NC} Directories created"

# Create .env file if it doesn't exist
echo ""
if [ ! -f ".env" ]; then
    echo "🔐 Creating .env file..."
    cp .env.example .env
    echo -e "${GREEN}✓${NC} .env file created"
    echo -e "${YELLOW}⚠${NC} Please edit .env and add your Google API key"
else
    echo -e "${YELLOW}⚠${NC} .env file already exists"
fi

# Check for pictures
echo ""
echo "🖼️ Checking for picture files..."
pic_count=$(ls pictures/*.{jpg,jpeg,png} 2>/dev/null | wc -l)
if [ $pic_count -eq 0 ]; then
    echo -e "${YELLOW}⚠${NC} No pictures found in pictures/ folder"
    echo "   Please add images: dog.jpg, cat.jpg, dolphin.jpg, car.jpg, rainbow.jpg"
else
    echo -e "${GREEN}✓${NC} Found $pic_count picture(s)"
fi

# Create .gitkeep files
touch pictures/.gitkeep
touch docs/screenshots/.gitkeep
touch outputs/.gitkeep

# Summary
echo ""
echo "======================================"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "======================================"
echo ""
echo "📝 Next Steps:"
echo "   1. Edit .env and add your Google API key"
echo "   2. Add picture files to pictures/ folder"
echo "   3. Run: streamlit run app.py"
echo ""
echo "📚 Documentation: README.md"
echo "🔒 Privacy Policy: ETHICS.md"
echo ""
echo "Happy coding! 🚀"