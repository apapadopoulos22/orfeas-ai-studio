@echo off
REM 
REM   THERION PROTOCOL - ORFEAS HTTP SERVER (BATCH LAUNCHER)                 
REM  Double-click to start PWA testing server                                     
REM 

cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "%~dp0START_HTTP_SERVER_SIMPLE.ps1"
pause
