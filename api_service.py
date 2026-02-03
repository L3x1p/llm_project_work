#!/usr/bin/env python3
"""
LLaMA Chat API Service
Runs on localhost:8002
"""

import os
import sys
import uuid
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from llama_cpp import Llama
import json
from langdetect import detect, LangDetectException

# Import model loading from main.py
from main import load_model

SYSTEM_PROMPT_BASE = (
    "You are a helpful assistant. "
    "Answer ONLY the user's latest question. "
    "Do NOT add extra sections like 'Actionable advice', 'User question', or multiple Q&A. "
    "If you need missing info, ask ONE short clarification question."
)

def detect_language(text: str) -> str:
    """Detect the language of the input text"""
    try:
        lang = detect(text)
        return lang
    except LangDetectException:
        return "en"  # Default to English if detection fails

def get_language_instruction(lang: str) -> str:
    """Get instruction to respond in the detected language"""
    language_names = {
        "de": "German",
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "ar": "Arabic",
        "nl": "Dutch",
        "pl": "Polish",
        "tr": "Turkish",
        "sv": "Swedish",
        "da": "Danish",
        "no": "Norwegian",
        "fi": "Finnish",
        "cs": "Czech",
        "hu": "Hungarian",
        "ro": "Romanian",
        "el": "Greek",
        "he": "Hebrew",
        "th": "Thai",
        "vi": "Vietnamese",
        "id": "Indonesian",
        "hi": "Hindi",
    }
    language_name = language_names.get(lang, "the same language")
    if lang == "en":
        return ""  # No extra instruction needed for English
    return f" IMPORTANT: Respond in {language_name}. Use {language_name} for your entire response."

app = FastAPI(
    title="LLaMA Chat API",
    description="Local LLaMA 3.1B Chat API Service",
    version="1.0.0"
)

# Enable CORS for all origins (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance
llm: Optional[Llama] = None

# In-memory session storage (use Redis/DB in production)
sessions: Dict[str, List[Dict[str, str]]] = {}


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 512
    top_p: Optional[float] = 0.9


class ChatResponse(BaseModel):
    response: str
    session_id: str
    tokens_used: Optional[int] = None


class ClearRequest(BaseModel):
    session_id: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    global llm
    model_path = os.getenv("MODEL_PATH", "qwen2.5-3b-instruct-q4_k_m.gguf")
    print(f"Loading model: {model_path}")
    llm = load_model(model_path)
    print("API Service ready on http://localhost:8002")


@app.get("/", tags=["Info"])
async def root():
    """API root endpoint"""
    return {
        "service": "LLaMA Chat API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if llm is not None else "model_not_loaded",
        model_loaded=llm is not None
    )


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Send a chat message and get a response.
    
    - **message**: Your message to the AI
    - **session_id**: Optional session ID for conversation history (auto-generated if not provided)
    - **temperature**: Sampling temperature (0.0-2.0, default: 0.7)
    - **max_tokens**: Maximum tokens in response (default: 512)
    - **top_p**: Nucleus sampling parameter (default: 0.9)
    """
    if llm is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    if session_id not in sessions:
        sessions[session_id] = []
    
    # Detect language and build language-aware prompt
    detected_lang = detect_language(request.message)
    lang_instruction = get_language_instruction(detected_lang)
    system_prompt = SYSTEM_PROMPT_BASE + lang_instruction
    
    # Build prompt with conversation history
    prompt = f"System: {system_prompt}\n\n"
    for msg in sessions[session_id]:
        prompt += f"User: {msg['user']}\nAssistant: {msg['assistant']}\n\n"
    prompt += f"User: {request.message}\nAssistant:"
    
    try:
        # Generate response
        response = llm(
            prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            repeat_penalty=1.1,
            stop=["User:", "System:", "Actionable advice:", "User question:", "\n\n\n"],
            stream=False,
        )
        
        full_response = response['choices'][0]['text'].strip()
        
        # Save to history
        sessions[session_id].append({
            'user': request.message,
            'assistant': full_response
        })
        
        # Limit history to last 5 exchanges
        if len(sessions[session_id]) > 5:
            sessions[session_id] = sessions[session_id][-5:]
        
        return ChatResponse(
            response=full_response,
            session_id=session_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")


@app.post("/chat/stream", tags=["Chat"])
async def chat_stream(request: ChatRequest):
    """
    Send a chat message and get a streaming response.
    
    Returns Server-Sent Events (SSE) stream of tokens.
    """
    if llm is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    if session_id not in sessions:
        sessions[session_id] = []
    
    # Detect language and build language-aware prompt
    detected_lang = detect_language(request.message)
    lang_instruction = get_language_instruction(detected_lang)
    system_prompt = SYSTEM_PROMPT_BASE + lang_instruction
    
    # Build prompt with conversation history
    prompt = f"System: {system_prompt}\n\n"
    for msg in sessions[session_id]:
        prompt += f"User: {msg['user']}\nAssistant: {msg['assistant']}\n\n"
    prompt += f"User: {request.message}\nAssistant:"
    
    def generate():
        full_response = ""
        try:
            response = llm(
                prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                repeat_penalty=1.1,
                stop=["User:", "System:", "Actionable advice:", "User question:", "\n\n\n"],
                stream=True,
            )
            
            for chunk in response:
                text = chunk['choices'][0]['text']
                full_response += text
                yield f"data: {json.dumps({'token': text, 'session_id': session_id})}\n\n"
            
            # Save to history
            sessions[session_id].append({
                'user': request.message,
                'assistant': full_response.strip()
            })
            
            # Limit history
            if len(sessions[session_id]) > 5:
                sessions[session_id] = sessions[session_id][-5:]
            
            # Send completion signal
            yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"
        
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/chat/clear", tags=["Chat"])
async def clear_chat(request: ClearRequest):
    """Clear conversation history for a session"""
    if request.session_id in sessions:
        sessions[request.session_id] = []
        return {"status": "cleared", "session_id": request.session_id}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@app.get("/sessions", tags=["Chat"])
async def list_sessions():
    """List all active sessions"""
    return {
        "sessions": list(sessions.keys()),
        "count": len(sessions)
    }


if __name__ == "__main__":
    import uvicorn
    
    # Get model path from command line or use default
    model_path = sys.argv[1] if len(sys.argv) > 1 else None
    if model_path:
        os.environ["MODEL_PATH"] = model_path
    
    print("Starting LLaMA Chat API Service on http://localhost:8002")
    print("API Documentation available at http://localhost:8002/docs")
    uvicorn.run(app, host="0.0.0.0", port=8002)


