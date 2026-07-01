import os
import tempfile
import requests
import streamlit as st
from backend.utils.export_service import ExportService
from backend.core.logger import logger

logger.info("Streamlit started")


# Configure the Streamlit page layout and title
st.set_page_config(
    page_title="AI Multi-Agent Research Writer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State values where appropriate
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "style" not in st.session_state:
    st.session_state.style = "Academic"
if "depth" not in st.session_state:
    st.session_state.depth = "Standard"
if "result" not in st.session_state:
    st.session_state.result = None

# Configure backend endpoint URL
backend_host = os.environ.get("BACKEND_HOST", "localhost")
if backend_host == "0.0.0.0":
    backend_host = "localhost"
backend_port = os.environ.get("BACKEND_PORT", "8000")
api_v1_str = os.environ.get("API_V1_STR", "/api/v1")
backend_url = f"http://{backend_host}:{backend_port}{api_v1_str}/research"

# --- Sidebar Layout ---
st.sidebar.title("AI Research Writer")
st.sidebar.markdown("---")
# Theme/logo placeholder
st.sidebar.info("🎨 Theme / Logo Placeholder")
st.sidebar.markdown("---")
# About section
st.sidebar.markdown(
    """
    ### About
    This platform simulates a collaborative team of specialized AI agents:
    - **Planner**: Outlines sections.
    - **Researcher**: Queries web/memory.
    - **Writer**: Drafts content.
    - **Reviewer**: Evaluates quality.
    - **Editor**: Refines the draft.
    """
)

# --- Main Page Layout ---
st.title("📝 AI Multi-Agent Research Writer")
st.markdown("Generate publication-ready technical and academic research reports autonomously.")
st.markdown("---")

# Main page inputs
col_style, col_depth = st.columns(2)
with col_style:
    st.session_state.style = st.selectbox(
        "Writing Style",
        ["Academic", "Technical", "Blog", "Business", "Simple"],
        index=["Academic", "Technical", "Blog", "Business", "Simple"].index(st.session_state.style)
    )
with col_depth:
    st.session_state.depth = st.selectbox(
        "Research Depth",
        ["Brief", "Standard", "Detailed"],
        index=["Brief", "Standard", "Detailed"].index(st.session_state.depth)
    )

st.session_state.topic = st.text_input(
    "Research Topic",
    value=st.session_state.topic,
    placeholder="Enter the topic you want to research (e.g., Quantum Computing, CRISPR Gene Editing)..."
)

col_buttons = st.columns([1, 4])
with col_buttons[0]:
    generate_clicked = st.button("Generate Research", type="primary", use_container_width=True)
with col_buttons[1]:
    # Clear button to reset the state
    if st.button("Clear Results", use_container_width=True):
        st.session_state.result = None
        st.rerun()

st.markdown("---")

# Generate Action Handlers
if generate_clicked:
    if not st.session_state.topic.strip():
        st.warning("Please enter a valid research topic first.")
    else:
        st.session_state.result = None
        status_placeholder = st.empty()
        status_placeholder.info("Orchestrating AI Research Writer workflow (this may take up to a minute)...")
        
        with st.spinner("Executing planning, research, writing, review, and editing steps..."):
            try:
                response = requests.post(
                    backend_url,
                    json={
                        "topic": st.session_state.topic,
                        "style": st.session_state.style,
                        "depth": st.session_state.depth
                    },
                    timeout=300
                )
                
                if response.status_code == 200:
                    st.session_state.result = response.json()
                    status_placeholder.success("Research report generated successfully!")
                    st.rerun()
                elif response.status_code == 422:
                    detail = response.json().get("detail", "Validation Error")
                    status_placeholder.error(f"Validation error returned by backend: {detail}")
                else:
                    detail = response.text
                    status_placeholder.error(f"Backend returned an unexpected error ({response.status_code}): {detail}")
                    
            except requests.exceptions.ConnectionError:
                status_placeholder.error("Failed to connect to the backend server. Please verify it is running on port 8000.")
            except requests.exceptions.Timeout:
                status_placeholder.error("The request to the backend timed out. Please try again.")
            except Exception as e:
                status_placeholder.error(f"An unexpected error occurred: {e}")

# --- Results UI Sections ---
has_result = st.session_state.result is not None
result = st.session_state.result if has_result else {}

st.subheader("Research Progress")
if has_result:
    st.progress(100, text="Generation complete!")
else:
    st.progress(0, text="Awaiting execution... Click 'Generate Research' to start.")

st.markdown("---")

if has_result:
    st.header(result.get("title", "Research Report"))
    
    col_article, col_review = st.columns([3, 1])
    
    with col_article:
        st.subheader("Final Article")
        st.markdown(result.get("final_markdown", ""))
        
    with col_review:
        st.subheader("Review Score")
        review = result.get("review", {})
        score = review.get("score", "N/A")
        st.metric(
            label="Quality Rating",
            value=str(score),
            help="Evaluated by the Reviewer Agent on a scale of 0-100."
        )
        
        st.subheader("Strengths")
        strengths = review.get("strengths", [])
        if strengths:
            for s in strengths:
                st.markdown(f"- {s}")
        else:
            st.markdown("*No specific strengths noted.*")
            
        st.subheader("Issues")
        issues = review.get("issues", [])
        if issues:
            for i in issues:
                st.markdown(f"- {i}")
        else:
            st.markdown("*No specific issues identified.*")
            
        st.subheader("Suggestions")
        suggestions = review.get("suggestions", [])
        if suggestions:
            for sug in suggestions:
                st.markdown(f"- {sug}")
        else:
            st.markdown("*No explicit suggestions.*")

        st.subheader("Changes Applied")
        changes = result.get("changes_applied", [])
        if changes:
            for c in changes:
                st.markdown(f"- {c}")
        else:
            st.markdown("*No changes applied.*")

    st.markdown("---")
    
    col_sources, col_memory = st.columns(2)
    
    with col_sources:
        st.subheader("Sources & Citations")
        sources = result.get("sources", [])
        if sources:
            for src in sources:
                st.markdown(f"- [{src.get('title', 'Source')}]({src.get('url', '#')})")
        else:
            st.info("Citations and sources are embedded directly inside the Markdown text.")
            
    with col_memory:
        st.subheader("Memory Hits")
        memory_hits = result.get("memory_hits", [])
        if memory_hits:
            for hit in memory_hits:
                st.markdown(f"- {hit}")
        else:
            st.info("No explicit memory hits returned by the API; vector memory is utilized internally by the agent during generation.")

else:
    col_article, col_review = st.columns([3, 1])
    with col_article:
        st.subheader("Final Article")
        st.text_area(
            label="Report Content (Markdown Preview)",
            value="The final generated article in markdown will appear here.",
            height=300,
            disabled=True
        )
    with col_review:
        st.subheader("Review Score")
        st.metric(label="Quality Rating", value="N/A")

    st.markdown("---")
    
    col_sources, col_memory = st.columns(2)
    with col_sources:
        st.subheader("Sources & Citations")
        st.info("Web search citations used by the researcher will be listed here.")
    with col_memory:
        st.subheader("Memory Hits")
        st.info("RAG search results retrieved from local ChromaDB memory will be displayed here.")

st.markdown("---")

# --- Export Report ---
st.subheader("Export Report")
export_col1, export_col2, export_col3 = st.columns(3)

markdown_data = b""
pdf_data = b""
docx_data = b""
report_title = "report"

if has_result:
    report_title = result.get("title", "report")
    # Sanitize title for filename
    report_title = "".join(c for c in report_title if c.isalnum() or c in (" ", "_", "-")).strip()
    report_title = report_title.replace(" ", "_")
    
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            md_path = os.path.join(tmp_dir, "report.md")
            pdf_path = os.path.join(tmp_dir, "report.pdf")
            docx_path = os.path.join(tmp_dir, "report.docx")
            
            # Generate exports using ExportService
            ExportService.export_markdown(result, md_path)
            ExportService.export_pdf(result, pdf_path)
            ExportService.export_docx(result, docx_path)
            
            # Read files back into memory
            if os.path.exists(md_path):
                with open(md_path, "rb") as f:
                    markdown_data = f.read()
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_data = f.read()
            if os.path.exists(docx_path):
                with open(docx_path, "rb") as f:
                    docx_data = f.read()
    except Exception as e:
        st.error(f"⚠️ Export failed: Unable to generate downloadable documents. Error: {str(e)}")

# Fallback to string encode if empty (e.g. if mocked or error)
if not markdown_data and has_result:
    markdown_data = result.get("final_markdown", "").encode("utf-8")

with export_col1:
    st.download_button(
        "Download PDF",
        data=pdf_data,
        file_name=f"{report_title}.pdf",
        mime="application/pdf",
        disabled=not has_result,
        use_container_width=True
    )
with export_col2:
    st.download_button(
        "Download DOCX",
        data=docx_data,
        file_name=f"{report_title}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        disabled=not has_result,
        use_container_width=True
    )
with export_col3:
    st.download_button(
        "Download Markdown",
        data=markdown_data,
        file_name=f"{report_title}.md",
        mime="text/markdown",
        disabled=not has_result,
        use_container_width=True
    )
