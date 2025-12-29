import streamlit as st
import pandas as pd
from pathlib import Path

# -----------------------------
# Config (no icons)
# -----------------------------
st.set_page_config(page_title="Gulf Uni Guide AI", layout="wide")

st.title("Gulf Uni Guide AI")
st.caption("Data source: universities.csv + programs.csv")

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
UNI_PATH = DATA_DIR / "universities.csv"
PROG_PATH = DATA_DIR / "programs.csv"

# -----------------------------
# Load + validate
# -----------------------------
REQUIRED_UNI_COLS = [
    "uni_id","name_ar","name_en","country","city","type","website",
    "admissions_url","programs_url","ranking_source","ranking_value","accreditation_notes"
]
REQUIRED_PROG_COLS = [
    "program_id","uni_id","level","degree_type","major_field","program_name_en",
    "program_name_ar","city","language","duration_years","tuition_notes",
    "admissions_requirements","url"
]

def load_csv(path: Path, required_cols: list[str], label: str) -> pd.DataFrame:
    if not path.exists():
        st.error(f"{label} not found: {path}")
        st.stop()

    df = pd.read_csv(path)

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        st.error(f"{label} is missing columns: {missing}")
        st.info(f"Current columns: {list(df.columns)}")
        st.stop()

    # Clean
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    for c in df.columns:
        if df[c].dtype == "object":
            df[c] = df[c].astype(str).str.strip().replace({"nan": ""})

    return df

unis = load_csv(UNI_PATH, REQUIRED_UNI_COLS, "universities.csv")
progs = load_csv(PROG_PATH, REQUIRED_PROG_COLS, "programs.csv")

# Normalize a bit
unis["type"] = unis["type"].str.title()
unis["country"] = unis["country"].replace({"KSA":"Saudi Arabia", "U.A.E":"UAE"}).str.strip()
progs["level"] = progs["level"].str.title().str.strip()
progs["major_field"] = progs["major_field"].str.strip()
progs["city"] = progs["city"].str.strip()

st.success("Data loaded successfully.")

# -----------------------------
# Layout
# -----------------------------
left, right = st.columns([1, 2], gap="large")

with left:
    st.subheader("Student profile")

    countries = sorted([c for c in unis["country"].unique() if c])
    country = st.selectbox("Where do you want to study?", countries if countries else [""])

    major = st.text_input("Intended major (example: Engineering, Medicine)", value="")

    pref_city = st.text_input("Preferred city (optional)", value="")

    uni_types = ["All"] + sorted([t for t in unis["type"].unique() if t])
    uni_type = st.selectbox("University type", uni_types, index=0)

    levels = ["All"] + sorted([lv for lv in progs["level"].unique() if lv])
    level = st.selectbox("Study level", levels, index=0)

    degree_types = ["All"] + sorted([d for d in progs["degree_type"].unique() if d])
    degree_type = st.selectbox("Degree type (BSc/BA/MSc/PhD/etc.)", degree_types, index=0)

    st.markdown("---")
    run = st.button("Get University Matches")

with right:
    st.subheader("Browse universities")
    q = st.text_input("Search (university / city)", value="")

    browse = unis.copy()

    # Country filter comes from profile selection
    if country:
        browse = browse[browse["country"].str.lower() == country.lower()]

    if uni_type != "All":
        browse = browse[browse["type"].str.lower() == uni_type.lower()]

    if q.strip():
        qq = q.strip().lower()
        browse = browse[
            browse["name_en"].str.lower().str.contains(qq, na=False) |
            browse["name_ar"].str.lower().str.contains(qq, na=False) |
            browse["city"].str.lower().str.contains(qq, na=False)
        ]

    st.dataframe(
        browse[REQUIRED_UNI_COLS],
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")
st.header("Programs")
st.caption("فلترة التخصصات حسب الدولة/الجامعة/المستوى/الدرجة/المجال")

# Programs filtering panel
f1, f2, f3, f4 = st.columns([1,1,1,1])

with f1:
    prog_country = st.selectbox("Country (programs)", ["All"] + sorted([c for c in unis["country"].unique() if c]))
with f2:
    prog_level = st.selectbox("Level", ["All"] + sorted([lv for lv in progs["level"].unique() if lv]))
with f3:
    prog_degree = st.selectbox("Degree type", ["All"] + sorted([d for d in progs["degree_type"].unique() if d]))
with f4:
    prog_field = st.selectbox("Major field", ["All"] + sorted([m for m in progs["major_field"].unique() if m]))

programs_view = progs.merge(
    unis[["uni_id","name_en","name_ar","country","type","website"]],
    on="uni_id",
    how="left"
).rename(columns={
    "name_en": "uni_name_en",
    "name_ar": "uni_name_ar",
    "website": "uni_website"
})

if prog_country != "All":
    programs_view = programs_view[programs_view["country"].str.lower() == prog_country.lower()]
if prog_level != "All":
    programs_view = programs_view[programs_view["level"].str.lower() == prog_level.lower()]
if prog_degree != "All":
    programs_view = programs_view[programs_view["degree_type"].str.lower() == prog_degree.lower()]
if prog_field != "All":
    programs_view = programs_view[programs_view["major_field"].str.lower() == prog_field.lower()]

st.dataframe(
    programs_view[[
        "program_id","uni_id","uni_name_en","country","type",
        "level","degree_type","major_field",
        "program_name_en","program_name_ar","city","language",
        "duration_years","tuition_notes","admissions_requirements","url"
    ]],
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# Matching (basic, deterministic)
# -----------------------------
st.markdown("---")
st.header("Matching (basic)")

if run:
    matches_uni = unis.copy()

    # apply filters
    if country:
        matches_uni = matches_uni[matches_uni["country"].str.lower() == country.lower()]

    if uni_type != "All":
        matches_uni = matches_uni[matches_uni["type"].str.lower() == uni_type.lower()]

    # join to programs to filter by major/level/degree_type
    merged = matches_uni.merge(progs, on="uni_id", how="left")

    if pref_city.strip():
        cc = pref_city.strip().lower()
        merged = merged[merged["city_y"].astype(str).str.lower().str.contains(cc, na=False) | merged["city_x"].astype(str).str.lower().str.contains(cc, na=False)]

    if level != "All":
        merged = merged[merged["level"].str.lower() == level.lower()]

    if degree_type != "All":
        merged = merged[merged["degree_type"].str.lower() == degree_type.lower()]

    if major.strip():
        mm = major.strip().lower()
        merged = merged[
            merged["major_field"].str.lower().str.contains(mm, na=False) |
            merged["program_name_en"].str.lower().str.contains(mm, na=False) |
            merged["program_name_ar"].str.lower().str.contains(mm, na=False)
        ]

    # show unique universities + a small program sample
    st.subheader("Matched universities")
    uni_cols = REQUIRED_UNI_COLS
    st.dataframe(
        merged[uni_cols].drop_duplicates(),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Matched programs (sample)")
    st.dataframe(
        merged[[
            "uni_id","name_en","country","type",
            "level","degree_type","major_field",
            "program_name_en","program_name_ar","language","duration_years","url"
        ]].head(200),
        use_container_width=True,
        hide_index=True
    )

    st.info("Next step: AI ranking + requirements extraction per university/program (RAG).")
