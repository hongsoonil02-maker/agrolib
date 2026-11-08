@echo off
chcp 65001 > nul
setlocal
cd /d "C:\Users\master\agrolib\reports\seo_automations"
python weekly_seo_runner.py >> "C:\Users\master\agrolib\reports\seo_automations\weekly_seo_runner.log" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [%DATE% %TIME%] [ERROR] weekly_seo_runner.py failed with exit code %ERRORLEVEL% >> "C:\Users\master\agrolib\reports\seo_automations\weekly_seo_runner.log"
    exit /b %ERRORLEVEL%
)
git -C "C:\Users\master\agrolib" add reports/seo_automations
git -C "C:\Users\master\agrolib" commit -m "auto: weekly seo and geo audit update"
git -C "C:\Users\master\agrolib" push origin main
endlocal
