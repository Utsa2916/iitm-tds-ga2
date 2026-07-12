from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, json
from datetime import datetime
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class InvoiceRequest(BaseModel):
    invoice_text: str

SYSTEM_PROMPT = """
Extract invoice information.
Return ONLY valid JSON with exactly these keys:
invoice_no, date, vendor, amount, tax, currency

Rules:
- date must be YYYY-MM-DD
- amount=subtotal before tax
- tax=tax amount only
- currency should be ISO-like code if obvious (INR, USD, EUR), otherwise null.
- Use null for missing values.
"""

@app.get("/")
def root():
    return {"status":"ok"}

@app.post("/extract")
def extract(req: InvoiceRequest):
    resp = client.responses.create(
        model="gpt-5",
        input=[
            {"role":"system","content":SYSTEM_PROMPT},
            {"role":"user","content":req.invoice_text}
        ]
    )
    text = resp.output_text.strip()
    data = json.loads(text)

    result = {
        "invoice_no": data.get("invoice_no"),
        "date": data.get("date"),
        "vendor": data.get("vendor"),
        "amount": data.get("amount"),
        "tax": data.get("tax"),
        "currency": data.get("currency"),
    }
    return result
