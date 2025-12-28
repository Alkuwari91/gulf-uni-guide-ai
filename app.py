import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gulf Uni Guide AI", layout="wide")

st.title("🎓 Gulf Uni Guide AI")
st.write("AI assistant for GCC high-school students")

# Load data
df = pd.read_csv("data/sample_programs.csv")

# Sidebar inputs
with st.sidebar:
    st.header("Student Profile")
    country = st.selectbox(
        "Where do you want to study?",
        df["country"].unique()
    )
    major = st.text_input("Intended major (e.g. Engineering, CS)")
    submit = st.button("Get Matches")

# Results
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
            [Official website]({row['link']})
            """)
