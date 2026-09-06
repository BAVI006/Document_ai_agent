from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from document_reader import extract_text_from_pdf
from llm_extractor import extract_with_llm
from validator import validate_invoice
from decision import make_decision


# --------------------------------------------------
# LANGGRAPH STATE
# --------------------------------------------------

class InvoiceState(TypedDict):
    pdf_path: str
    text: str
    invoice: object
    validation: dict
    decision: dict


# --------------------------------------------------
# READ DOCUMENT
# --------------------------------------------------

def read_document(state):
    pdf_path = state["pdf_path"]

    text = extract_text_from_pdf(pdf_path)

    print("\n----- READING DOCUMENT -----")
    print(text)

    return {
        "text": text
    }


# --------------------------------------------------
# GEMINI EXTRACTION
# --------------------------------------------------

def extract_invoice(state):
    print("\n----- GEMINI EXTRACTION -----")

    invoice = extract_with_llm(state["text"])

    print(invoice)

    return {
        "invoice": invoice
    }


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

def validate_invoice_node(state):
    print("\n----- VALIDATION -----")

    validation = validate_invoice(state["invoice"])

    print(validation)

    return {
        "validation": validation
    }


# --------------------------------------------------
# BUSINESS DECISION
# --------------------------------------------------

def decision_node(state):
    print("\n----- BUSINESS DECISION -----")

    decision = make_decision(
        state["invoice"],
        state["validation"]
    )

    print(decision)

    return {
        "decision": decision
    }


# --------------------------------------------------
# CONDITIONAL ROUTING
# --------------------------------------------------

def route_decision(state):
    if state["decision"]["decision"] == "APPROVE":
        return "approve"

    return "review"


# --------------------------------------------------
# APPROVAL PATH
# --------------------------------------------------

def approve_node(state):
    print("\n✅ APPROVAL PATH")
    print("Invoice is approved.")

    return state


# --------------------------------------------------
# REVIEW PATH
# --------------------------------------------------

def review_node(state):
    print("\n⚠️ REVIEW PATH")
    print("Invoice requires human review.")

    return state


# --------------------------------------------------
# FINAL RESULT
# --------------------------------------------------

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


# --------------------------------------------------
# BUILD LANGGRAPH
# --------------------------------------------------

builder = StateGraph(InvoiceState)

builder.add_node("read_document", read_document)
builder.add_node("extract_invoice", extract_invoice)
builder.add_node("validate_invoice", validate_invoice_node)
builder.add_node("decision", decision_node)
builder.add_node("approve", approve_node)
builder.add_node("review", review_node)
builder.add_node("final_result", final_result)


# --------------------------------------------------
# WORKFLOW EDGES
# --------------------------------------------------

builder.add_edge(
    START,
    "read_document"
)

builder.add_edge(
    "read_document",
    "extract_invoice"
)

builder.add_edge(
    "extract_invoice",
    "validate_invoice"
)

builder.add_edge(
    "validate_invoice",
    "decision"
)


# --------------------------------------------------
# CONDITIONAL ROUTING
# --------------------------------------------------

builder.add_conditional_edges(
    "decision",
    route_decision,
    {
        "approve": "approve",
        "review": "review"
    }
)


# --------------------------------------------------
# FINAL PATH
# --------------------------------------------------

builder.add_edge(
    "approve",
    "final_result"
)

builder.add_edge(
    "review",
    "final_result"
)

builder.add_edge(
    "final_result",
    END
)


# --------------------------------------------------
# COMPILE GRAPH
# --------------------------------------------------

graph = builder.compile()


# --------------------------------------------------
# TEST LANGGRAPH DIRECTLY
# --------------------------------------------------

if __name__ == "__main__":

    graph.invoke({
        "pdf_path": "data/sample_invoice_3500.pdf",
        "text": "",
        "invoice": None,
        "validation": {},
        "decision": {}
    })