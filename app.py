import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Gulf Uni Guide AI", layout="wide")

BASE = Path(__file__).resolve().parent
UNI_PATH = BASE / "data" / "universities.csv"
PROG_PATH = BASE / "data" / "programs.csv"

st.title("Gulf Uni Guide AI")

if not UNI_PATH.exists():
    st.error(f"universities.csv not found: {UNI_PATH}")
    st.stop()

unis = pd.read_csv(UNI_PATH)

st.write("Data loaded successfully.")
st.dataframe(unis, use_container_width=True)

# فلترة بسيطة كبداية
countries = ["All"] + sorted(unis["country"].dropna().unique().tolist())
selected_country = st.selectbox("Study country", countries)

filtered = unis if selected_country == "All" else unis[unis["country"] == selected_country]
st.subheader("Universities")
st.dataframe(filtered, use_container_width=True)
