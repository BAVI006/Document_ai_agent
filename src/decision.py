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