@echo off
REM DM工具箱 - Windows Docker部署脚本
REM 使用方法: deploy.bat

cd /d %~dp0

echo ========================================
echo [1] 停止旧容器
echo ========================================
docker stop testflask 2>nul
docker rm testflask 2>nul

echo ========================================
echo [2] 构建新镜像
echo ========================================
docker build -t testflask:latest .

echo ========================================
echo [3] 启动新容器
echo ========================================
docker run -d --name testflask -p 8088:8003 testflask:latest

echo ========================================
echo [4] 检查容器状态
echo ========================================
timeout /t 3 /nobreak >nul
docker ps | findstr testflask

echo ========================================
echo 部署完成!
echo 访问地址: http://localhost:8003/dm_gubi/
echo ========================================
pause