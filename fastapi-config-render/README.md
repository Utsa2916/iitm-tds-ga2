# Layered Configuration API (Render)

## Files
- `main.py`: FastAPI service
- `config.development.yaml`: environment-specific YAML layer
- `.env`: local dotenv layer
- `requirements.txt`: dependencies

## Local run
```bash
python -m pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
Try:
`http://127.0.0.1:8000/effective-config?set=port=9000&set=debug=false`

## Render deployment
Create a **Web Service** from this repository:
- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

Set these Render environment variables:
- `APP_PORT=8056`
- `APP_WORKERS=16`
- `APP_LOG_LEVEL=info`
- `APP_API_KEY=key-bv7uuewyoc`
- `APP_ENV=development`

Render's `$PORT` is used only for the web server's listening socket. `APP_PORT` is the application config value returned by `/effective-config`.

After deployment, use the actual URL Render gives you, e.g.:
`https://YOUR-SERVICE-NAME.onrender.com/effective-config`

Example query overrides:
`?set=port=9000&set=debug=true`

The API key is always masked as `****` in responses. Do not put real secrets in a public repository; the supplied keys here are the assignment's example values.
