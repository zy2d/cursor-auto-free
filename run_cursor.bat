@echo off
:: 设置控制台代码页为 UTF-8
chcp 65001
:: 设置 Python 环境变量为 UTF-8
set PYTHONIOENCODING=utf-8

echo [%date% %time%] 开始执行脚本 >> log.txt
cd /d "%~dp0"
python cursor_pro_keep_alive.py >> log.txt 2>&1
echo [%date% %time%] 脚本执行完成 >> log.txt
pause