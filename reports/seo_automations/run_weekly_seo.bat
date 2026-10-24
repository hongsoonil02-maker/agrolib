@echo off
setlocal
cd /d "C:\Users\master\agrolib\reports\seo_automations"
python weekly_seo_runner.py >> "C:\Users\master\agrolib\reports\seo_automations\weekly_seo_runner.log" 2>&1
git -C "C:\Users\master\agrolib" add reports/seo_automations
git -C "C:\Users\master\agrolib" commit -m "auto: weekly seo and geo audit update"
git -C "C:\Users\master\agrolib" push origin main
endlocal
