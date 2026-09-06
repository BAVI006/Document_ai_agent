from document_reader import extract_text_from_pdf
from llm_extractor import extract_with_llm
from validator import validate_invoice
from decision import make_decision


def main():

    # 1. Read the invoice PDF
    pdf_path = "data/sample_invoice_3500.pdf"

    text = extract_text_from_pdf(pdf_path)

    print("----- PDF READ SUCCESSFULLY -----")

    # 2. Extract invoice information using Gemini
    invoice_data = extract_with_llm(text)

    print("\n----- GEMINI EXTRACTION -----")
    print(invoice_data)

    # 3. Validate the extracted information
    validation_result = validate_invoice(invoice_data)

    print("\n----- VALIDATION -----")
    print(validation_result)

    # 4. Make the business decision
    decision = make_decision(invoice_data, validation_result)

    print("\n----- FINAL DECISION -----")
    print(decision)


if __name__ == "__main__":
    main()