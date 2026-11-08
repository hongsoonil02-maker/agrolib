@echo off
chcp 65001 > nul
setlocal
echo ======================================================================
echo   [CTO 안그래] 7대 도메인 AI SEO/GEO 실배포 & 멀티채널 마케팅 공장 원클릭 가동
echo ======================================================================
echo.
echo [1/2] 7대 도메인(파보겔·100배거·몬스멕타·로타갈·베타콜·한국아그로·S^&J) SEO/GEO 자동 배포 가동...
python "C:\Users\master\agrolib\reports\seo_automations\weekly_seo_runner.py"
if %ERRORLEVEL% neq 0 (
    echo [WARN] weekly_seo_runner.py exited with code %ERRORLEVEL%
)
echo.
echo [2/2] 파보겔/바이오 멀티채널 마케팅 팩토리(다큐·랭킹·1초펌프 쇼츠 3종 + 8대 채널) 가동...
cd /d "C:\Users\master\parvogel_landing"
python "C:\Users\master\parvogel_landing\marketing_factory\core\marketing_master.py" %*
echo.
echo ======================================================================
echo   [완료] 7대 홈페이지 SEO/GEO 코드 주입 및 멀티채널 마케팅 파이프라인 실행 완료!
echo ======================================================================
if "%1"=="--interactive" pause
endlocal
