@echo off
echo ========================================
echo R1D3 COMPLETE DATABASE RESET
echo ========================================
echo.
echo WARNING: This will DELETE your database and start fresh!
echo.
set /p confirm="Type YES to continue: "

if /i not "%confirm%"=="YES" (
    echo Cancelled.
    pause
    exit /b
)

echo.
echo Step 1: Backing up old database...
if exist db.sqlite3 (
    copy db.sqlite3 db_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%.sqlite3
    echo Backup created
    del db.sqlite3
    echo Old database deleted
) else (
    echo No existing database found
)

echo.
echo Step 2: Running migrations...
python manage.py migrate

echo.
echo Step 3: Creating quick links table...
python create_quicklink_table.py

echo.
echo ========================================
echo DATABASE RESET COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Create superuser: python manage.py createsuperuser
echo 2. Start server: python run_server.py
echo.
pause
