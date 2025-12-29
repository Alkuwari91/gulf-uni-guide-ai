import streamlit as st
import pandas as pd
from pathlib import Path

# ----------------------------
# Page config (no icons/emojis)
# ----------------------------
st.set_page_config(page_title="Gulf Uni Guide AI", layout="wide")

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

UNIS_PATH = DATA_DIR / "universities.csv"
PROGRAMS_PATH = DATA_DIR / "programs.csv"          # optional later
SAMPLE_PATH = DATA_DIR / "sample_programs.csv"     # fallback

GCC_COUNTRIES_ORDER = [
    "Qatar",
    "Saudi Arabia",
    "UAE",
    "Kuwait",
    "Bahrain",
    "Oman",
]

# ----------------------------
# Load data safely
# ----------------------------
def load_universities():
    if UNIS_PATH.exists():
        df = pd.read_csv(UNIS_PATH)
        source = str(UNIS_PATH)
        return df, source

    # fallback to sample_programs.csv if universities.csv not ready
    if SAMPLE_PATH.exists():
        df = pd.read_csv(SAMPLE_PATH)
        source = str(SAMPLE_PATH)
        return df, source

    return None, None

df, source_path = load_universities()

st.title("Gulf Uni Guide AI")

if df is None:
    st.error("No data file found in /data. Add universities.csv (recommended) or sample_programs.csv.")
    st.stop()

st.caption(f"Data source: {source_path}")

# ----------------------------
# Normalize expected columns
# ----------------------------
# We expect universities.csv to have at least these columns:
# uni_id, name_ar, name_en, country, city, type, website
expected_cols = ["uni_id", "name_ar", "name_en", "country", "city", "type", "website"]
for col in expected_cols:
    if col not in df.columns:
        df[col] = ""

# Clean strings
for c in ["name_ar", "name_en", "country", "city", "type", "website"]:
    df[c] = df[c].astype(str).fillna("").str.strip()

# ----------------------------
# Filters UI
# ----------------------------
col1, col2 = st.columns([2, 3], gap="large")

with col1:
    st.subheader("Student profile")
    target_country = st.selectbox(
        "Where do you want to study?",
        options=["All"] + GCC_COUNTRIES_ORDER,
        index=0,
    )
    intended_major = st.text_input("Intended major (example: Engineering, Medicine)", value="")
    study_city = st.text_input("Preferred city (optional)", value="")
    uni_type = st.selectbox("University type", options=["All", "Public", "Private"], index=0)

with col2:
    st.subheader("Browse universities")
    search = st.text_input("Search (university / city)", value="")

# ----------------------------
# Apply filters
# ----------------------------
filtered = df.copy()

# ensure GCC list even if data missing
# (filter uses data, dropdown shows all anyway)

if target_country != "All":
    filtered = filtered[filtered["country"].str.lower() == target_country.lower()]

if uni_type != "All":
    filtered = filtered[filtered["type"].str.lower() == uni_type.lower()]

if study_city.strip():
    filtered = filtered[filtered["city"].str.lower().str.contains(study_city.lower(), na=False)]

if search.strip():
    s = search.lower()
    filtered = filtered[
        filtered["name_en"].str.lower().str.contains(s, na=False)
        | filtered["name_ar"].str.lower().str.contains(s, na=False)
        | filtered["city"].str.lower().str.contains(s, na=False)
    ]

st.divider()

st.subheader("Universities")
st.dataframe(
    filtered[["uni_id", "name_ar", "name_en", "country", "city", "type", "website"]],
    use_container_width=True,
    hide_index=True
)

st.divider()

# ----------------------------
# Simple AI-style matching placeholder (no icons)
# ----------------------------
st.subheader("Matching (basic)")
if st.button("Get University Matches"):
    # For now: basic sorting by country match + keyword match in program name is future
    # We'll upgrade this to full AI next step.
    st.write("Selected country:", target_country)
    st.write("Intended major:", intended_major if intended_major else "Not provided")
    st.write("Results shown above based on filters. Next step: AI ranking + requirements per university.")
