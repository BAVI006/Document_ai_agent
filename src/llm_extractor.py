import os
import json
from dotenv import load_dotenv
from google import genai
from schema import Invoice

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        import streamlit as st
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

if not api_key:
    raise ValueError("GEMINI_API_KEY is not configured.")

client = genai.Client(api_key=api_key)


def extract_with_llm(text):
    prompt = f"""
You are an invoice extraction assistant.

Extract the following information from the invoice:

- invoice_number
- invoice_date
- vendor
- total_amount

Return ONLY valid JSON in this exact format:

{{
    "invoice_number": "...",
    "invoice_date": "...",
    "vendor": "...",
    "total_amount": 0
}}

Invoice text:
{text}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    data = json.loads(response.text)

    invoice = Invoice(**data)

    return invoice


if __name__ == "__main__":

    # Read the actual invoice PDF
    from document_reader import extract_text_from_pdf

    pdf_path = "data/sample_invoice.pdf"

    text = extract_text_from_pdf(pdf_path)

    print("----- PDF TEXT -----")
    print(text)

    # Send the PDF text to Gemini
    result = extract_with_llm(text)

    print("\n----- GEMINI INVOICE EXTRACTION -----")
    print(result)
