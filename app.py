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

nav = ["الرئيسية", "بحث الجامعات", "المقارنة", "رُشد", "من نحن"]
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
elif st.session_state.page == "المقارنة":
    st.markdown('<h1 class="page-title">المقارنة بين الجامعات</h1>', unsafe_allow_html=True)

    unis = normalize_unis(load_csv(UNIS_PATH))
    if unis.empty:
        st.error(f"universities.csv not found or empty: {UNIS_PATH}")
        st.stop()

    unis = unis.copy()
    unis["label"] = unis.apply(
        lambda r: f"{str(r['name_ar']).strip()} — {str(r['name_en']).strip()} ({str(r['city']).strip()}, {str(r['country']).strip()})",
        axis=1
    )
    unis = unis.sort_values(["country", "city", "name_en"], na_position="last")

    selected_ids = st.multiselect(
        "اختار 2 إلى 4 جامعات للمقارنة",
        options=unis["uni_id"].tolist(),
        format_func=lambda x: unis.loc[unis["uni_id"] == x, "label"].values[0],
        max_selections=4
    )

    if len(selected_ids) < 2:
        st.info("يرجى اختيار جامعتين على الأقل لتظهر المقارنة.")
        st.stop()

    comp = unis[unis["uni_id"].isin(selected_ids)].copy()

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
        row = comp[comp["uni_id"] == uni_id].iloc[0]
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
# Page: رُشد
# ----------------------------
elif st.session_state.page == "رُشد":
    st.markdown('<h1 class="page-title">رُشد — المعاون الذكي</h1>', unsafe_allow_html=True)

    user_q = st.text_area(
        "اكتب احتياجك",
        placeholder="مثال: أبي بكالوريوس في علوم الحاسب في الإمارات باللغة الإنجليزية"
    )
    st.button("حلّل الطلب")


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
