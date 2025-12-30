import streamlit as st
import pandas as pd
from pathlib import Path

# ----------------------------
# Config (NO ICONS)
# ----------------------------
st.set_page_config(page_title="Gulf Uni Guide AI", layout="wide")
<style>
  :root{
    /* ✅ ألوانك */
    --bg: #F5F7FA;          /* رمادي فاتح للخلفية */
    --card: #FFFFFF;        /* أبيض للكروت */
    --text: #334155;        /* رمادي غامق للنص */
    --navy: #0F1B33;        /* كحلي */
    --navy2:#12264A;        /* كحلي أفتح للـ gradient */
    --sky: #38BDF8;         /* سماوي */
    --sky2:#60A5FA;         /* أزرق فاتح */
    --border:#E5E7EB;       /* حدود */
    --muted:#64748B;        /* نص ثانوي */
  }

  body{
    font-family:'Cairo', sans-serif;
    background-color: var(--bg);
    color: var(--text);
    margin:0;
    direction: rtl;
  }

  /* ===== الهيدر (نفس ستايل الصورة) ===== */
  header{
    background: linear-gradient(135deg, var(--navy2), var(--navy));
    color: white;
    padding: 2.2em 1em;
    position: relative;
    text-align: center;
  }

  .brand-title{
    font-size: 2.7em;
    font-weight: 800;
    letter-spacing: 1px;
    margin: 0;
    color:#fff;
  }

  .brand-slogan{
    font-size: 1.1em;
    margin-top: 0.4em;
    color: rgba(255,255,255,0.85);
  }

  /* أزرار الهيدر فوق يمين */
  .header-buttons{
    position:absolute;
    right: 20px;
    top: 20px;
    display:flex;
    gap: .6em;
  }

  .small-btn{
    padding: .45em 1em;
    font-size: .85em;
    border-radius: 10px;
    font-weight: 800;
    text-decoration:none;
    border: 1px solid rgba(255,255,255,0.18);
    backdrop-filter: blur(6px);
  }

  /* زر أبيض */
  .white-btn{
    background:#ffffff;
    color: var(--navy) !important;
    border: 1px solid #ffffff;
  }

  /* زر سماوي */
  .maroon-btn{
    background: linear-gradient(135deg, var(--sky), var(--sky2));
    color:#ffffff !important;
    border: none;
  }
  .maroon-btn:hover{ filter: brightness(0.95); }

  /* ===== شريط التنقل ===== */
  nav ul{
    display:flex;
    justify-content:center;
    list-style:none;
    background: var(--navy);
    padding: 1em;
    margin:0;
    flex-wrap:wrap;
    gap: .3em;
  }

  nav ul li{ margin: .4em .9em; }

  nav ul li a{
    color: rgba(255,255,255,0.92);
    text-decoration:none;
    font-weight: 800;
    padding: .35em .6em;
    border-radius: 10px;
  }

  nav ul li a:hover{
    background: rgba(56,189,248,0.16);
    color:#ffffff;
  }

  /* ===== المحتوى ===== */
  main{
    max-width: 1100px;
    margin:auto;
    padding: 2em 1em 3em;
  }

  h1{
    color: var(--navy);
    text-align:center;
    margin-top:0;
  }

  .intro{
    text-align:center;
    margin-bottom:2em;
    line-height:1.8;
    color: var(--muted);
  }

  .card, .toggle-box, .tab-card, .owner{
    background: var(--card);
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(15,27,51,0.08);
    border: 1px solid var(--border);
  }

  .card{ padding:1.5em; box-sizing:border-box; }
  .card h2{ margin-top:0; color: var(--navy); font-size: 1.3em; }

  input[type="text"], textarea, select{
    width:100%;
    padding:.6em .8em;
    border-radius:10px;
    border:1px solid #CBD5E1;
    font-family:'Cairo', sans-serif;
    font-size:.95em;
    box-sizing:border-box;
    margin-bottom:.9em;
    background:#FFFFFF;
  }

  button{
    background: linear-gradient(135deg, var(--sky), var(--sky2));
    color:#fff;
    border:none;
    padding:.65em 1.6em;
    border-radius:10px;
    cursor:pointer;
    font-size:.95em;
    font-weight: 800;
  }
  button:hover{ filter: brightness(0.95); }

  .btn-secondary{
    background:#E2E8F0;
    color: var(--navy);
    border:1px solid #CBD5E1;
  }

  /* الرؤية والرسالة */
  .toggle-box{
    padding:1.5em;
    width:100%;
    max-width:500px;
    cursor:pointer;
    transition:.25s;
    text-align:center;
  }

  .toggle-box h2{
    color: var(--navy);
    margin:0;
    font-size: 1.6em;
  }

  .toggle-box:hover{
    background: rgba(56,189,248,0.08);
    border-color: rgba(56,189,248,0.35);
  }

  .toggle-content{
    margin-top:1em;
    line-height:1.8;
    color: var(--text);
  }

  /* بطاقات الأقسام */
  .tabs-grid{
    display:flex;
    flex-wrap:wrap;
    justify-content:center;
    gap: 1.5em;
  }

  .tab-card{
    padding: 1.5em;
    transition: transform .25s, box-shadow .25s;
    text-align:center;
    width:220px;
    text-decoration:none;
    color: inherit;
  }

  .tab-card:hover{
    transform: translateY(-8px);
    box-shadow: 0 12px 26px rgba(15,27,51,0.14);
    border-color: rgba(56,189,248,0.35);
  }

  .tab-card img{ width:60px; margin-bottom:.7em; }

  .tab-card h3{
    color: var(--navy);
    margin:.5em 0;
    font-size: 1.05em;
  }

  footer{
    background: var(--navy);
    color:white;
    text-align:center;
    padding: 1.5em;
    margin-top: 3em;
  }
</style>

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

st.markdown("""
<div class="bawsala-header">
  <div class="bawsala-inner">
    <div class="brand-wrap">
      <div>
        <p class="brand-title">بوصلة</p>
        <p class="brand-tag">دليلك الذكي لاختيار الجامعة والبرنامج في دول الخليج</p>
      </div>
      <div class="brand-icon">🧭</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# أزرار (واجهة فقط) تحت الهيدر بشكل مرتب
a, b, c = st.columns([6, 1, 1])
with b:
    st.button("تسجيل الدخول", key="login_btn")
with c:
    st.button("حساب جديد", key="signup_btn")

st.write("")

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
