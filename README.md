# 🧠 AI Interviewer

A full-stack application that simulates real-world technical interviews. Practice answering conceptual and coding questions verbally or programmatically and receive instant AI-driven feedback on your performance.

---

## ✨ Features

- **Customizable Interviews** — Choose your Role, Difficulty Level, and Interview Type (Oral or Coding Mix)
- **Voice Responses** — OpenAI Whisper transcribes verbal answers in real time
- **Code Editor** — Monaco Editor for solving coding challenges directly in the browser
- **AI Question Generation** — Google Gemini dynamically generates unique interview questions
- **Smart Evaluation** — Scores both code logic and verbal answers with a Technical Score & Confidence Score
- **Session Analytics** — View history, per-question breakdowns, and performance charts
- **Secure Auth** — JWT-based login, registration, and Google Sign-In

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React (Vite), Redux Toolkit, Tailwind CSS, React Router |
| **Backend** | Node.js, Express.js, MongoDB (Mongoose), JWT |
| **AI Service** | Python, FastAPI, Google Gemini API, OpenAI Whisper, PyDub |
| **Editor** | Monaco Editor (`@monaco-editor/react`) |
| **Charts** | Chart.js / React-Chartjs-2 |

---

## ⚙️ Prerequisites

- [Node.js](https://nodejs.org/) v18+
- [Python](https://python.org/) v3.9+
- [FFmpeg](https://ffmpeg.org/) (in system PATH — required for audio processing)
- [MongoDB Atlas](https://www.mongodb.com/atlas) account or local MongoDB instance
- [Google Gemini API Key](https://aistudio.google.com/app/apikey) (free)
- [Google OAuth Client ID](https://console.cloud.google.com/apis/credentials) (for Google Sign-In)

---

## 🚀 Getting Started

### First Time Setup (Windows)

Just double-click **`for-first-time.bat`** — it installs all dependencies automatically.

Then on every subsequent run, double-click **`start-all.bat`** to launch all three services.

---

### Manual Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-interviewer.git
cd ai-interviewer
```

#### 2. Backend (`/backend`)

```bash
cd backend
npm install
```

Create `backend/.env`:

```env
PORT=5000
MONGO_URI=mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/ai-interviewer
JWT_SECRET=your_jwt_secret
NODE_ENV=development
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

```bash
npm run dev
```

#### 3. AI Service (`/ai-service`)

```bash
cd ai-service
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

Create `ai-service/.env`:

```env
AI_SERVICE_PORT=8000
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL_NAME=gemini-2.5-flash
```

```bash
python main.py
```

#### 4. Frontend (`/frontend`)

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:5000/api
VITE_AI_SERVICE_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your_google_client_id
```

```bash
npm run dev
```

---

## 🌐 Service URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:5000 |
| AI Microservice | http://localhost:8000 |

---

## 📐 Architecture

```
Browser (React)
    │
    ├──► Node.js API (port 5000)
    │         │
    │         ├──► MongoDB (auth, sessions, history)
    │         └──► Python AI Service (port 8000)
    │                   │
    │                   ├──► Google Gemini (question generation & evaluation)
    │                   └──► OpenAI Whisper (speech-to-text transcription)
    │
    └──► Python AI Service (port 8000) [direct calls for transcription]
```

---

## 🤝 Contributing

1. Fork the project
2. Create your feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License.