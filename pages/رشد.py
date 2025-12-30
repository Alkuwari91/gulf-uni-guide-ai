import streamlit as st
from ui import render_shell

render_shell()

st.write("")
st.subheader("رُشد — المعاون الذكي")
st.write("هنا سنضيف لاحقًا المساعد الذكي لتحويل طلب المستخدم إلى فلاتر واقتراح جامعات وبرامج مناسبة.")

user_q = st.text_area("اكتب احتياجك", placeholder="مثال: أبي بكالوريوس في علوم الحاسب في الإمارات باللغة الإنجليزية")
st.button("حلّل الطلب")

