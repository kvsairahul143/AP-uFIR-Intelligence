import streamlit as st
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------
# AP u-FIR INTELLIGENCE - STEP 4
# Excel Data Connected Dashboard
# ---------------------------------------------------------

st.set_page_config(
    page_title="AP u-FIR Intelligence",
    page_icon="🔎",
    layout="wide"
)

# ---------------------------------------------------------
# FILE LOCATION
# ---------------------------------------------------------

EXCEL_FILE = Path("data/excel/synthetic_ufir_cases.xlsx")


# ---------------------------------------------------------
# LOAD EXCEL DATA
# ---------------------------------------------------------

@st.cache_data
def load_data():

    if not EXCEL_FILE.exists():
        return None

    df = pd.read_excel(EXCEL_FILE)

    # Remove completely empty rows
    df = df.dropna(how="all")

    # Convert column names to clean text
    df.columns = [
        str(col).strip().replace("\n", " ")
        for col in df.columns
    ]

    return df


df = load_data()


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("🔎 AP u-FIR Intelligence")
st.caption(
    "AI-Enabled Unified First Information Report "
    "(u-FIR) Prototype | Bhashini Hackathon"
)

st.divider()


# ---------------------------------------------------------
# CHECK EXCEL FILE
# ---------------------------------------------------------

if df is None:

    st.error(
        "Excel file not found."
    )

    st.info(
        "Please keep the Excel file at:\n\n"
        "C:\\AP_uFIR\\data\\excel\\synthetic_ufir_cases.xlsx"
    )

    st.stop()


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title("u-FIR Modules")

page = st.sidebar.radio(
    "Select Module",
    [
        "Dashboard",
        "Case Search",
        "Case Data",
        "About Prototype"
    ]
)


# ---------------------------------------------------------
# HELPER FUNCTION
# ---------------------------------------------------------

def find_column(possible_names):

    for name in possible_names:

        for col in df.columns:

            if str(col).strip().lower() == name.lower():
                return col

    return None


# Try to identify important columns automatically

case_col = find_column([
    "case_id",
    "case no",
    "case number",
    "fir_no",
    "fir number",
    "fir_no."
])

person_col = find_column([
    "person",
    "person_name",
    "accused",
    "accused_name",
    "suspect",
    "suspect_name"
])

district_col = find_column([
    "district",
    "excise district"
])

location_col = find_column([
    "location",
    "place",
    "incident_location"
])

vehicle_col = find_column([
    "vehicle",
    "vehicle_number",
    "vehicle_no",
    "registration_number"
])

risk_col = find_column([
    "risk",
    "risk_level",
    "risk_label"
])


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

if page == "Dashboard":

    st.header("📊 u-FIR Dashboard")

    total_cases = len(df)

    # Count people if person column exists
    if person_col:
        people_count = df[person_col].dropna().nunique()
    else:
        people_count = 0

    # Repeat offenders
    if person_col:
        repeat_count = (
            df[person_col]
            .value_counts()
            .loc[lambda x: x > 1]
            .shape[0]
        )
    else:
        repeat_count = 0

    # High risk
    if risk_col:

        high_risk = df[
            df[risk_col]
            .astype(str)
            .str.lower()
            .str.contains("high")
        ]

        high_risk_count = len(high_risk)

    else:

        high_risk_count = 0


    # KPI CARDS

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Cases",
        total_cases
    )

    col2.metric(
        "Persons Identified",
        people_count
    )

    col3.metric(
        "Repeat Offenders",
        repeat_count
    )

    col4.metric(
        "High Risk Cases",
        high_risk_count
    )


    st.divider()

    # District analysis

    if district_col:

        st.subheader("📍 Cases by District")

        district_counts = (
            df[district_col]
            .fillna("Unknown")
            .value_counts()
        )

        st.bar_chart(district_counts)


    # Risk analysis

    if risk_col:

        st.subheader("⚠️ Risk Distribution")

        risk_counts = (
            df[risk_col]
            .fillna("Unknown")
            .value_counts()
        )

        st.bar_chart(risk_counts)


# ---------------------------------------------------------
# CASE SEARCH
# ---------------------------------------------------------

elif page == "Case Search":

    st.header("🔍 Smart Case Search")

    search_text = st.text_input(
        "Search by Case ID, Person, Vehicle, Location or any available information"
    )

    filtered_df = df.copy()

    if search_text:

        search_text = search_text.lower()

        mask = filtered_df.astype(str).apply(
            lambda column:
            column.str.lower().str.contains(
                search_text,
                na=False
            )
        ).any(axis=1)

        filtered_df = filtered_df[mask]


    st.write(
        f"**{len(filtered_df)} case(s) found**"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )


# ---------------------------------------------------------
# CASE DATA
# ---------------------------------------------------------

elif page == "Case Data":

    st.header("📁 Case Records")

    st.write(
        "Data loaded from the synthetic u-FIR Excel dataset."
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Dataset Information")

    col1, col2 = st.columns(2)

    col1.metric(
        "Rows",
        df.shape[0]
    )

    col2.metric(
        "Columns",
        df.shape[1]
    )

    st.write("### Available Columns")

    for column in df.columns:

        st.write(
            f"• {column}"
        )


# ---------------------------------------------------------
# ABOUT
# ---------------------------------------------------------

elif page == "About Prototype":

    st.header("ℹ️ About AP u-FIR Intelligence")

    st.write("""
    AP u-FIR Intelligence is a prototype developed for the
    AI Living Labs Foundation / Bhashini Hackathon challenge.

    The objective is to convert unstructured case records into
    searchable and useful case intelligence.
    """)

    st.subheader("Current Prototype Features")

    st.write("""
    ✅ Excel case-data integration

    ✅ Case dashboard

    ✅ Smart case search

    ✅ Case records viewer

    ✅ District analytics

    ✅ Risk distribution

    ✅ Repeat-person detection

    """)

    st.warning(
        "This prototype currently uses synthetic/demo data. "
        "No real police or Excise Department records should be "
        "uploaded during development."
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "AP u-FIR Intelligence | Prototype | Synthetic Data Only"
)