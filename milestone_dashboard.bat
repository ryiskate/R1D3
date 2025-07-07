@echo off
title R1D3 Milestone Dashboard
color 0B

:menu
cls
echo.
echo ===================================================
echo            R1D3 MILESTONE DASHBOARD
echo ===================================================
echo.

:: Display current milestone at the top of the menu
echo CURRENT MILESTONE:
echo -----------------
python manage.py shell -c "from projects.game_models import GameMilestone; print('* ' + GameMilestone.objects.filter(is_completed=False).first().title if GameMilestone.objects.filter(is_completed=False).exists() else '* None')"
echo.
echo ===================================================
echo.
echo  1. Show detailed milestone status
echo  2. Start milestone monitor (auto-updates)
echo  3. Set new current milestone
echo  4. List all milestones
echo  5. Exit
echo.
echo ===================================================
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto show_status
if "%choice%"=="2" goto start_monitor
if "%choice%"=="3" goto set_milestone
if "%choice%"=="4" goto list_milestones
if "%choice%"=="5" goto end

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto menu

:show_status
cls
echo.
echo Running milestone status check...
echo.
python manage.py show_current_milestone --verbose
echo.
pause
goto menu

:start_monitor
cls
echo.
echo Starting milestone monitor...
echo The monitor will update automatically when milestone changes.
echo Press Ctrl+C to stop monitoring and return to menu.
echo.
python manage.py monitor_milestone
goto menu

:list_milestones
cls
echo.
echo ===================================================
echo            ALL MILESTONES
echo ===================================================
echo.
python manage.py shell -c "from projects.game_models import GameMilestone; print('\n'.join([f'* {m.title} - {\'IN PROGRESS\' if not m.is_completed else \'Completed\'}' for m in GameMilestone.objects.all().order_by('is_completed')]))"
echo.
pause
goto menu

:set_milestone
cls
echo.
echo ===================================================
echo            SET CURRENT MILESTONE
echo ===================================================
echo.
echo Available phases:
echo  1. indie_dev   - Indie Game Development
echo  2. arcade      - Arcade Machine Development
echo  3. theme_park  - Theme Park Development
echo.
echo Available milestones:
python manage.py shell -c "from projects.game_models import GameMilestone; print('\n'.join([f'  - {m.title}' for m in GameMilestone.objects.all()]))"
echo.
echo ===================================================
echo.

set /p milestone="Enter milestone title: "
set /p phase="Enter phase (indie_dev, arcade, theme_park): "

echo.
echo Setting milestone "%milestone%" as current for phase "%phase%"...
python manage.py set_current_milestone --milestone "%milestone%" --phase %phase% --clear-others
echo.
pause
goto menu

:end
cls
echo.
echo Thank you for using R1D3 Milestone Dashboard
echo.
timeout /t 2 >nul
exit
