@echo off
title Clara Answers - AI Voice Agent Pipeline Demo
color 0A

echo.
echo  ============================================================
echo     Clara Answers - AI Voice Agent Configuration Pipeline
echo  ============================================================
echo.
echo  This demo will:
echo    1. Install Python dependencies
echo    2. Run the full pipeline on 10 call transcripts
echo    3. Open the web dashboard to view results
echo.
echo  Press any key to start...
pause >nul

echo.
echo  [1/3] Installing dependencies...
echo  -----------------------------------------------
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo  ERROR: pip install failed. Make sure Python 3.10+ is installed.
    echo  Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo  Done.

echo.
echo  [2/3] Running the full pipeline (10 transcripts)...
echo  -----------------------------------------------
cd /d "%~dp0scripts"
python pipeline.py --mode all --clean
if errorlevel 1 (
    echo.
    echo  ERROR: Pipeline failed. Check the output above for details.
    pause
    exit /b 1
)

echo.
echo  [3/3] Starting the web dashboard...
echo  -----------------------------------------------
cd /d "%~dp0dashboard"
echo.
echo  Opening http://localhost:5000 in your browser...
start http://localhost:5000
python app.py
