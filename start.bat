@echo off
echo ========================================
echo Advanced ACO - TSP Solver
echo ========================================
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting Flask server...
echo.
echo Open your browser to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.
python app.py
pause
