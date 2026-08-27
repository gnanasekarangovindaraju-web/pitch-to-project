import json
import time
import io
import docx
import streamlit as st
from google import genai
from google.genai import types

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Pitch to Project | Smart Scope Engine",
    page_icon="⚡",
    layout="wide",
)

# -----------------------------------------------------------------------------
# 2. Comprehensive Custom CSS (Global + Complete Autofill & Contrast Fixes)
# -----------------------------------------------------------------------------
css_code = """
<style>
/* 1. Global Mesh Gradient Background Baseline */
.stApp {
    background: linear-gradient(125deg, #0f172a 0%, #1e1b4b 35%, #311042 70%, #0284c7 100%) !important;
    background-attachment: fixed;
}

/* 2. HIGH-VISIBILITY & EXTRA-LARGE FONT LOGIN PAGE STYLING */
div[data-testid="stForm"] {
    background: rgba(15, 23, 42, 0.95) !important;
    border: 2px solid #a855f7 !important;
    border-radius: 0 0 16px 16px !important;
    padding: 36px !important;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5) !important;
}

/* Input Text Labels Visibility (Username / Password) */
div[data-testid="stForm"] label,
div[data-testid="stForm"] label p,
div[data-testid="stTextInput"] label p {
    color: #38bdf8 !important;
    font-weight: 900 !important;
    font-size: 1.4rem !important;
    letter-spacing: 0.5px !important;
    margin-bottom: 8px !important;
}

/* High-Contrast Inputs (Typed Text, Font Size & Dark Background) */
div[data-testid="stForm"] div[data-testid="stTextInput"] input,
div[data-testid="stTextInput"] input,
input[type="text"],
input[type="password"] {
    background-color: #0f172a !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border: 2.5px solid #38bdf8 !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    font-size: 1.35rem !important;
    padding: 16px 20px !important;
    box-shadow: 0 0 14px rgba(56, 189, 248, 0.3) !important;
}

/* CRITICAL FIX: Stops Browser Autofill / Focus from Forcing Light White Backgrounds */
input:-webkit-autofill,
input:-webkit-autofill:hover, 
input:-webkit-autofill:focus,
input:-webkit-autofill:active {
    -webkit-box-shadow: 0 0 0 1000px #0f172a inset !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
    border: 2.5px solid #38bdf8 !important;
}

/* Placeholder Text Visibility */
div[data-testid="stTextInput"] input::placeholder,
input::placeholder {
    color: #94a3b8 !important;
    -webkit-text-fill-color: #94a3b8 !important;
    font-weight: 700 !important;
    font-size: 1.25rem !important;
    opacity: 1 !important;
}

/* Input Focus Glow */
div[data-testid="stTextInput"] input:focus {
    border-color: #f43f5e !important;
    box-shadow: 0 0 25px rgba(244, 63, 94, 0.7) !important;
}

/* Password Eye Icon Visibility */
div[data-testid="stTextInput"] button svg,
div[data-testid="stForm"] svg {
    fill: #38bdf8 !important;
    stroke: #38bdf8 !important;
    width: 26px !important;
    height: 26px !important;
}

/* LOGIN BUTTON HIGH CONTRAST STYLING */
div[data-testid="stForm"] button[type="submit"],
div[data-testid="stForm"] button[data-testid="stFormSubmitButton"],
div[data-testid="stForm"] button {
    background: linear-gradient(90deg, #ec4899 0%, #8b5cf6 50%, #06b6d4 100%) !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 18px 32px !important;
    box-shadow: 0 0 30px rgba(236, 72, 153, 0.7) !important;
    transition: all 0.3s ease !important;
    margin-top: 18px !important;
    width: 100% !important;
}

div[data-testid="stForm"] button[type="submit"] *,
div[data-testid="stForm"] button[type="submit"] p,
div[data-testid="stForm"] button[type="submit"] span,
div[data-testid="stForm"] button[data-testid="stFormSubmitButton"] *,
div[data-testid="stForm"] button[data-testid="stFormSubmitButton"] p,
div[data-testid="stForm"] button[data-testid="stFormSubmitButton"] span {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 900 !important;
    font-size: 1.5rem !important;
    letter-spacing: 1.2px !important;
}

div[data-testid="stForm"] button[type="submit"]:hover {
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 0 40px rgba(244, 63, 94, 0.9) !important;
}

/* 3. Sidebar Dark Theme */
section[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.95) !important;
    border-right: 1.5px solid #a855f7 !important;
}

section[data-testid="stSidebar"] h3 {
    color: #38bdf8 !important;
    font-size: 1.3rem !important;
    font-weight: 800 !important;
}

section[data-testid="stSidebar"] p, 
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: #f8fafc !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    background: transparent !important;
}

section[data-testid="stSidebar"] div.stButton > button {
    background: linear-gradient(90deg, #ec4899 0%, #f43f5e 100%) !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    font-size: 1.1rem !important;
    border-radius: 10px !important;
    box-shadow: 0 0 15px rgba(244, 63, 94, 0.5) !important;
    border: none !important;
    margin-top: 10px !important;
}

/* 4. Main App Typography & Components */
.main h1 {
    background: linear-gradient(90deg, #38bdf8, #a855f7, #f43f5e) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    font-weight: 900 !important;
    font-size: 2.8rem !important;
}

h2, h3 {
    color: #f8fafc !important;
    font-weight: 800 !important;
    text-shadow: 0 0 10px rgba(168, 85, 247, 0.3) !important;
}

div[data-testid="stMarkdownContainer"] p, 
label[data-testid="stWidgetLabel"] p,
div[data-testid="stToggle"] span {
    color: #f8fafc !important;
    font-weight: 700 !important;
}

div[data-testid="stCaptionContainer"] p {
    color: #38bdf8 !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
}

/* File Uploaders */
div[data-testid="stFileUploader"] {
    background: rgba(15, 23, 42, 0.95) !important;
    border: 2px solid #a855f7 !important;
    border-radius: 14px !important;
    padding: 12px !important;
}

div[data-testid="stFileUploader"] section,
div[data-testid="stFileUploaderDropzone"],
div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
    background: #1e1b4b !important;
    border: 2px dashed #38bdf8 !important;
    border-radius: 10px !important;
}

div[data-testid="stFileUploaderDropzone"] *,
div[data-testid="stFileUploaderDropzone"] span,
div[data-testid="stFileUploaderDropzone"] small,
div[data-testid="stFileUploaderDropzone"] p {
    color: #ffffff !important;
    font-weight: 700 !important;
}

div[data-testid="stFileUploaderDropzone"] button {
    background: linear-gradient(90deg, #ec4899 0%, #8b5cf6 100%) !important;
    border: 1px solid #f43f5e !important;
    border-radius: 8px !important;
}

div[data-testid="stFileUploaderDropzone"] button * {
    color: #ffffff !important;
    font-weight: 800 !important;
}

/* Toast Notifications */
div[data-testid="stToast"],
div[data-testid="stToast"] > div {
    background-color: #1e1b4b !important;
    background: #1e1b4b !important;
    border: 2px solid #38bdf8 !important;
    border-radius: 12px !important;
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.5) !important;
}

div[data-testid="stToast"] * {
    color: #ffffff !important;
    font-weight: 800 !important;
}

/* Export Button */
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    border-radius: 12px !important;
    border: none !important;
    box-shadow: 0 0 18px rgba(16, 185, 129, 0.5) !important;
    width: 100%;
}

div[data-testid="stDownloadButton"] > button * {
    color: #ffffff !important;
    font-weight: 900 !important;
}

/* Text Area Input */
div[data-testid="stTextArea"] textarea {
    background: rgba(15, 23, 42, 0.85) !important;
    border: 2px solid #a855f7 !important;
    border-radius: 14px !important;
    color: #ffffff !important;
}

/* Main Buttons */
div.stButton > button {
    background: linear-gradient(90deg, #ec4899 0%, #8b5cf6 50%, #3b82f6 100%) !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    font-size: 1.05rem !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 14px 28px !important;
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.5) !important;
    width: 100%;
}

/* Navigation Tabs & Cards */
button[aria-selected="true"] {
    background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
    color: #ffffff !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: rgba(15, 23, 42, 0.8) !important;
    backdrop-filter: blur(10px) !important;
    border-left: 6px solid #06b6d4 !important;
    border-radius: 14px !important;
    padding: 20px !important;
}

code {
    background-color: rgba(30, 27, 75, 0.95) !important;
    color: #38bdf8 !important;
    border: 1px solid #a855f7 !important;
    border-radius: 6px !important;
    padding: 3px 8px !important;
}
</style>
"""

st.markdown(css_code, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. Authentication Shield
# -----------------------------------------------------------------------------
def check_password():
    """Returns `True` if the user enters correct credentials."""
    if st.session_state.get("authenticated", False):
        return True

    # Render High-Contrast Gradient Login Card with Direct Inline Style Attributes
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2.4, 1])
    
    with col2:
        # Explicit Inlined Dark Purple Card Banner Header
        st.markdown(
            """
            <div style="
                background: #1e1b4b !important;
                border: 2.5px solid #a855f7 !important;
                border-bottom: none !important;
                border-radius: 18px 18px 0 0 !important;
                padding: 32px 24px !important;
                box-shadow: 0 0 35px rgba(168, 85, 247, 0.5) !important;
                text-align: center !important;
                margin-bottom: -1px !important;
            ">
                <div style="margin-bottom: 8px !important;">
                    <span style="
                        color: #ffffff !important; 
                        -webkit-text-fill-color: #ffffff !important;
                        font-size: 3rem !important; 
                        font-weight: 900 !important; 
                        text-shadow: 0 3px 12px rgba(0,0,0,0.8) !important;
                        letter-spacing: -0.5px !important;
                        display: inline-block !important;
                    ">🔒 Pitch to Project</span>
                </div>
                <div>
                    <span style="
                        color: #38bdf8 !important; 
                        -webkit-text-fill-color: #38bdf8 !important;
                        font-weight: 800 !important; 
                        font-size: 1.35rem !important; 
                        letter-spacing: 1.2px !important;
                        text-shadow: 0 2px 10px rgba(0,0,0,0.8) !important;
                        display: inline-block !important;
                    ">⚡ Scope Intelligence Engine Access</span>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Form Container
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submit = st.form_submit_button("🔑 LOGIN TO ENGINE")

            if submit:
                VALID_USER = st.secrets.get("APP_USER", "admin")
                VALID_PASSWORD = st.secrets.get("APP_PASSWORD", "project2026")

                if username == VALID_USER and password == VALID_PASSWORD:
                    st.session_state["authenticated"] = True
                    st.toast("⚡ Login Successful!", icon="✅")
                    st.rerun()
                else:
                    st.error("❌ Invalid Username or Password")

    return False

# Stop execution here if user is not authenticated
if not check_password():
    st.stop()

# -----------------------------------------------------------------------------
# 4. Sidebar Logout Control
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 👤 User Session")
    st.write("Logged in as **Admin**")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()

# -----------------------------------------------------------------------------
# 5. API Client & Helper Functions
# -----------------------------------------------------------------------------
@st.cache_resource
def get_gemini_client():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        return genai.Client(api_key=api_key)
    except Exception:
        return None

client = get_gemini_client()

def render_stylish_progress(percentage, status_text):
    """Renders a custom neon Emerald-Gold shimmering progress bar."""
    return f"""
    <div style="margin: 10px 0 18px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span style="color: #06b6d4; font-weight: 800; font-size: 0.95rem;">{status_text}</span>
            <span style="color: #f59e0b; font-weight: 900; font-size: 1.05rem; text-shadow: 0 0 10px rgba(245, 158, 11, 0.5);">{percentage}%</span>
        </div>
        <div style="
            background: rgba(15, 23, 42, 0.9);
            border: 2px solid #10b981;
            border-radius: 12px;
            padding: 3px;
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.3);
            position: relative;
            overflow: hidden;
        ">
            <div style="
                width: {percentage}%;
                height: 18px;
                background: linear-gradient(90deg, #10b981 0%, #3b82f6 50%, #f59e0b 100%);
                border-radius: 8px;
                box-shadow: 0 0 20px rgba(245, 158, 11, 0.8);
                transition: width 0.2s ease-in-out;
            "></div>
        </div>
    </div>
    """

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
    """Generates Word document in-memory."""
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

    target_stream = io.BytesIO()
    doc.save(target_stream)
    return target_stream.getvalue()

# -----------------------------------------------------------------------------
# 6. Main App Header Banner & Controls
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
# 7. Dual Column Layout
# -----------------------------------------------------------------------------
left_col, right_col = st.columns([1, 1], gap="medium")

with left_col:
    st.header("1. Intake Documents & Media")
    
    sow_files = st.file_uploader("Proposals / SOWs (.docx)", type=["docx"], accept_multiple_files=True)
    notes_files = st.file_uploader("Transcripts / Notes (.txt)", type=["txt"], accept_multiple_files=True)
    media_files = st.file_uploader("Diagrams & Media (.png, .jpg, .mp4, .mp3)", type=["png", "jpg", "mp4", "mp3"], accept_multiple_files=True)
    
    loose_notes = st.text_area(
        "Or Paste Loose Client Emails / Notes:", 
        height=120, 
        placeholder="Paste kickoff notes or client requirements here..."
    )
    
    generate_btn = st.button("⚡ GENERATE SMART SCOPE")

with right_col:
    st.header("2. AI Scope & Handover Analysis")

    if generate_btn:
        progress_card = st.empty()
        
        if demo_mode:
            with progress_card.container(border=True):
                st.markdown("### 🧠 Running Scope Analysis")
                bar_ph = st.empty()
                
                for i in range(101):
                    time.sleep(0.01)
                    bar_ph.markdown(
                        render_stylish_progress(i, "⚙️ Processing intake materials & generating user stories..."), 
                        unsafe_allow_html=True
                    )
                st.success("✅ Demo Analysis Loaded Successfully!")
                time.sleep(0.4)
            
            progress_card.empty()
            st.session_state["analysis_data"] = MOCK_ANALYSIS
            st.toast("⚡ Demo Analysis Loaded!", icon="✅")
        else:
            raw_text = extract_text_from_uploads(sow_files, notes_files, loose_notes)
            if not raw_text.strip():
                st.warning("Please upload at least one document or paste text before analyzing.")
            else:
                with progress_card.container(border=True):
                    st.markdown("### 🧠 Live Gemini Scope Extraction")
                    bar_ph = st.empty()
                    
                    bar_ph.markdown(render_stylish_progress(20, "📄 Step 1/3: Extracting raw text from intake documents..."), unsafe_allow_html=True)
                    time.sleep(0.3)
                    
                    bar_ph.markdown(render_stylish_progress(50, "⚡ Step 2/3: Transmitting payload to Gemini 3.6 API..."), unsafe_allow_html=True)
                    time.sleep(0.3)
                    
                    bar_ph.markdown(render_stylish_progress(80, "🔍 Step 3/3: Auditing missing SLAs, risks & user stories..."), unsafe_allow_html=True)
                    
                    result = analyze_with_gemini(raw_text)
                    
                    if result:
                        bar_ph.markdown(render_stylish_progress(100, "✅ Smart Scope Handover Analysis Complete!"), unsafe_allow_html=True)
                        st.success("✅ Scope Successfully Extracted!")
                        time.sleep(0.5)
                        st.session_state["analysis_data"] = result
                        st.toast("⚡ Live Gemini Extraction Complete!", icon="✅")
                    else:
                        st.error("❌ Extraction Failed")
                
                progress_card.empty()

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
