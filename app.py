import streamlit as st
import os
import re # Added for finding the Mermaid graph in the text
from src.core.cloner import RepositoryCloner
from src.core.parser import RepositoryParser
from src.core.analyzer import RepositoryAnalyzer

# --- Page Config ---
# 'initial_sidebar_state="expanded"' ensures the sidebar is open by default
st.set_page_config(
    page_title="Better-README", 
    page_icon="📖", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

st.title("📖 Better-README")
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
        # 1. Clone
        st.write("Cloning repository...")
        cloner = RepositoryCloner(repo_url, target_dir)
        cloner.clone_repository()
        
        # 2. Parse
        st.write("Parsing files...")
        parser = RepositoryParser(target_dir)
        files_data = parser.get_all_files()
        
        # 3. Analyze
        st.write("AI Analysis in progress...")
        analyzer = RepositoryAnalyzer()
        report = analyzer.analyze_repository(files_data)
        
        status.update(label="Analysis Complete!", state="complete", expanded=False)

    # --- Display Results ---
    st.divider()
    st.header(f"Project Workflow: {repo_name}")
    
    # 4. Extract and Display the Mermaid Graph
    # This looks for the ```mermaid ... ``` block in the AI response
    mermaid_match = re.search(r"```mermaid\s+(.*?)\s+```", report, re.DOTALL)
    
    if mermaid_match:
        st.subheader("Visual Flowchart")
        # We wrap it back in mermaid blocks so st.markdown renders it as a graph
        st.markdown(f"```mermaid\n{mermaid_match.group(1)}\n```")
        
        # Show the text report without the mermaid code block to avoid duplication
        clean_report = re.sub(r"```mermaid.*?```", "", report, flags=re.DOTALL)
        st.markdown(clean_report)
    else:
        # Fallback if no mermaid block is found
        st.markdown(report)

elif analyze_button and not repo_url:
    st.error("Please enter a valid GitHub URL.")