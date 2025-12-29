import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Gulf Uni Guide AI", layout="wide")

BASE = Path(__file__).resolve().parent

# Try both possible data locations
possible_paths = [
    BASE / "data" / "sample_programs.csv",
    BASE / "gulf-uni-guide-ai" / "data" / "sample_programs.csv",
]

DATA_PATH = None
for p in possible_paths:
    if p.exists():
        DATA_PATH = p
        break

if DATA_PATH is None:
    st.error("❌ sample_programs.csv not found in any expected location")
    st.write("Checked paths:")
    for p in possible_paths:
        st.write(p)
    st.stop()

df = pd.read_csv(DATA_PATH)

st.title("🎓 Gulf Uni Guide AI")
st.success(f"Loaded data from: {DATA_PATH}")
# ---------- UI ----------
st.subheader("Student Profile")

with st.sidebar:
    country = st.selectbox(
        "Where do you want to study?",
        sorted(df["country"].unique())
    )
    major = st.text_input("Intended major (e.g. Engineering, CS)")
    submit = st.button("Get University Matches")

if submit:
    st.subheader("Recommended Universities")

    results = df[df["country"] == country]

    if major:
        results = results[
            results["program"].str.contains(major, case=False, na=False)
        ]

    if results.empty:
        st.warning("No matching universities found.")
    else:
        for _, row in results.iterrows():
            st.markdown(f"""
            ### 🏫 {row['university']}
            **Program:** {row['program']}  
            **Language:** {row['language']}  
            **Requirements:** {row['requirements']}  
            🔗 [Official website]({row['link']})
            """)
