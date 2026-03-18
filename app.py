import streamlit as st
import streamlit.components.v1 as components
import os
import re
import base64
import zlib
from src.core.cloner import RepositoryCloner
from src.core.parser import RepositoryParser
from src.core.analyzer import RepositoryAnalyzer

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_kroki_url(mermaid_code: str) -> str | None:
    try:
        compressed = zlib.compress(mermaid_code.encode("utf-8"), 9)
        payload = base64.urlsafe_b64encode(compressed).decode("ascii")
        return f"https://kroki.io/mermaid/svg/{payload}"
    except Exception:
        return None


def clean_report(report: str) -> str:
    """Strip mermaid fences and unwanted section headings from the LLM report."""
    text = re.sub(r"```mermaid.*?```", "", report, flags=re.DOTALL)
    text = re.sub(r"(?i)\n*#+\s*Visual Graph\s*\n*.*?(?=\n#|$)", "", text, flags=re.DOTALL)
    text = re.sub(r"(?i)\n*#+\s*Hub\s*\n*.*?(?=\n#|$)", "", text, flags=re.DOTALL)
    return text.strip()


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="traceRepo — Visualize Any Codebase",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Global CSS — injected into the parent frame so it persists across reruns
# ---------------------------------------------------------------------------

components.html("""
<!DOCTYPE html><html><head>
<script>
const css = `
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

  html, body, [class*="css"], p, div, span, h1, h2, h3 {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  }

  /* ── Background: dark gradient that NEVER gets overridden ── */
  .stApp,
  .stApp > div,
  section[data-testid="stMain"],
  section[data-testid="stMain"] > div {
    background: linear-gradient(160deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
    background-attachment: fixed !important;
  }

  .block-container { padding: 0 !important; max-width: 100% !important; }

  /* Center markdown containers (hero) while keeping analysis cards left-aligned */
  [data-testid="stMarkdownContainer"],
  [data-testid="stMarkdownContainer"] > div { width: 100% !important; text-align: center !important; }

  /* ── Text input ── */
  div[data-testid="stTextInput"] > div > div > input {
    background: #1e293b !important;
    border: 1.5px solid #475569 !important;
    border-radius: 14px !important;
    color: #ffffff !important;
    font-size: 1rem !important;
    padding: 16px 20px !important;
    caret-color: #818cf8 !important;
    box-shadow: none !important;
  }
  div[data-testid="stTextInput"] > div > div > input::placeholder { color: #94a3b8 !important; }
  div[data-testid="stTextInput"] > div > div > input:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.25) !important;
    background: #0f172a !important;
  }
  div[data-testid="stTextInput"] label { display: none !important; }

  /* ── Primary button ── */
  .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    color: #fff !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    padding: 14px 28px !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
  }
  .stButton > button[kind="primary"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 18px 36px -10px rgba(99,102,241,0.55) !important;
  }
  .stButton > button[kind="primary"]:active { transform: translateY(-1px) !important; }

  /* ── Status widget: hide default SVG arrow, inject emoji via ::before ── */
  [data-testid="stStatusWidget"] summary svg,
  [data-testid="stExpander"] summary svg,
  details summary svg { display: none !important; }

  /* Running state  → show → */
  [data-testid="stStatusWidget"][data-state="running"] summary::before,
  details[open] summary::before { content: "→ "; font-size: 1.1rem; }

  /* Complete state → show ↓ */
  [data-testid="stStatusWidget"][data-state="complete"] summary::before { content: "↓ "; font-size: 1.1rem; }

  /* ── Feature pills ── */
  .pills { display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; padding: 28px 24px 48px; }
  .pill {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 100px; color: #94a3b8;
    font-size: 0.8rem; font-weight: 500; padding: 7px 16px;
    display: inline-flex; align-items: center; gap: 7px;
  }
  .pdot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }

  /* ── Stats bar ── */
  .stats-bar {
    background: rgba(255,255,255,0.03);
    border-top: 1px solid rgba(255,255,255,0.08);
    border-bottom: 1px solid rgba(255,255,255,0.08);
    padding: 32px 24px;
    display: flex; justify-content: center; gap: 72px; flex-wrap: wrap;
  }
  .stat-item { text-align: center; }
  .stat-value { font-size: 1.9rem; font-weight: 800; color: #f8fafc; line-height: 1; }
  .stat-value span {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  }
  .stat-label { font-size: 0.72rem; font-weight: 600; color: #94a3b8; margin-top: 5px; text-transform: uppercase; letter-spacing: 0.09em; }

  /* ── Results header ── */
  .results-header { padding: 56px 0 32px; text-align: center; }
  .results-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: linear-gradient(135deg, #ede9fe, #ddd6fe);
    border-radius: 100px; color: #6d28d9;
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
    padding: 5px 14px; margin-bottom: 14px;
  }
  .results-title { font-size: 2.2rem; font-weight: 800; color: #ffffff; letter-spacing: -0.03em; margin-bottom: 6px; }
  .results-title code {
    font-family: 'SF Mono','Fira Code', monospace;
    color: #a5b4fc; background: rgba(99,102,241,0.15);
    padding: 2px 12px; border-radius: 8px; font-size: 1.9rem;
  }
  .results-sub { font-size: 0.95rem; color: #a1a1aa; }

  /* ── Map card ── */
  .map-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 20px; overflow: hidden; box-shadow: 0 4px 24px -8px rgba(0,0,0,0.08); margin-bottom: 8px; }
  .map-header { background: #f8fafc; border-bottom: 1px solid #e2e8f0; padding: 14px 20px; display: flex; align-items: center; gap: 7px; }
  .mac { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }

  /* ── Analysis card ── */
  div[data-testid="stVerticalBlock"]:has(.analysis-box-marker) {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 36px 48px;
    box-shadow: 0 4px 24px -8px rgba(0,0,0,0.07);
    margin-top: 16px;
  }
  div[data-testid="stVerticalBlock"]:has(.analysis-box-marker) * { color: #0f172a !important; text-align: left !important; }
  div[data-testid="stVerticalBlock"]:has(.analysis-box-marker) h3 {
    color: #1a1a2e !important;
    border-bottom: 2px solid #f1f5f9;
    padding-bottom: 12px; margin-bottom: 20px;
  }

  /* ── Hide Streamlit chrome ── */
  #MainMenu, footer, header, .stDeployButton { visibility: hidden; display: none; }
  .stMarkdown a.header-anchor { display: none !important; }
`;

const old = window.parent.document.getElementById('tracerepo-styles');
if (old) old.remove();
const el = window.parent.document.createElement('style');
el.id = 'tracerepo-styles';
el.textContent = css;
window.parent.document.head.appendChild(el);
</script>
</head><body style="margin:0;padding:0;overflow:hidden;background:transparent;"></body></html>
""", height=0)

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------

st.markdown("""
<div style="width:100%;box-sizing:border-box;padding:80px 24px 56px;text-align:center;">
  <div style="display:inline-block;background:rgba(99,102,241,0.18);border:1px solid rgba(99,102,241,0.38);color:#a5b4fc;font-size:0.7rem;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;padding:6px 18px;border-radius:100px;margin-bottom:28px;">✦ Code Intelligence</div>
  <h1 style="font-size:clamp(2.6rem,5.5vw,4.8rem);font-weight:900;line-height:1.06;letter-spacing:-0.03em;color:#fff;margin:0 auto 20px;max-width:820px;text-align:center;">
    See how any repo<br>
    <span style="background:linear-gradient(90deg,#818cf8,#c084fc,#e879f9);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">actually works.</span>
  </h1>
  <p style="font-size:1.1rem;color:#94a3b8;max-width:500px;margin:0 auto;line-height:1.8;text-align:center;">
    Paste a GitHub URL and get a beautiful, interactive architecture map of the entire codebase — instantly.
  </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

_, sc, _ = st.columns([1, 2.2, 1])
with sc:
    repo_url = st.text_input("url", placeholder="https://github.com/user/repo", label_visibility="collapsed")
    analyze_button = st.button("🔍  Analyze Repository", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Feature pills
# ---------------------------------------------------------------------------

st.markdown("""
<div class="pills">
  <span class="pill"><span class="pdot" style="background:#34d399"></span>Any public repo</span>
  <span class="pill"><span class="pdot" style="background:#60a5fa"></span>Interactive flowchart</span>
  <span class="pill"><span class="pdot" style="background:#c084fc"></span>Deep code analysis</span>
  <span class="pill"><span class="pdot" style="background:#f472b6"></span>SVG export</span>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Stats bar
# ---------------------------------------------------------------------------

st.markdown("""
<div class="stats-bar">
  <div class="stat-item">
    <div class="stat-value"><span>&lt; 60s</span></div>
    <div class="stat-label">Analysis Time</div>
  </div>
  <div class="stat-item">
    <div class="stat-value"><span>SVG</span></div>
    <div class="stat-label">Export Format</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

if analyze_button and not repo_url:
    _, ecol, _ = st.columns([1, 2, 1])
    with ecol:
        st.error("⚠️  Please enter a valid GitHub repository URL.")

elif analyze_button and repo_url:
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    target_dir = os.path.join("data", "repos", repo_name)

    _, pc, _ = st.columns([0.05, 0.90, 0.05])
    with pc:
        with st.status("⚙️  Analyzing repository…", expanded=True) as status:
            cloner = RepositoryCloner(repo_url, target_dir)
            cloner.clone_repository()

            parser = RepositoryParser(target_dir)
            files_data = parser.get_all_files()

            analyzer = RepositoryAnalyzer()
            report = analyzer.analyze_repository(files_data)

            status.update(label="✅  Analysis complete!", state="complete", expanded=False)

    # Results header
    st.markdown(f"""
    <div class="results-header">
      <div class="results-badge">✦ Results</div>
      <div class="results-title">Architecture of <code>{repo_name}</code></div>
      <div class="results-sub">Here's what was found inside this repository.</div>
    </div>
    """, unsafe_allow_html=True)

    mermaid_match = re.search(r"```mermaid\s+(.*?)\s+```", report, re.DOTALL)

    _, mc, _ = st.columns([0.05, 0.90, 0.05])
    with mc:
        # ── Diagram ──
        if mermaid_match:
            mermaid_code = mermaid_match.group(1).strip().replace("|>", "|").replace("()", "")
            kroki_url = get_kroki_url(mermaid_code)

            if kroki_url:
                cc1, cc2, cc3 = st.columns([3, 1, 1], vertical_alignment="bottom")
                with cc1:
                    graph_height = st.slider("Map height (px)", 350, 1200, 560)
                with cc2:
                    st.link_button("🔗 Full Image", kroki_url, use_container_width=True)
                with cc3:
                    st.link_button("📥 Download SVG", kroki_url, use_container_width=True)

                st.markdown(f"""
                <div class="map-card">
                  <div class="map-header">
                    <span class="mac" style="background:#ff5f57;"></span>
                    <span class="mac" style="background:#febc2e;"></span>
                    <span class="mac" style="background:#28c840;"></span>
                    <span style="margin-left:12px;font-size:0.8rem;color:#94a3b8;font-weight:500;">Architecture Map — {repo_name}</span>
                  </div>
                  <div style="height:{graph_height}px;overflow:auto;background:#fafafa;display:flex;justify-content:center;align-items:flex-start;padding:20px;">
                    <img src="{kroki_url}" style="max-width:none;height:auto;" />
                  </div>
                </div>
                <p style="text-align:center;color:#94a3b8;font-size:0.8rem;margin-top:10px;">
                  Scroll inside the frame to explore the full architecture
                </p>
                """, unsafe_allow_html=True)

        # ── Analysis text ──
        with st.container():
            st.markdown('<div class="analysis-box-marker"></div>', unsafe_allow_html=True)
            st.markdown(f"### Detailed Analysis\n\n{clean_report(report)}")
            st.markdown("<br><br>", unsafe_allow_html=True)