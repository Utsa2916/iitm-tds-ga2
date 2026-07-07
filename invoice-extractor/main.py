from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import re

app = FastAPI(title="Invoice Extractor")


class InvoiceRequest(BaseModel):
    text: str


class InvoiceResponse(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


def extract_vendor(text: str) -> str:
    patterns = [
        r"(?im)^(?:vendor|supplier|from)\s*:\s*(.+)$",
        r"(?im)^bill\s+from\s*:\s*(.+)$",
        r"(?im)^company\s*:\s*(.+)$",
    ]

    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1).strip()

    # Fallback: first non-empty line
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line

    return ""


def extract_currency(text: str) -> str:
    m = re.search(r"\b(USD|EUR|GBP)\b", text, re.I)
    if m:
        return m.group(1).upper()
    return ""


def extract_amount(text: str) -> float:
    patterns = [
        r"(?i)(?:total\s+due|amount\s+due|grand\s+total|total)\D*([0-9]+(?:\.[0-9]{1,2})?)",
        r"\b(?:USD|EUR|GBP)\s*([0-9]+(?:\.[0-9]{1,2})?)",
        r"([0-9]+(?:\.[0-9]{1,2})?)\s*(?:USD|EUR|GBP)",
    ]

    for p in patterns:
        m = re.search(p, text)
        if m:
            return float(m.group(1))

    nums = re.findall(r"\b[0-9]+(?:\.[0-9]{1,2})?\b", text)
    if nums:
        return float(nums[-1])

    return 0.0


def extract_date(text: str) -> str:
    patterns = [
        r"\b(20\d{2}-\d{2}-\d{2})\b",
        r"(?i)(?:due\s+date|payment\s+due)\D*(20\d{2}-\d{2}-\d{2})",
    ]

    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1)

    return ""


@app.post("/extract", response_model=InvoiceResponse)
def extract(req: InvoiceRequest):
    text = req.text.strip()

    if not text:
        return InvoiceResponse(
            vendor="",
            amount=0.0,
            currency="",
            date=""
        )

    return InvoiceResponse(
        vendor=extract_vendor(text),
        amount=extract_amount(text),
        currency=extract_currency(text),
        date=extract_date(text),
    )