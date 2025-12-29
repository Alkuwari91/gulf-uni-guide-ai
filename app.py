import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Gulf Uni Guide AI", layout="wide")

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"

UNIS_PATH = DATA_DIR / "universities.csv"
PROG_PATH = DATA_DIR / "programs.csv"

st.title("Gulf Uni Guide AI")

# ---------- Load universities ----------
if not UNIS_PATH.exists():
    st.error(f"universities.csv not found: {UNIS_PATH}")
    st.stop()

unis = pd.read_csv(UNIS_PATH)

# ---------- Load programs (optional for now) ----------
programs = None
if PROG_PATH.exists():
    programs = pd.read_csv(PROG_PATH)
    st.caption(f"Data source: {UNIS_PATH} + {PROG_PATH}")
else:
    st.caption(f"Data source: {UNIS_PATH} (programs.csv not added yet)")

# ---------- Layout ----------
left, right = st.columns([1, 2], gap="large")

with left:
    st.subheader("Student profile")

    country = st.selectbox(
        "Where do you want to study?",
        sorted(unis["country"].dropna().unique().tolist())
    )

    major = st.text_input("Intended major (example: Engineering, Medicine)")

    preferred_city = st.text_input("Preferred city (optional)")

    uni_type = st.selectbox(
        "University type",
        ["All"] + sorted(unis["type"].dropna().unique().tolist())
    )

    level = None
    if programs is not None:
        level = st.selectbox(
            "Level",
            ["All"] + sorted(programs["level"].dropna().unique().tolist())
        )

with right:
    st.subheader("Browse universities")
    q = st.text_input("Search (university / city)", "")

    filtered_unis = unis.copy()
    filtered_unis = filtered_unis[filtered_unis["country"] == country]

    if uni_type != "All":
        filtered_unis = filtered_unis[filtered_unis["type"] == uni_type]

    if preferred_city.strip():
        filtered_unis = filtered_unis[filtered_unis["city"].astype(str).str.contains(preferred_city, case=False, na=False)]

    if q.strip():
        filtered_unis = filtered_unis[
            filtered_unis["name_en"].astype(str).str.contains(q, case=False, na=False)
            | filtered_unis["name_ar"].astype(str).str.contains(q, case=False, na=False)
            | filtered_unis["city"].astype(str).str.contains(q, case=False, na=False)
        ]

    st.dataframe(filtered_unis, use_container_width=True)

st.divider()

st.subheader("Matching (basic)")
if st.button("Get University Matches"):
    # Basic result: universities filtered above
    st.write(f"Selected country: {country}")
    st.write(f"Intended major: {major if major else '(not provided)'}")

    if programs is None:
        st.info("Next step: add programs.csv to enable level + major-based program matching.")
    else:
        # Program matching
        prog = programs.copy()
        prog = prog[prog["uni_id"].isin(filtered_unis["uni_id"])]

        if level and level != "All":
            prog = prog[prog["level"] == level]

        if major.strip():
            # match against major_field + program names
            m = major.strip()
            prog = prog[
                prog["major_field"].astype(str).str.contains(m, case=False, na=False)
                | prog["program_name_en"].astype(str).str.contains(m, case=False, na=False)
                | prog["program_name_ar"].astype(str).str.contains(m, case=False, na=False)
            ]

        st.subheader("Matched programs")
        st.dataframe(prog, use_container_width=True)
