import os
import json

from dotenv import load_dotenv
from google import genai

from schema import Invoice

load_dotenv()


# Get Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

# For Streamlit Cloud
if not api_key:
    try:
        import streamlit as st
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass


if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not configured.")


# Create Gemini client
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

    # Call Gemini
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

    except Exception as e:
        error_message = str(e)

        # Gemini quota error
        if (
            "429" in error_message
            or "RESOURCE_EXHAUSTED" in error_message
            or "quota" in error_message.lower()
        ):
            raise RuntimeError(
                "⚠️ Gemini API quota temporarily unavailable. "
                "Please try again later."
            ) from None

        # Gemini server unavailable
        if (
            "503" in error_message
            or "UNAVAILABLE" in error_message
        ):
            raise RuntimeError(
                "⚠️ Gemini is temporarily unavailable. "
                "Please try again in a few minutes."
            ) from None

        # Other Gemini errors
        raise RuntimeError(
            "⚠️ Gemini API error. Please try again later."
        ) from None


    # Check Gemini response
    if not response.text:
        raise RuntimeError(
            "⚠️ Gemini returned an empty response."
        )


    # Convert Gemini response to JSON
    try:
        data = json.loads(response.text)

    except json.JSONDecodeError:
        raise RuntimeError(
            "⚠️ Gemini returned invalid JSON."
        ) from None


    # Validate using Pydantic
    try:
        invoice = Invoice(**data)

    except Exception:
        raise RuntimeError(
            "⚠️ Invoice data validation failed."
        ) from None


    return invoice


# Local testing
if __name__ == "__main__":

    from document_reader import extract_text_from_pdf

    pdf_path = "data/sample_invoice.pdf"

    text = extract_text_from_pdf(pdf_path)

    print("----- PDF TEXT -----")
    print(text)

    result = extract_with_llm(text)

    print("\n----- GEMINI INVOICE EXTRACTION -----")
    print(result)