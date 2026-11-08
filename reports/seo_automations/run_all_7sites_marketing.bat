@echo off
chcp 65001 > nul
setlocal
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

echo ======================================================================
echo   [CTO Antigravity] 7-Site AI SEO/GEO + Marketing Factory Master Runner
echo ======================================================================
echo.
echo [Step 1/2] Running 7-Site SEO/GEO Auto-Deployer + Telegram Briefing...
python "C:\Users\master\agrolib\reports\seo_automations\weekly_seo_runner.py"
if %ERRORLEVEL% neq 0 (
    echo [WARN] weekly_seo_runner.py exited with code %ERRORLEVEL%
)

echo.
echo [Step 2/2] Running Parvogel Multi-Channel Marketing Factory...
cd /d "C:\Users\master\parvogel_landing"
python "C:\Users\master\parvogel_landing\marketing_factory\core\marketing_master.py" %*
if %ERRORLEVEL% neq 0 (
    echo [WARN] marketing_master.py exited with code %ERRORLEVEL%
)

echo.
echo ======================================================================
echo   [DONE] 7-Site SEO/GEO + Multi-Channel Marketing Pipeline Completed!
echo ======================================================================
if "%1"=="--interactive" pause
endlocal
