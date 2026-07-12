from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import tempfile
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma3:4b"

class ImageRequest(BaseModel):
    image_base64: str
    question: str

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/answer-image")
def answer_image(req: ImageRequest):
    image_bytes = base64.b64decode(req.image_base64)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
        f.write(image_bytes)
        image_path = f.name

    with open(image_path, "rb") as f:
        img = base64.b64encode(f.read()).decode()

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": req.question,
                "images": [img]
            }
        ],
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    answer = response.json()["message"]["content"].strip()

    return {"answer": answer}
