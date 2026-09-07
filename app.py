import sys
import tempfile
import os

import streamlit as st

# --------------------------------------------------
# ALLOW IMPORTS FROM SRC
# --------------------------------------------------

sys.path.append("src")

from graph import graph


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="InvoiceAI",
    page_icon="📄",
    layout="wide"
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.main {
    padding-top: 2rem;
}

.hero {
    padding: 35px;
    border-radius: 20px;
    background: linear-gradient(135deg, #111827, #1e293b);
    color: white;
    margin-bottom: 30px;
}

.hero h1 {
    font-size: 42px;
    margin-bottom: 5px;
}

.hero p {
    font-size: 18px;
    color: #cbd5e1;
}

.upload-box {
    padding: 25px;
    border-radius: 18px;
    border: 1px solid #334155;
    background-color: #f8fafc;
    margin-bottom: 25px;
}

.result-card {
    padding: 25px;
    border-radius: 18px;
    margin-top: 20px;
}

.approved {
    background-color: #ecfdf5;
    border: 1px solid #10b981;
}

.review {
    background-color: #fff7ed;
    border: 1px solid #f97316;
}

.small-text {
    color: #64748b;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div class="hero">

<h1>📄 InvoiceAI</h1>

<p>
Intelligent invoice processing powered by Gemini AI and LangGraph
</p>

</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("## ⚙️ InvoiceAI")

    st.markdown("""
### How it works

1. 📄 Upload invoice
2. 🤖 Gemini extracts data
3. ✅ Pydantic validates data
4. 🧠 Business rules evaluate invoice
5. 🔀 LangGraph routes decision
6. 📊 Result is displayed

---

**AI Engine:** Gemini  
**Workflow:** LangGraph  
**Validation:** Pydantic  
**Interface:** Streamlit
""")


# --------------------------------------------------
# UPLOAD SECTION
# --------------------------------------------------

st.markdown("## 📤 Upload Invoice")

st.markdown("""
<div class="upload-box">

<b>Upload your invoice PDF</b>

<p class="small-text">
Supported format: PDF
</p>

</div>
""", unsafe_allow_html=True)


uploaded_file = st.file_uploader(
    "Choose an invoice PDF",
    type=["pdf"],
    label_visibility="collapsed"
)


# --------------------------------------------------
# PROCESS INVOICE
# --------------------------------------------------

if uploaded_file is not None:

    st.success(f"Uploaded: {uploaded_file.name}")

    if st.button(
        "🚀 Process Invoice",
        use_container_width=True
    ):

        temp_path = None

        try:

            # ------------------------------------------
            # CREATE TEMPORARY PDF
            # ------------------------------------------

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as temp_file:

                temp_file.write(
                    uploaded_file.getvalue()
                )

                temp_path = temp_file.name


            # ------------------------------------------
            # RUN LANGGRAPH
            # ------------------------------------------

            with st.spinner(
                "🤖 AI is analyzing your invoice..."
            ):

                result = graph.invoke({

                    "pdf_path": temp_path,

                    "text": "",

                    "invoice": None,

                    "validation": {},

                    "decision": {}

                })


            # ------------------------------------------
            # GET RESULTS FROM LANGGRAPH
            # ------------------------------------------

            invoice = result["invoice"]

            validation = result["validation"]

            decision = result["decision"]


            # ------------------------------------------
            # RESULTS
            # ------------------------------------------

            st.markdown("---")

            st.markdown("## 📊 Invoice Analysis")


            # ------------------------------------------
            # INVOICE INFORMATION
            # ------------------------------------------

            col1, col2, col3, col4 = st.columns(4)


            with col1:

                st.metric(
                    "Invoice Number",
                    invoice.invoice_number
                )


            with col2:

                st.metric(
                    "Vendor",
                    invoice.vendor
                )


            with col3:

                st.metric(
                    "Total Amount",
                    f"${invoice.total_amount:,.2f}"
                )


            with col4:

                st.metric(
                    "Invoice Date",
                    invoice.invoice_date
                )


            # ------------------------------------------
            # VALIDATION
            # ------------------------------------------

            st.markdown("### ✅ Validation")


            if validation["valid"]:

                st.success(
                    "Invoice data is valid."
                )

            else:

                st.error(
                    "Invoice data contains errors."
                )

                for error in validation["errors"]:

                    st.write(
                        f"• {error}"
                    )


            # ------------------------------------------
            # DECISION
            # ------------------------------------------

            st.markdown("### 🧠 AI Decision")


            if decision["decision"] == "APPROVE":

                st.markdown("""
                <div class="result-card approved">

                <h2>✅ APPROVED</h2>

                <p>
                This invoice meets the approval criteria.
                </p>

                </div>
                """, unsafe_allow_html=True)


            else:

                st.markdown("""
                <div class="result-card review">

                <h2>⚠️ NEEDS REVIEW</h2>

                <p>
                This invoice requires human review.
                </p>

                </div>
                """, unsafe_allow_html=True)


            st.info(
                f"Reason: {decision['reason']}"
            )


            # ------------------------------------------
            # PROCESSING PIPELINE
            # ------------------------------------------

            st.markdown(
                "### 🔄 Processing Pipeline"
            )


            pipeline_col1, pipeline_col2, pipeline_col3, pipeline_col4 = st.columns(4)


            with pipeline_col1:

                st.success("📄 PDF Read")


            with pipeline_col2:

                st.success("🤖 AI Extraction")


            with pipeline_col3:

                st.success("✅ Validation")


            with pipeline_col4:

                if decision["decision"] == "APPROVE":

                    st.success("✅ Approved")

                else:

                    st.warning("⚠️ Review")


        # ------------------------------------------
        # ERROR HANDLING
        # ------------------------------------------

        except Exception as e:

            message = str(e)

            st.exception(e)  
            if (
                "429" in message
                or "RESOURCE_EXHAUSTED" in message
                or "quota" in message.lower()
            ):

                st.error(
                    "⚠️ Gemini API quota temporarily unavailable. "
                    "Please try again later."
                )


            elif (
                "503" in message
                or "UNAVAILABLE" in message
            ):

                st.error(
                    "⚠️ Gemini is temporarily unavailable. "
                    "Please try again in a few minutes."
                )


            else:

                st.error(
                    "⚠️ Something went wrong while processing "
                    "the invoice."
                )


        # ------------------------------------------
        # DELETE TEMPORARY FILE
        # ------------------------------------------

        finally:

            if (
                temp_path
                and os.path.exists(temp_path)
            ):

                try:

                    os.remove(temp_path)

                except Exception:

                    pass


else:

    st.info(
        "👆 Upload an invoice PDF above to start processing."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")

st.markdown(
    "<p style='text-align:center; color:#64748b;'>"
    "InvoiceAI • Gemini + LangGraph + Pydantic"
    "</p>",
    unsafe_allow_html=True
)