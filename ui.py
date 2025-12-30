import streamlit as st

CUSTOM_CSS = """
<style>
/* اخفاء السايدبار بالكامل */
[data-testid="stSidebar"], section[data-testid="stSidebar"], [data-testid="stSidebarNav"] {
  display: none !important;
}
button[kind="header"] { display: none !important; } /* زر الهامبرغر */

/* منيو أزرار مثل الصورة */
.nav-row {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 18px;
  margin-top: 18px;
}
.nav-btn {
  width: 100%;
  padding: 14px 10px;
  border-radius: 14px;
  border: 1px solid #E5E7EB;
  background: #ffffff;
  font-weight: 800;
  font-size: 1.05rem;
  cursor: pointer;
}
.nav-btn:hover {
  background: rgba(56,189,248,0.08);
}
@media (max-width: 1000px){
  .nav-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>
"""

def render_shell(title="بوصلة", subtitle="دليلك الذكي لاختيار الجامعة والبرنامج في دول الخليج"):
    st.set_page_config(page_title=title, layout="wide", initial_sidebar_state="collapsed")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # الهيدر (خليه مثل كودك الحالي)
    st.markdown(f"""
    <div class="custom-header">
      <div class="header-actions">
        <a href="#" class="btn-login">تسجيل الدخول</a>
        <a href="#" class="btn-signup">إنشاء حساب</a>
      </div>
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def render_top_nav(active: str = ""):
    # منيو مثل الصورة لكن بأزرار Streamlit (نحافظ على الشكل بالـCSS)
    st.markdown('<div class="nav-row">', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        if st.button("الرئيسية", use_container_width=True):
            st.switch_page("pages/1_الرئيسية.py")
    with c2:
        if st.button("بحث الجامعات", use_container_width=True):
            st.switch_page("pages/2_بحث_الجامعات.py")
    with c3:
        if st.button("المقارنة", use_container_width=True):
            st.switch_page("pages/3_المقارنة.py")
    with c4:
        if st.button("رُشد", use_container_width=True):
            st.switch_page("pages/4_رشد.py")
    with c5:
        if st.button("من نحن", use_container_width=True):
            st.switch_page("pages/5_من_نحن.py")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")


    st.markdown(f"""
    <div class="custom-header">
      <div class="header-actions">
        <a href="#" class="btn-login">تسجيل الدخول</a>
        <a href="#" class="btn-signup">إنشاء حساب</a>
      </div>
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

# =========================
# Cards (2 columns)
# =========================
def cards_2col(items):
    # نعرض بطاقتين بكل صف باستخدام Streamlit columns
    for i in range(0, len(items), 2):
        cols = st.columns(2)
        for j in range(2):
            idx = i + j
            if idx >= len(items):
                break
            it = items[idx]
            with cols[j]:
                st.markdown(
                    f"""
                    <div class="card">
                      <div class="card-title">{it["title"]}</div>
                      <div class="card-text">{it["text"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
