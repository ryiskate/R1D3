@echo off
REM Database Sync Script for R1D3 Project
REM This script helps sync the SQLite database between team members

echo ========================================
echo R1D3 Database Sync
echo ========================================
echo.

REM Check if there are uncommitted changes
git status --porcelain | findstr "db.sqlite3" >nul
if %errorlevel% equ 0 (
    echo [!] You have uncommitted database changes!
    echo.
    choice /C YN /M "Do you want to commit and push these changes"
    if errorlevel 2 goto :pull_only
    if errorlevel 1 goto :commit_and_push
) else (
    echo [*] No local database changes detected
    goto :pull_only
)

:commit_and_push
echo.
set /p commit_msg="Enter commit message (describe your changes): "
if "%commit_msg%"=="" set commit_msg="Updated database"

echo.
echo [*] Committing database changes...
git add db.sqlite3
git commit -m "Database: %commit_msg%"

echo [*] Pushing to remote...
git push

if %errorlevel% neq 0 (
    echo [!] Push failed! There might be conflicts.
    echo [!] Try pulling first: git pull
    pause
    exit /b 1
)

echo [✓] Database changes pushed successfully!
echo.
goto :end

:pull_only
echo.
echo [*] Pulling latest changes from remote...
git pull

if %errorlevel% neq 0 (
    echo [!] Pull failed! You might have conflicts.
    echo.
    echo To resolve:
    echo   - Keep your version: git checkout --ours db.sqlite3
    echo   - Keep their version: git checkout --theirs db.sqlite3
    echo   - Then: git add db.sqlite3 ^&^& git commit -m "Resolved database conflict"
    pause
    exit /b 1
)

echo [✓] Database synced successfully!
echo.

REM Check if database was updated
git diff HEAD@{1} HEAD --name-only | findstr "db.sqlite3" >nul
if %errorlevel% equ 0 (
    echo [!] Database was updated by the other person!
    echo [!] Restart your Django server to use the new database.
) else (
    echo [*] Database was already up to date.
)

:end
echo.
echo ========================================
echo Sync Complete!
echo ========================================
pause
