@echo off
REM Auto YouTube Pipeline — Windows Task Scheduler Setup
REM This creates scheduled tasks to run the pipeline automatically.

set SCRIPTS_DIR=D:\PROJECT\Coding\auto-youtube-pipeline\scripts
set PYTHON=D:\PROJECT\Coding\auto-youtube-pipeline\.venv\Scripts\python.exe
set PIPELINE=%SCRIPTS_DIR%\pipeline.py

REM Check if venv exists; create if needed
if not exist "%PYTHON%" (
    echo Creating virtual environment...
    python -m venv %SCRIPTS_DIR%\..\ .venv
    %SCRIPTS_DIR%\..\ .venv\Scripts\pip.exe install -q -r %SCRIPTS_DIR%\..\requirements.txt
)

REM Daily full run at 6:00 AM
schtasks /create /tn "AutoYouTube_DailyRun" /tr "\"%PYTHON%\" \"%PIPELINE%\" --run-all" /sc daily /st 06:00 /f
echo Created: Daily full run at 6:00 AM

REM Kids videos at 8:00 AM
schtasks /create /tn "AutoYouTube_Kids" /tr "\"%PYTHON%\" \"%PIPELINE%\" --category kids" /sc daily /st 08:00 /f
echo Created: Kids videos at 8:00 AM

REM News at 7:00 AM
schtasks /create /tn "AutoYouTube_News" /tr "\"%PYTHON%\" \"%PIPELINE%\" --category news" /sc daily /st 07:00 /f
echo Created: News at 7:00 AM

REM Weather at 6:00 AM
schtasks /create /tn "AutoYouTube_Weather" /tr "\"%PYTHON%\" \"%PIPELINE%\" --category weather" /sc daily /st 06:00 /f
echo Created: Weather at 6:00 AM

REM Facts at 12:00 PM
schtasks /create /tn "AutoYouTube_Facts" /tr "\"%PYTHON%\" \"%PIPELINE%\" --category facts" /sc daily /st 12:00 /f
echo Created: Facts at 12:00 PM

REM Motivational at 6:00 PM
schtasks /create /tn "AutoYouTube_Motivational" /tr "\"%PYTHON%\" \"%PIPELINE%\" --category motivational" /sc daily /st 18:00 /f
echo Created: Motivational at 6:00 PM

REM Also create background scheduler task (runs continuously)
schtasks /create /tn "AutoYouTube_Scheduler" /tr "\"%PYTHON%\" \"%PIPELINE%\" --scheduler" /sc onlogon /rl highest /f
echo Created: Background scheduler (starts on login)

echo.
echo ============================================
echo Setup complete. Tasks are scheduled.
echo To view: schtasks /query /fo LIST /v
echo To remove: schtasks /delete /tn "AutoYouTube_*" /f
echo ============================================
