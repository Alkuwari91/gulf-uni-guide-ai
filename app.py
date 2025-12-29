import streamlit as st
import pandas as pd
from pathlib import Path

# ----------------------------
# Config (MUST BE FIRST)
# ----------------------------
st.set_page_config(page_title="Gulf Uni Guide AI", layout="wide")

# ----------------------------
# Paths
# ----------------------------
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

UNIS_PATH = DATA_DIR / "universities.csv"
PROGS_PATH = DATA_DIR / "programs.csv"

# ----------------------------
# Expected schemas
# ----------------------------
UNIS_COLS = [
    "uni_id",
    "name_ar",
    "name_en",
    "country",
    "city",
    "type",
    "website",
    "admissions_url",
    "programs_url",
    "ranking_source",
    "ranking_value",
    "accreditation_notes",
]

PROGS_COLS = [
    "program_id",
    "uni_id",
    "level",
    "degree_type",
    "major_field",
    "program_name_en",
    "program_name_ar",
    "city",
    "language",
    "duration_years",
    "tuition_notes",
    "admissions_requirements",
    "url",
]

# ----------------------------
# Robust CSV loader
# ----------------------------
@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    if (not path.exists()) or path.stat().st_size == 0:
        raise FileNotFoundError(f"{path.name} not found or empty: {path}")

    # Robust parsing for messy CSV rows
    df = pd.read_csv(
        path,
        encoding="utf-8",
        engine="python",
        on_bad_lines="skip",
    )
    return df


def normalize_universities(df: pd.DataFrame) -> pd.DataFrame:
    """
    Your universities.csv currently has 12 columns, but the app expects UNIS_COLS.
    We map your current format into the expected schema safely.
    """
    # If file has no header and got auto-numbered columns, we still handle it
    # But from your screenshot, you already set them; we do it safely here anyway.

    # Common current file layout (12 cols):
    # uni_id, name_ar, name_en, country, city, type, website,
    # admissions_url, programs_url, ranking_source, extra_1, extra_2
    current_cols_12 = [
        "uni_id",
        "name_ar",
        "name_en",
        "country",
        "city",
        "type",
        "website",
        "admissions_url",
        "programs_url",
        "ranking_source",
        "extra_1",
        "extra_2",
    ]

    # If columns count matches, rename them first
    if len(df.columns) == 12:
        df = df.copy()
        df.columns = current_cols_12

        # Now map into expected columns:
        # ranking_value <- extra_1
        # accreditation_notes <- extra_2
        df["ranking_value"] = df.get("extra_1", "")
        df["accreditation_notes"] = df.get("extra_2", "")

        # Keep only expected columns order
        df = df[
            [
                "uni_id",
                "name_ar",
                "name_en",
                "country",
                "city",
                "type",
                "website",
                "admissions_url",
                "programs_url",
                "ranking_source",
                "ranking_value",
                "accreditation_notes",
            ]
        ]
        return df

    # If already matches expected schema
    if set(UNIS_COLS).issubset(set(df.columns)):
        df = df.copy()
        # Ensure order
        return df[UNIS_COLS]

    # Otherwise: best-effort fill missing columns
    df = df.copy()
    for c in UNIS_COLS:
        if c not in df.columns:
            df[c] = ""
    return df[UNIS_COLS]


def normalize_programs(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure programs has the expected columns; fill missing if needed."""
    df = df.copy()
    for c in PROGS_COLS:
        if c not in df.columns:
            df[c] = ""
    return df[PROGS_COLS]


# ----------------------------
# Load data
# ----------------------------
try:
    unis_raw = load_csv(UNIS_PATH)
    unis = normalize_universities(unis_raw)
except Exception as e:
    st.error(f"❌ Failed to load universities.csv: {e}")
    st.stop()

programs = None
if PROGS_PATH.exists() and PROGS_PATH.stat().st_size > 0:
    try:
        programs_raw = load_csv(PROGS_PATH)
        programs = normalize_programs(programs_raw)
    except Exception as e:
        st.warning(f"⚠️ programs.csv found but failed to load: {e}")
        programs = None

# ----------------------------
# UI
# ----------------------------
st.title("Gulf Uni Guide AI")

with st.expander("✅ Data status", expanded=True):
    st.write("Universities file:", str(UNIS_PATH))
    st.write("Universities rows loaded:", len(unis))
    st.write("Universities columns:", unis.columns.tolist())

    if programs is not None:
        st.write("Programs file:", str(PROGS_PATH))
        st.write("Programs rows loaded:", len(programs))
        st.write("Programs columns:", programs.columns.tolist())
    else:
        st.write("Programs: not loaded (missing/empty or failed).")

st.subheader("Universities preview")
st.dataframe(unis.head(20), use_container_width=True)

# Simple search/filter (optional but useful)
st.subheader("Search")
q = st.text_input("Search by name (Arabic/English) or city/country", "").strip().lower()

filtered = unis
if q:
    def _s(x):
        return "" if pd.isna(x) else str(x).lower()

    mask = (
        unis["name_ar"].map(_s).str.contains(q, na=False)
        | unis["name_en"].map(_s).str.contains(q, na=False)
        | unis["city"].map(_s).str.contains(q, na=False)
        | unis["country"].map(_s).str.contains(q, na=False)
    )
    filtered = unis[mask]

st.write(f"Results: {len(filtered)}")
st.dataframe(filtered, use_container_width=True)
