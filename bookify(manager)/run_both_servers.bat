@echo off
echo Starting both Django and Flask servers...

:: Start Flask API in a new window
start cmd /k "cd trip_planner_api && python app.py"

:: Wait a moment to let Flask start
timeout /t 2 /nobreak > nul

:: Start Django server in this window
cd mainProject
python manage.py runserver

:: This part will only execute when Django server is stopped
echo Both servers have been stopped. 