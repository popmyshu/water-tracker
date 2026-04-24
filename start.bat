@echo off
chcp 65001 >nul 2>nul
title 小财神卖水统计 - 服务器

echo ========================================
echo   小财神卖水统计表 - 启动中...
echo ========================================
echo.

:: 启动Python服务器（后台）
echo [1/2] 启动数据服务器...
start /b python "%~dp0server.py"
timeout /t 2 /nobreak >nul

:: 启动Cloudflare隧道
echo [2/2] 启动公网隧道...
echo.
echo   隧道地址会显示在下方，发给帮手就能一起填数据
echo   按 Ctrl+C 可停止服务器
echo.
echo ========================================
"%~dp0cloudflared.exe" tunnel --url http://localhost:8080

echo.
echo 服务器已关闭
pause
