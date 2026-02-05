#!/bin/bash
# Automatic NPM Installation Script
# Cleans and installs all frontend dependencies

set -e  # Exit on error

echo "============================================================"
echo "Phonebook Frontend - Automatic Dependency Installation"
echo "============================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if in correct directory
if [ ! -d "frontend" ] && [ ! -f "package.json" ]; then
    echo -e "${RED}[ERROR] Run this from phonebook-app/ folder or frontend/ folder!${NC}"
    echo ""
    echo "Current directory: $(pwd)"
    echo "Expected: .../phonebook-app/ or .../phonebook-app/frontend/"
    exit 1
fi

# Determine if we're in root or frontend
if [ -d "frontend" ]; then
    echo "[INFO] Detected root directory, switching to frontend/"
    cd frontend
fi

echo "Current directory: $(pwd)"
echo ""

# Check Node.js
echo "[1/6] Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}[ERROR] Node.js is not installed!${NC}"
    echo ""
    echo "Please install Node.js 18+:"
    echo "  macOS: brew install node@18"
    echo "  Ubuntu: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
    echo "          sudo apt install nodejs"
    exit 1
fi

echo -e "${GREEN}[OK] Node.js found:${NC}"
node --version
npm --version
echo ""

# Clean everything
echo "[2/6] Cleaning old installation..."
echo "Removing node_modules..."
if [ -d "node_modules" ]; then
    rm -rf node_modules
    echo -e "${GREEN}[OK] node_modules deleted${NC}"
else
    echo "[INFO] node_modules not found (OK)"
fi

echo "Removing package-lock.json..."
if [ -f "package-lock.json" ]; then
    rm -f package-lock.json
    echo -e "${GREEN}[OK] package-lock.json deleted${NC}"
else
    echo "[INFO] package-lock.json not found (OK)"
fi

echo "Removing dist..."
if [ -d "dist" ]; then
    rm -rf dist
    echo -e "${GREEN}[OK] dist deleted${NC}"
else
    echo "[INFO] dist not found (OK)"
fi
echo ""

# Clear npm cache
echo "[3/6] Clearing npm cache..."
npm cache clean --force
echo -e "${GREEN}[OK] npm cache cleared${NC}"
echo ""

# Verify registry
echo "[4/6] Checking npm registry..."
echo "Current registry:"
npm config get registry
echo ""

# Install dependencies
echo "[5/6] Installing dependencies..."
echo "This will take 2-5 minutes, please wait..."
echo ""

npm install

echo ""
echo -e "${GREEN}[OK] All dependencies installed!${NC}"
echo ""

# Verify critical packages
echo "[6/6] Verifying installation..."
echo ""

check_package() {
    if [ -f "node_modules/$1/package.json" ]; then
        version=$(cat "node_modules/$1/package.json" | grep -o '"version": "[^"]*' | grep -o '[^"]*$')
        echo -e "${GREEN}[OK]${NC} $1: $version"
    else
        echo -e "${RED}[ERROR]${NC} $1 not found!"
        exit 1
    fi
}

check_package "react"
check_package "react-dom"
check_package "react-router-dom"
check_package "axios"
check_package "vite"
check_package "typescript"
check_package "tailwindcss"

echo ""
echo "============================================================"
echo -e "${GREEN}[SUCCESS] All dependencies installed and verified!${NC}"
echo "============================================================"
echo ""

echo "Installed packages summary:"
echo "  - react ^18.2.0"
echo "  - react-dom ^18.2.0"
echo "  - react-router-dom ^6.21+"
echo "  - axios ^1.6+"
echo "  - typescript ^5.3+"
echo "  - vite ^5.0+"
echo "  - tailwindcss ^3.4+"
echo "  + 20+ other dev dependencies"
echo ""

echo "You can now run:"
echo "  npm run dev        - Start development server"
echo "  npm run build      - Build for production"
echo "  npm run preview    - Preview production build"
echo ""

read -p "Do you want to start dev server now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting development server..."
    echo "Press Ctrl+C to stop"
    echo ""
    npm run dev
fi
