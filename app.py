
import re
from pathlib import Path

import pandas as pd
import streamlit as st

# --------------------------------------------------
# AP u-FIR Intelligence
# AI-Enabled Unified First Information Report
# Demonstration prototype - synthetic data only
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
EXCEL_FILE = BASE_DIR / "synthetic_ufir_cases.xlsx"

st.set_page_config(
    page_title="AP u-FIR Intelligence",
    page_icon="🔎",
    layout="wide",
)

# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def load_cases():
    if not EXCEL_FILE.exists():
        return pd.DataFrame()

    try:
        return pd.read_excel(EXCEL_FILE).fillna("")
    except Exception as exc:
        st.error(f"Could not read the Excel dataset: {exc}")
        return pd.DataFrame()


def find_column(df, possible_names):
    """Find a column using case-insensitive name matching."""
    lookup = {str(col).strip().lower(): col for col in df.columns}

    for name in possible_names:
        if name.lower() in lookup:
            return lookup[name.lower()]

    for col in df.columns:
        for name in possible_names:
            if name.lower() in str(col).lower():
                return col

    return None


def extract_field(text, labels):
    """
    Extract a value appearing either:
    Label: value
    or
    Label
    Demonstration value
    actual value
    """
    lines = [line.strip() for line in text.splitlines()]

    skip_values = {
        "",
        "field",
        "demonstration value",
        "value",
    }

    for i, line in enumerate(lines):
        for label in labels:
            pattern = (
                r"^\s*" + re.escape(label)
                + r"\s*(?::|[-–])\s*(.*?)\s*$"
            )

            match = re.match(pattern, line, re.IGNORECASE)

            if match:
                value = match.group(1).strip()

                if value:
                    return value

                # If the label has no value on the same line,
                # inspect the following lines.
                for next_line in lines[i + 1:i + 5]:
                    if next_line.lower() not in skip_values:
                        return next_line

            # Handle a label printed on its own line.
            if line.rstrip(":").strip().lower() == label.lower():
                for next_line in lines[i + 1:i + 5]:
                    if next_line.lower() not in skip_values:
                        return next_line

    return "Not found"


def extract_fir_details(text):
    """Extract basic fields from selectable PDF/TXT text."""

    return {
        "FIR Number": extract_field(
            text,
            ["Demo FIR Number", "FIR Number", "FIR No"],
        ),
        "Registration Date": extract_field(
            text,
            ["Registration Date", "FIR Registration Date"],
        ),
        "Incident Date": extract_field(
            text,
            ["Date of Incident", "Incident date"],
        ),
        "Incident Time": extract_field(
            text,
            ["Approximate time", "Incident Time", "Time of Incident"],
        ),
        "Police Station": extract_field(
            text,
            ["Police Station"],
        ),
        "District": extract_field(
            text,
            ["District"],
        ),
        "Location": extract_field(
            text,
            ["Incident Location", "Location"],
        ),
        "Complainant": extract_field(
            text,
            ["Complainant Name", "Name"],
        ),
        "Vehicle Type": extract_field(
            text,
            ["Vehicle Type", "Vehicle type"],
        ),
        "Vehicle Number": extract_field(
            text,
            ["Registration Number", "Vehicle Number"],
        ),
        "Investigation Status": extract_field(
            text,
            ["Demonstration Investigation Status", "Investigation Status", "Status"],
        ),
    }


# --------------------------------------------------
# Load case dataset
# --------------------------------------------------

df = load_cases()

# --------------------------------------------------
# Sidebar navigation
# --------------------------------------------------

st.sidebar.title("🗂️ u-FIR Modules")

module = st.sidebar.radio(
    "Select Module",
    [
        "Dashboard",
        "Case Search",
        "Case Data",
        "About Prototype",
    ],
)

st.sidebar.caption(
    "AI-Enabled Unified First Information Report (u-FIR)"
)

# --------------------------------------------------
# Main application
# --------------------------------------------------

st.title("🔎 AP u-FIR Intelligence")

st.caption(
    "AI-Enabled Unified First Information Report (u-FIR) "
    "Prototype | Bhashini Hackathon"
)

# --------------------------------------------------
# FIR document upload
# --------------------------------------------------

with st.expander("📄 Upload and Analyze FIR", expanded=True):

    uploaded_fir = st.file_uploader(
        "Upload a sample FIR document",
        type=["pdf", "txt"],
        help="Use fictional or authorized documents only.",
    )

    if uploaded_fir is not None:

        fir_text = ""
        filename = uploaded_fir.name.lower()

        try:
            if filename.endswith(".txt"):
                fir_text = uploaded_fir.getvalue().decode(
                    "utf-8",
                    errors="replace",
                )

            elif filename.endswith(".pdf"):
                try:
                    import pymupdf
                except ImportError:
                    st.error(
                        "PDF reading package is missing. "
                        "Add pymupdf to requirements.txt "
                        "and redeploy."
                    )
                    st.stop()

                pdf_document = pymupdf.open(
                    stream=uploaded_fir.getvalue(),
                    filetype="pdf",
                )

                fir_text = "\n".join(
                    page.get_text() for page in pdf_document
                )

                pdf_document.close()

            st.success(f"Uploaded: {uploaded_fir.name}")

            if not fir_text.strip():
                st.warning(
                    "No selectable text was found. "
                    "This may be a scanned PDF. OCR is not "
                    "included in this version."
                )
            else:
                st.subheader("📃 Extracted FIR Text")

                st.text_area(
                    "Document text",
                    fir_text,
                    height=250,
                    key="fir_extracted_text",
                )

                details = extract_fir_details(fir_text)

                st.subheader("🔍 Automatically Extracted FIR Details")

                st.caption(
                    "Rule-based extraction for demonstration. "
                    "Verify every field against the original document."
                )

                items = list(details.items())

                for start in range(0, len(items), 2):
                    columns = st.columns(2)

                    for offset, (label, value) in enumerate(
                        items[start:start + 2]
                    ):
                        with columns[offset]:
                            st.markdown(f"**{label}**")
                            st.write(value)

                result_df = pd.DataFrame(
                    list(details.items()),
                    columns=["Field", "Extracted Value"],
                )

                st.download_button(
                    "⬇️ Download Extracted Details (CSV)",
                    data=result_df.to_csv(index=False).encode("utf-8"),
                    file_name="extracted_fir_details.csv",
                    mime="text/csv",
                )

        except Exception as exc:
            st.error(f"Could not process the uploaded file: {exc}")


st.divider()

# --------------------------------------------------
# Dashboard module
# --------------------------------------------------

if module == "Dashboard":

    st.header("📊 u-FIR Dashboard")

    if df.empty:
        st.warning(
            "The Excel dataset is missing or empty. "
            "Check synthetic_ufir_cases.xlsx in your GitHub repository."
        )
    else:
        total_cases = len(df)

        person_col = find_column(
            df,
            ["person_name", "person", "accused_name", "suspect_name"],
        )

        district_col = find_column(
            df,
            ["district", "district_name"],
        )

        risk_col = find_column(
            df,
            ["risk_level", "risk", "case_risk"],
        )

        vehicle_col = find_column(
            df,
            ["vehicle_number", "vehicle_no", "registration_number"],
        )

        person_count = (
            df[person_col].astype(str).str.strip().replace("", pd.NA).nunique()
            if person_col else 0
        )

        repeat_count = (
            int(
                df[person_col].astype(str).str.strip()
                .replace("", pd.NA).dropna().duplicated(keep=False).sum()
            )
            if person_col else 0
        )

        high_risk_count = (
            int(
                df[risk_col].astype(str).str.lower()
                .str.contains("high", na=False).sum()
            )
            if risk_col else 0
        )

        metric1, metric2, metric3, metric4 = st.columns(4)

        metric1.metric("Total Cases", total_cases)
        metric2.metric("Persons Identified", person_count)
        metric3.metric("Repeated Person Records", repeat_count)
        metric4.metric("High Risk Labels", high_risk_count)

        st.divider()

        left, right = st.columns(2)

        with left:
            st.subheader("📍 Cases by District")

            if district_col:
                district_counts = (
                    df[district_col].astype(str)
                    .replace("", "Unknown")
                    .value_counts()
                )
                st.bar_chart(district_counts)
            else:
                st.info(
                    "No district column was detected in the dataset."
                )

        with right:
            st.subheader("🚗 Vehicle Records")

            if vehicle_col:
                vehicle_counts = (
                    df[vehicle_col].astype(str)
                    .replace("", "Unknown")
                    .value_counts()
                )
                st.bar_chart(vehicle_counts)
            else:
                st.info(
                    "No vehicle number column was detected in the dataset."
                )

        st.subheader("📋 Recent Case Records")
        st.dataframe(df, use_container_width=True)


# --------------------------------------------------
# Case Search module
# --------------------------------------------------

elif module == "Case Search":

    st.header("🔍 Smart Case Search")

    if df.empty:
        st.warning("No case dataset is available.")
    else:
        query = st.text_input(
            "Search by FIR number, person, vehicle, district, or keyword",
            placeholder="Enter a search term...",
        )

        if query.strip():
            mask = df.astype(str).apply(
                lambda column: column.str.contains(
                    re.escape(query.strip()),
                    case=False,
                    na=False,
                )
            ).any(axis=1)

            results = df[mask]

            st.write(f"Matching records: {len(results)}")
            st.dataframe(results, use_container_width=True)
        else:
            st.info("Enter a search term to find matching cases.")
            st.dataframe(df.head(10), use_container_width=True)


# --------------------------------------------------
# Case Data module
# --------------------------------------------------

elif module == "Case Data":

    st.header("🗃️ Case Data")

    if df.empty:
        st.warning(
            "No data loaded. Check the Excel file in your repository."
        )
    else:
        st.write(f"Records: {len(df)}")
        st.write(f"Columns: {len(df.columns)}")

        st.dataframe(df, use_container_width=True)

        st.download_button(
            "⬇️ Download Current Dataset (CSV)",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="ufir_case_data.csv",
            mime="text/csv",
        )


# --------------------------------------------------
# About module
# --------------------------------------------------

elif module == "About Prototype":

    st.header("ℹ️ About AP u-FIR Intelligence")

    st.markdown(
        """
        **Purpose**

        Demonstrate how unstructured FIR documents and case records
        can be made easier to search and review.

        **Current prototype capabilities**

        - Upload PDF and TXT documents
        - Extract selectable PDF text
        - Apply basic rule-based FIR field extraction
        - Search the synthetic case dataset
        - Display dashboard metrics and charts
        - Export extracted fields as CSV

        **Important limitations**

        - This version does not provide full AI-based understanding.
        - OCR for scanned documents is not included.
        - Repeat-person counts are not verified identity matches.
        - Risk labels are not validated predictions.
        - Extracted details require human verification.
        - Use synthetic demonstration data only.
        """
    )

    st.info(
        "This is a demonstration prototype, not an official police "
        "system or a substitute for legal or investigative decisions."
    )

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "AP u-FIR Intelligence | Hackathon Demonstration Prototype | "
    "Synthetic data only"
)
