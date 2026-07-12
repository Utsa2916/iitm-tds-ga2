# Multimodal Image QA API

## Install
pip install -r requirements.txt

## Install Ollama
Download: https://ollama.com/download

Then:

ollama pull gemma3:4b
ollama serve

## Run API

uvicorn app:app --host 0.0.0.0 --port 8000

## Public URL

cloudflared tunnel --url http://localhost:8000

Submit the Cloudflare URL.
