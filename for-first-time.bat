@echo off
echo =====================================
echo Installing Dependencies & Starting AI Interviewer...
echo =====================================

REM ===============================
REM 1. Start AI Service (Python / FastAPI)
REM ===============================
start cmd /k ^
"cd ai-service ^
&& echo Activating virtual environment... ^
&& call venv\Scripts\activate.bat ^
&& echo Installing Python dependencies... ^
&& pip install -r requirements.txt ^
&& echo Starting AI service... ^
&& python main.py"

REM ===============================
REM 2. Start Backend (Node.js)
REM ===============================
start cmd /k ^
"cd backend ^
&& echo Installing backend dependencies... ^
&& npm install ^
&& echo Starting backend... ^
&& npm run dev"

REM ===============================
REM 3. Start Frontend (Vite / React)
REM ===============================
start cmd /k ^
"cd frontend ^
&& echo Installing frontend dependencies... ^
&& npm install ^
&& echo Starting frontend... ^
&& npm run dev"

echo =====================================
echo All services launched 🚀
echo   - Frontend:   http://localhost:5173
echo   - Backend:    http://localhost:5000
echo   - AI Service: http://localhost:8000
echo =====================================
pause