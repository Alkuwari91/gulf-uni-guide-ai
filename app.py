import streamlit as st
import pandas as pd
from pathlib import Path
from ui import render_shell

# ----------------------------
# Page config (لازم تكون أول شيء)
# ----------------------------
st.set_page_config(page_title="بوصلة", layout="wide", initial_sidebar_state="collapsed")

render_shell()

# ----------------------------
# إخفاء السايدبار نهائياً (حتى المساحة)
# ----------------------------
st.markdown(
    """
    <style>
      [data-testid="stSidebar"] {display: none !important;}
      [data-testid="stSidebarNav"] {display: none !important;}
      button[kind="header"] {display: none !important;} /* زر الهامبرغر */
      section[data-testid="stSidebar"] {display:none !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# CSS: Expander كأنه كارد (مثل راسخون) + RTL + توسيط العناوين + تصغير المنسدلات
# ----------------------------
st.markdown(
    """
    <style>
      /* ============ Expander Card ============ */
      div[data-testid="stExpander"] {
        border: 0 !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 30px rgba(15,27,51,0.06) !important;
        overflow: hidden !important;
        background: white !important;
        margin-bottom: 16px !important;
      }
      div[data-testid="stExpander"] summary {
        padding: 18px 18px !important;
        font-size: 1.25rem !important;
        font-weight: 800 !important;
        cursor: pointer !important;
      }
      div[data-testid="stExpander"] summary:hover {
        background: rgba(56,189,248,0.10) !important;
      }
      div[data-testid="stExpander"] .stMarkdown,
      div[data-testid="stExpander"] .stText {
        padding: 0 18px 18px 18px !important;
        color: #334155 !important;
        line-height: 1.9 !important;
        font-size: 1.05rem !important;
      }

      /* ============ RTL Global ============ */
      html, body, [class*="stApp"]{
        direction: rtl !important;
        text-align: right !important;
      }
      input, textarea, [role="textbox"]{
        direction: rtl !important;
        text-align: right !important;
      }
      div[data-baseweb="select"] *{
        direction: rtl !important;
        text-align: right !important;
      }
      label{
        direction: rtl !important;
        text-align: right !important;
      }

      /* ============ Center titles ============ */
      .page-title{
        text-align: center !important;
        font-weight: 900;
        margin: 10px 0 18px 0;
      }

      /* ============ Smaller dropdowns ============ */
      div[data-baseweb="select"] > div{
        min-height: 38px !important;
      }
      div[data-baseweb="select"] > div > div{
        padding-top: 2px !important;
        padding-bottom: 2px !important;
      }
      div[data-baseweb="select"] span{
        font-size: 0.95rem !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Helpers / Paths
# ----------------------------
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
UNIS_PATH = DATA_DIR / "universities.csv"
PROGS_PATH = DATA_DIR / "programs.csv"


@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    """
    قراءة CSV بشكل مرن:
    - نجرب قراءة بهيدر طبيعي.
    - إذا فشل/طلع أعمدة رقمية فقط أو ملف بدون هيدر -> نقرأ header=None.
    """
    if (not path.exists()) or path.stat().st_size == 0:
        return pd.DataFrame()

    try:
        df = pd.read_csv(path, encoding="utf-8", engine="python", on_bad_lines="skip")
        # إذا الأعمدة كلها أرقام (0,1,2...) غالباً انقرأ كأنه بدون هيدر بشكل غلط
        if all(isinstance(c, int) for c in df.columns):
            df = pd.read_csv(path, encoding="utf-8", engine="python", on_bad_lines="skip", header=None)
        return df
    except Exception:
        # fallback
        return pd.read_csv(path, encoding="utf-8", engine="python", on_bad_lines="skip", header=None)


@st.cache_data(show_spinner=False)
def load_unis_csv(path: Path) -> pd.DataFrame:
    if (not path.exists()) or path.stat().st_size == 0:
        return pd.DataFrame()

    # نقرأ أول سطر عشان نعرف: فيه هيدر ولا لا
    first_line = path.read_text(encoding="utf-8", errors="ignore").splitlines()[0].strip().lower()

    has_header = first_line.startswith("uni_id")  # يعني عندك هيدر فعلي

    if has_header:
        df = pd.read_csv(path, encoding="utf-8", engine="python", on_bad_lines="skip")
    else:
        df = pd.read_csv(path, encoding="utf-8", engine="python", on_bad_lines="skip", header=None)

    return df


def normalize_unis(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    cols_12 = [
        "uni_id", "name_ar", "name_en", "country", "city", "type",
        "website", "admissions_url", "programs_url",
        "ranking_source", "extra_1", "extra_2"
    ]

    cols_15 = cols_12 + ["scholarship", "sch_notes", "sch_url"]

    # ✅ لو الملف انقرأ بدون هيدر (header=None) بيكون أعمدة مرقمة 0..14
    if list(df.columns) == list(range(len(df.columns))):
        if len(df.columns) == 12:
            df.columns = cols_12
        elif len(df.columns) == 15:
            df.columns = cols_15

    # ✅ لو الملف انقرأ بهيدر لكن أول صف كان هيدر بالغلط داخل البيانات
    # (يصير لما يكون الملف بدون هيدر بس pandas اعتبر أول سطر هيدر)
    # نتحقق: إذا أول قيمة في uni_id هي "uni_id" نحذف السطر
    if "uni_id" in df.columns:
        first_val = str(df.iloc[0]["uni_id"]).strip().lower()
        if first_val == "uni_id":
            df = df.iloc[1:].copy()

    # ربط extra_1/extra_2
    if "ranking_value" not in df.columns:
        df["ranking_value"] = df.get("extra_1", "")
    if "accreditation_notes" not in df.columns:
        df["accreditation_notes"] = df.get("extra_2", "")

    # scholarship (عمود واحد)
    if "scholarship" not in df.columns:
        df["scholarship"] = "Unknown"

    df["scholarship"] = (
        df["scholarship"]
        .fillna("Unknown")
        .astype(str)
        .str.replace("  ", " ")
        .str.strip()
        .replace({"": "Unknown", "nan": "Unknown"})
    )

    if "sch_notes" not in df.columns:
        df["sch_notes"] = ""
    if "sch_url" not in df.columns:
        df["sch_url"] = ""

    needed = [
        "uni_id", "name_ar", "name_en", "country", "city", "type",
        "scholarship", "sch_notes", "sch_url",
        "website", "admissions_url", "programs_url",
        "ranking_source", "ranking_value", "accreditation_notes"
    ]

    for c in needed:
        if c not in df.columns:
            df[c] = ""

    return df[needed]


def normalize_progs(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    needed = [
        "program_id", "uni_id", "level", "degree_type", "major_field",
        "program_name_en", "program_name_ar", "city", "language",
        "duration_years", "tuition_notes", "admissions_requirements", "url"
    ]

    # إذا الملف فيه هيدر طبيعي (أسماء الأعمدة)
    if "program_id" in df.columns:
        for c in needed:
            if c not in df.columns:
                df[c] = ""
        return df[needed]

    # إذا بدون هيدر (أعمدة رقمية) — نحاول نسميها لو العدد كافي
    if len(df.columns) >= len(needed):
        df = df.iloc[:, :len(needed)]
        df.columns = needed
        return df

    # fallback: رجّع DataFrame فارغ بنفس الأعمدة
    return pd.DataFrame(columns=needed)


def make_uni_label(row: pd.Series) -> str:
    ar = str(row.get("name_ar", "")).strip()
    en = str(row.get("name_en", "")).strip()
    city = str(row.get("city", "")).strip()
    country = str(row.get("country", "")).strip()
    return f"{ar} — {en} ({city}, {country})"


def get_uni_by_id(unis: pd.DataFrame, uni_id: str) -> pd.DataFrame:
    if unis.empty or not uni_id:
        return pd.DataFrame()
    return unis[unis["uni_id"].astype(str) == str(uni_id)].copy()


def ensure_cols(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """يتأكد إن كل الأعمدة المطلوبة موجودة قبل العرض (يمنع KeyError)."""
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    return df


# ----------------------------
# Navigation (بدون سايدبار) — RTL: الأزرار من اليمين لليسار
# ----------------------------
if "page" not in st.session_state:
    st.session_state.page = "الرئيسية"

nav = ["من نحن", "رُشد", "المقارنة", "بحث الجامعات", "الرئيسية"]
cols_nav = st.columns(len(nav))
for i, name in enumerate(nav):
    # نخلي أول عنصر يطلع أقصى اليمين
    col = cols_nav[-(i + 1)]
    if col.button(name, use_container_width=True):
        st.session_state.page = name
        st.rerun()

st.write("")
st.markdown("---")
st.write("")


# ----------------------------
# Page: الرئيسية
# ----------------------------
if st.session_state.page == "الرئيسية":
    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.expander("رؤيتنا", expanded=True):
            st.write("أن تكون بوصلة المرجع الأول لاتخاذ قرار جامعي واعٍ في دول الخليج عبر معلومات موثوقة وتجربة ذكية.")

    with col2:
        with st.expander("رسالتنا", expanded=False):
            st.write("تمكين الطلاب وأولياء الأمور من مقارنة الخيارات الجامعية والبرامج بسهولة، وتبسيط رحلة الاختيار باستخدام أدوات ذكية.")

    col3, col4 = st.columns(2, gap="large")

    with col3:
        with st.expander("قيمنا", expanded=False):
            st.write("الموثوقية، الشفافية، الحياد، تبسيط المعرفة، واحترام خصوصية المستخدم.")

    with col4:
        with st.expander("لماذا بوصلة؟", expanded=False):
            st.write("لأن قرار الجامعة من أهم القرارات، وبوصلة تجمع البيانات وتعرضها بوضوح وتساعدك على المقارنة واتخاذ القرار.")

    st.write("")
    st.markdown("---")
    b1, b2, b3 = st.columns(3)
    if b1.button("ابدأ البحث", use_container_width=True):
        st.session_state.page = "بحث الجامعات"
        st.rerun()
    if b2.button("قارن الجامعات", use_container_width=True):
        st.session_state.page = "المقارنة"
        st.rerun()
    if b3.button("تحدث مع رُشد", use_container_width=True):
        st.session_state.page = "رُشد"
        st.rerun()


# ----------------------------
# Page: بحث الجامعات
# ----------------------------
elif st.session_state.page == "بحث الجامعات":
    st.markdown('<h1 class="page-title">بحث الجامعات</h1>', unsafe_allow_html=True)

    unis = normalize_unis(load_unis_csv(UNIS_PATH))
    progs = normalize_progs(load_csv(PROGS_PATH))

    if unis.empty:
        st.error(f"universities.csv not found or empty: {UNIS_PATH}")
        st.stop()

    # (اختياري) لو البرامج فاضية ما نوقف البحث
    if progs.empty:
        st.warning(f"programs.csv not found or empty: {PROGS_PATH}")

    # ----------------------------
    # Filters (RTL columns order)
    # ----------------------------
    st.write("")
    # ترتيب الأعمدة يمشي RTL: نخلي أول فلتر (الدولة) في أقصى اليمين
    c4, c3, c2, c1 = st.columns([1.2, 1, 1, 1.2])

    countries = sorted([x for x in unis["country"].unique() if str(x).strip()])
    country = c4.selectbox("الدولة", ["All"] + countries, index=0)

    uni_types = sorted([x for x in unis["type"].unique() if str(x).strip()])
    uni_type = c3.selectbox("نوع الجامعة", ["All"] + uni_types, index=0)

    levels = sorted([x for x in progs["level"].unique() if str(x).strip()]) if not progs.empty else []
    level = c2.selectbox("المرحلة", ["All"] + levels, index=0)

    majors = sorted([x for x in progs["major_field"].unique() if str(x).strip()]) if not progs.empty else []
    major = c1.selectbox("التخصص", ["All"] + majors, index=0)

    st.write("")
    # صف المنح RTL: نخلي (توفر المنحة) يمين و(نوع المنحة) يسار
    right_s, left_s = st.columns([2.8, 1.2])

    yn = left_s.selectbox("توفر المنح", ["All", "Yes", "No", "Unknown"], index=0)
    sch_tags = ["Local", "GCC", "International", "Children of citizen mothers"]
    selected_tags = right_s.multiselect("نوع المنحة", sch_tags, default=[])

    q = st.text_input("بحث (الجامعة / المدينة)", value="").strip().lower()

    # ----------------------------
    # apply filters
    # ----------------------------
    unis_f = unis.copy()

    if country != "All":
        unis_f = unis_f[unis_f["country"] == country]
    if uni_type != "All":
        unis_f = unis_f[unis_f["type"] == uni_type]

    # Scholarship availability derived from scholarship column
    if yn != "All":
        def availability(x: str) -> str:
            x = str(x).strip()
            if x == "No":
                return "No"
            if x == "Unknown" or x == "":
                return "Unknown"
            return "Yes"

        unis_f = unis_f[unis_f["scholarship"].apply(availability) == yn]

    # Tags filter (inside scholarship)
    if selected_tags:
        def has_tags(x: str) -> bool:
            x = str(x).strip()
            if x in ["No", "Unknown", ""]:
                return False
            parts = [p.strip() for p in x.split("|") if p.strip()]
            return all(tag in parts for tag in selected_tags)

        unis_f = unis_f[unis_f["scholarship"].apply(has_tags)]

    if q:
        mask_u = (
            unis_f["name_en"].astype(str).str.lower().str.contains(q, na=False)
            | unis_f["name_ar"].astype(str).str.lower().str.contains(q, na=False)
            | unis_f["city"].astype(str).str.lower().str.contains(q, na=False)
        )
        unis_f = unis_f[mask_u]

    # ----------------------------
    # Results
    # ----------------------------
    st.divider()
    st.markdown('<h2 class="page-title" style="font-size:1.6rem;">الجامعات</h2>', unsafe_allow_html=True)

    cols_show = [
        "uni_id", "name_ar", "name_en", "country", "city", "type",
        "scholarship",
        "website", "admissions_url", "programs_url",
        "ranking_source", "ranking_value"
    ]

    unis_f = ensure_cols(unis_f, cols_show)

    st.dataframe(
        unis_f[cols_show],
        use_container_width=True,
        hide_index=True,
        column_config={
            "website": st.column_config.LinkColumn("Website", display_text="Click here"),
            "admissions_url": st.column_config.LinkColumn("Admissions", display_text="Click here"),
            "programs_url": st.column_config.LinkColumn("Programs", display_text="Click here"),
        }
    )


# ----------------------------
# Page: المقارنة
# ----------------------------
# ----------------------------
# Page: المقارنة
# ----------------------------
elif st.session_state.page == "المقارنة":
    st.markdown('<h1 class="page-title">المقارنة بين الجامعات</h1>', unsafe_allow_html=True)

    # ✅ استخدم نفس قراءة/تطبيع الجامعات بشكل موحّد
    unis = normalize_unis(load_unis_csv(UNIS_PATH))

    if unis.empty:
        st.error(f"universities.csv not found or empty: {UNIS_PATH}")
        st.stop()

    # ✅ نظّف uni_id وخله نص دائماً عشان ما يضيع/يتكرر
    unis = unis.copy()
    unis["uni_id"] = unis["uni_id"].astype(str).str.strip()
    unis = unis[unis["uni_id"].ne("") & unis["uni_id"].ne("nan")]

    # ✅ جهّز label بشكل آمن + خريطة للعرض (أسرع وما فيها errors)
    unis["label"] = unis.apply(make_uni_label, axis=1)
    label_map = dict(zip(unis["uni_id"].tolist(), unis["label"].tolist()))

    # ✅ أحياناً يصير تكرار في uni_id داخل الملف — نخليها فريدة
    unis = unis.drop_duplicates(subset=["uni_id"], keep="first")

    # ترتيب
    unis = unis.sort_values(["country", "city", "name_en"], na_position="last")

    selected_ids = st.multiselect(
        "اختار 2 إلى 4 جامعات للمقارنة",
        options=unis["uni_id"].tolist(),
        format_func=lambda x: label_map.get(str(x), str(x)),
        max_selections=4
    )

    if len(selected_ids) < 2:
        st.info("يرجى اختيار جامعتين على الأقل لتظهر المقارنة.")
        st.stop()

    comp = unis[unis["uni_id"].isin([str(x).strip() for x in selected_ids])].copy()

    cols_compare = [
        "uni_id","name_ar","name_en","country","city","type",
        "scholarship","ranking_source","ranking_value","accreditation_notes",
        "website","admissions_url","programs_url"
    ]
    for c in cols_compare:
        if c not in comp.columns:
            comp[c] = ""

    st.markdown("### جدول المقارنة")
    st.dataframe(
        comp[cols_compare],
        use_container_width=True,
        hide_index=True,
        column_config={
            "website": st.column_config.LinkColumn("Website", display_text="Click here"),
            "admissions_url": st.column_config.LinkColumn("Admissions", display_text="Click here"),
            "programs_url": st.column_config.LinkColumn("Programs", display_text="Click here"),
        }
    )

    st.write("")
    st.markdown("---")
    st.markdown("### مقارنة سريعة (بطاقات)")

    cols = st.columns(len(selected_ids))
    for i, uni_id in enumerate(selected_ids):
        row = comp[comp["uni_id"] == str(uni_id)].iloc[0]
        with cols[i]:
            with st.expander(f"{row['name_ar']} — {row['name_en']}", expanded=True):
                st.write(f"**الموقع:** {row['city']} — {row['country']}")
                st.write(f"**النوع:** {row['type']}")
                st.write(f"**المنح:** {row.get('scholarship','')}")
                st.write(f"**الترتيب:** {str(row.get('ranking_source','')).strip()} {str(row.get('ranking_value','')).strip()}".strip())

                notes = str(row.get("accreditation_notes", "")).strip()
                if notes:
                    st.write(f"**ملاحظات:** {notes}")

                st.write("")
                c1, c2, c3 = st.columns(3)
                if str(row.get("website", "")).strip():
                    c1.link_button("Website", str(row["website"]))
                if str(row.get("admissions_url", "")).strip():
                    c2.link_button("Admissions", str(row["admissions_url"]))
                if str(row.get("programs_url", "")).strip():
                    c3.link_button("Programs", str(row["programs_url"]))


# ----------------------------
# Page: رُشد (Student Advisor - الجزء الأول)
# ----------------------------
st.markdown(
    """
    <div dir="rtl" style="text-align:center; margin-top:0;">
      <h2 style="margin-top:0;">
        رُشد — المرشد الطلابي (قبل القبول)
      </h2>

      <p style="
        font-size:1.05rem;
        line-height:1.9;
        color:#475569;
        max-width:720px;
        margin: 0 auto;
      ">
        حلّل فرص القبول واقترح أفضل الجامعات بناءً على بياناتك،
        مع توضيح المتطلبات المتوقعة ومراكز الاختبار القريبة منك.
      </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# مساعدات: أعمدة متطلبات القبول (اختيارية - لو مو موجودة ما ينكسر)
# ----------------------------
def ensure_program_requirements(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=df.columns if df is not None else [])

    df = df.copy()

    for c in ["english_test", "english_score", "math_requirement", "admission_notes"]:
        if c not in df.columns:
            df[c] = ""

    return df


progs = ensure_program_requirements(progs)

    # ----------------------------
    # قاعدة بيانات بسيطة لمراكز الاختبارات (نبدأ بها ونكبرها لاحقًا)
    # ----------------------------
    TEST_CENTERS = {
        ("Qatar", "Doha"): {
            "IELTS": [
                {"name": "British Council (Doha)", "url": ""},
                {"name": "IDP Education (Doha)", "url": ""},
            ],
            "Placement": [
                {"name": "University Assessment Center", "url": ""},
            ],
        },
        ("Bahrain", "Manama"): {
            "IELTS": [
                {"name": "IELTS test center (Bahrain)", "url": ""},
            ]
        },
        ("Oman", "Muscat"): {
            "IELTS": [
                {"name": "IELTS test center (Muscat)", "url": ""},
            ]
        },
        ("Saudi Arabia", "Riyadh"): {
            "IELTS": [
                {"name": "IELTS test center (Riyadh)", "url": ""},
            ]
        },
        ("UAE", "Abu Dhabi"): {
            "IELTS": [
                {"name": "IELTS test center (Abu Dhabi)", "url": ""},
            ]
        },
        ("Kuwait", "Kuwait City"): {
            "IELTS": [
                {"name": "IELTS test center (Kuwait)", "url": ""},
            ]
        },
    }

    # ----------------------------
    # نموذج ملف الطالب (Student Snapshot)
    # ----------------------------
    with st.expander("ملف الطالب", expanded=True):
        c1, c2, c3 = st.columns(3)
        countries = sorted([x for x in unis["country"].unique() if str(x).strip()])
        pref_country = c1.selectbox("الدولة المفضلة", ["All"] + countries, index=0)

        # المدن تتغير حسب الدولة (لو All نخلي كل المدن)
        if pref_country != "All":
            cities = sorted([x for x in unis.loc[unis["country"] == pref_country, "city"].unique() if str(x).strip()])
        else:
            cities = sorted([x for x in unis["city"].unique() if str(x).strip()])

        pref_city = c2.selectbox("المدينة (اختياري)", ["All"] + cities, index=0)

        level_options = []
        if not progs.empty and "level" in progs.columns:
            level_options = sorted([x for x in progs["level"].unique() if str(x).strip()])
        study_level = c3.selectbox("المستوى الدراسي المطلوب", ["All"] + level_options, index=0)

        d1, d2, d3 = st.columns(3)
        major_field_options = []
        if not progs.empty and "major_field" in progs.columns:
            major_field_options = sorted([x for x in progs["major_field"].unique() if str(x).strip()])
        major_field = d1.selectbox("مجال التخصص", ["All"] + major_field_options, index=0)

        language_options = []
        if not progs.empty and "language" in progs.columns:
            language_options = sorted([x for x in progs["language"].unique() if str(x).strip()])
        prog_lang = d2.selectbox("لغة الدراسة", ["All"] + language_options, index=0)

        scholarship_need = d3.selectbox("المنح مهمة؟", ["All", "Yes", "No"], index=0)

        st.write("")
        e1, e2, e3 = st.columns(3)
        hs_avg = e1.number_input("معدل/نسبة تقريبية (اختياري)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
        ielts = e2.number_input("IELTS (اختياري)", min_value=0.0, max_value=9.0, value=0.0, step=0.5)
        math_avg = e3.number_input("رياضيات (اختياري)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)

        q_free = st.text_input("ملاحظة/تفضيل (اختياري)", placeholder="مثال: أبي جامعة قوية في التقنية + منح")

    # ----------------------------
    # منطق التصفية + التقييم
    # ----------------------------
    def uni_has_scholarship(s: str) -> bool:
        if not isinstance(s, str):
            return False
        s = s.strip()
        if s in ["", "No", "Unknown"]:
            return False
        return True

    def match_programs_for_uni(uni_id: str) -> pd.DataFrame:
        if progs.empty or "uni_id" not in progs.columns:
            return pd.DataFrame()
        df = progs[progs["uni_id"] == uni_id].copy()

        if study_level != "All" and "level" in df.columns:
            df = df[df["level"] == study_level]
        if major_field != "All" and "major_field" in df.columns:
            df = df[df["major_field"] == major_field]
        if prog_lang != "All" and "language" in df.columns:
            df = df[df["language"] == prog_lang]

        return df

    def admission_label(required_ielts: float, user_ielts: float) -> str:
        # لو ما عندنا متطلب أو ما عند المستخدم درجة
        if required_ielts <= 0:
            return "Unknown"
        if user_ielts <= 0:
            return "Conditional"  # يحتاج يثبت اللغة/يختبر
        if user_ielts >= required_ielts:
            return "Suitable"
        return "Conditional"

    def safe_float(x) -> float:
        try:
            return float(str(x).strip())
        except Exception:
            return 0.0

    def estimate_req_from_programs(df_prog: pd.DataFrame) -> dict:
        """
        يرجع متطلبات تقديرية من بيانات البرامج إن وجدت.
        لو مافي -> Unknown
        """
        req = {
            "english_test": "",
            "english_score": "",
            "math_requirement": "",
            "admission_notes": "",
        }
        if df_prog is None or df_prog.empty:
            return req

        # ناخذ أول قيمة غير فاضية
        for k in req.keys():
            vals = [v for v in df_prog.get(k, "").astype(str).tolist() if str(v).strip()]
            req[k] = vals[0].strip() if vals else ""

        return req

    def score_uni(row: pd.Series) -> dict:
        """
        سكورنق بسيط واحترافي:
        - مطابقة البرامج (أهم شيء)
        - المنح (إذا مطلوبة)
        - القرب (الدولة/المدينة)
        """
        score = 0
        reasons = []

        # 1) مطابقة البرامج
        df_prog = match_programs_for_uni(row["uni_id"])
        if not df_prog.empty:
            score += 40
            reasons.append("يوجد برامج مطابقة لخياراتك")
        else:
            reasons.append("لا توجد برامج مطابقة (جرّبي توسيع الفلاتر)")

        # 2) الدولة/المدينة
        if pref_country != "All" and row["country"] == pref_country:
            score += 15
            reasons.append("ضمن الدولة المفضلة")
        if pref_city != "All" and row["city"] == pref_city:
            score += 10
            reasons.append("ضمن المدينة المفضلة")

        # 3) المنح
        if scholarship_need == "Yes":
            if uni_has_scholarship(str(row.get("scholarship", "Unknown"))):
                score += 20
                reasons.append("تظهر كجامعة لديها منح (حسب البيانات)")
            else:
                score += 0
                reasons.append("المنح غير متاحة/غير واضحة (حسب البيانات)")

        # 4) دعم بسيط للمعدل/الرياضيات (بدون ما نفترض أرقام جامدة)
        if hs_avg > 0:
            score += 5
            reasons.append("تم إدخال معدل تقريبي (يُستخدم للتوجيه)")
        if math_avg > 0:
            score += 5
            reasons.append("تم إدخال مستوى الرياضيات (يُستخدم للتوجيه)")

        # متطلبات تقديرية من البرامج
        req = estimate_req_from_programs(match_programs_for_uni(row["uni_id"]))
        req_ielts = safe_float(req.get("english_score", "")) if str(req.get("english_test", "")).upper().find("IELTS") >= 0 else 0.0
        status = admission_label(req_ielts, ielts)

        return {
            "score": score,
            "reasons": reasons,
            "req": req,
            "status": status,
        }

    run = st.button("حلّل فرص قبولي", use_container_width=True)

    if run:
        # فلترة أولية حسب الدولة/المدينة (لتسريع)
        unis_f = unis.copy()
        if pref_country != "All":
            unis_f = unis_f[unis_f["country"] == pref_country]
        if pref_city != "All":
            unis_f = unis_f[unis_f["city"] == pref_city]

        if scholarship_need == "Yes":
            # نخليها ما تمنع نهائياً، بس تقلل النتائج لو تبين
            pass

        if unis_f.empty:
            st.warning("ما لقيت جامعات حسب اختياراتك الحالية. جرّبي توسعين الدولة/المدينة أو الفلاتر.")
            st.stop()

        # نحسب السكور
        results = []
        for _, r in unis_f.iterrows():
            meta = score_uni(r)
            results.append({
                "uni_id": r["uni_id"],
                "name_ar": r["name_ar"],
                "name_en": r["name_en"],
                "country": r["country"],
                "city": r["city"],
                "type": r["type"],
                "scholarship": r.get("scholarship", "Unknown"),
                "score": meta["score"],
                "status": meta["status"],
                "reasons": " • ".join(meta["reasons"][:3]),
                "website": r.get("website", ""),
                "admissions_url": r.get("admissions_url", ""),
                "programs_url": r.get("programs_url", ""),
                "req_english_test": meta["req"].get("english_test", ""),
                "req_english_score": meta["req"].get("english_score", ""),
                "req_math": meta["req"].get("math_requirement", ""),
                "req_notes": meta["req"].get("admission_notes", ""),
            })

        out = pd.DataFrame(results).sort_values(["score", "status"], ascending=[False, True])

        st.divider()
        st.subheader("أفضل الخيارات المقترحة")
        top = out.head(3).copy()

        # عرض بطاقات قصيرة لكل جامعة
        for _, row in top.iterrows():
            with st.expander(f"{row['name_ar']} — {row['country']} / {row['city']}  |  التقييم: {row['score']}", expanded=True):
                cA, cB = st.columns([2, 1])

                with cA:
                    st.write(f"**تقييم القبول:** {ar_status(row['status'])}")
                    st.write(f"**المنح (حسب البيانات):** {row['scholarship']}")
                    st.write(f"**لماذا هذا خيار جيد؟** {row['reasons'] if row['reasons'] else '—'}")

                    st.write("")
                    st.markdown("**متطلبات القبول المتوقعة (إن توفرت بياناتها في programs.csv):**")
                    et = row["req_english_test"] if str(row["req_english_test"]).strip() else "Unknown"
                    es = row["req_english_score"] if str(row["req_english_score"]).strip() else "Unknown"
                    mr = row["req_math"] if str(row["req_math"]).strip() else "Unknown"
                    st.write(f"- اللغة الإنجليزية: {et} / الدرجة: {es}")
                    st.write(f"- الرياضيات: {mr}")
                    if str(row["req_notes"]).strip():
                        st.write(f"- ملاحظات: {row['req_notes']}")

                with cB:
                    st.markdown("**روابط رسمية**")
                    if str(row["website"]).strip():
                        st.link_button("Website", row["website"], use_container_width=True)
                    if str(row["admissions_url"]).strip():
                        st.link_button("Admissions", row["admissions_url"], use_container_width=True)
                    if str(row["programs_url"]).strip():
                        st.link_button("Programs", row["programs_url"], use_container_width=True)

        # جدول مختصر (اختياري)
        st.write("")
        st.subheader("نتائج إضافية (جدول)")
        cols_show = ["name_ar", "country", "city", "type", "scholarship", "status", "score", "website", "admissions_url", "programs_url"]
        st.dataframe(
            out[cols_show].head(30),
            use_container_width=True,
            hide_index=True,
            column_config={
                "website": st.column_config.LinkColumn("Website", display_text="Click here"),
                "admissions_url": st.column_config.LinkColumn("Admissions", display_text="Click here"),
                "programs_url": st.column_config.LinkColumn("Programs", display_text="Click here"),
            }
        )

        # مراكز اختبارات قريبة
        st.write("")
        st.subheader("أماكن اختبارات قريبة منك")
        key = (pref_country if pref_country != "All" else "", pref_city if pref_city != "All" else "")
        centers = TEST_CENTERS.get(key, {})

        if not centers:
            st.info("حالياً ما عندي مراكز محفوظة لهذي المدينة. تقدرين تضيفينها في test_centers.csv لاحقًا وسأربطها فوراً.")
        else:
            for test_type, items in centers.items():
                with st.expander(test_type, expanded=False):
                    for it in items:
                        name = it.get("name", "")
                        url = it.get("url", "")
                        if url:
                            st.link_button(name, url)
                        else:
                            st.write(f"- {name}")


# ----------------------------
# Page: من نحن
# ----------------------------
elif st.session_state.page == "من نحن":
    st.markdown('<h1 class="page-title">من نحن</h1>', unsafe_allow_html=True)
    st.write("")

    left, center, right = st.columns([1, 2.8, 1])
    with center:
        st.markdown(
            """
            <div style="text-align:center; font-size:1.05rem; line-height:2;">
              <p><b>بوصلة</b> منصة رقمية ذكية تهدف إلى مساعدة الطلاب وأولياء الأمور في اتخاذ قرار واعٍ ومدروس لاختيار الجامعة والبرنامج الأكاديمي داخل دول الخليج.</p>

              <p>جاءت فكرة بوصلة استجابةً لتحدٍ واقعي يواجه الكثير من الطلبة، وهو <b>تشتّت المعلومات</b> وصعوبة المقارنة بين الجامعات والبرامج وتعدد المصادر غير الموثوقة.</p>

              <p>نعمل في بوصلة على جمع البيانات وتنظيمها ثم تقديمها بطريقة مبسطة وقابلة للمقارنة، مع توظيف أدوات ذكية تساعد المستخدم على فهم الخيارات واتخاذ القرار بثقة.</p>

              <hr style="margin:18px 0; border:none; border-top:1px solid #e5e7eb;">

              <p style="margin-bottom:10px;"><b>ماذا يميز بوصلة؟</b></p>
              <p>تركيز على السياق الخليجي واحتياجات الطلبة في المنطقة</p>
              <p>عرض واضح ومقارنات سهلة بين الجامعات والبرامج</p>
              <p>استخدام مسؤول للذكاء الاصطناعي لدعم القرار لا استبداله</p>
              <p>الحياد والشفافية واحترام خصوصية المستخدم</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")
    st.markdown("---")
    st.write("")

    st.markdown("<h3 style='text-align:center;'>تواصل معنا</h3>", unsafe_allow_html=True)
    st.write("")

    left2, center2, right2 = st.columns([1, 2.8, 1])
    with center2:
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("الاسم", placeholder="اكتب اسمك")
            st.text_input("البريد الإلكتروني", placeholder="example@email.com")
        with c2:
            st.text_area("رسالتك", placeholder="اكتب رسالتك هنا...", height=120)

        if st.button("إرسال", use_container_width=True):
            st.success("تم الاستلام. شكرًا لتواصلك!")

        st.caption("للتعاون والشراكات: يسعدنا التواصل مع الجهات التعليمية والمبادرات المجتمعية.")
