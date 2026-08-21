import json
import time
import docx
import streamlit as st
from google import genai
from google.genai import types

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Pitch to Project | Vibrant Scope Engine",
    page_icon="⚡",
    layout="wide",
)

# Initialize Gemini Client (Uses GEMINI_API_KEY from st.secrets)
@st.cache_resource
def get_gemini_client():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        return genai.Client(api_key=api_key)
    except Exception:
        return None

client = get_gemini_client()

# -----------------------------------------------------------------------------
# 2. Helper Functions for Live Parsing
# -----------------------------------------------------------------------------
def extract_text_from_uploads(sow_files, notes_files, loose_notes):
    """Extracts raw text content from uploaded files and text area."""
    combined_text = ""
    
    if sow_files:
        for file in sow_files:
            doc = docx.Document(file)
            combined_text += f"\n--- FILE: {file.name} ---\n"
            for para in doc.paragraphs:
                if para.text.strip():
                    combined_text += para.text + "\n"
                    
    if notes_files:
        for file in notes_files:
            combined_text += f"\n--- FILE: {file.name} ---\n"
            combined_text += file.read().decode("utf-8") + "\n"
            
    if loose_notes and loose_notes.strip():
        combined_text += f"\n--- LOOSE NOTES / EMAILS ---\n{loose_notes}\n"
        
    return combined_text

def analyze_with_gemini(raw_text):
    """Calls Gemini API (gemini-3.6-flash) using structured JSON output mode."""
    if not client:
        st.error("GEMINI_API_KEY is missing in Streamlit Secrets! Falling back to mock data.")
        return None

    prompt = f"""
    You are an expert IT Delivery Lead and Systems Analyst. 
    Analyze the following project intake materials and generate a structured JSON analysis.

    Return ONLY a valid JSON object matching this schema:
    {{
      "extracted_scope": [
        {{
          "module": "MODULE NAME",
          "source": "Source file and paragraph/line",
          "points": ["Requirement detail 1", "Requirement detail 2"]
        }}
      ],
      "gaps_and_risks": [
        {{
          "severity": "HIGH/MEDIUM/LOW",
          "type": "Risk Category (e.g., Missing SLA, Conflict)",
          "description": "Detailed explanation"
        }}
      ],
      "jira_user_stories": [
        {{
          "title": "Short Story Title",
          "user_role": "Target User",
          "want_statement": "action to perform",
          "so_that_statement": "business value",
          "acceptance_criteria": [
            "Given condition...",
            "When action...",
            "Then result..."
          ]
        }}
      ]
    }}

    INTAKE MATERIALS:
    {raw_text}
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Gemini API Error: {str(e)}")
        return None

def build_docx_report(data):
    doc = docx.Document()
    doc.add_heading("Pitch to Project - Handover Scope Analysis", 0)
    
    doc.add_heading("1. Extracted Scope", level=1)
    for mod in data.get("extracted_scope", []):
        doc.add_heading(f"Module: {mod.get('module', 'General')}", level=2)
        doc.add_paragraph(f"Source: {mod.get('source', 'Uploaded Docs')}")
        for pt in mod.get("points", []):
            doc.add_paragraph(f"• {pt}")
            
    doc.add_heading("2. Gaps & Risk Audit", level=1)
    for gap in data.get("gaps_and_risks", []):
        doc.add_paragraph(f"[{gap.get('severity', 'INFO')}] {gap.get('type', 'Risk')}: {gap.get('description', '')}")

    doc.add_heading("3. Jira User Stories", level=1)
    for story in data.get("jira_user_stories", []):
        doc.add_heading(story.get('title', 'User Story'), level=2)
        doc.add_paragraph(f"As a {story.get('user_role', 'User')}, I want to {story.get('want_statement', '')} so that {story.get('so_that_statement', '')}.")
        doc.add_paragraph("Acceptance Criteria:")
        for ac in story.get("acceptance_criteria", []):
            doc.add_paragraph(f"  - {ac}")

    doc_path = "/tmp/Handover_Report.docx"
    doc.save(doc_path)
    with open(doc_path, "rb") as file:
        return file.read()

# -----------------------------------------------------------------------------
# 3. High-Energy Colorful Custom CSS
# -----------------------------------------------------------------------------
css_code = """
<style>
/* 1. Dynamic Mesh Gradient Background */
.stApp {
    background: linear-gradient(125deg, #0f172a 0%, #1e1b4b 35%, #311042 70%, #0284c7 100%) !important;
    background_attachment: fixed;
}

/* 2. Neon Titles & Headings */
h1 {
    background: linear-gradient(90deg, #38bdf8, #a855f7, #f43f5e) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    font-weight: 900 !important;
    font-size: 2.8rem !important;
    letter-spacing: -0.03em !important;
}

h2, h3 {
    color: #f8fafc !important;
    font-weight: 800 !important;
    text-shadow: 0 0 10px rgba(168, 85, 247, 0.3) !important;
}

/* 3. High-Contrast Text Labels */
div[data-testid="stMarkdownContainer"] p, 
label[data-testid="stWidgetLabel"] p,
div[data-testid="stToggle"] span {
    color: #e2e8f0 !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
}

/* 4. Glassmorphic Color-Shift Toggle Card */
div[data-testid="stToggle"] {
    background: rgba(30, 27, 75, 0.75) !important;
    backdrop-filter: blur(12px) !important;
    padding: 12px 20px !important;
    border-radius: 14px !important;
    border: 1px solid rgba(168, 85, 247, 0.4) !important;
    box-shadow: 0 8px 32px 0 rgba(168, 85, 247, 0.2) !important;
}

/* 5. Vibrant Gradient Input Containers */
div[data-testid="stFileUploader"], 
div[data-testid="stTextArea"] textarea {
    background: rgba(15, 23, 42, 0.85) !important;
    border: 2px solid #a855f7 !important;
    border-radius: 14px !important;
    color: #ffffff !important;
    box-shadow: 0 4px 20px rgba(168, 85, 247, 0.15) !important;
    transition: all 0.35s ease !important;
}

div[data-testid="stFileUploaderDropzone"] {
    background: rgba(30, 27, 75, 0.5) !important;
    border: 2px dashed #38bdf8 !important;
    border-radius: 10px !important;
}

div[data-testid="stFileUploader"]:hover, 
div[data-testid="stTextArea"] textarea:focus {
    border-color: #f43f5e !important;
    box-shadow: 0 0 25px rgba(244, 63, 94, 0.4) !important;
    transform: translateY(-2px) !important;
}

/* 6. Multi-Glow Primary Button */
div.stButton > button {
    background: linear-gradient(90deg, #ec4899 0%, #8b5cf6 50%, #3b82f6 100%) !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    font-size: 1.05rem !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 14px 28px !important;
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.5) !important;
    transition: all 0.3s ease !important;
    width: 100%;
}

div.stButton > button:hover {
    transform: translateY(-3px) scale(1.01) !important;
    box-shadow: 0 0 30px rgba(236, 72, 153, 0.8) !important;
    background: linear-gradient(90deg, #f43f5e 0%, #a855f7 50%, #06b6d4 100%) !important;
}

/* 7. Neon Tab Navigation Styling */
button[data-baseweb="tab"] {
    background-color: rgba(15, 23, 42, 0.6) !important;
    border-radius: 8px 8px 0 0 !important;
    color: #94a3b8 !important;
    font-weight: 700 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

button[aria-selected="true"] {
    background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 0 15px rgba(236, 72, 153, 0.4) !important;
}

/* 8. Vibrant Content Cards */
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: rgba(15, 23, 42, 0.8) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-left: 6px solid #06b6d4 !important;
    border-radius: 14px !important;
    padding: 20px !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3) !important;
    margin-bottom: 16px !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
    border-left: 6px solid #f43f5e !important;
    box-shadow: 0 0 20px rgba(244, 63, 94, 0.25) !important;
    transform: translateY(-2px) !important;
}

/* 9. Glowing Export Button */
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    border-radius: 12px !important;
    border: none !important;
    box-shadow: 0 0 15px rgba(16, 185, 129, 0.4) !important;
}

div[data-testid="stDownloadButton"] > button:hover {
    box-shadow: 0 0 25px rgba(16, 185, 129, 0.7) !important;
    transform: translateY(-2px) !important;
}
</style>
"""

st.markdown(css_code, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. Multi-Color Ticker Banner
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div style="
        background: linear-gradient(90deg, #ec4899 0%, #8b5cf6 33%, #06b6d4 66%, #10b981 100%);
        color: #ffffff;
        padding: 10px 0px;
        border-radius: 10px;
        font-weight: 800;
        font-size: 1.05rem;
        letter-spacing: 0.8px;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.4);
        margin-bottom: 24px;
    ">
        <marquee behavior="scroll" direction="left" scrollamount="8">
            ⚡ Smart Scope Handover Engine &nbsp;|&nbsp; Project Intelligence Layer &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ⚡ Smart Scope Handover Engine &nbsp;|&nbsp; Project Intelligence Layer
        </marquee>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 5. App Header & Safe Mode Control
# -----------------------------------------------------------------------------
col_title, col_toggle = st.columns([3, 1])

with col_title:
    st.title("Pitch to Project")
    st.caption("🚀 AI-Powered Scope Intelligence & Handover Engine")

with col_toggle:
    demo_mode = st.toggle("Demo Mode (Safe Pitch)", value=True)

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

    if generate_btn:
        if demo_mode:
            progress_container = st.empty()
            with progress_container.container():
                my_bar = st.progress(0, text="Running Demo Mode analysis...")
                for percent in range(100):
                    time.sleep(0.01)
                    my_bar.progress(percent + 1, text="Running Demo Mode analysis...")
            progress_container.empty()
            
            st.session_state["analysis_data"] = MOCK_ANALYSIS
            st.toast("⚡ Demo Analysis Complete!", icon="✅")
        else:
            raw_text = extract_text_from_uploads(sow_files, notes_files, loose_notes)
            if not raw_text.strip():
                st.warning("Please upload at least one document or paste text before analyzing.")
            else:
                progress_container = st.empty()
                with progress_container.container():
                    my_bar = st.progress(15, text="📄 Parsing intake materials...")
                    time.sleep(0.3)
                    
                    my_bar.progress(45, text="⚡ Sending data to Gemini API...")
                    time.sleep(0.3)
                    
                    my_bar.progress(75, text="🧠 Analyzing requirements, risks, and user stories...")
                    
                    result = analyze_with_gemini(raw_text)
                    
                    my_bar.progress(100, text="✅ Analysis complete!")
                    time.sleep(0.4)
                
                progress_container.empty()

                if result:
                    st.session_state["analysis_data"] = result
                    st.toast("⚡ Live Gemini Extraction Complete!", icon="✅")

    if "analysis_data" not in st.session_state:
        st.session_state["analysis_data"] = MOCK_ANALYSIS

    data = st.session_state["analysis_data"]

    tab_scope, tab_risks, tab_jira = st.tabs(
        ["📌 Extracted Scope", "🚨 Missing Items & Risks", "🚀 Jira User Stories"]
    )
    
    with tab_scope:
        for item in data.get("extracted_scope", []):
            with st.container(border=True):
                st.markdown(f"### 📌 MODULE: {item.get('module', 'General Scope')}")
                st.caption(f"Source: {item.get('source', 'Uploaded Files')}")
                for pt in item.get("points", []):
                    st.markdown(f"• {pt}")
                    
    with tab_risks:
        for risk in data.get("gaps_and_risks", []):
            with st.container(border=True):
                severity = risk.get('severity', 'INFO').upper()
                badge_color = "🔴" if severity == "HIGH" else "🟡" if severity == "MEDIUM" else "🔵"
                st.markdown(f"### {badge_color} [{severity}] {risk.get('type', 'Risk')}")
                st.write(risk.get("description", ""))

    with tab_jira:
        for story in data.get("jira_user_stories", []):
            with st.container(border=True):
                st.markdown(f"### 🚀 {story.get('title', 'User Story')}")
                st.markdown(f"**As a** `{story.get('user_role', 'User')}`, **I want to** {story.get('want_statement', '')} **so that** {story.get('so_that_statement', '')}.")
                st.markdown("**Acceptance Criteria:**")
                for ac in story.get("acceptance_criteria", []):
                    st.markdown(f"- `{ac}`")

    st.divider()
    docx_bytes = build_docx_report(data)
    st.download_button(
        label="📄 Export Handover Report (.docx)",
        data=docx_bytes,
        file_name="Pitch_to_Project_Handover_Report.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True
    )