import streamlit as st
import pandas as pd
from pathlib import Path
from ui import render_shell

# --- لازم نخلي السايدبار مقفل من البداية
st.set_page_config(page_title="بوصلة", layout="wide", initial_sidebar_state="collapsed")
render_shell()

# --- إخفاء السايدبار نهائياً (حتى المساحة)
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
# Navigation (بدون سايدبار)
# ----------------------------
if "page" not in st.session_state:
    st.session_state.page = "الرئيسية"

nav = ["الرئيسية", "بحث الجامعات", "المقارنة", "رُشد", "من نحن"]
c = st.columns(len(nav))
for i, name in enumerate(nav):
    if c[i].button(name, use_container_width=True):
        st.session_state.page = name
        st.rerun()

st.write("")
st.markdown("---")
st.write("")

# ----------------------------
# Helper: شكل الـ Expander مثل كارد (بدون HTML divs للبطاقات)
# ----------------------------
st.markdown(
    """
    <style>
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
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Page: الرئيسية (كارد مثل راسخون)
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
    st.subheader("بحث الجامعات")

    ROOT = Path(__file__).resolve().parent
    DATA_DIR = ROOT / "data"
    UNIS_PATH = DATA_DIR / "universities.csv"
    PROGS_PATH = DATA_DIR / "programs.csv"

    @st.cache_data(show_spinner=False)
    def load_csv(path: Path) -> pd.DataFrame:
        if (not path.exists()) or path.stat().st_size == 0:
            return pd.DataFrame()
        return pd.read_csv(path, encoding="utf-8", engine="python", on_bad_lines="skip")

def normalize_unis(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    # الأعمدة الأساسية (12)
    cols_12 = [
        "uni_id","name_ar","name_en","country","city","type",
        "website","admissions_url","programs_url",
        "ranking_source","extra_1","extra_2"
    ]

    # الأعمدة بعد إضافة المنح (18)
    cols_18 = cols_12 + [
        "sch_local",
        "sch_gcc",
        "sch_intl",
        "sch_children_citizen_mothers",
        "sch_notes",
        "sch_url"
    ]

    # تسمية الأعمدة حسب العدد المقروء
    if len(df.columns) == 12:
        df.columns = cols_12
    elif len(df.columns) == 18:
        df.columns = cols_18
    else:
        # في حال وجود فواصل/مسافات زائدة في بعض السطور
        # لا نكسر الكود — نكمل ونضيف الأعمدة الناقصة
        pass

    # اشتقاق أعمدة الترتيب والاعتماد
    if "ranking_value" not in df.columns:
        df["ranking_value"] = df.get("extra_1", "")
    if "accreditation_notes" not in df.columns:
        df["accreditation_notes"] = df.get("extra_2", "")

    # أعمدة المنح — لو غير موجودة نخليها Unknown
    for c in [
        "sch_local",
        "sch_gcc",
        "sch_intl",
        "sch_children_citizen_mothers"
    ]:
        if c not in df.columns:
            df[c] = "Unknown"
        df[c] = (
            df[c]
            .fillna("Unknown")
            .astype(str)
            .replace({"": "Unknown", "nan": "Unknown"})
        )

    if "sch_notes" not in df.columns:
        df["sch_notes"] = ""
    if "sch_url" not in df.columns:
        df["sch_url"] = ""

    # الأعمدة النهائية المعتمدة في التطبيق
    needed = [
        "uni_id","name_ar","name_en","country","city","type",
        "sch_local","sch_gcc","sch_intl","sch_children_citizen_mothers",
        "sch_notes","sch_url",
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

    if unis.empty:
        st.error(f"universities.csv not found or empty: {UNIS_PATH}")
        st.stop()
    if progs.empty:
        st.warning(f"programs.csv not found or empty: {PROGS_PATH}")

    # ----------------------------
    # Filters
    # ----------------------------
    st.write("")
    col1, col2, col3, col4, col5 = st.columns([1.2, 1, 1, 1.2, 1])

    countries = sorted([c for c in unis["country"].unique() if str(c).strip()])
    country = col1.selectbox("Country", options=["All"] + countries, index=0)

    uni_types = sorted([t for t in unis["type"].unique() if str(t).strip()])
    uni_type = col2.selectbox("University type", options=["All"] + uni_types, index=0)

    levels = sorted([x for x in progs["level"].unique() if str(x).strip()]) if not progs.empty else []
    level = col3.selectbox("Level", options=["All"] + levels, index=0)

    majors = sorted([m for m in progs["major_field"].unique() if str(m).strip()]) if not progs.empty else []
    major = col4.selectbox("Major field", options=["All"] + majors, index=0)

    sch_opt = ["All", "Yes", "No", "Unknown"]
    scholarship = col5.selectbox("Scholarships", sch_opt, index=0)

    q = st.text_input("Search (university / program / city)", value="").strip().lower()

    # ----------------------------
    # Apply filters on universities
    # ----------------------------
    unis_f = unis.copy()

    if country != "All":
        unis_f = unis_f[unis_f["country"] == country]
    if uni_type != "All":
        unis_f = unis_f[unis_f["type"] == uni_type]
    if scholarship != "All":
        unis_f = unis_f[unis_f["scholarship_available"] == scholarship]

    if q:
        mask_u = (
            unis_f["name_en"].str.lower().str.contains(q, na=False)
            | unis_f["name_ar"].str.lower().str.contains(q, na=False)
            | unis_f["city"].str.lower().str.contains(q, na=False)
        )
        unis_f = unis_f[mask_u]

    # ----------------------------
    # Results
    # ----------------------------
    st.divider()
    st.subheader("Universities")

    cols_show = [
        "uni_id","name_ar","name_en","country","city","type",
        "scholarship_available",
        "website","admissions_url","programs_url",
        "ranking_source","ranking_value","accreditation_notes"
    ]
    st.dataframe(unis_f[cols_show], use_container_width=True, hide_index=True)

# ----------------------------
# Page: المقارنة
# ----------------------------
elif st.session_state.page == "المقارنة":
    st.subheader("المقارنة بين الجامعات")
    st.info("هذه الصفحة نربطها بالاختيار من نتائج البحث لاحقًا.")

# ----------------------------
# Page: رُشد
# ----------------------------
elif st.session_state.page == "رُشد":
    st.subheader("رُشد — المعاون الذكي")
    user_q = st.text_area("اكتب احتياجك", placeholder="مثال: أبي بكالوريوس في علوم الحاسب في الإمارات باللغة الإنجليزية")
    st.button("حلّل الطلب")

# ----------------------------
# Page: من نحن (متمركز + محتوى أكثر + تواصل)
# ----------------------------
elif st.session_state.page == "من نحن":
    st.markdown("<h2 style='text-align:center; margin-top: 0;'>من نحن</h2>", unsafe_allow_html=True)
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
