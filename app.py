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
