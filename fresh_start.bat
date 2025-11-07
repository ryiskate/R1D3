@echo off
echo ========================================
echo R1D3 Fresh Database Setup
echo ========================================
echo.

REM Backup and remove old database
if exist db.sqlite3 (
    echo Backing up old database...
    copy db.sqlite3 db_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.sqlite3
    del db.sqlite3
    echo Old database removed
) else (
    echo No existing database found
)

echo.
echo Running migrations...
python manage.py migrate

echo.
echo ========================================
echo Database setup complete!
echo.
echo Next step: Create a superuser
echo Run: python manage.py createsuperuser
echo ========================================
pause
