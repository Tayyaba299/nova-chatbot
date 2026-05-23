import streamlit as st

from engine import ChatbotEngine

st.set_page_config(
    page_title="Nova — GSCWU Student Assistant",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

# styles 
st.html("""
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
<style>
  /* layout */
  .block-container { padding-top: 2.5rem; padding-bottom: 0.5rem; max-width: 780px; }

  /* chat bubbles */
  .msg-user {
    background: #1e3a5f; color: #fff;
    padding: 10px 16px; margin: 4px 0 2px 80px;
    border-radius: 16px 16px 4px 16px;
    font-size: 14px; line-height: 1.6;
  }
  .msg-bot {
    background: #f1f4f8; color: #1a1a1a;
    padding: 10px 16px; margin: 4px 80px 2px 0;
    border-radius: 16px 16px 16px 4px;
    border-left: 3px solid #1e3a5f;
    font-size: 14px; line-height: 1.7;
  }
  .msg-label { font-size: 11px; color: #aaa; margin: 8px 2px 1px; }
  .msg-label.right { text-align: right; }

  .welcome {
    background: #f1f4f8; border-left: 3px solid #1e3a5f;
    padding: 16px 20px; border-radius: 8px;
    font-size: 14px; line-height: 1.8; color: #1a1a1a;
    margin-bottom: 20px;
  }

  section[data-testid="stSidebar"] { background: #1e3a5f; }
  section[data-testid="stSidebar"],
  section[data-testid="stSidebar"] *:not(button) { color: #fff !important; }
  section[data-testid="stSidebar"] a { color: #a8d0f0 !important; }
  section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15) !important; margin: 10px 0;
  }

  section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.08) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 7px; text-align: left;
    font-size: 13px; width: 100%;
    margin: 2px 0; padding: 7px 12px;
    transition: background 0.15s;
  }
  section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.18) !important;
    border-color: rgba(255,255,255,0.35) !important;
  }

  .clear-btn .stButton > button {
    background: rgba(210,50,50,0.18) !important;
    border-color: rgba(210,50,50,0.45) !important;
    color: #ffbbbb !important;
  }
  .clear-btn .stButton > button:hover {
    background: rgba(210,50,50,0.30) !important;
  }

  .section-label {
    font-size: 10px; text-transform: uppercase;
    letter-spacing: 1px; opacity: 0.5;
    margin-bottom: 6px; color: #fff;
  }

  footer { visibility: hidden; }
  hr.divider { border: none; border-top: 1px solid #e4e8ee; margin: 10px 0; }
</style>
""")


# bot (one instance per session, loaded once) 
@st.cache_resource(show_spinner="Loading Nova...")
def load_bot():
    return ChatbotEngine()


bot = load_bot()


def send(text: str):
    text = text.strip()
    if not text:
        return
    st.session_state.setdefault('history', [])
    st.session_state.history.append(('user', text))
    st.session_state.history.append(('bot', bot.get_response(text)))


#sidebar
with st.sidebar:
    st.markdown("""
    <div style='padding: 4px 0 14px'>
      <div style='font-size: 22px; font-weight: 700;'>Nova</div>
      <div style='font-size: 12px; opacity: .7; margin-top: 2px;'>University Student Assistant</div>
      <div style='font-size: 11px; opacity: .5; margin-top: 1px;'>GSCWU Bahawalpur</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Session</div>', unsafe_allow_html=True)
    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("Clear Conversation", key="clear", use_container_width=True):
        st.session_state.history = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Quick Topics</div>', unsafe_allow_html=True)

    QUICK_TOPICS = [
        ("Admissions",    "How do I apply for admission at GSCWU?"),
        ("Fee Structure", "What is the fee structure for BS Computer Science?"),
        ("Timetable",     "Show me the class timetable for CS department"),
        ("Departments",   "What departments are available at GSCWU?"),
        ("Teachers",      "I need the contact details of the CS faculty"),
    ]
    for label, query in QUICK_TOPICS:
        if st.button(label, key=f"q_{label}", use_container_width=True):
            send(query)
            st.rerun()

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">University Contacts</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size: 13px; line-height: 2.1;'>
      <i class='bi bi-telephone-fill'></i>&nbsp; Admin: 0629-2880012<br>
      <i class='bi bi-telephone-fill'></i>&nbsp; Finance: 0629-2880014<br>
      <i class='bi bi-telephone-fill'></i>&nbsp; CS Dept: 0629-2880013<br>
      <i class='bi bi-envelope-fill'></i>&nbsp; info@gscwu.edu.pk<br>
      <i class='bi bi-clock-fill'></i>&nbsp; Mon–Fri, 9am–4pm
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size: 11px; opacity: .4; line-height: 1.7;'>
      Nova v1.0 · DCS and IT, GSCWU · 2025
    </div>
    """, unsafe_allow_html=True)


# main
st.markdown("""
<div style='margin-bottom: 4px;'>
  <div style='font-size: 21px; font-weight: 600; color: #1e3a5f;'>Nova — Student Assistant</div>
  <div style='font-size: 11px; color: #999; margin-top: 2px;'>
    Government Sadiq College Women University Bahawalpur
  </div>
</div>
""", unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

history = st.session_state.get('history', [])

if not history:
    st.markdown("""
    <div class='welcome'>
      <strong>Assalam o Alaikum.</strong> I am Nova, your student assistant at GSCWU Bahawalpur.<br><br>
      I can answer questions about <strong>admissions</strong>, <strong>fee structure</strong>,
      <strong>timetables</strong>, <strong>departments</strong>, and <strong>teacher contacts</strong>.<br><br>
      Use the topic buttons on the left, or just type your question below.<br>
      <span style='font-size: 12px; color: #666;'>
        <i class='bi bi-translate'></i>&nbsp; Urdu mein bhi pooch sakte hain.
      </span>
    </div>
    """, unsafe_allow_html=True)

for role, content in history:
    if role == 'user':
        st.markdown('<div class="msg-label right">You</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="msg-user">{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="msg-label">Nova</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="msg-bot">{content}</div>', unsafe_allow_html=True)

st.markdown('<br>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

user_input = st.chat_input("Type your question here...")
if user_input:
    send(user_input)
    st.rerun()

st.markdown("""
<div style='text-align: center; color: #ccc; font-size: 11px; margin-top: 6px;'>
  Nova v1.0 &nbsp;·&nbsp; DCS and IT, Government Sadiq College Women University Bahawalpur &nbsp;·&nbsp; 2025
</div>
""", unsafe_allow_html=True)
