@echo off
title Agent-Ocean-Project 一键启动脚本

echo -----------------------------------------
echo   启动：基于大语言模型的智能体调度系统
echo -----------------------------------------

:: 切换到当前脚本所在目录
cd /d "%~dp0"

echo [1/4] 进入 backend 目录...
cd backend

echo [2/4] 安装依赖（fastapi、uvicorn 等）...
pip install fastapi uvicorn >nul 2>&1

if %errorlevel% neq 0 (
    echo 依赖安装失败，请检查 Python 和 pip 是否正常安装。
    pause
    exit /b
)

echo [3/4] 启动后端服务（http://localhost:8000）...
start cmd /k uvicorn main:app --reload

timeout /t 2 >nul

echo [4/4] 打开前端界面...
cd ..
cd frontend

:: 如果你喜欢用默认浏览器可自动打开 index.html
start "" "index.html"

echo -----------------------------------------
echo   系统已启动完成！
echo   后端：http://localhost:8000
echo   前端已自动打开
echo -----------------------------------------

pause
