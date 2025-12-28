from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "sample_programs.csv"

if not DATA_PATH.exists():
    st.error(f"Data file not found: {DATA_PATH}")
    st.stop()

df = pd.read_csv(DATA_PATH)
