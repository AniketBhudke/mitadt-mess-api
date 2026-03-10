@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Running migrations...
python manage.py migrate

echo.
echo Starting Django development server...
python manage.py runserver

pause
