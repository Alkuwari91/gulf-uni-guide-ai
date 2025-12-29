import streamlit as st
import pandas as pd
from pathlib import Path

# ----------------------------
# Config (NO ICONS)
# ----------------------------
st.set_page_config(page_title="Gulf Uni Guide AI", layout="wide")
# ===== UI THEME (HEADER + STYLE) — UI ONLY =====
st.markdown("""
<style>
/* Page background */
.stApp{
  background: linear-gradient(180deg, #0B1220 0%, #0F1B33 45%, #0B1220 100%);
  color: #E5E7EB;
}

/* Reduce top padding */
.block-container{ padding-top: 1.2rem; }

/* Header */
.bawsala-header{
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 18px;
  padding: 18px 18px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 12px;
  backdrop-filter: blur(10px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

.brand-wrap{
  display:flex;
  align-items:center;
  gap: 12px;
  min-width: 260px;
}
.brand-icon{
  width: 44px; height: 44px;
  border-radius: 14px;
  background: radial-gradient(circle at 30% 30%, rgba(56,189,248,0.9), rgba(56,189,248,0.25) 55%, rgba(255,255,255,0.08) 70%);
  border: 1px solid rgba(255,255,255,0.12);
  display:flex; align-items:center; justify-content:center;
  font-size: 20px;
}
.brand-title{
  margin:0;
  font-size: 1.4rem;
  font-weight: 800;
  letter-spacing: .3px;
  color: #F9FAFB;
}
.brand-tag{
  margin:0;
  font-size: 0.95rem;
  color: rgba(229,231,235,0.85);
}
.brand-tag b{ color: #38BDF8; font-weight: 700; }

/* Header actions (buttons) */
.header-actions{
  display:flex;
  align-items:center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content:flex-end;
}

.hbtn{
  border-radius: 12px;
  padding: 10px 14px;
  font-weight: 700;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.07);
  color: #F9FAFB;
}
.hbtn-primary{
  border: 1px solid rgba(56,189,248,0.35);
  background: rgba(56,189,248,0.16);
  color: #EAF7FF;
}
.hbtn:hover{
  filter: brightness(1.07);
  transform: translateY(-1px);
  transition: 0.15s ease;
}

/* Make Streamlit buttons in header look like our buttons */
div[data-testid="stHorizontalBlock"] button{
  border-radius: 12px !important;
  padding: 10px 14px !important;
  font-weight: 700 !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  background: rgba(255,255,255,0.07) !important;
  color: #F9FAFB !important;
}
div[data-testid="stHorizontalBlock"] button[kind="primary"]{
  border: 1px solid rgba(56,189,248,0.35) !important;
  background: rgba(56,189,248,0.16) !important;
  color: #EAF7FF !important;
}

/* Section titles */
h1,h2,h3{ color:#F9FAFB; }
h2,h3{ color:#EAF7FF; }

/* Inputs */
div[data-baseweb="select"] > div,
input[type="text"]{
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  color:#F9FAFB !important;
  border-radius: 14px !important;
}

/* Dataframes */
[data-testid="stDataFrame"]{
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 16px;
  padding: 10px;
}

/* Divider */
hr{
  border:none;
  height:1px;
  background: linear-gradient(90deg, transparent, rgba(56,189,248,0.8), transparent);
  margin: 1.6rem 0;
}
</style>
""", unsafe_allow_html=True)

# ===== HEADER (UI ONLY) =====
left, right = st.columns([3.2, 1.2])
with left:
    st.markdown("""
    <div class="bawsala-header">
      <div class="brand-wrap">
        <div class="brand-icon">🧭</div>
        <div>
          <p class="brand-title">بوصلة</p>
          <p class="brand-tag">دليلك الذكي لاختيار <b>الجامعة</b> والبرنامج في دول الخليج</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

with right:
    # أزرار UI فقط (لاحقًا نربطها بتسجيل دخول حقيقي إذا تبين)
    a1, a2 = st.columns(2)
    with a1:
        st.button("تسجيل الدخول", key="login_btn")
    with a2:
        st.button("حساب جديد", key="signup_btn")

st.write("")  # مسافة بسيطة تحت الهيدر


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
UNIS_PATH = DATA_DIR / "universities.csv"
PROGS_PATH = DATA_DIR / "programs.csv"

# ----------------------------
# Loaders (ROBUST)
# ----------------------------
@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    if (not path.exists()) or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(
        path,
        encoding="utf-8",
        engine="python",      # مهم لتجاوز السطور المكسّرة
        on_bad_lines="skip",  # يتجاوز السطور اللي تكسر الأعمدة بدل ما يطيّح التطبيق
    )

def normalize_unis(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize universities columns to expected names without changing UI."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    # إذا ملفك جاي بصيغة 12 عمود: extra_1/extra_2
    current_cols_12 = [
        "uni_id","name_ar","name_en","country","city","type",
        "website","admissions_url","programs_url","ranking_source",
        "extra_1","extra_2"
    ]

    # إذا ما فيه هيدر مضبوط وعدد الأعمدة 12 → نسميها ثم نعمل mapping
    if len(df.columns) == 12 and not set(["ranking_value","accreditation_notes"]).issubset(set(df.columns)):
        df.columns = current_cols_12
        df["ranking_value"] = df.get("extra_1", "")
        df["accreditation_notes"] = df.get("extra_2", "")

    # تأكدي الأعمدة الأساسية موجودة (حتى لو ناقصة نعبّيها فاضي)
    needed = [
        "uni_id","name_ar","name_en","country","city","type",
        "website","admissions_url","programs_url",
        "ranking_source","ranking_value","accreditation_notes"
    ]
    for c in needed:
        if c not in df.columns:
            df[c] = ""

    return df[needed]

def normalize_progs(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.copy()
    # نضمن وجود الأعمدة اللي واجهتك تستخدمها
    needed = [
        "program_id","uni_id","level","degree_type","major_field",
        "program_name_en","program_name_ar","city","language",
        "duration_years","tuition_notes","admissions_requirements","url"
    ]
    for c in needed:
        if c not in df.columns:
            df[c] = ""
    return df

unis = normalize_unis(load_csv(UNIS_PATH))
progs = normalize_progs(load_csv(PROGS_PATH))

st.title("Gulf Uni Guide AI")
st.caption("Data source: universities.csv + programs.csv")

if unis.empty:
    st.error(f"universities.csv not found or empty: {UNIS_PATH}")
    st.stop()

if progs.empty:
    st.warning(f"programs.csv not found or empty: {PROGS_PATH}")

# ----------------------------
# Normalize basics (safe)
# ----------------------------
unis = unis.copy()
for c in ["country", "type", "city", "name_en", "name_ar"]:
    unis[c] = unis[c].fillna("").astype(str)

progs = progs.copy()
if not progs.empty:
    for c in ["uni_id", "level", "degree_type", "major_field", "program_name_en", "program_name_ar", "city", "language"]:
        if c in progs.columns:
            progs[c] = progs[c].fillna("").astype(str)

# Join programs with university info (country/type/uni names)
if (not progs.empty) and ("uni_id" in progs.columns) and ("uni_id" in unis.columns):
    progs_joined = progs.merge(
        unis[["uni_id", "name_en", "name_ar", "country", "type", "city", "website", "admissions_url", "programs_url"]],
        on="uni_id",
        how="left",
        suffixes=("", "_uni")
    )
else:
    progs_joined = progs

# ----------------------------
# Single unified filters (NO DUPLICATION)
# ----------------------------
st.subheader("Filters")

col1, col2, col3, col4 = st.columns([1.2, 1, 1, 1.2])

countries = sorted([c for c in unis["country"].unique() if str(c).strip()])
country = col1.selectbox("Country", options=["All"] + countries, index=0)

uni_types = sorted([t for t in unis["type"].unique() if str(t).strip()])
uni_type = col2.selectbox("University type", options=["All"] + uni_types, index=0)

levels = []
if not progs.empty and "level" in progs.columns:
    levels = sorted([x for x in progs["level"].unique() if str(x).strip()])
level = col3.selectbox("Level", options=["All"] + levels, index=0)

majors = []
if not progs.empty and "major_field" in progs.columns:
    majors = sorted([m for m in progs["major_field"].unique() if str(m).strip()])
major = col4.selectbox("Major field", options=["All"] + majors, index=0)

q = st.text_input("Search (university / program / city)", value="").strip().lower()

# ----------------------------
# Apply filters
# ----------------------------
unis_f = unis.copy()
if country != "All":
    unis_f = unis_f[unis_f["country"] == country]
if uni_type != "All":
    unis_f = unis_f[unis_f["type"] == uni_type]
if q:
    mask_u = (
        unis_f["name_en"].str.lower().str.contains(q, na=False)
        | unis_f["name_ar"].str.lower().str.contains(q, na=False)
        | unis_f["city"].str.lower().str.contains(q, na=False)
    )
    unis_f = unis_f[mask_u]

progs_f = progs_joined.copy()
if not progs_f.empty:
    if country != "All" and "country" in progs_f.columns:
        progs_f = progs_f[progs_f["country"] == country]
    if uni_type != "All" and "type" in progs_f.columns:
        progs_f = progs_f[progs_f["type"] == uni_type]
    if level != "All" and "level" in progs_f.columns:
        progs_f = progs_f[progs_f["level"] == level]
    if major != "All" and "major_field" in progs_f.columns:
        progs_f = progs_f[progs_f["major_field"] == major]
    if q:
        mask_p = (
            progs_f.get("program_name_en", "").str.lower().str.contains(q, na=False)
            | progs_f.get("program_name_ar", "").str.lower().str.contains(q, na=False)
            | progs_f.get("name_en", "").str.lower().str.contains(q, na=False)
            | progs_f.get("name_ar", "").str.lower().str.contains(q, na=False)
            | progs_f.get("city", "").astype(str).str.lower().str.contains(q, na=False)
        )
        progs_f = progs_f[mask_p]

# ----------------------------
# Results (clean, only once)
# ----------------------------
st.divider()
left, right = st.columns([1, 1])

with left:
    st.subheader("Universities")
    cols_unis = [
        "uni_id", "name_ar", "name_en", "country", "city", "type",
        "website", "admissions_url", "programs_url",
        "ranking_source", "ranking_value", "accreditation_notes"
    ]
    st.dataframe(unis_f[cols_unis], use_container_width=True, hide_index=True)

with right:
    st.subheader("Programs")
    if progs_f.empty:
        st.info("No programs match the filters (or programs.csv is empty).")
    else:
        cols_prog = [
            "program_id", "uni_id", "name_en", "country", "type",
            "level", "degree_type", "major_field",
            "program_name_en", "program_name_ar",
            "city", "language", "duration_years",
            "tuition_notes", "admissions_requirements", "url"
        ]
        cols_prog = [c for c in cols_prog if c in progs_f.columns]
        st.dataframe(progs_f[cols_prog], use_container_width=True, hide_index=True)
