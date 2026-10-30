@echo off
echo =====================================
echo Starting AI Interviewer Services...
echo =====================================

REM ===============================
REM 1. Start AI Service (Python / FastAPI)
REM ===============================
start cmd /k "cd ai-service && echo Activating Python Virtual Environment... && call venv\Scripts\activate.bat && python main.py"

REM ===============================
REM 2. Start Backend (Node.js / Express)
REM ===============================
start cmd /k "cd backend && echo Starting Express Backend... && npm run dev"

REM ===============================
REM 3. Start Frontend (React / Vite)
REM ===============================
start cmd /k "cd frontend && echo Starting Vite Frontend... && npm run dev"

echo =====================================
echo All services launched 🚀
echo   - Frontend:   http://localhost:5173
echo   - Backend:    http://localhost:5000
echo   - AI Service: http://localhost:8000
echo =====================================
pause
