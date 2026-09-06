import re
from document_reader import extract_text_from_pdf


def extract_invoice_data(text):
    """
    Extract basic invoice information from invoice text.
    """

    invoice_data = {
        "invoice_number": None,
        "invoice_date": None,
        "vendor": None,
        "total_amount": None,
    }

    # Invoice number
    invoice_number = re.search(
    r"Invoice\s*(?:Number|No|#)?\s*[:\-]?\s*(INV[-\s]?\d+)",
    text,
    re.IGNORECASE
)

    if invoice_number:
        invoice_data["invoice_number"] = invoice_number.group(1)

    # Invoice date
    invoice_date = re.search(
        r"Invoice\s*Date\s*[:\-]?\s*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4})",
        text,
        re.IGNORECASE
    )

    if invoice_date:
        invoice_data["invoice_date"] = invoice_date.group(1)

    # Vendor
    vendor = re.search(
        r"Vendor\s*[:\-]?\s*(.+)",
        text,
        re.IGNORECASE
    )

    if vendor:
        invoice_data["vendor"] = vendor.group(1).strip()

    # Total amount
    total = re.search(
        r"Total\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
        text,
        re.IGNORECASE
    )

    if total:
        invoice_data["total_amount"] = float(
            total.group(1).replace(",", "")
        )

    return invoice_data


if __name__ == "__main__":

    # Step 1: Read the PDF
    pdf_path = "data/sample_invoice.pdf"

    text = extract_text_from_pdf(pdf_path)

    print("----- PDF TEXT -----")
    print(text)

    # Step 2: Extract structured information
    invoice_data = extract_invoice_data(text)

    print("\n----- EXTRACTED INVOICE DATA -----")
    print(invoice_data)