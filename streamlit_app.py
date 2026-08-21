import json
import time
import docx
import streamlit as st

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Pitch to Project | mart Scope Engine",
    page_icon="⚡",
    layout="wide",
)

# -----------------------------------------------------------------------------
# 2. Rich Custom CSS (Glassmorphism, High-Contrast Labels, Hover Animations)
# -----------------------------------------------------------------------------
css_code = """
<style>
/* Page Background Baseline */
.stApp {
    background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%) !important;
}

/* Typography & Headings */
h1, h2, h3 {
    color: #0f172a !important;
    font-weight: 800 !important;
    letter-spacing: -0.025em !important;
}

/* Fix Label & Text Visibility */
div[data-testid="stMarkdownContainer"] p, 
label[data-testid="stWidgetLabel"] p,
div[data-testid="stToggle"] span {
    color: #0f172a !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    text-shadow: 0 1px 1px rgba(255, 255, 255, 0.8);
}

/* Glassmorphism Wrapper for Demo Mode Toggle */
div[data-testid="stToggle"] {
    background: rgba(255, 255, 255, 0.85) !important;
    backdrop-filter: blur(8px) !important;
    padding: 10px 18px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(203, 213, 225, 0.6) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
}

/* Input Cards (Uploaders & Text Area) */
div[data-testid="stFileUploader"], 
div[data-testid="stTextArea"] textarea {
    background: #ffffff !important;
    border: 2px solid #6366f1 !important;
    border-radius: 14px !important;
    padding: 14px !important;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.04) !important;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* Dropzone Interior Styling */
div[data-testid="stFileUploaderDropzone"] {
    background: #f8fafc !important;
    border: 1px dashed #cbd5e1 !important;
    border-radius: 10px !important;
}

/* Glowing Hover & Focus Animations */
div[data-testid="stFileUploader"]:hover, 
div[data-testid="stTextArea"] textarea:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 12px 20px -5px rgba(99, 102, 241, 0.25), 0 0 0 4px rgba(99, 102, 241, 0.15) !important;
    transform: translateY(-3px) scale(1.005) !important;
}

/* Primary Action Buttons */
div.stButton > button {
    background: linear-gradient(135deg, #4f46e5 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 12px 24px !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4) !important;
    transition: all 0.3s ease !important;
    width: 100%;
}

div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(79, 70, 229, 0.55) !important;
    background: linear-gradient(135deg, #4338ca 0%, #1d4ed8 100%) !important;
}

/* Export Download Button Hover State */
div[data-testid="stDownloadButton"] > button:hover {
    background: #16a34a !important;
    color: #ffffff !important;
    border-color: #15803d !important;
    transition: all 0.3s ease;
}

/* Bordered Container Cards for Scope Content */
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-left: 5px solid #6366f1 !important;
    border-radius: 12px !important;
    padding: 20px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
    margin-bottom: 16px !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08) !important;
    transform: translateY(-2px) !important;
}
</style>
"""

st.markdown(css_code, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. Scrolling Ticker Banner
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div style="
        background: linear-gradient(90deg, #1e1b4b 0%, #312e81 100%);
        color: #ffffff;
        padding: 10px 0px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.05rem;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    ">
        <marquee behavior="scroll" direction="left" scrollamount="8">
            ⚡ Smart Scope Handover Engine &nbsp;|&nbsp; Project Intelligence Layer &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ⚡ Smart Scope Handover Engine &nbsp;|&nbsp; Project Intelligence Layer
        </marquee>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 4. App Header & Safe Mode Control
# -----------------------------------------------------------------------------
col_title, col_toggle = st.columns([3, 1])

with col_title:
    st.title("Pitch to Project")
    st.caption("AI-Powered Scope Intelligence & Handover Engine")

with col_toggle:
    demo_mode = st.toggle("Demo Mode (Safe Pitch)", value=True)

# -----------------------------------------------------------------------------
# 5. Mock Data Engine (for Safe Pitch / Demo Mode)
# -----------------------------------------------------------------------------
MOCK_ANALYSIS = {
    "extracted_scope": [
        {
            "module": "AUTHENTICATION & SECURITY",
            "source": "Proposal Page 4, Section 2",
            "points": [
                "Multi-factor authentication (MFA) via SMS/Email.",
                "Role-based access control (RBAC) for Admin and Client roles."
            ]
        },
        {
            "module": "HANDOVER INTELLIGENCE ENGINE",
            "source": "Kickoff Transcript Lines 12-45",
            "points": [
                "Multi-format document parsing (.docx, .txt, tables, media).",
                "Automated gap auditing and structured JSON extraction."
            ]
        }
    ],
    "gaps_and_risks": [
        {
            "severity": "HIGH",
            "type": "Missing SLA",
            "description": "No operational SLA defined for real-time document processing speed."
        },
        {
            "severity": "MEDIUM",
            "type": "Cross-Document Conflict",
            "description": "Kickoff transcript requests 500MB upload support, while SOW specifies a 200MB limit."
        }
    ],
    "jira_user_stories": [
        {
            "title": "Configurable Document Processing Engine",
            "user_role": "Delivery Lead",
            "want_statement": "ingest intake SOWs and transcripts concurrently",
            "so_that_statement": "I can automatically extract system requirements without manual document review",
            "acceptance_criteria": [
                "Given a user uploads .docx or .txt files",
                "When clicking 'Generate Smart Scope'",
                "Then the AI parses and outputs structured scope modules within seconds"
            ]
        }
    ]
}

# Helper to generate downloadable DOCX report
def build_docx_report(data):
    doc = docx.Document()
    doc.add_heading("Pitch to Project - Handover Scope Analysis", 0)
    
    doc.add_heading("1. Extracted Scope", level=1)
    for mod in data.get("extracted_scope", []):
        doc.add_heading(f"Module: {mod['module']}", level=2)
        doc.add_paragraph(f"Source: {mod['source']}")
        for pt in mod["points"]:
            doc.add_paragraph(f"• {pt}")
            
    doc.add_heading("2. Gaps & Risk Audit", level=1)
    for gap in data.get("gaps_and_risks", []):
        doc.add_paragraph(f"[{gap['severity']}] {gap['type']}: {gap['description']}")

    doc.add_heading("3. Jira User Stories", level=1)
    for story in data.get("jira_user_stories", []):
        doc.add_heading(story['title'], level=2)
        doc.add_paragraph(f"As a {story['user_role']}, I want to {story['want_statement']} so that {story['so_that_statement']}.")
        doc.add_paragraph("Acceptance Criteria:")
        for ac in story.get("acceptance_criteria", []):
            doc.add_paragraph(f"  - {ac}")

    doc_path = "/tmp/Handover_Report.docx"
    doc.save(doc_path)
    with open(doc_path, "rb") as file:
        return file.read()

# -----------------------------------------------------------------------------
# 6. Main Dual Column Layout
# -----------------------------------------------------------------------------
left_col, right_col = st.columns([1, 1], gap="medium")

with left_col:
    st.header("1. Intake Documents & Media")
    
    sow_files = st.file_uploader(
        "Proposals / SOWs (.docx)", 
        type=["docx"], 
        accept_multiple_files=True
    )
    
    notes_files = st.file_uploader(
        "Transcripts / Notes (.txt)", 
        type=["txt"], 
        accept_multiple_files=True
    )
    
    media_files = st.file_uploader(
        "Diagrams & Media (.png, .jpg, .mp4, .mp3)", 
        type=["png", "jpg", "mp4", "mp3"], 
        accept_multiple_files=True
    )
    
    loose_notes = st.text_area(
        "Or Paste Loose Client Emails / Notes:", 
        height=120, 
        placeholder="Paste kickoff notes or client requirements here..."
    )
    
    generate_btn = st.button("⚡ GENERATE SMART SCOPE")

with right_col:
    st.header("2. AI Scope & Handover Analysis")

    # Trigger analysis with a progress bar and spinner badge
    if generate_btn:
        progress_text = "Parsing intake materials and extracting functional scope..."
        my_bar = st.progress(0, text=progress_text)

        # Animated progress step sequence
        for percent_complete in range(100):
            time.sleep(0.012)
            my_bar.progress(percent_complete + 1, text=progress_text)

        # Clear progress bar when 100% complete
        my_bar.empty()

        # Processing spinner wrapper
        with st.spinner("Finalizing Jira user stories and risk audit..."):
            if demo_mode:
                st.session_state["analysis_data"] = MOCK_ANALYSIS
            else:
                # Place live Gemini API call logic here when ready
                st.session_state["analysis_data"] = MOCK_ANALYSIS

            st.toast("⚡ Analysis Complete!", icon="✅")

    # Default fallback state
    if "analysis_data" not in st.session_state:
        st.session_state["analysis_data"] = MOCK_ANALYSIS

    data = st.session_state["analysis_data"]

    # Navigation Tabs
    tab_scope, tab_risks, tab_jira = st.tabs(
        ["Extracted Scope", "Missing Items & Risks", "Jira User Stories"]
    )
    
    with tab_scope:
        for item in data["extracted_scope"]:
            with st.container(border=True):
                st.markdown(f"### 📌 MODULE: {item['module']}")
                st.caption(f"Source: {item['source']}")
                for pt in item["points"]:
                    st.markdown(f"• {pt}")
                    
    with tab_risks:
        for risk in data["gaps_and_risks"]:
            with st.container(border=True):
                st.markdown(f"**[{risk['severity']}] {risk['type']}**")
                st.write(risk["description"])

    with tab_jira:
        for story in data["jira_user_stories"]:
            with st.container(border=True):
                st.markdown(f"### 🚀 {story['title']}")
                st.markdown(f"**As a** {story['user_role']}, **I want to** {story['want_statement']} **so that** {story['so_that_statement']}.")
                st.markdown("**Acceptance Criteria:**")
                for ac in story["acceptance_criteria"]:
                    st.markdown(f"- `{ac}`")

    # Download Button
    st.divider()
    docx_bytes = build_docx_report(data)
    st.download_button(
        label="📄 Export Handover Report (.docx)",
        data=docx_bytes,
        file_name="Pitch_to_Project_Handover_Report.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True
    )