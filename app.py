"""
AI Video Assistant — app.py
Premium Streamlit frontend for meeting intelligence.

Design: Obsidian terminal aesthetic — fine-grain scanlines, razor-sharp
        mono type, heated amber accents on a near-black ground.
        Every element earns its pixel.
"""

import time
import html
import streamlit as st
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Meridian — Meeting Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — Obsidian Terminal
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Imports ── */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

/* ── Tokens ── */
:root {
    --bg:          #0c0c0e;
    --surface:     #121215;
    --surface-2:   #18181d;
    --surface-3:   #1e1e26;
    --border:      rgba(255,255,255,0.07);
    --border-hi:   rgba(255,255,255,0.13);
    --amber:       #e8a245;
    --amber-dim:   rgba(232,162,69,0.15);
    --amber-glow:  rgba(232,162,69,0.08);
    --teal:        #3ecfb2;
    --teal-dim:    rgba(62,207,178,0.12);
    --red:         #e85d5d;
    --red-dim:     rgba(232,93,93,0.12);
    --text:        #d8d8e8;
    --text-mid:    #8888a8;
    --text-dim:    #44445a;
    --mono:        'IBM Plex Mono', monospace;
    --sans:        'IBM Plex Sans', sans-serif;
    --radius:      6px;
    --radius-lg:   10px;
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: var(--mono) !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }

/* Fine scanline texture */
.stApp::after {
    content: '';
    position: fixed;
    inset: 0;
    background-image: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,0,0,0.15) 2px,
        rgba(0,0,0,0.15) 3px
    );
    pointer-events: none;
    z-index: 9999;
    opacity: 0.4;
}

/* Corner grid dot */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: radial-gradient(circle, rgba(232,162,69,0.04) 1px, transparent 1px);
    background-size: 28px 28px;
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    padding-top: 1.5rem !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] .block-container { padding: 1rem 1.25rem !important; }

/* ── Headings ── */
h1,h2,h3,h4,h5,h6 {
    font-family: var(--mono) !important;
    color: var(--text) !important;
    letter-spacing: -0.02em !important;
}

/* ── Wordmark ── */
.wordmark {
    font-family: var(--mono);
    font-size: 1.15rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: var(--amber);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.15rem;
}
.wordmark-glyph {
    width: 24px; height: 24px;
    border: 1.5px solid var(--amber);
    border-radius: 4px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    color: var(--amber);
    flex-shrink: 0;
}
.wordmark-sub {
    font-family: var(--mono);
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    color: var(--text-dim);
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

/* ── Section label ── */
.section-label {
    font-family: var(--mono);
    font-size: 0.6rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 0.4rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.section-label::before {
    content: '';
    display: inline-block;
    width: 12px;
    height: 1px;
    background: var(--amber);
    opacity: 0.5;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
    font-size: 0.82rem !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 2px var(--amber-glow) !important;
    outline: none !important;
}
label {
    font-family: var(--mono) !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.08em !important;
    color: var(--text-mid) !important;
    text-transform: uppercase !important;
}

/* ── Primary button ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--amber) !important;
    border-radius: var(--radius) !important;
    color: var(--amber) !important;
    font-family: var(--mono) !important;
    font-weight: 500 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    padding: 0.55rem 1.25rem !important;
    transition: background 0.18s, box-shadow 0.18s !important;
    position: relative !important;
}
.stButton > button:hover {
    background: var(--amber-dim) !important;
    box-shadow: 0 0 16px var(--amber-glow) !important;
}
.stButton > button:active {
    transform: scale(0.98) !important;
}
/* Secondary/clear variant */
.stButton > button[kind="secondary"] {
    border-color: var(--border-hi) !important;
    color: var(--text-mid) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: var(--surface-3) !important;
    box-shadow: none !important;
}

/* ── Hero ── */
.hero {
    padding: 0.5rem 0 1.5rem;
}
.hero-eyebrow {
    font-family: var(--mono);
    font-size: 0.6rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--amber);
    opacity: 0.7;
    margin-bottom: 0.35rem;
}
.hero-title {
    font-family: var(--mono);
    font-size: clamp(1.6rem, 3.5vw, 2.6rem);
    font-weight: 600;
    letter-spacing: -0.03em;
    line-height: 1.1;
    color: var(--text);
    margin: 0;
}
.hero-title span { color: var(--amber); }
.hero-sub {
    font-family: var(--mono);
    font-size: 0.78rem;
    color: var(--text-mid);
    margin-top: 0.5rem;
    letter-spacing: 0.02em;
}

/* ── Info cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.25rem 1.35rem;
    margin-bottom: 0.75rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.card:hover { border-color: var(--border-hi); }
.card-accent {
    position: absolute;
    top: 0; left: 0;
    width: 2px; height: 100%;
    background: var(--amber);
    opacity: 0.6;
}
.card-accent.teal  { background: var(--teal); }
.card-accent.red   { background: var(--red); }
.card-label {
    font-family: var(--mono);
    font-size: 0.58rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.card-body {
    font-family: var(--mono);
    font-size: 0.82rem;
    line-height: 1.75;
    color: var(--text);
    white-space: pre-wrap;
}

/* ── Session title banner ── */
.session-banner {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 2px solid var(--amber);
    border-radius: var(--radius-lg);
    padding: 1rem 1.35rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.session-id {
    font-family: var(--mono);
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    color: var(--amber);
    opacity: 0.7;
    text-transform: uppercase;
    white-space: nowrap;
}
.session-title-text {
    font-family: var(--mono);
    font-size: 1.05rem;
    font-weight: 500;
    color: var(--text);
    letter-spacing: -0.01em;
}

/* ── Transcript scroll ── */
.transcript-scroll {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.1rem;
    font-family: var(--mono);
    font-size: 0.78rem;
    line-height: 1.85;
    max-height: 280px;
    overflow-y: auto;
    color: var(--text-mid);
    white-space: pre-wrap;
    word-break: break-word;
}

/* ── Pipeline step bars ── */
.step-row {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    padding: 0.55rem 0.8rem;
    border-radius: var(--radius);
    margin: 0.22rem 0;
    font-family: var(--mono);
    font-size: 0.72rem;
    color: var(--text-mid);
    border: 1px solid transparent;
    transition: border-color 0.2s;
}
.step-row.active {
    border-color: var(--border);
    background: var(--surface-2);
    color: var(--amber);
}
.step-row.done {
    color: var(--teal);
}
.pip {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--text-dim);
    flex-shrink: 0;
}
.pip.active { background: var(--amber); box-shadow: 0 0 6px var(--amber); animation: blink 1.4s infinite; }
.pip.done   { background: var(--teal); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.35} }

/* ── Chat ── */
.chat-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1rem 1.1rem;
    max-height: 400px;
    overflow-y: auto;
    margin-bottom: 0.75rem;
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
}
.cmsg { display: flex; flex-direction: column; gap: 0.15rem; }
.cmsg-label {
    font-family: var(--mono);
    font-size: 0.58rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
}
.cmsg-label.you { color: var(--amber); opacity: 0.7; text-align: right; }
.cmsg-label.bot { color: var(--teal); opacity: 0.7; }
.cbubble {
    font-family: var(--mono);
    font-size: 0.8rem;
    line-height: 1.65;
    padding: 0.6rem 0.9rem;
    border-radius: var(--radius);
    max-width: 88%;
    white-space: pre-wrap;
    word-break: break-word;
}
.cbubble.you {
    background: var(--amber-dim);
    border: 1px solid rgba(232,162,69,0.18);
    align-self: flex-end;
    color: var(--text);
}
.cbubble.bot {
    background: var(--teal-dim);
    border: 1px solid rgba(62,207,178,0.15);
    align-self: flex-start;
    color: var(--text);
}

/* ── Chat section heading ── */
.chat-heading {
    font-family: var(--mono);
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-mid);
    margin: 0.5rem 0 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.chat-heading::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── Empty state ── */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 5rem 2rem 4rem;
    text-align: center;
    gap: 0.75rem;
}
.empty-glyph {
    font-family: var(--mono);
    font-size: 2.8rem;
    color: var(--text-dim);
    line-height: 1;
    opacity: 0.4;
}
.empty-title {
    font-family: var(--mono);
    font-size: 1rem;
    font-weight: 500;
    color: var(--text-mid);
}
.empty-hint {
    font-family: var(--mono);
    font-size: 0.75rem;
    color: var(--text-dim);
    max-width: 320px;
    line-height: 1.7;
}
.pill-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 0.5rem;
}
.pill {
    font-family: var(--mono);
    font-size: 0.6rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.25rem 0.7rem;
    border-radius: 3px;
    border: 1px solid;
}
.pill-a { color: var(--amber); border-color: rgba(232,162,69,0.3); background: var(--amber-glow); }
.pill-t { color: var(--teal);  border-color: rgba(62,207,178,0.25); background: var(--teal-dim); }
.pill-r { color: var(--text-mid); border-color: var(--border); background: var(--surface-2); }

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.25rem 0 !important;
}

/* ── Streamlit overrides ── */
.stProgress > div > div > div { background: var(--amber) !important; }
.stSpinner > div { border-top-color: var(--amber) !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text) !important; font-family: var(--mono) !important; }
.stAlert { border-radius: var(--radius) !important; font-family: var(--mono) !important; font-size: 0.82rem !important; }
[data-testid="stExpander"] { border: 1px solid var(--border) !important; border-radius: var(--radius-lg) !important; background: var(--surface) !important; }
[data-testid="stExpander"] summary { font-family: var(--mono) !important; font-size: 0.8rem !important; color: var(--text-mid) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--amber); }

/* ── Responsive ── */
@media (max-width: 768px) {
    .hero-title { font-size: 1.4rem !important; }
    .card { padding: 0.9rem 1rem; }
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────────────────────
_DEFAULTS = {
    "result": None,
    "chat_history": [],
    "pipeline_done": False,
    "pipeline_steps": {},
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────
_PIPELINE_STEPS = [
    ("audio",      "01", "Audio extract"),
    ("transcript", "02", "Transcription"),
    ("title",      "03", "Title generation"),
    ("summary",    "04", "Summarisation"),
    ("extract",    "05", "Item extraction"),
    ("rag",        "06", "RAG indexing"),
]

def _step_class(key: str) -> str:
    s = st.session_state.pipeline_steps.get(key, "pending")
    return s  # "pending" | "active" | "done"

def _render_pipeline_steps():
    for key, idx, label in _PIPELINE_STEPS:
        cls = _step_class(key)
        row_class = "step-row active" if cls == "active" else ("step-row done" if cls == "done" else "step-row")
        pip_class  = f"pip {cls}"
        st.markdown(
            f'<div class="{row_class}">'
            f'<div class="{pip_class}"></div>'
            f'<span style="opacity:0.45;margin-right:0.25rem">{idx}</span>{label}'
            f'</div>',
            unsafe_allow_html=True,
        )

def _safe(text: str) -> str:
    """Escape user-supplied text before embedding in HTML."""
    return html.escape(str(text))

def _update_step(key: str, state: str):
    st.session_state.pipeline_steps[key] = state

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="wordmark">'
        '<div class="wordmark-glyph">◈</div>MERIDIAN</div>'
        '<div class="wordmark-sub">Meeting Intelligence</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">Source</div>', unsafe_allow_html=True)
    source = st.text_input(
        "URL or path",
        placeholder="https://youtube.com/watch?v=… or /path/to/file.mp4",
        label_visibility="collapsed",
    )

    st.markdown('<div class="section-label" style="margin-top:0.75rem">Language</div>', unsafe_allow_html=True)
    language = st.selectbox(
        "Language",
        options=["english", "hinglish"],
        index=0,
        label_visibility="collapsed",
    )

    run_btn = st.button("⬡  Run Analysis", use_container_width=True)

    if st.session_state.pipeline_done:
        st.markdown("---")
        st.markdown('<div class="section-label">Pipeline Log</div>', unsafe_allow_html=True)
        _render_pipeline_steps()

# ──────────────────────────────────────────────────────────────────────────────
# MAIN AREA — HERO
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="hero">'
    '<div class="hero-eyebrow">v2.0 · AI PLATFORM</div>'
    '<div class="hero-title">Meeting<span>.</span><br>Intelligence<span>.</span></div>'
    '<div class="hero-sub">Transcribe · Summarise · Chat with your recordings</div>'
    '</div>',
    unsafe_allow_html=True,
)
st.markdown("<hr>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# PIPELINE EXECUTION
# ──────────────────────────────────────────────────────────────────────────────
if run_btn:
    raw_source = source.strip() if source else ""

    # ── Input validation ──
    if not raw_source:
        st.error("⚠  Enter a YouTube URL or a local file path to continue.")
    else:
        # Reset state for fresh run
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        status_ph = st.empty()

        try:
            with status_ph.container():
                st.info("Pipeline initialised — live status in the sidebar.")

            _update_step("audio", "active")
            chunks = process_input(raw_source)
            _update_step("audio", "done")

            _update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            _update_step("transcript", "done")

            _update_step("title", "active")
            title = generate_title(transcript)
            _update_step("title", "done")

            _update_step("summary", "active")
            summary = summarize(transcript)
            _update_step("summary", "done")

            _update_step("extract", "active")
            action_items = extract_action_items(transcript)
            decisions    = extract_key_decisions(transcript)
            questions    = extract_questions(transcript)
            _update_step("extract", "done")

            _update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            _update_step("rag", "done")

            st.session_state.result = {
                "title":          title,
                "transcript":     transcript,
                "summary":        summary,
                "action_items":   action_items,
                "key_decisions":  decisions,
                "open_questions": questions,
                "rag_chain":      rag_chain,
            }
            st.session_state.pipeline_done = True
            status_ph.success("✓  Analysis complete.")
            time.sleep(0.6)
            status_ph.empty()
            st.rerun()

        except Exception as exc:
            # Mark any active step as pending so the sidebar doesn't freeze
            for k, _, _ in _PIPELINE_STEPS:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            status_ph.error(f"Pipeline error: {exc}")

# ──────────────────────────────────────────────────────────────────────────────
# RESULTS
# ──────────────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    # ── Session banner ──
    st.markdown(
        f'<div class="session-banner">'
        f'<span class="session-id">Session</span>'
        f'<span class="session-title-text">{_safe(r["title"])}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Row 1 : Summary + Transcript ──
    col_sum, col_tx = st.columns([3, 2], gap="medium")

    with col_sum:
        st.markdown(
            f'<div class="card">'
            f'<div class="card-accent"></div>'
            f'<div class="card-label">◈ Summary</div>'
            f'<div class="card-body">{_safe(r["summary"])}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col_tx:
        with st.expander("Full Transcript", expanded=False):
            st.markdown(
                f'<div class="transcript-scroll">{_safe(r["transcript"])}</div>',
                unsafe_allow_html=True,
            )

    # ── Row 2 : Three extraction columns ──
    c1, c2, c3 = st.columns(3, gap="medium")

    _extractions = [
        (c1, "▸ Action Items",  r["action_items"],   ""),
        (c2, "◆ Key Decisions", r["key_decisions"],  "teal"),
        (c3, "? Open Questions",r["open_questions"], "red"),
    ]
    for col, label, body, accent in _extractions:
        with col:
            st.markdown(
                f'<div class="card">'
                f'<div class="card-accent {accent}"></div>'
                f'<div class="card-label">{label}</div>'
                f'<div class="card-body">{_safe(body)}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── RAG Chat ──
    st.markdown(
        '<div class="chat-heading">◈ Chat with your Meeting</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.chat_history:
        chat_html = '<div class="chat-wrap">'
        for msg in st.session_state.chat_history:
            role = msg.get("role", "")
            content = _safe(msg.get("content", ""))
            if role == "user":
                chat_html += (
                    f'<div class="cmsg">'
                    f'<span class="cmsg-label you">You</span>'
                    f'<div class="cbubble you">{content}</div>'
                    f'</div>'
                )
            else:
                chat_html += (
                    f'<div class="cmsg">'
                    f'<span class="cmsg-label bot">◈ Meridian</span>'
                    f'<div class="cbubble bot">{content}</div>'
                    f'</div>'
                )
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="card" style="text-align:center;padding:1.75rem">'
            '<div style="font-family:var(--mono);font-size:0.72rem;color:var(--text-dim);'
            'letter-spacing:0.12em;text-transform:uppercase">'
            'Ask anything about the meeting transcript'
            '</div></div>',
            unsafe_allow_html=True,
        )

    # Chat input row
    inp_col, btn_col = st.columns([5, 1], gap="small")
    with inp_col:
        user_input = st.text_input(
            "question",
            placeholder="What decisions were made? Who owns the follow-ups?",
            label_visibility="collapsed",
            key="chat_input",
        )
    with btn_col:
        send_btn = st.button("Send", use_container_width=True, key="send_btn")

    if send_btn and user_input and user_input.strip():
        query = user_input.strip()
        with st.spinner("Thinking…"):
            try:
                answer = ask_question(r["rag_chain"], query)
            except Exception as exc:
                answer = f"[Error retrieving answer: {exc}]"
        st.session_state.chat_history.append({"role": "user",      "content": query})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("Clear conversation", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

# ──────────────────────────────────────────────────────────────────────────────
# EMPTY STATE
# ──────────────────────────────────────────────────────────────────────────────
else:
    st.markdown(
        '<div class="empty-state">'
        '<div class="empty-glyph">◈</div>'
        '<div class="empty-title">Nothing analysed yet</div>'
        '<div class="empty-hint">'
        'Paste a YouTube URL or local file path in the sidebar,<br>'
        'choose the audio language, then hit <strong>Run Analysis</strong>.'
        '</div>'
        '<div class="pill-row">'
        '<span class="pill pill-a">Transcription</span>'
        '<span class="pill pill-t">Summarisation</span>'
        '<span class="pill pill-r">RAG Chat</span>'
        '<span class="pill pill-r">Action Items</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
