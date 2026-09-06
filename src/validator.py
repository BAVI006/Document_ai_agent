from schema import Invoice


def validate_invoice(invoice: Invoice):
    """
    Check whether the extracted invoice data is valid.
    """

    errors = []

    # Check invoice number
    if not invoice.invoice_number:
        errors.append("Invoice number is missing.")

    # Check invoice date
    if not invoice.invoice_date:
        errors.append("Invoice date is missing.")

    # Check vendor
    if not invoice.vendor:
        errors.append("Vendor is missing.")

    # Check total amount
    if invoice.total_amount <= 0:
        errors.append("Total amount must be greater than zero.")

    if errors:
        return {
            "valid": False,
            "errors": errors
        }

    return {
        "valid": True,
        "errors": []
    }