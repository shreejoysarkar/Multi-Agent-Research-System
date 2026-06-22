"""
Streamlit UI for the Multi-Agent Research Pipeline
====================================================
Run with:  streamlit run app.py
"""

import base64
import os
import threading
import time
from pathlib import Path
from datetime import datetime

import streamlit as st

# ── Page config (must be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="AI Research System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
/* ── Google Font ─────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

/* ── Root variables ──────────────────────────────────────────────────── */
:root {
    --bg-primary: #0a0e1a;
    --bg-secondary: #111827;
    --bg-card: rgba(17, 24, 39, 0.65);
    --border-subtle: rgba(99, 102, 241, 0.15);
    --border-glow: rgba(99, 102, 241, 0.4);
    --accent-indigo: #6366f1;
    --accent-violet: #8b5cf6;
    --accent-cyan: #22d3ee;
    --accent-emerald: #34d399;
    --accent-rose: #f43f5e;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
}

/* ── Global bg ───────────────────────────────────────────────────────── */
.stApp {
    background: linear-gradient(135deg, var(--bg-primary) 0%, #0f172a 50%, #1e1b4b 100%);
    color: var(--text-primary);
}

/* ── Hide Streamlit defaults ─────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem; padding-bottom: 2rem; }

/* ── Hero banner ─────────────────────────────────────────────────────── */
.hero-container {
    position: relative;
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 2rem;
    border: 1px solid var(--border-subtle);
}
.hero-container img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    filter: brightness(0.5);
}
.hero-overlay {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: linear-gradient(180deg, rgba(10,14,26,0.3) 0%, rgba(10,14,26,0.85) 100%);
}
.hero-overlay h1 {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent-cyan), var(--accent-indigo), var(--accent-violet));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: -0.5px;
}
.hero-overlay p {
    color: var(--text-secondary);
    font-size: 1rem;
    margin-top: 0.3rem;
    font-weight: 400;
}

/* ── Glass cards ─────────────────────────────────────────────────────── */
.glass-card {
    background: var(--bg-card);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1rem;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.glass-card:hover {
    border-color: var(--border-glow);
    box-shadow: 0 0 30px rgba(99, 102, 241, 0.08);
}

/* ── Stage cards ─────────────────────────────────────────────────────── */
.stage-card {
    background: var(--bg-card);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: all 0.3s ease;
}
.stage-card.active {
    border-color: var(--accent-indigo);
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.15);
}
.stage-card.done {
    border-color: var(--accent-emerald);
}
.stage-card.failed {
    border-color: var(--accent-rose);
}
.stage-icon {
    font-size: 1.6rem;
    min-width: 40px;
    text-align: center;
}
.stage-label {
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--text-primary);
}
.stage-sub {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-top: 2px;
}

/* ── Progress pill ───────────────────────────────────────────────────── */
.progress-pill {
    display: inline-block;
    padding: 0.25rem 0.8rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.pill-running {
    background: rgba(99, 102, 241, 0.15);
    color: var(--accent-indigo);
    animation: pulse-glow 2s ease-in-out infinite;
}
.pill-done {
    background: rgba(52, 211, 153, 0.15);
    color: var(--accent-emerald);
}
.pill-error {
    background: rgba(244, 63, 94, 0.15);
    color: var(--accent-rose);
}

@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 5px rgba(99,102,241,0.2); }
    50% { box-shadow: 0 0 20px rgba(99,102,241,0.4); }
}

/* ── Stat badges ─────────────────────────────────────────────────────── */
.stat-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}
.stat-badge {
    flex: 1;
    min-width: 160px;
    background: var(--bg-card);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.stat-value {
    font-size: 1.6rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent-cyan), var(--accent-indigo));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stat-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 0.3rem;
}

/* ── Input area ──────────────────────────────────────────────────────── */
.stTextArea textarea {
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    padding: 1rem !important;
    transition: border-color 0.3s ease !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent-indigo) !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important;
}

/* ── Buttons ─────────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-indigo), var(--accent-violet)) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.7rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 0.3px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(99,102,241,0.4) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ── Download button ─────────────────────────────────────────────────── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #059669, var(--accent-emerald)) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 15px rgba(52,211,153,0.3) !important;
}

/* ── Expanders ───────────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}
div[data-testid="stExpander"] {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    overflow: hidden;
}

/* ── Tabs ────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.2rem !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(99,102,241,0.15) !important;
    border-color: var(--accent-indigo) !important;
    color: var(--accent-indigo) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding-top: 1rem;
}

/* ── Scrollable log ──────────────────────────────────────────────────── */
.log-box {
    background: rgba(0,0,0,0.3);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    padding: 1rem;
    max-height: 200px;
    overflow-y: auto;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 0.82rem;
    line-height: 1.7;
    color: var(--text-secondary);
}
.log-box .log-line { margin: 0; }

/* ── Divider ─────────────────────────────────────────────────────────── */
.gradient-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-indigo), var(--accent-violet), transparent);
    border: none;
    margin: 1.5rem 0;
    border-radius: 2px;
}

/* ── Sidebar tweaks ──────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-subtle) !important;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ── Helper: encode image to base64 for inline HTML ───────────────────────────
def img_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ── Hero Banner ──────────────────────────────────────────────────────────────
BANNER_PATH = Path(__file__).parent / "assets" / "hero_banner.png"
if BANNER_PATH.exists():
    b64 = img_to_base64(str(BANNER_PATH))
    st.markdown(
        f"""
        <div class="hero-container">
            <img src="data:image/png;base64,{b64}" alt="banner" />
            <div class="hero-overlay">
                <h1>🔬 Multi-Agent Research System</h1>
                <p>AI-powered research &bull; Search &bull; Scrape &bull; Write &bull; Critique</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div style="text-align:center; padding: 2rem 0 1.5rem;">
            <h1 style="font-size:2.4rem; font-weight:800;
                background: linear-gradient(135deg, #22d3ee, #6366f1, #8b5cf6);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                🔬 Multi-Agent Research System
            </h1>
            <p style="color:#94a3b8;">AI-powered research &bull; Search &bull; Scrape &bull; Write &bull; Critique</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Session state defaults ───────────────────────────────────────────────────
for key, default in {
    "results": None,
    "running": False,
    "logs": [],
    "current_stage": 0,
    "stage_status": ["pending", "pending", "pending", "pending"],
    "error": None,
    "start_time": None,
    "elapsed": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Stage metadata ───────────────────────────────────────────────────────────
STAGES = [
    {"icon": "🔍", "label": "Search Agent",   "desc": "Discovering relevant sources"},
    {"icon": "📄", "label": "Research Agent",  "desc": "Scraping & extracting content"},
    {"icon": "✍️",  "label": "Writer Agent",    "desc": "Drafting the article"},
    {"icon": "🔬", "label": "Critic Agent",    "desc": "Peer-reviewing the article"},
]


def render_stage_tracker():
    """Draw the 4-stage progress cards."""
    for i, s in enumerate(STAGES):
        status = st.session_state.stage_status[i]
        css_class = ""
        badge = ""
        if status == "running":
            css_class = "active"
            badge = '<span class="progress-pill pill-running">Running</span>'
        elif status == "done":
            css_class = "done"
            badge = '<span class="progress-pill pill-done">Done</span>'
        elif status == "failed":
            css_class = "failed"
            badge = '<span class="progress-pill pill-error">Failed</span>'
        else:
            badge = '<span class="progress-pill" style="background:rgba(100,116,139,0.15);color:#64748b;">Pending</span>'

        st.markdown(
            f"""
            <div class="stage-card {css_class}">
                <div class="stage-icon">{s['icon']}</div>
                <div style="flex:1;">
                    <div class="stage-label">{s['label']}</div>
                    <div class="stage-sub">{s['desc']}</div>
                </div>
                {badge}
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Layout ───────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([3, 2], gap="large")


# ── Left column: Input + Results ─────────────────────────────────────────────
with left_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 💡 Enter Your Research Topic")
    topic = st.text_area(
        label="Research topic",
        placeholder="e.g. Latest breakthroughs in quantum computing 2026",
        height=100,
        label_visibility="collapsed",
        key="topic_input",
    )

    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        run_clicked = st.button(
            "🚀  Start Research",
            disabled=st.session_state.running,
            use_container_width=True,
            key="run_btn",
        )
    with col_info:
        if st.session_state.running:
            st.markdown(
                '<span class="progress-pill pill-running" style="margin-top:0.6rem;display:inline-block;">'
                "⏳ Pipeline running…</span>",
                unsafe_allow_html=True,
            )
        elif st.session_state.results and "report" in st.session_state.results:
            st.markdown(
                '<span class="progress-pill pill-done" style="margin-top:0.6rem;display:inline-block;">'
                "✔ Complete</span>",
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Results area ─────────────────────────────────────────────────────
    if st.session_state.results:
        res = st.session_state.results
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        # Stats row
        word_count = len(res.get("report", "").split()) if "report" in res else 0
        source_count = len(res.get("urls", []))
        elapsed = st.session_state.elapsed or 0

        st.markdown(
            f"""
            <div class="stat-row">
                <div class="stat-badge">
                    <div class="stat-value">{word_count:,}</div>
                    <div class="stat-label">Words</div>
                </div>
                <div class="stat-badge">
                    <div class="stat-value">{source_count}</div>
                    <div class="stat-label">Sources</div>
                </div>
                <div class="stat-badge">
                    <div class="stat-value">{elapsed:.0f}s</div>
                    <div class="stat-label">Time</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Tabbed results
        tab_article, tab_critique, tab_sources, tab_raw = st.tabs(
            ["📝 Article", "🔬 Critique", "🔗 Sources", "📦 Raw Data"]
        )

        with tab_article:
            if "report" in res:
                st.markdown(res["report"])
                st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
                st.download_button(
                    label="⬇️  Download Article (.md)",
                    data=res["report"],
                    file_name=f"research_article_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            else:
                st.warning("Article was not generated — a stage may have failed.")

        with tab_critique:
            if "feedback" in res:
                st.markdown(res["feedback"])
            else:
                st.info("Critique not available.")

        with tab_sources:
            source_urls = res.get("urls", [])
            if source_urls:
                for i, url in enumerate(source_urls, 1):
                    st.markdown(f"**{i}.** [{url}]({url})")
            else:
                st.info("No source URLs were extracted from the search results.")

        with tab_raw:
            with st.expander("🔍 Search Results", expanded=False):
                st.text(res.get("search_result", "N/A"))
            with st.expander("📄 Scraped Content", expanded=False):
                st.text(res.get("scraped_content", "N/A"))

    elif st.session_state.error:
        st.error(f"Pipeline error: {st.session_state.error}")


# ── Right column: Pipeline tracker + logs ────────────────────────────────────
with right_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### ⚙️ Pipeline Progress")
    stage_placeholder = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 📋 Live Log")
    log_placeholder = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)

    # Render current state
    with stage_placeholder.container():
        render_stage_tracker()

    if st.session_state.logs:
        log_html = "".join(
            f'<p class="log-line">{line}</p>' for line in st.session_state.logs
        )
        log_placeholder.markdown(
            f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True
        )
    else:
        log_placeholder.markdown(
            '<div class="log-box"><p class="log-line" style="color:#64748b;">'
            "Waiting for pipeline to start…</p></div>",
            unsafe_allow_html=True,
        )


# ── Pipeline execution ───────────────────────────────────────────────────────
def _map_status_to_stage(msg: str) -> None:
    """Parse on_status messages and update stage states."""
    msg_lower = msg.lower()

    if "stage 1" in msg_lower and "search" in msg_lower and "discovering" in msg_lower:
        st.session_state.stage_status = ["running", "pending", "pending", "pending"]
        st.session_state.current_stage = 0
    elif "search complete" in msg_lower:
        st.session_state.stage_status[0] = "done"
    elif "stage 2" in msg_lower and "scraping" in msg_lower:
        st.session_state.stage_status = ["done", "running", "pending", "pending"]
        st.session_state.current_stage = 1
    elif "research complete" in msg_lower:
        st.session_state.stage_status[1] = "done"
    elif "stage 3" in msg_lower and "drafting" in msg_lower:
        st.session_state.stage_status = ["done", "done", "running", "pending"]
        st.session_state.current_stage = 2
    elif "article drafted" in msg_lower:
        st.session_state.stage_status[2] = "done"
    elif "stage 4" in msg_lower and "reviewing" in msg_lower:
        st.session_state.stage_status = ["done", "done", "done", "running"]
        st.session_state.current_stage = 3
    elif "pipeline finished" in msg_lower:
        st.session_state.stage_status = ["done", "done", "done", "done"]
    elif "[X]" in msg or "failed" in msg_lower or "aborting" in msg_lower:
        idx = st.session_state.current_stage
        st.session_state.stage_status[idx] = "failed"


if run_clicked and topic.strip():
    # Reset state
    st.session_state.results = None
    st.session_state.running = True
    st.session_state.logs = []
    st.session_state.current_stage = 0
    st.session_state.stage_status = ["pending", "pending", "pending", "pending"]
    st.session_state.error = None
    st.session_state.start_time = time.time()
    st.session_state.elapsed = None

    def on_status(msg: str):
        """Callback passed to run_pipeline for live updates."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.logs.append(f"[{timestamp}] {msg}")
        _map_status_to_stage(msg)

    try:
        from pipeline import run_pipeline

        results = run_pipeline(topic.strip(), on_status=on_status)
        st.session_state.results = results
        st.session_state.elapsed = time.time() - st.session_state.start_time
    except Exception as e:
        st.session_state.error = str(e)
        idx = st.session_state.current_stage
        st.session_state.stage_status[idx] = "failed"
    finally:
        st.session_state.running = False

    st.rerun()

elif run_clicked and not topic.strip():
    st.toast("⚠️ Please enter a research topic first.", icon="⚠️")


# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align:center; padding:2rem 0 1rem; color:#64748b; font-size:0.78rem;">
        Built with <span style="color:#f43f5e;">♥</span> using LangChain &bull; LangGraph &bull; Groq &bull; Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
