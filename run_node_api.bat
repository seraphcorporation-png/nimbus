@echo off
rem ------------------------------------------------------------
rem Run the vanilla Node.js API server for Carnimbus
rem ------------------------------------------------------------

rem Attempt to locate node in the system PATH
where node >nul 2>&1
if %errorlevel% neq 0 (
    rem Node not in PATH – try a local bundled copy
    set "NODE_EXE=%~dp0node\node.exe"
    if not exist "%NODE_EXE%" (
        echo ERROR: Node.js executable not found. Install Node or add it to PATH.
        exit /b 1
    )
) else (
    set "NODE_EXE=node"
)

rem Launch the API server
"%NODE_EXE%" "%~dp0api\dovc-gateway.js"
