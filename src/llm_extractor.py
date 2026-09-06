import os
import json
import time

from dotenv import load_dotenv
from google import genai

from schema import Invoice


# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# GET GEMINI API KEY
# --------------------------------------------------

api_key = os.getenv("GEMINI_API_KEY")


# If running on Streamlit Cloud, get key from secrets
if not api_key:
    try:
        import streamlit as st
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass


# Make sure API key exists
if not api_key:
    raise ValueError("GEMINI_API_KEY is not configured.")


# --------------------------------------------------
# CREATE GEMINI CLIENT
# --------------------------------------------------

client = genai.Client(api_key=api_key)


# --------------------------------------------------
# GEMINI INVOICE EXTRACTION
# --------------------------------------------------

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


    # --------------------------------------------------
    # GEMINI API CALL WITH RETRY
    # --------------------------------------------------

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            # If successful, stop retrying
            break

        except Exception as e:

            # Last attempt failed
            if attempt == 2:
                raise e

            print(
                f"Gemini request failed. "
                f"Retrying... ({attempt + 1}/3)"
            )

            # Wait before trying again
            time.sleep(5)


    # --------------------------------------------------
    # CONVERT GEMINI RESPONSE TO JSON
    # --------------------------------------------------

    data = json.loads(response.text)


    # --------------------------------------------------
    # VALIDATE USING PYDANTIC
    # --------------------------------------------------

    invoice = Invoice(**data)


    # --------------------------------------------------
    # RETURN STRUCTURED INVOICE
    # --------------------------------------------------

    return invoice


# --------------------------------------------------
# LOCAL TEST
# --------------------------------------------------

if __name__ == "__main__":

    # Read the actual invoice PDF
    from document_reader import extract_text_from_pdf


    pdf_path = "data/sample_invoice.pdf"


    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)


    print("----- PDF TEXT -----")
    print(text)


    # Send invoice text to Gemini
    result = extract_with_llm(text)


    print("\n----- GEMINI INVOICE EXTRACTION -----")
    print(result)