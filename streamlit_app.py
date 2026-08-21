import json
import time
import docx
import streamlit as st
from google import genai

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Pitch to Project | Smart Scope Engine",
    page_icon="⚡",
    layout="wide",
)

# Initialize Gemini Client (Uses GEMINI_API_KEY from st.secrets or environment)
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
    
    # Process DOCX files
    if sow_files:
        for file in sow_files:
            doc = docx.Document(file)
            combined_text += f"\n--- FILE: {file.name} ---\n"
            for para in doc.paragraphs:
                if para.text.strip():
                    combined_text += para.text + "\n"
                    
    # Process TXT files
    if notes_files:
        for file in notes_files:
            combined_text += f"\n--- FILE: {file.name} ---\n"
            combined_text += file.read().decode("utf-8") + "\n"
            
    # Process text area
    if loose_notes.strip():
        combined_text += f"\n--- LOOSE NOTES / EMAILS ---\n{loose_notes}\n"
        
    return combined_text

def analyze_with_gemini(raw_text):
    """Calls Gemini API to perform live scope analysis and return structured JSON."""
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
        )
        # Clean JSON string response
        cleaned_json = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_json)
    except Exception as e:
        st.error(f"Gemini API Error: {str(e)}")
        return None

# -----------------------------------------------------------------------------
# 3. Rich Custom CSS Styling
# -----------------------------------------------------------------------------
css_code = """
<style>
.stApp {
    background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%) !important;
}
h1, h2, h3 {
    color: #0f172a !important;
    font-weight: 800 !important;
}
div[data-testid="stMarkdownContainer"] p, 
label[data-testid="stWidgetLabel"] p,
div[data-testid="stToggle"] span {
    color: #0f172a !important;
    font-weight: 700 !important;
}
div[data-testid="stToggle"] {
    background: rgba(255, 255, 255, 0.85) !important;
    padding: 10px 18px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(203, 213, 225, 0.6) !important;
}
div[data-testid="stFileUploader"], 
div[data-testid="stTextArea"] textarea {
    background: #ffffff !important;
    border: 2px solid #6366f1 !important;
    border-radius: 14px !important;
}
div.stButton > button {
    background: linear-gradient(135deg, #4f46e5 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    border: none !important;
    width: 100%;
}
</style>
"""
st.markdown(css_code, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. App Header & Safe Mode Control
# -----------------------------------------------------------------------------
col_title, col_toggle = st.columns([3, 1])

with col_title:
    st.title("Pitch to Project")
    st.caption("AI-Powered Scope Intelligence & Handover Engine")

with col_toggle:
    demo_mode = st.toggle("Demo Mode (Safe Pitch)", value=True)

# Static Mock Data for Demo Mode
MOCK_ANALYSIS = {
    "extracted_scope": [
        {
            "module": "AUTHENTICATION & SECURITY",
            "source": "Proposal Page 4, Section 2",
            "points": [
                "Multi-factor authentication (MFA) via SMS/Email.",
                "Role-based access control (RBAC) for Admin and Client roles."
            ]
        }
    ],
    "gaps_and_risks": [
        {
            "severity": "HIGH",
            "type": "Missing SLA",
            "description": "No operational SLA defined for real-time document processing speed."
        }
    ],
    "jira_user_stories": [
        {
            "title": "Configurable Document Processing Engine",
            "user_role": "Delivery Lead",
            "want_statement": "ingest intake SOWs concurrently",
            "so_that_statement": "I can automatically extract requirements",
            "acceptance_criteria": ["Given uploaded DOCX files", "When clicking Generate", "Then scope is extracted"]
        }
    ]
}

def build_docx_report(data):
    doc = docx.Document()
    doc.add_heading("Pitch to Project - Handover Scope Analysis", 0)
    for mod in data.get("extracted_scope", []):
        doc.add_heading(f"Module: {mod['module']}", level=2)
        doc.add_paragraph(f"Source: {mod['source']}")
        for pt in mod["points"]:
            doc.add_paragraph(f"• {pt}")
    doc_path = "/tmp/Handover_Report.docx"
    doc.save(doc_path)
    with open(doc_path, "rb") as file:
        return file.read()

# -----------------------------------------------------------------------------
# 5. Dual Column Layout
# -----------------------------------------------------------------------------
left_col, right_col = st.columns([1, 1], gap="medium")

with left_col:
    st.header("1. Intake Documents & Media")
    sow_files = st.file_uploader("Proposals / SOWs (.docx)", type=["docx"], accept_multiple_files=True)
    notes_files = st.file_uploader("Transcripts / Notes (.txt)", type=["txt"], accept_multiple_files=True)
    media_files = st.file_uploader("Diagrams & Media (.png, .jpg, .mp4, .mp3)", type=["png", "jpg", "mp4", "mp3"], accept_multiple_files=True)
    loose_notes = st.text_area("Or Paste Loose Client Emails / Notes:", height=120)
    generate_btn = st.button("⚡ GENERATE SMART SCOPE")

with right_col:
    st.header("2. AI Scope & Handover Analysis")

    if generate_btn:
        if demo_mode:
            progress_text = "Running Demo Mode..."
            my_bar = st.progress(0, text=progress_text)
            for percent in range(100):
                time.sleep(0.01)
                my_bar.progress(percent + 1, text=progress_text)
            my_bar.empty()
            st.session_state["analysis_data"] = MOCK_ANALYSIS
            st.toast("⚡ Demo Analysis Complete!", icon="✅")
        else:
            # LIVE PROCESSING logic
            raw_text = extract_text_from_uploads(sow_files, notes_files, loose_notes)
            if not raw_text.strip():
                st.warning("Please upload at least one document or paste text before analyzing.")
            else:
                with st.spinner("Analyzing document content with Gemini API..."):
                    result = analyze_with_gemini(raw_text)
                    if result:
                        st.session_state["analysis_data"] = result
                        st.toast("⚡ Live Gemini Extraction Complete!", icon="✅")

    if "analysis_data" not in st.session_state:
        st.session_state["analysis_data"] = MOCK_ANALYSIS

    data = st.session_state["analysis_data"]

    tab_scope, tab_risks, tab_jira = st.tabs(["Extracted Scope", "Missing Items & Risks", "Jira User Stories"])
    
    with tab_scope:
        for item in data.get("extracted_scope", []):
            with st.container(border=True):
                st.markdown(f"### 📌 MODULE: {item['module']}")
                st.caption(f"Source: {item['source']}")
                for pt in item["points"]:
                    st.markdown(f"• {pt}")
                    
    with tab_risks:
        for risk in data.get("gaps_and_risks", []):
            with st.container(border=True):
                st.markdown(f"**[{risk['severity']}] {risk['type']}**")
                st.write(risk["description"])

    with tab_jira:
        for story in data.get("jira_user_stories", []):
            with st.container(border=True):
                st.markdown(f"### 🚀 {story['title']}")
                st.markdown(f"**As a** {story['user_role']}, **I want to** {story['want_statement']} **so that** {story['so_that_statement']}.")
                st.markdown("**Acceptance Criteria:**")
                for ac in story["acceptance_criteria"]:
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