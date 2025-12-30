import streamlit as st

CUSTOM_CSS = """
<style>
:root{
  --bg:#F5F7FA;
  --card:#FFFFFF;
  --text:#334155;
  --navy:#0F1B33;
  --navy2:#12264A;
  --sky:#38BDF8;
  --sky2:#60A5FA;
  --border:#E5E7EB;
  --muted:#64748B;
}

html, body, [class*="css"] {
  font-family: 'Cairo', sans-serif;
  background-color: var(--bg);
  color: var(--text);
}

/* ===== HEADER ===== */
.custom-header{
  background: linear-gradient(135deg, var(--navy2), var(--navy));
  padding: 60px 20px 50px;
  text-align: center;
  position: relative;
  border-radius: 0 0 28px 28px;
}

.custom-header h1{
  font-size: 3rem;
  font-weight: 800;
  margin: 0;
  color: white;
}

.custom-header p{
  margin-top: 10px;
  font-size: 1.15rem;
  color: rgba(255,255,255,.85);
}

/* buttons */
.header-actions{
  position: absolute;
  top: 20px;
  right: 30px;
  display: flex;
  gap: 10px;
}

.header-actions a{
  padding: 8px 16px;
  border-radius: 10px;
  font-weight: 700;
  text-decoration: none;
  font-size: 0.9rem;
}

.btn-login{
  background: white;
  color: var(--navy);
}

.btn-signup{
  background: linear-gradient(135deg, var(--sky), var(--sky2));
  color: white;
}

/* ===== Cards ===== */
.cards-wrap{
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  margin-top: 24px;
}

.card{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 20px 22px;
  box-shadow: 0 10px 30px rgba(15,27,51,0.06);
}

.card-title{
  font-size: 1.4rem;
  font-weight: 800;
  margin-bottom: 10px;
}

.card-text{
  color: var(--muted);
  line-height: 1.9;
  font-size: 1.05rem;
}

@media (max-width: 900px){
  .cards-wrap{ grid-template-columns: 1fr; }
}
</style>
"""

def render_shell(title: str = "بوصلة", subtitle: str = "دليلك الذكي لاختيار الجامعة والبرنامج في دول الخليج"):
    st.set_page_config(page_title="بوصلة", layout="wide")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
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

def cards_2col(items):
    """
    items: list of dicts: [{"title":"...", "text":"..."}, ...]
    """
    html = '<div class="cards-wrap">'
    for it in items:
        html += f"""
        <div class="card">
          <div class="card-title">{it["title"]}</div>
          <div class="card-text">{it["text"]}</div>
        </div>
        """
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
