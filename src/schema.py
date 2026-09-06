from pydantic import BaseModel


class Invoice(BaseModel):
    invoice_number: str
    invoice_date: str
    vendor: str
    total_amount: float


if __name__ == "__main__":

    invoice = Invoice(
        invoice_number="INV-1001",
        invoice_date="09/04/2026",
        vendor="ABC Supplies",
        total_amount=1250.50
    )

    print(invoice)