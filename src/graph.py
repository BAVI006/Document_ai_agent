from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from document_reader import extract_text_from_pdf
from llm_extractor import extract_with_llm
from validator import validate_invoice
from decision import make_decision


class InvoiceState(TypedDict):
    text: str
    invoice: object
    validation: dict
    decision: dict


def read_document(state):
    pdf_path = "data/sample_invoice_3500.pdf"

    text = extract_text_from_pdf(pdf_path)

    print("Reading document...")
    print(text)

    return {
        "text": text
    }


def extract_invoice(state):
    print("\nExtracting invoice data with Gemini...")

    invoice = extract_with_llm(state["text"])

    print(invoice)

    return {
        "invoice": invoice
    }


def validate_invoice_node(state):
    print("\nValidating invoice...")

    validation = validate_invoice(state["invoice"])

    print(validation)

    return {
        "validation": validation
    }


def decision_node(state):
    print("\nMaking decision...")

    decision = make_decision(
        state["invoice"],
        state["validation"]
    )

    print(decision)

    return {
        "decision": decision
    }


def route_decision(state):
    """
    Decide which path the workflow should take.
    """

    if state["decision"]["decision"] == "APPROVE":
        return "approve"

    return "review"


def approve_node(state):
    print("\n✅ APPROVAL PATH")
    print("Invoice is approved.")

    return state


def review_node(state):
    print("\n⚠️ REVIEW PATH")
    print("Invoice requires human review.")

    return state


def final_result(state):
    print("\n========== FINAL RESULT ==========")
    print("Invoice Number :", state["invoice"].invoice_number)
    print("Invoice Date   :", state["invoice"].invoice_date)
    print("Vendor         :", state["invoice"].vendor)
    print("Total Amount   :", state["invoice"].total_amount)
    print("Validation     :", state["validation"]["valid"])
    print("Decision       :", state["decision"]["decision"])
    print("Reason         :", state["decision"]["reason"])
    print("==================================")


builder = StateGraph(InvoiceState)

builder.add_node("read_document", read_document)
builder.add_node("extract_invoice", extract_invoice)
builder.add_node("validate_invoice", validate_invoice_node)
builder.add_node("decision", decision_node)
builder.add_node("approve", approve_node)
builder.add_node("review", review_node)
builder.add_node("final_result", final_result)

builder.add_edge(START, "read_document")
builder.add_edge("read_document", "extract_invoice")
builder.add_edge("extract_invoice", "validate_invoice")
builder.add_edge("validate_invoice", "decision")

# Conditional routing
builder.add_conditional_edges(
    "decision",
    route_decision,
    {
        "approve": "approve",
        "review": "review"
    }
)

builder.add_edge("approve", "final_result")
builder.add_edge("review", "final_result")
builder.add_edge("final_result", END)

graph = builder.compile()


if __name__ == "__main__":
    graph.invoke({
        "text": "",
        "invoice": None,
        "validation": {},
        "decision": {}
    })