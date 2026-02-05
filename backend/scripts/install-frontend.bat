@echo off
REM Automatic NPM Installation Script
REM Cleans and installs all frontend dependencies

echo ============================================================
echo Phonebook Frontend - Automatic Dependency Installation
echo ============================================================
echo.

REM Check if in correct directory
if not exist "frontend" (
    if not exist "package.json" (
        echo [ERROR] Run this from phonebook-app\ folder or frontend\ folder!
        echo.
        echo Current directory: %CD%
        echo Expected: C:\...\phonebook-app\ or C:\...\phonebook-app\frontend\
        pause
        exit /b 1
    )
)

REM Determine if we're in root or frontend
if exist "frontend" (
    echo [INFO] Detected root directory, switching to frontend\
    cd frontend
)

echo Current directory: %CD%
echo.

REM Check Node.js
echo [1/6] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed!
    echo.
    echo Please install Node.js 18+ from: https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Node.js found:
node --version
npm --version
echo.

REM Clean everything
echo [2/6] Cleaning old installation...
echo Removing node_modules...
if exist "node_modules" (
    rmdir /s /q node_modules
    echo [OK] node_modules deleted
) else (
    echo [INFO] node_modules not found (OK)
)

echo Removing package-lock.json...
if exist "package-lock.json" (
    del /q package-lock.json
    echo [OK] package-lock.json deleted
) else (
    echo [INFO] package-lock.json not found (OK)
)

echo Removing dist...
if exist "dist" (
    rmdir /s /q dist
    echo [OK] dist deleted
) else (
    echo [INFO] dist not found (OK)
)
echo.

REM Clear npm cache
echo [3/6] Clearing npm cache...
npm cache clean --force
if errorlevel 1 (
    echo [WARNING] npm cache clean failed, continuing anyway...
) else (
    echo [OK] npm cache cleared
)
echo.

REM Verify registry
echo [4/6] Checking npm registry...
echo Current registry:
npm config get registry
echo.
echo If slow in Poland, you can use:
echo   npm config set registry https://registry.npmjs.org/
echo.

REM Install dependencies
echo [5/6] Installing dependencies...
echo This will take 2-5 minutes, please wait...
echo.

npm install

if errorlevel 1 (
    echo.
    echo [ERROR] npm install failed!
    echo.
    echo Common solutions:
    echo   1. Check internet connection
    echo   2. Run as Administrator
    echo   3. Try: npm config set registry https://registry.npmjs.org/
    echo   4. Delete C:\Users\%USERNAME%\AppData\Roaming\npm-cache
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] All dependencies installed!
echo.

REM Verify critical packages
echo [6/6] Verifying installation...
echo.

echo Checking React...
if not exist "node_modules\react\package.json" (
    echo [ERROR] React not found!
    pause
    exit /b 1
)
echo [OK] react: 
type node_modules\react\package.json | findstr version | more +0

echo Checking React DOM...
if not exist "node_modules\react-dom\package.json" (
    echo [ERROR] React DOM not found!
    pause
    exit /b 1
)
echo [OK] react-dom: 
type node_modules\react-dom\package.json | findstr version | more +0

echo Checking React Router...
if not exist "node_modules\react-router-dom\package.json" (
    echo [ERROR] React Router DOM not found!
    pause
    exit /b 1
)
echo [OK] react-router-dom: 
type node_modules\react-router-dom\package.json | findstr version | more +0

echo Checking Axios...
if not exist "node_modules\axios\package.json" (
    echo [ERROR] Axios not found!
    pause
    exit /b 1
)
echo [OK] axios: 
type node_modules\axios\package.json | findstr version | more +0

echo Checking Vite...
if not exist "node_modules\vite\package.json" (
    echo [ERROR] Vite not found!
    pause
    exit /b 1
)
echo [OK] vite: 
type node_modules\vite\package.json | findstr version | more +0

echo Checking TypeScript...
if not exist "node_modules\typescript\package.json" (
    echo [ERROR] TypeScript not found!
    pause
    exit /b 1
)
echo [OK] typescript: 
type node_modules\typescript\package.json | findstr version | more +0

echo Checking Tailwind CSS...
if not exist "node_modules\tailwindcss\package.json" (
    echo [ERROR] Tailwind CSS not found!
    pause
    exit /b 1
)
echo [OK] tailwindcss: 
type node_modules\tailwindcss\package.json | findstr version | more +0

echo.
echo ============================================================
echo [SUCCESS] All dependencies installed and verified!
echo ============================================================
echo.

echo Installed packages summary:
echo   - react ^18.2.0
echo   - react-dom ^18.2.0
echo   - react-router-dom ^6.21+
echo   - axios ^1.6+
echo   - typescript ^5.3+
echo   - vite ^5.0+
echo   - tailwindcss ^3.4+
echo   + 20+ other dev dependencies
echo.

echo You can now run:
echo   npm run dev        - Start development server
echo   npm run build      - Build for production
echo   npm run preview    - Preview production build
echo.

choice /C YN /M "Do you want to start dev server now?"
if not errorlevel 2 (
    echo.
    echo Starting development server...
    echo Press Ctrl+C to stop
    echo.
    npm run dev
)

pause
