@echo off
echo Running Django command: %*
cd mainProject
python manage.py %*
echo Command completed
pause
