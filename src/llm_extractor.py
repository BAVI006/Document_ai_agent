import os
import json
import time

from dotenv import load_dotenv
from google import genai

from schema import Invoice


# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================

load_dotenv()


# ==================================================
# GET GEMINI API KEY
# ==================================================

api_key = os.getenv("GEMINI_API_KEY")


# Streamlit Cloud
if not api_key:
    try:
        import streamlit as st
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass


# Check API key
if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is not configured."
    )


# ==================================================
# CREATE GEMINI CLIENT
# ==================================================

client = genai.Client(
    api_key=api_key
)


# ==================================================
# EXTRACT INVOICE USING GEMINI
# ==================================================

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


    # ==================================================
    # CALL GEMINI
    # ==================================================

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            # Gemini succeeded
            break


        except Exception as e:

            error_message = str(e)


            # ==================================================
            # 429 - QUOTA EXCEEDED
            # ==================================================

            if (
                "429" in error_message
                or "RESOURCE_EXHAUSTED" in error_message
            ):

                raise RuntimeError(
                    "⚠️ Gemini API quota exceeded. "
                    "Please try again later."
                )


            # ==================================================
            # 503 - TEMPORARY GEMINI SERVER ERROR
            # ==================================================

            if (
                "503" in error_message
                or "UNAVAILABLE" in error_message
            ):

                if attempt == 2:

                    raise RuntimeError(
                        "⚠️ Gemini is temporarily unavailable. "
                        "Please try again in a few minutes."
                    )

                # Wait before retry
                time.sleep(5)

                continue


            # ==================================================
            # OTHER GEMINI ERROR
            # ==================================================

            raise RuntimeError(
                f"Gemini API error: {error_message}"
            )


    # ==================================================
    # PARSE GEMINI JSON
    # ==================================================

    try:

        data = json.loads(
            response.text
        )

    except json.JSONDecodeError:

        raise RuntimeError(
            "⚠️ Gemini returned an invalid JSON response."
        )


    # ==================================================
    # PYDANTIC VALIDATION
    # ==================================================

    try:

        invoice = Invoice(
            **data
        )

    except Exception as e:

        raise RuntimeError(
            f"⚠️ Invoice validation failed: {e}"
        )


    # ==================================================
    # RETURN INVOICE
    # ==================================================

    return invoice


# ==================================================
# LOCAL TEST
# ==================================================

if __name__ == "__main__":

    from document_reader import extract_text_from_pdf


    # Invoice PDF
    pdf_path = "data/sample_invoice.pdf"


    # --------------------------------------------------
    # READ PDF
    # --------------------------------------------------

    text = extract_text_from_pdf(
        pdf_path
    )


    print(
        "----- PDF TEXT -----"
    )

    print(text)


    # --------------------------------------------------
    # SEND TO GEMINI
    # --------------------------------------------------

    result = extract_with_llm(
        text
    )


    # --------------------------------------------------
    # DISPLAY RESULT
    # --------------------------------------------------

    print(
        "\n----- GEMINI INVOICE EXTRACTION -----"
    )

    print(result)
    