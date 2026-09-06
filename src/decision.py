from document_reader import extract_text_from_pdf
from extractor import extract_invoice_data
from validator import validate_invoice


def make_decision(invoice_data, validation_result):
    """
    Decide whether an invoice should be APPROVED or sent for REVIEW.
    """

    # If validation failed, send for review
    if not validation_result["valid"]:
        return {
            "decision": "REVIEW",
            "reason": "Invoice data is incomplete or invalid."
        }

    # Business rule: invoices up to $2,000 can be approved
    if invoice_data.total_amount <= 2000:
        return {
            "decision": "APPROVE",
            "reason": "Invoice is valid and total amount is within the approval limit."
        }

    # Anything above $2,000 needs review
    return {
        "decision": "REVIEW",
        "reason": "Invoice amount exceeds the $2,000 approval limit."
    }


if __name__ == "__main__":

    # 1. Read PDF
    pdf_path = "data/sample_invoice.pdf"
    text = extract_text_from_pdf(pdf_path)

    # 2. Extract invoice data
    invoice_data = extract_invoice_data(text)

    # 3. Validate invoice
    validation_result = validate_invoice(invoice_data)

    # 4. Make business decision
    decision = make_decision(invoice_data, validation_result)

    print("----- INVOICE DATA -----")
    print(invoice_data)

    print("\n----- VALIDATION -----")
    print(validation_result)

    print("\n----- FINAL DECISION -----")
    print(decision)