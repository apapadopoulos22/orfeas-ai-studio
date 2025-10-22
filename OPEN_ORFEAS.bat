@echo off
REM 
REM  ORFEAS AI 2D→3D STUDIO - BROWSER LAUNCHER                                    
REM  THERION AI Project - EREVUS Collective                                       
REM 

echo.
echo   ORFEAS AI 2D→3D STUDIO 
echo.
echo Opening ORFEAS Studio in your default browser...
echo URL: http://localhost:8000/orfeas-studio.html
echo.

REM Open in default browser
start http://localhost:8000/orfeas-studio.html

echo  Browser launched!
echo.
echo  Make sure both services are running:
echo    - Backend: http://localhost:5000
echo    - Frontend: http://localhost:8000
echo.
echo  If services aren't running, use:
echo    - START_ORFEAS_AUTO.bat (starts everything)
echo.
pause
