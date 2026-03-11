@echo off
echo ========================================
echo  Push to NEW GitHub Repository
echo ========================================
echo.
echo Step 1: Create a new repository on GitHub
echo   - Go to: https://github.com/new
echo   - Name: mitadt-mess-api
echo   - Make it PUBLIC
echo   - DO NOT add README or .gitignore
echo   - Click "Create repository"
echo.
pause
echo.
echo Step 2: Pushing code...
git remote remove origin
git remote add origin https://github.com/AniketBhudke/mitadt-mess-api.git
git push -u origin main
echo.
echo ========================================
echo  Done! Your code is on GitHub
echo ========================================
echo.
echo Next: Deploy to Render.com
pause
