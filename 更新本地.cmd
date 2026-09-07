@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".git" (
  echo 这是 ZIP 资料副本，不包含 Git 历史。请从 GitHub 下载新版，或使用完整 Git 克隆副本。
  pause
  exit /b 1
)
git pull --ff-only
if errorlevel 1 (
  echo 更新未完成，请保留本地修改并查看上方提示。
) else (
  echo 已完成同步。
)
pause
