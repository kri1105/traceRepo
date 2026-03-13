import streamlit as st
import os
import re
import base64
import zlib
from src.core.cloner import RepositoryCloner
from src.core.parser import RepositoryParser
from src.core.analyzer import RepositoryAnalyzer

# --- Helper Function for Third-Party Flowchart Rendering ---
def get_kroki_url(mermaid_code):
    try:
        compressed = zlib.compress(mermaid_code.encode('utf-8'), 9)
        payload = base64.urlsafe_b64encode(compressed).decode('ascii')
        return f"https://kroki.io/mermaid/svg/{payload}"
    except Exception:
        return None

# --- Page Config ---
st.set_page_config(
    page_title="traceRepo", 
    page_icon="📖", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

st.title("📖 traceRepo")
st.markdown("Understand any GitHub repository's workflow instantly.")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("Settings")
    repo_url = st.text_input("GitHub Repository URL", placeholder="https://github.com/user/repo")
    analyze_button = st.button("Analyze Workflow", type="primary")
    st.divider()
    st.info("Paste a GitHub link above to generate a visual flow of the code logic.")

# --- Main Logic ---
if analyze_button and repo_url:
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    target_dir = os.path.join("data", "repos", repo_name)

    with st.status("Processing Repository...", expanded=True) as status:
        cloner = RepositoryCloner(repo_url, target_dir)
        cloner.clone_repository()
        parser = RepositoryParser(target_dir)
        files_data = parser.get_all_files()
        analyzer = RepositoryAnalyzer()
        report = analyzer.analyze_repository(files_data)
        status.update(label="Analysis Complete!", state="complete", expanded=False)

    st.divider()
    st.header(f"Project Workflow: {repo_name}")
    
    # Extract Mermaid Graph
    mermaid_match = re.search(r"```mermaid\s+(.*?)\s+```", report, re.DOTALL)
    
    if mermaid_match:
        mermaid_code = mermaid_match.group(1).strip().replace("|>", "|").replace("()", "")
        kroki_url = get_kroki_url(mermaid_code)
        
        if kroki_url:
            st.subheader("🛠️ Architecture Map")

            # --- NAVIGATION CONTROLS (Moved here from Sidebar) ---
            # Using columns to keep the UI tight and organized
            ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 1, 1], vertical_alignment="bottom")
            
            with ctrl_col1:
                graph_height = st.slider("Adjust Map Height (px)", 300, 1200, 500)
            
            with ctrl_col2:
                st.markdown(f"🔗 [Open Full Image]({kroki_url})")
            
            with ctrl_col3:
                st.markdown(f"📥 [Download SVG]({kroki_url})")

            # --- THE SCROLLABLE CONTAINER ---
            html_viewer = f"""
            <div style="
                height: {graph_height}px; 
                overflow: auto; 
                border: 1px solid #d1d5db; 
                border-radius: 10px; 
                padding: 15px;
                background-color: white;
                display: flex;
                justify-content: center;
                align-items: flex-start;
            ">
                <img src="{kroki_url}" style="max-width: none; height: auto;" />
            </div>
            """
            st.markdown(html_viewer, unsafe_allow_html=True)
            st.caption("Scroll inside the box to explore the full architecture.")
        
        # Clean text report below
        clean_report = re.sub(r"```mermaid.*?```", "", report, flags=re.DOTALL)
        st.markdown(clean_report)
    else:
        st.markdown(report)

elif analyze_button and not repo_url:
    st.error("Please enter a valid GitHub URL.")