import streamlit as st
from ui import render_shell, cards_2col
st.set_page_config(page_title="الرئيسية", layout="wide")

# ----------------------------
# Main Landing Page
# ----------------------------
render_shell()

st.write("")

# بطاقات: الرؤية – الرسالة – القيم – لماذا بوصلة؟
cards_2col([
    {
        "title": "رؤيتنا",
        "text": "أن تكون بوصلة المرجع الأول لاتخاذ قرار جامعي واعٍ في دول الخليج عبر معلومات موثوقة وتجربة ذكية."
    },
    {
        "title": "رسالتنا",
        "text": "تمكين الطلاب وأولياء الأمور من مقارنة الخيارات الجامعية والبرامج بسهولة، وتبسيط رحلة الاختيار باستخدام أدوات ذكية."
    },
    {
        "title": "قيمنا",
        "text": "الموثوقية، الشفافية، الحياد، تبسيط المعرفة، واحترام خصوصية المستخدم."
    },
    {
        "title": "لماذا بوصلة؟",
        "text": "لأن قرار الجامعة من أهم القرارات، وبوصلة تجمع البيانات وتعرضها بوضوح وتساعدك على المقارنة واتخاذ القرار."
    },
])

st.write("")
st.markdown("---")

# ----------------------------
# Navigation Buttons (UI only)
# ----------------------------
c1, c2, c3 = st.columns(3)

with c1:
    st.button("ابدأ البحث", use_container_width=True)

with c2:
    st.button("قارن الجامعات", use_container_width=True)

with c3:
    st.button("تحدث مع رُشد", use_container_width=True)


