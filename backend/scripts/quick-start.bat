@echo off
REM Phonebook App - Quick Start Script for Windows
REM Automatyczna instalacja i uruchomienie aplikacji

setlocal enabledelayedexpansion

echo ============================================================
echo Phonebook Application - Quick Start Installation (Windows)
echo ============================================================
echo.

REM Check if running in correct directory
if not exist "docker-compose.yml" (
    echo [ERROR] docker-compose.yml not found!
    echo Please run this script from the project root directory.
    echo.
    echo Expected structure:
    echo   phonebook-app\
    echo   ├── backend\
    echo   ├── frontend\
    echo   ├── docker-compose.yml
    echo   └── QUICK_START.bat  ^(this file^)
    pause
    exit /b 1
)

REM Check Docker is installed
echo Checking prerequisites...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed!
    echo Please install Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed!
    echo Please install Docker Compose: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

echo [OK] Docker found
echo [OK] Docker Compose found
echo.

REM Setup environment file
echo Setting up environment variables...
if not exist ".env" (
    copy .env.example .env >nul
    echo [OK] Created .env file from template
    echo.
    echo [WARNING] Generating secure secrets...
    
    REM Generate secrets using PowerShell
    for /f %%i in ('powershell -Command "[System.Convert]::ToBase64String((1..32 | %%{Get-Random -Maximum 256}))"') do set SECRET_KEY=%%i
    for /f %%i in ('powershell -Command "[System.Convert]::ToBase64String((1..24 | %%{Get-Random -Maximum 256}))"') do set POSTGRES_PASSWORD=%%i
    
    REM Update .env file
    powershell -Command "(gc .env) -replace 'CHANGE_ME_TO_RANDOM_32_CHAR_HEX', '%SECRET_KEY%' | Out-File -encoding ASCII .env"
    powershell -Command "(gc .env) -replace 'CHANGE_ME_TO_SECURE_PASSWORD', '%POSTGRES_PASSWORD%' | Out-File -encoding ASCII .env"
    
    echo [OK] Secrets generated and saved to .env
) else (
    echo [OK] .env file already exists
)
echo.

REM Ask user for installation option
echo Installation Options:
echo   1^) Quick Start ^(Docker^) - Recommended!
echo   2^) Manual Setup ^(No Docker^)
echo   3^) Exit
echo.
set /p choice="Choose option [1-3]: "

if "%choice%"=="1" (
    echo.
    echo Starting Docker containers...
    echo This will:
    echo   - Build backend image ^(FastAPI^)
    echo   - Build frontend image ^(React + Nginx^)
    echo   - Start PostgreSQL database
    echo   - Initialize database schema
    echo.
    
    REM Build and start containers
    docker-compose up -d --build
    
    echo.
    echo Waiting for services to start ^(30 seconds^)...
    timeout /t 30 /nobreak >nul
    
    REM Check services
    echo.
    echo Checking service health...
    docker-compose ps
    
    echo.
    echo ============================================================
    echo [SUCCESS] Installation complete!
    echo ============================================================
    echo.
    echo Application is running!
    echo --------------------------------------------------------
    echo Frontend:    http://localhost
    echo Backend API: http://localhost:8000
    echo API Docs:    http://localhost:8000/docs
    echo --------------------------------------------------------
    echo.
    echo Next Steps:
    echo   1. Open http://localhost in your browser
    echo   2. Click 'Register' to create an account
    echo   3. Login and start managing contacts!
    echo.
    echo Useful Commands:
    echo   View logs:  docker-compose logs -f
    echo   Stop app:   docker-compose down
    echo   Restart:    docker-compose restart
    echo.
    
) else if "%choice%"=="2" (
    echo.
    echo Manual Setup Instructions:
    echo.
    echo Backend Setup:
    echo   1. cd backend
    echo   2. python -m venv venv
    echo   3. venv\Scripts\activate
    echo   4. pip install -r requirements.txt
    echo   5. Edit .env file with database connection
    echo   6. python init_db.py
    echo   7. uvicorn app.main:app --reload --port 8000
    echo.
    echo Frontend Setup ^(in new terminal^):
    echo   1. cd frontend
    echo   2. npm install
    echo   3. npm run dev
    echo.
    echo Database Setup:
    echo   You need PostgreSQL 15+ running locally
    echo   Create database: createdb phonebook_db
    echo.
    
) else if "%choice%"=="3" (
    echo Exiting...
    exit /b 0
    
) else (
    echo [ERROR] Invalid option
    pause
    exit /b 1
)

pause
