#!/bin/bash
# Phonebook App - Quick Start Script
# Automatyczna instalacja i uruchomienie aplikacji

set -e  # Exit on error

echo "🚀 Phonebook Application - Quick Start Installation"
echo "===================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running in correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Error: docker-compose.yml not found!${NC}"
    echo "Please run this script from the project root directory."
    echo ""
    echo "Expected structure:"
    echo "  phonebook-app/"
    echo "  ├── backend/"
    echo "  ├── frontend/"
    echo "  ├── docker-compose.yml"
    echo "  └── QUICK_START.sh  (this file)"
    exit 1
fi

# Check Docker is installed
echo "🔍 Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed!${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker found: $(docker --version)${NC}"
echo -e "${GREEN}✅ Docker Compose found: $(docker-compose --version)${NC}"
echo ""

# Setup environment file
echo "⚙️  Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}📝 Created .env file from template${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Generating secure secrets...${NC}"
    
    # Generate SECRET_KEY (32 random hex characters)
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
    
    # Generate POSTGRES_PASSWORD
    POSTGRES_PASSWORD=$(openssl rand -base64 24 2>/dev/null || python3 -c "import secrets; print(secrets.token_urlsafe(24))")
    
    # Update .env file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/CHANGE_ME_TO_RANDOM_32_CHAR_HEX/$SECRET_KEY/" .env
        sed -i '' "s/CHANGE_ME_TO_SECURE_PASSWORD/$POSTGRES_PASSWORD/" .env
    else
        # Linux
        sed -i "s/CHANGE_ME_TO_RANDOM_32_CHAR_HEX/$SECRET_KEY/" .env
        sed -i "s/CHANGE_ME_TO_SECURE_PASSWORD/$POSTGRES_PASSWORD/" .env
    fi
    
    echo -e "${GREEN}✅ Secrets generated and saved to .env${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi
echo ""

# Ask user for quick or full setup
echo "📦 Installation Options:"
echo "  1) Quick Start (Docker) - Recommended! ⚡"
echo "  2) Manual Setup (No Docker)"
echo "  3) Exit"
echo ""
read -p "Choose option [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "🐳 Starting Docker containers..."
        echo "This will:"
        echo "  - Build backend image (FastAPI)"
        echo "  - Build frontend image (React + Nginx)"
        echo "  - Start PostgreSQL database"
        echo "  - Initialize database schema"
        echo ""
        
        # Build and start containers
        docker-compose up -d --build
        
        echo ""
        echo "⏳ Waiting for services to start (30 seconds)..."
        sleep 30
        
        # Check if services are running
        echo ""
        echo "🔍 Checking service health..."
        docker-compose ps
        
        echo ""
        echo -e "${GREEN}✅ Installation complete!${NC}"
        echo ""
        echo "🎉 Application is running!"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo -e "${GREEN}Frontend:${NC}    http://localhost"
        echo -e "${GREEN}Backend API:${NC} http://localhost:8000"
        echo -e "${GREEN}API Docs:${NC}    http://localhost:8000/docs"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "📖 Next Steps:"
        echo "  1. Open http://localhost in your browser"
        echo "  2. Click 'Register' to create an account"
        echo "  3. Login and start managing contacts!"
        echo ""
        echo "🔧 Useful Commands:"
        echo "  View logs:    docker-compose logs -f"
        echo "  Stop app:     docker-compose down"
        echo "  Restart:      docker-compose restart"
        echo ""
        ;;
    
    2)
        echo ""
        echo "📝 Manual Setup Instructions:"
        echo ""
        echo "Backend Setup:"
        echo "  1. cd backend"
        echo "  2. python3 -m venv venv"
        echo "  3. source venv/bin/activate  (Linux/Mac) or venv\\Scripts\\activate (Windows)"
        echo "  4. pip install -r requirements.txt"
        echo "  5. Edit .env file with database connection"
        echo "  6. python init_db.py"
        echo "  7. uvicorn app.main:app --reload --port 8000"
        echo ""
        echo "Frontend Setup (in new terminal):"
        echo "  1. cd frontend"
        echo "  2. npm install"
        echo "  3. npm run dev"
        echo ""
        echo "Database Setup:"
        echo "  You need PostgreSQL 15+ running locally"
        echo "  Create database: createdb phonebook_db"
        echo ""
        ;;
    
    3)
        echo "👋 Exiting..."
        exit 0
        ;;
    
    *)
        echo -e "${RED}❌ Invalid option${NC}"
        exit 1
        ;;
esac
