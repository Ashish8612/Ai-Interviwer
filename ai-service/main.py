import uvicorn
import os
import io
import json
import tempfile
import re
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional
from google import genai
from google.genai import types
import whisper
from pydub import AudioSegment

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=env_path)

AI_SERVICE_PORT = int(os.getenv("AI_SERVICE_PORT", 8000))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-3.5-flash-lite").strip()

# Initialize Gemini Client
gemini_client = None
if GEMINI_API_KEY:
    try:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        print(f"Gemini Client initialized successfully with model: {GEMINI_MODEL_NAME}")
    except Exception as e:
        print(f"Failed to initialize Gemini Client: {e}")
else:
    print("Warning: GEMINI_API_KEY is not set. Add your API key to ai-service/.env")

app = FastAPI(title="AI Interviewer Microservice", version="1.0")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WHISPER_MODEL = None

try:
    print("Loading Whisper Model ...")
    WHISPER_MODEL = whisper.load_model("base.en")
    print("Whisper Model Loaded Successfully")
except Exception as e:
    print("Error while loading Whisper Model:", e)

class QuestionRequest(BaseModel):
    role: str = "MERN Stack Developer"
    level: str = "Junior"
    count: int = 5
    interview_type: str = "coding-mix"

# Alias for backward compatibility
QuestionResquest = QuestionRequest

class QuestionResponse(BaseModel):
    questions: list[str]
    model_used: str

class EvaluationRequest(BaseModel):
    question: str
    question_type: str
    role: str
    level: str
    user_answer: Optional[str] = None
    user_code: Optional[str] = None

class EvaluationResponse(BaseModel):
    technicalScore: int
    confidenceScore: int
    aiFeedback: str
    idealAnswer: str

def get_gemini_client() -> genai.Client:
    global gemini_client
    if gemini_client:
        return gemini_client
    
    # Check again in case env was updated
    key = os.getenv("GEMINI_API_KEY", "").strip() or GEMINI_API_KEY
    if key:
        gemini_client = genai.Client(api_key=key)
        return gemini_client
    
    raise HTTPException(
        status_code=500,
        detail="GEMINI_API_KEY is missing. Please set your GEMINI_API_KEY in ai-service/.env."
    )

@app.get("/")
async def root():
    return {
        "message": "Hello from AI Interviewer Microservice !",
        "provider": "google-gemini",
        "model": GEMINI_MODEL_NAME,
        "gemini_configured": bool(gemini_client or os.getenv("GEMINI_API_KEY", "").strip())
    }

@app.post("/generate-questions", response_model=QuestionResponse)
async def generate_questions(request: QuestionRequest):
    client = get_gemini_client()
    try:
        if request.interview_type == "coding-mix":
            coding_count = int(request.count * 0.2)
            oral_oral = int(request.count) - int(coding_count)

            instruction = (
                f"The first {coding_count} questions MUST be coding challenges requiring function implementation. "
                f"The remaining {oral_oral} questions MUST be conceptual oral questions."
            )
        else:
            instruction = "All questions MUST be conceptual oral questions. Do Not generate any coding or implementation challenges."

        system_prompt = (
            "You are a professional technical interviewer. "
            "Task: Generate interview questions. No conversational text or numbering. "
            f"Crucial: {instruction} "
            "Output exactly one question per line without numbers or bullet points."
        )

        user_prompt = (
            f"Generate exactly {request.count} unique interview questions for a {request.level} level {request.role}."
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.6,
            )
        )
        raw_text = response.text.strip() if response.text else ""
        lines = [re.sub(r'^\d+[\.\)]\s*', '', q.strip()) for q in raw_text.split('\n') if q.strip()]
        questions = [q for q in lines if len(q) > 5][:request.count]
        return QuestionResponse(questions=questions, model_used=f"gemini:{GEMINI_MODEL_NAME}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    temp_audio_path = None
    try:
        audio_bytes = await file.read()
        audio_in_memory = io.BytesIO(audio_bytes)
        audio_segment = AudioSegment.from_file(audio_in_memory)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            temp_audio_path = tmp.name
            audio_segment.export(temp_audio_path, format="mp3")
        if not WHISPER_MODEL:
            raise HTTPException(status_code=503, detail="Whisper Model is not loaded")
        
        result = WHISPER_MODEL.transcribe(temp_audio_path)
                
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        return {"transcription": result["text"].strip()}

    except Exception as e:
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate(request: EvaluationRequest):
    client = get_gemini_client()
    try:
        if request.question_type == "oral":
            assessment_instruction = (
                "This is a conceptual oral question. Focus purely on candidate's verbal explanation. "
                "Ignore any code blocks. "
                "CRITICAL: If the transcript is empty, nonsense (e.g. 'blah blah','testing') or irrelevant to the question, SCORE 0."
            )
        else:
            assessment_instruction = (
                "This is a coding challenge question. Evaluate the code logic and efficiency. "
                "Use the transcription only for insight into their thought process. "
                "CRITICAL: If the code is 'undefined', empty, just random comments, or random characters, SCORE 0."
            )
        
        system_prompt = (
            "You are a strict technical interviewer. "
            "Do NOT hallucinate positive reviews for bad input. "
            "RULE 1: If the answer is gibberish, irrelevant, or missing, return 'technicalScore':0 and 'confidenceScore':0. "
            "RULE 2: For 'idealAnswer', provide a clean Markdown string. Do NOT return a nested JSON object. "
            f"Context: {assessment_instruction}\n"
            "Respond ONLY with a valid JSON object matching the required schema: "
            "{'technicalScore': int 0-100, 'confidenceScore': int 0-100, 'aiFeedback': str, 'idealAnswer': str}"
        )
        user_prompt = (
            f"Role: {request.role}\n"
            f"Question: {request.question}\n"
            f"Level: {request.level}\n"
            f"Verbal Answer: {request.user_answer or 'No verbal answer provided'}\n"
            f"Code Answer: {request.user_code or 'No code provided'}\n"
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                temperature=0.1,
            )
        )
        response_text = response.text.strip() if response.text else "{}"

        try:
            evaluation_data = json.loads(response_text)
            if 'idealAnswer' in evaluation_data and not isinstance(evaluation_data['idealAnswer'], str):
                evaluation_data['idealAnswer'] = json.dumps(evaluation_data['idealAnswer'])
            return EvaluationResponse(**evaluation_data)
        except json.JSONDecodeError:
            fixed_text = re.sub(r'[\r\n\t]', ' ', response_text)
            try:
                evaluation_data = json.loads(fixed_text)
                if 'idealAnswer' in evaluation_data and not isinstance(evaluation_data['idealAnswer'], str):
                    evaluation_data['idealAnswer'] = json.dumps(evaluation_data['idealAnswer'])
                return EvaluationResponse(**evaluation_data)
            except Exception:
                print(f"Failed to parse response: {response_text}")
                return EvaluationResponse(
                    technicalScore=0,
                    confidenceScore=0,
                    aiFeedback="Failed to parse response",
                    idealAnswer="Failed to parse response"
                )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Failed to generate response: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=AI_SERVICE_PORT)