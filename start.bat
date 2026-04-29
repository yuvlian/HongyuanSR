@echo off

start "gameserver" cmd /k "uv run -m gameserver"
start "sdkserver" cmd /k "uv run -m sdkserver"
start "kcpshimmy" cmd /k "cd /d kcpshimmy && uv run shim.py"

exit
