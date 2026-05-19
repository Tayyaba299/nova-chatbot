# app.py
# Nova - University Student Assistant Chatbot
# GSCWU Bahawalpur | DCS and IT

import streamlit as st
from chatbot import ChatbotEngine

st.set_page_config(
    page_title="Nova - GSCWU Student Assistant",
    page_icon="N",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
<style>
    /* ── layout ── */
    .block-container {
        padding-top: 2.8rem;
        padding-bottom: 0.5rem;
        max-width: 780px;
    }

    /* ── chat bubbles ── */
    .msg-user {
        background: #1e3a5f;
        color: #ffffff;
        padding: 10px 16px;
        border-radius: 16px 16px 4px 16px;
        margin: 4px 0 2px 80px;
        font-size: 14px;
        line-height: 1.6;
    }
    .msg-nova {
        background: #f1f4f8;
        color: #1a1a1a;
        padding: 10px 16px;
        border-radius: 16px 16px 16px 4px;
        margin: 4px 80px 2px 0;
        font-size: 14px;
        line-height: 1.7;
        border-left: 3px solid #1e3a5f;
    }
    .lbl { font-size: 11px; color: #aaa; margin: 8px 2px 1px 2px; }
    .lbl-u { text-align: right; }
    .lbl-n { text-align: left;  }

    /* ── welcome box ── */
    .welcome-box {
        background: #f1f4f8;
        border-left: 3px solid #1e3a5f;
        padding: 16px 20px;
        border-radius: 8px;
        font-size: 14px;
        line-height: 1.8;
        color: #1a1a1a;
        margin-bottom: 20px;
    }

    /* ── sidebar ── */
    section[data-testid="stSidebar"] {
        background: #1e3a5f;
    }
    /* force ALL text white in sidebar */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] *:not(button) {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] a {
        color: #a8d0f0 !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.15) !important;
        margin: 10px 0;
    }

    /* sidebar buttons - topic */
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.08) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        border-radius: 7px;
        text-align: left;
        font-size: 13px;
        width: 100%;
        margin: 2px 0;
        padding: 7px 12px;
        transition: background 0.15s;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.18) !important;
        border-color: rgba(255,255,255,0.35) !important;
    }

    /* clear button - red tint */
    .clear-wrap .stButton > button {
        background: rgba(210,50,50,0.18) !important;
        border-color: rgba(210,50,50,0.45) !important;
        color: #ffbbbb !important;
    }
    .clear-wrap .stButton > button:hover {
        background: rgba(210,50,50,0.30) !important;
    }

    /* ── section labels ── */
    .sec-label {
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.5;
        margin-bottom: 6px;
        color: #fff;
    }

    /* ── page title area ── */
    .page-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 4px;
    }
    .page-title {
        font-size: 21px;
        font-weight: 600;
        color: #1e3a5f;
    }
    .page-sub {
        font-size: 11px;
        color: #999;
        margin-top: 1px;
    }

    footer { visibility: hidden; }
    .main-hr {
        border: none;
        border-top: 1px solid #e4e8ee;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# ── session state ─────────────────────────────────────────────────────────────
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'bot' not in st.session_state:
    with st.spinner("Loading Nova..."):
        st.session_state.bot = ChatbotEngine()


def send_message(text):
    text = text.strip()
    if not text:
        return
    st.session_state.messages.append({'role': 'user', 'content': text})
    response = st.session_state.bot.get_response(text)
    st.session_state.messages.append({'role': 'assistant', 'content': response})


# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:

    # brand
    st.markdown("""
    <div style='padding:4px 0 12px 0;'>
        <div style='font-size:22px; font-weight:700;'>Nova</div>
        <div style='font-size:12px; opacity:0.7; margin-top:2px;'>University Student Assistant</div>
        <div style='font-size:11px; opacity:0.5; margin-top:1px;'>GSCWU Bahawalpur</div>
    </div>
    """, unsafe_allow_html=True)

    # clear button at top
    st.markdown('<div class="sec-label">Session</div>', unsafe_allow_html=True)
    st.markdown('<div class="clear-wrap">', unsafe_allow_html=True)
    if st.button("Clear Conversation", key="clear_btn", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # quick topics
    st.markdown('<div class="sec-label">Quick Topics</div>', unsafe_allow_html=True)

    topics = [
        ("Admissions",    "How do I apply for admission at GSCWU?"),
        ("Fee Structure", "What is the fee structure for BS Computer Science?"),
        ("Timetable",     "Show me the class timetable for CS department"),
        ("Departments",   "What departments are available at GSCWU?"),
        ("Teachers",      "I need the contact details of the CS faculty"),
    ]

    for label, query in topics:
        if st.button(label, key=f"btn_{label}", use_container_width=True):
            send_message(query)
            st.rerun()

    st.markdown('<hr>', unsafe_allow_html=True)

    # contacts
    st.markdown('<div class="sec-label">University Contacts</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:13px; line-height:2.1;'>
        <i class='bi bi-telephone-fill'></i>&nbsp; Admin: 0629-2880012<br>
        <i class='bi bi-telephone-fill'></i>&nbsp; Finance: 0629-2880014<br>
        <i class='bi bi-telephone-fill'></i>&nbsp; CS Dept: 0629-2880013<br>
        <i class='bi bi-envelope-fill'></i>&nbsp; info@gscwu.edu.pk<br>
        <i class='bi bi-clock-fill'></i>&nbsp; Mon–Fri, 9am–4pm
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size:11px; opacity:0.4; line-height:1.7;'>
        Nova v1.0<br>
        DCS and IT, GSCWU<br>
        2025
    </div>
    """, unsafe_allow_html=True)


# ── main area ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:4px;">
    <div class="page-title">Nova — Student Assistant</div>
    <div class="page-sub">Government Sadiq College Women University Bahawalpur</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="main-hr">', unsafe_allow_html=True)

# welcome
if not st.session_state.messages:
    st.markdown("""
<div class='welcome-box'>
    <strong>Assalam o Alaikum.</strong> I am Nova, your student assistant at GSCWU Bahawalpur.<br><br>
    I can answer your questions about <strong>admissions</strong>, <strong>fee structure</strong>,
    <strong>class timetables</strong>, <strong>departments</strong>, and <strong>teacher contacts</strong>.<br><br>
    Use the topic buttons on the left, or type your question below.<br>
    <span style='font-size:12px; color:#666;'>
        <i class='bi bi-translate'></i>&nbsp;
        Urdu mein bhi pooch sakte hain — main detect kar lunga.
    </span>
</div>
""", unsafe_allow_html=True)

# chat history
for msg in st.session_state.messages:
    if msg['role'] == 'user':
        st.markdown('<div class="lbl lbl-u">You</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="lbl lbl-n">Nova</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="msg-nova">{msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('<br>', unsafe_allow_html=True)
st.markdown('<hr class="main-hr">', unsafe_allow_html=True)

# input
user_input = st.chat_input("Type your question here...")
if user_input:
    send_message(user_input)
    st.rerun()

st.markdown("""
<div style='text-align:center; color:#ccc; font-size:11px; margin-top:6px;'>
    Nova v1.0 &nbsp;|&nbsp; DCS and IT, Government Sadiq College Women University Bahawalpur &nbsp;|&nbsp; 2025
</div>
""", unsafe_allow_html=True)