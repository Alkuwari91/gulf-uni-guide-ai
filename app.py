import os
import json
import streamlit as st
import pandas as pd
from pathlib import Path

# ---------------- Page config ----------------
st.set_page_config(page_title="Gulf Uni Guide AI", layout="wide")

# ---------------- Load data ----------------
BASE = Path(__file__).resolve().parent
DATA_PATH = BASE / "data" / "universities.csv"

st.title("Gulf Uni Guide AI")
st.caption(f"Data source: {DATA_PATH}")

if not DATA_PATH.exists():
    st.error(f"universities.csv not found: {DATA_PATH}")
    st.stop()

df = pd.read_csv(DATA_PATH)

# Normalize a bit
for col in ["country", "city", "type", "name_en", "name_ar"]:
    if col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()

# ---------------- UI layout ----------------
left, right = st.columns([1, 1.4], gap="large")

with left:
    st.subheader("Student profile")

    gcc = ["Qatar", "Saudi Arabia", "UAE", "Kuwait", "Bahrain", "Oman"]
    # Study country options from data (plus All)
    countries = sorted([c for c in df["country"].unique().tolist() if c])
    study_country = st.selectbox("Where do you want to study?", options=countries or gcc, index=0)

    intended_major = st.text_input("Intended major (example: Engineering, Medicine)", value="Medicine")
    preferred_city = st.text_input("Preferred city (optional)", value="")

    uni_type = st.selectbox("University type", options=["All", "Public", "Private"], index=1)

with right:
    st.subheader("Browse universities")
    q = st.text_input("Search (university / city)", value="").strip().lower()

# ---------------- Filtering ----------------
filtered = df.copy()

if study_country:
    filtered = filtered[filtered["country"].str.lower() == study_country.lower()]

if preferred_city.strip():
    filtered = filtered[filtered["city"].str.lower().str.contains(preferred_city.strip().lower(), na=False)]

if uni_type != "All":
    filtered = filtered[filtered["type"].str.lower() == uni_type.lower()]

if q:
    hay = (
        filtered["name_en"].str.lower().fillna("")
        + " "
        + filtered["name_ar"].str.lower().fillna("")
        + " "
        + filtered["city"].str.lower().fillna("")
    )
    filtered = filtered[hay.str.contains(q, na=False)]

st.divider()
st.subheader("Universities")
st.dataframe(
    filtered[["uni_id", "name_ar", "name_en", "country", "city", "type", "website", "admissions_url"]]
    if "admissions_url" in filtered.columns
    else filtered[["uni_id", "name_ar", "name_en", "country", "city", "type", "website"]],
    use_container_width=True,
    hide_index=True
)

# ---------------- Matching + AI ranking ----------------
st.divider()
st.subheader("Matching")

btn = st.button("Get University Matches")

# Read OpenAI key from Streamlit secrets OR env
OPENAI_API_KEY = None
if "OPENAI_API_KEY" in st.secrets:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
else:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def ai_rank_unis(student_country: str, major: str, city: str, uni_type_choice: str, candidates: pd.DataFrame) -> dict:
    """
    Uses OpenAI to rank universities and summarize admissions hints.
    Expects columns: name_en, country, city, type, website, admissions_url (optional)
    """
    # Lazy import (so app still runs if package missing)
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)

    # Keep prompt small: send top N candidates only
    top = candidates.head(30).copy()

    # Prepare a compact list
    items = []
    for _, r in top.iterrows():
        items.append({
            "uni_id": r.get("uni_id", ""),
            "name_en": r.get("name_en", ""),
            "country": r.get("country", ""),
            "city": r.get("city", ""),
            "type": r.get("type", ""),
            "website": r.get("website", ""),
            "admissions_url": r.get("admissions_url", ""),
        })

    system = "You are an expert GCC university admissions counselor. Be accurate, concise, and structured."
    user = {
        "student_profile": {
            "target_country": student_country,
            "intended_major": major,
            "preferred_city": city,
            "university_type": uni_type_choice,
        },
        "universities": items,
        "task": (
            "Rank the best 10 universities for this student within the given country and filters. "
            "For each university: provide a short reason (1-2 lines) and list likely admissions requirements. "
            "If admissions_url exists, prioritize it as the reference to infer requirements. "
            "Return STRICT JSON with keys: ranked (list), notes (string)."
        ),
        "json_schema": {
            "ranked": [
                {
                    "uni_id": "string",
                    "name_en": "string",
                    "city": "string",
                    "type": "string",
                    "why_good_fit": "string",
                    "likely_requirements": ["string", "string"],
                    "links": {"website": "string", "admissions_url": "string"}
                }
            ],
            "notes": "string"
        }
    }

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)}
        ],
        temperature=0.3,
    )

    text = resp.choices[0].message.content.strip()
    # Try parse JSON
    try:
        return json.loads(text)
    except Exception:
        # Fallback
        return {"ranked": [], "notes": "AI output was not valid JSON.", "raw": text}

if btn:
    st.write(f"Selected country: {study_country}")
    st.write(f"Intended major: {intended_major}")

    if filtered.empty:
        st.warning("No universities match your filters yet. Add more rows in data/universities.csv.")
        st.stop()

    if not OPENAI_API_KEY:
        st.warning("OPENAI_API_KEY is missing. Add it in Streamlit Cloud → App settings → Secrets.")
        st.info("For now, showing filtered universities only (no AI ranking).")
        st.stop()

    with st.spinner("Generating AI ranking + requirements..."):
        out = ai_rank_unis(study_country, intended_major, preferred_city, uni_type, filtered)

    ranked = out.get("ranked", [])
    notes = out.get("notes", "")

    st.subheader("AI Ranking (Top 10)")
    if not ranked:
        st.error("AI ranking did not return results.")
        st.code(out.get("raw", ""), language="json")
    else:
        for i, r in enumerate(ranked, 1):
            st.markdown(f"### {i}. {r.get('name_en','')}")
            st.write(r.get("why_good_fit", ""))
            reqs = r.get("likely_requirements", [])
            if reqs:
                st.write("Likely requirements:")
                st.write("\n".join([f"- {x}" for x in reqs]))
            links = r.get("links", {})
            w = links.get("website", "")
            a = links.get("admissions_url", "")
            if w or a:
                st.write("Links:")
                if w: st.write(f"- Website: {w}")
                if a: st.write(f"- Admissions: {a}")

    if notes:
        st.info(notes)
