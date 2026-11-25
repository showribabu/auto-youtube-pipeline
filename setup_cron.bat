@echo off
REM Auto YouTube Pipeline — Windows Task Scheduler Setup
REM Creates permanent daily scheduled tasks to generate and publish videos automatically.

set PYTHON=C:\Users\kanta\AppData\Local\Programs\Python\Python313\python.exe
set PIPELINE=D:\PROJECT\Coding\auto-youtube-pipeline\scripts\pipeline.py

echo Registering Automated YouTube Daily Pipeline Tasks...

REM Daily full run across all categories and languages
schtasks /create /tn "AutoYouTube_DailyRun" /tr "\"%PYTHON%\" \"%PIPELINE%\" --run-all" /sc daily /st 06:00 /rl highest /f

REM Background daemon scheduler on startup/logon
schtasks /create /tn "AutoYouTube_Scheduler" /tr "\"%PYTHON%\" \"%PIPELINE%\" --scheduler" /sc onlogon /rl highest /f

echo.
echo ========================================================
echo Auto YouTube Pipeline scheduled successfully!
echo - Daily Run: Every day at 06:00 AM (all categories & languages)
echo - Background Daemon: Runs continuously on logon
echo ========================================================
