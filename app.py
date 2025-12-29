import streamlit as st
import pandas as pd
from pathlib import Path

# ----------------------------
# Config (NO ICONS)
# ----------------------------
st.set_page_config(page_title="Gulf Uni Guide AI", layout="wide")

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
UNIS_PATH = DATA_DIR / "universities.csv"
PROGS_PATH = DATA_DIR / "programs.csv"

# ----------------------------
# Loaders
# ----------------------------
@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    # keep_default_na=False helps avoid NaN in text fields (optional)
    return pd.read_csv(path, dtype=str, keep_default_na=False)

def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip spaces + remove BOM from column names."""
    if df is None or df.empty:
        return df
    df = df.copy()
    df.columns = [str(c).replace("\ufeff", "").strip() for c in df.columns]
    return df

unis = clean_columns(load_csv(UNIS_PATH))
progs = clean_columns(load_csv(PROGS_PATH))

st.title("Gulf Uni Guide AI")
st.caption("Data source: universities.csv + programs.csv")

if unis.empty:
    st.error(f"universities.csv not found or empty: {UNIS_PATH}")
    st.stop()

# Validate required columns after cleaning
required_unis_cols = ["uni_id", "country", "type", "city", "name_en", "name_ar"]
missing = [c for c in required_unis_cols if c not in unis.columns]
if missing:
    st.error(
        "universities.csv columns are not as expected.\n\n"
        f"Missing: {missing}\n\n"
        f"Found columns: {list(unis.columns)}"
    )
    st.stop()

if progs.empty:
    st.warning(f"programs.csv not found or empty: {PROGS_PATH}")

# ----------------------------
# Normalize basics (safe)
# ----------------------------
unis = unis.copy()
for c in ["country", "type", "city", "name_en", "name_ar"]:
    if c in unis.columns:
        unis[c] = unis[c].fillna("").astype(str).str.strip()

progs = progs.copy()
if not progs.empty:
    for c in ["uni_id", "level", "degree_type", "major_field", "program_name_en", "program_name_ar", "city", "language"]:
        if c in progs.columns:
            progs[c] = progs[c].fillna("").astype(str).str.strip()

# Join programs with university info (country/type/uni names)
if not progs.empty and "uni_id" in progs.columns and "uni_id" in unis.columns:
    # Only include columns that exist to avoid KeyError if you remove some fields later
    uni_cols = [c for c in ["uni_id","name_en","name_ar","country","type","city","website",
                            "admissions_url","programs_url","ranking_source","ranking_value","accreditation_notes"]
                if c in unis.columns]

    progs_joined = progs.merge(
        unis[uni_cols],
        on="uni_id",
        how="left",
        suffixes=("", "_uni")
    )
else:
    progs_joined = progs

# ----------------------------
# Single unified filters (NO DUPLICATION)
# ----------------------------
st.subheader("Filters")

col1, col2, col3, col4 = st.columns([1.2, 1, 1, 1.2])

countries = sorted([c for c in unis["country"].unique() if str(c).strip()])
country = col1.selectbox("Country", options=["All"] + countries, index=0)

uni_types = sorted([t for t in unis["type"].unique() if str(t).strip()])
uni_type = col2.selectbox("University type", options=["All"] + uni_types, index=0)

levels = []
if not progs.empty and "level" in progs.columns:
    levels = sorted([x for x in progs["level"].unique() if str(x).strip()])
level = col3.selectbox("Level", options=["All"] + levels, index=0)

majors = []
if not progs.empty and "major_field" in progs.columns:
    majors = sorted([m for m in progs["major_field"].unique() if str(m).strip()])
major = col4.selectbox("Major field", options=["All"] + majors, index=0)

q = st.text_input("Search (university / program / city)", value="").strip().lower()

# ----------------------------
# Apply filters
# ----------------------------
unis_f = unis.copy()
if country != "All":
    unis_f = unis_f[unis_f["country"] == country]
if uni_type != "All":
    unis_f = unis_f[unis_f["type"] == uni_type]
if q:
    mask_u = (
        unis_f.get("name_en", "").str.lower().str.contains(q, na=False)
        | unis_f.get("name_ar", "").str.lower().str.contains(q, na=False)
        | unis_f.get("city", "").str.lower().str.contains(q, na=False)
    )
    unis_f = unis_f[mask_u]

progs_f = progs_joined.copy()
if not progs_f.empty:
    if country != "All" and "country" in progs_f.columns:
        progs_f = progs_f[progs_f["country"] == country]
    if uni_type != "All" and "type" in progs_f.columns:
        progs_f = progs_f[progs_f["type"] == uni_type]
    if level != "All" and "level" in progs_f.columns:
        progs_f = progs_f[progs_f["level"] == level]
    if major != "All" and "major_field" in progs_f.columns:
        progs_f = progs_f[progs_f["major_field"] == major]
    if q:
        mask_p = (
            progs_f.get("program_name_en", "").str.lower().str.contains(q, na=False)
            | progs_f.get("program_name_ar", "").str.lower().str.contains(q, na=False)
            | progs_f.get("name_en", "").str.lower().str.contains(q, na=False)
            | progs_f.get("name_ar", "").str.lower().str.contains(q, na=False)
            | progs_f.get("city", "").str.lower().str.contains(q, na=False)
        )
        progs_f = progs_f[mask_p]

# ----------------------------
# Results (clean, only once)
# ----------------------------
st.divider()
left, right = st.columns([1, 1])

with left:
    st.subheader("Universities")
    cols_unis = [
        "uni_id", "name_ar", "name_en", "country", "city", "type",
        "website", "admissions_url", "programs_url",
        "ranking_source", "ranking_value", "accreditation_notes"
    ]
    cols_unis = [c for c in cols_unis if c in unis_f.columns]
    st.dataframe(unis_f[cols_unis], use_container_width=True, hide_index=True)

with right:
    st.subheader("Programs")
    if progs_f.empty:
        st.info("No programs match the filters (or programs.csv is empty).")
    else:
        cols_prog = [
            "program_id", "uni_id", "name_en", "country", "type",
            "level", "degree_type", "major_field",
            "program_name_en", "program_name_ar",
            "city", "language", "duration_years",
            "tuition_notes", "admissions_requirements", "url"
        ]
        cols_prog = [c for c in cols_prog if c in progs_f.columns]
        st.dataframe(progs_f[cols_prog], use_container_width=True, hide_index=True)
