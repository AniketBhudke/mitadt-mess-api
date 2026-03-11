@echo off
echo ========================================
echo  Push to GitHub - MIT-MESS Repository
echo ========================================
echo.

set /p username="Enter your GitHub username: "

echo.
echo Connecting to GitHub repository...
git remote remove origin 2>nul
git remote add origin https://github.com/%username%/MIT-MESS.git

echo.
echo Pushing code to GitHub...
git push -u origin main

echo.
echo ========================================
echo  Done! Check your GitHub repository
echo ========================================
pause
