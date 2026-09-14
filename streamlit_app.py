import json
import time
import io
import docx
import pypdf
import requests
import urllib.parse
import jwt
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from google import genai
from google.genai import types

# =============================================================================
# 1. PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Pitch to Project | Smart Scope Engine",
    page_icon="⚡",
    layout="wide",
)

# =============================================================================
# 2. GLOBAL NEON CSS
# =============================================================================

css_code = """
<style>

.stApp {
    background: linear-gradient(125deg, #0f172a 0%, #1e1b4b 35%, #311042 70%, #0284c7 100%) !important;
    background-attachment: fixed;
}

div[data-testid="stForm"] {
    background: rgba(15, 23, 42, 0.95) !important;
    border: 2.5px solid #a855f7 !important;
    border-radius: 18px !important;
    padding: 36px !important;
    box-shadow: 0 0 40px rgba(168, 85, 247, 0.5) !important;
}

div[data-testid="stForm"] label p, div[data-testid="stTextInput"] label p {
    color: #38bdf8 !important;
    font-weight: 900 !important;
    font-size: 1.3rem !important;
}

div[data-testid="stForm"] div[data-testid="stTextInput"] input,
div[data-testid="stTextInput"] input {
    background-color: #0f172a !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border: 2.5px solid #38bdf8 !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    font-size: 1.2rem !important;
    padding: 12px 16px !important;
}

section[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.95) !important;
    border-right: 1.5px solid #a855f7 !important;
}

section[data-testid="stSidebar"] h3 {
    color: #38bdf8 !important;
    font-size: 1.3rem !important;
    font-weight: 800 !important;
}

section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span {
    color: #f8fafc !important;
    font-weight: 700 !important;
}

div.stButton > button {
    background: linear-gradient(90deg, #ec4899 0%, #8b5cf6 50%, #3b82f6 100%) !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    font-size: 1.05rem !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 12px 24px !important;
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.5) !important;
    width: 100%;
}

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

</style>
"""

st.markdown(css_code, unsafe_allow_html=True)

# =============================================================================
# 3. GOOGLE WORKSPACE OAUTH AUTHENTICATION & DOMAIN GUARDRAIL
# =============================================================================

def check_google_oauth():
    """
    Enforces Google Workspace OAuth login restricted strictly to @hurix.com users.
    Handles callback authorization code parsing via st.query_params.
    """
    if st.session_state.get("authenticated", False):
        return True

    oauth_config = st.secrets.get("oauth", {})
    client_id = oauth_config.get("client_id")
    client_secret = oauth_config.get("client_secret")
    redirect_uri = oauth_config.get("redirect_uri")
    required_domain = st.secrets.get("COMPANY_DOMAIN", "@hurix.com")

    # Step 1: Handle OAuth Callback Code from Query Parameters
    query_params = st.query_params
    auth_code = query_params.get("code")

    if auth_code:
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": auth_code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        try:
            token_response = requests.post(token_url, data=data).json()
            id_token = token_response.get("id_token")

            if id_token:
                user_info = jwt.decode(id_token, options={"verify_signature": False})
                user_email = user_info.get("email", "")

                # Step 2: Validate Domain Restriction
                if user_email.endswith(required_domain):
                    st.session_state["authenticated"] = True
                    st.session_state["user_email"] = user_email
                    
                    st.query_params.clear()
                    st.toast("⚡ Login Successful!", icon="✅")
                    st.rerun()
                else:
                    st.error(f"⛔ Access Blocked: {user_email} is unauthorized. Must log in with an official {required_domain} account.")
                    st.stop()
        except Exception as exc:
            st.error(f"🚨 OAuth Token Verification Failed: {exc}")
            st.stop()

    # Step 3: Render Google Workspace SSO Login Form
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            f"""
            <div style="background: rgba(15, 23, 42, 0.95); border: 2.5px solid #a855f7; border-radius: 18px; padding: 36px; text-align: center;">
                <h1 style="color: #ffffff; font-size: 2.2rem; margin: 0;">🔒 Pitch to Project</h1>
                <p style="color: #38bdf8; font-weight: 800; font-size: 1.1rem; margin-top: 8px;">
                    Restricted Access to {required_domain} Employees
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        google_auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            + urllib.parse.urlencode({
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": "openid email profile",
                "prompt": "select_account",
            })
        )

        st.markdown(
            f"""
            <a href="{google_auth_url}" target="_self" style="text-decoration: none;">
                <div style="background: linear-gradient(90deg, #ec4899 0%, #8b5cf6 50%, #06b6d4 100%);
                            border-radius: 12px; padding: 16px; text-align: center; color: white;
                            font-weight: 900; font-size: 1.2rem; margin-top: 20px; box-shadow: 0 0 25px rgba(236, 72, 153, 0.5);">
                    🔑 SIGN IN WITH HURIX GOOGLE WORKSPACE
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )

    return False


if not check_google_oauth():
    st.stop()

# =============================================================================
# 4. SIDEBAR SESSION
# =============================================================================

with st.sidebar:
    st.markdown("### 👤 Active Session")
    st.write(f"Logged in: **{st.session_state.get('user_email', 'User')}**")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()

# =============================================================================
# 5. GEMINI CLIENT
# =============================================================================

@st.cache_resource
def get_gemini_client():
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            return None
        return genai.Client(api_key=api_key)
    except Exception:
        return None

client = get_gemini_client()

# =============================================================================
# 6. STYLISH PROGRESS BAR
# =============================================================================

def render_stylish_progress(percentage, status_text):
    return f"""
    <div style="margin: 10px 0 18px 0; width: 100%;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span style="color: #06b6d4; font-weight: 800; font-size: 0.95rem;">{status_text}</span>
            <span style="color: #f59e0b; font-weight: 900; font-size: 1.05rem;">{percentage}%</span>
        </div>
        <div style="background: rgba(15, 23, 42, 0.9); border: 2px solid #10b981; border-radius: 12px; padding: 3px; height: 24px;">
            <div style="width: {percentage}%; height: 18px; background: linear-gradient(90deg, #10b981 0%, #3b82f6 50%, #f59e0b 100%); border-radius: 8px; transition: width 0.3s ease-in-out;"></div>
        </div>
    </div>
    """

# =============================================================================
# 7. MULTIMODAL EXTRACTION PIPELINE
# =============================================================================

def extract_docx_details(file):
    extracted_text = ""
    extracted_images = []
    try:
        file.seek(0)
        doc = docx.Document(file)
        extracted_text += f"\n--- FILE: {file.name} ---\n"

        for para in doc.paragraphs:
            if para.text.strip():
                extracted_text += f"{para.text.strip()}\n"

        for table in doc.tables:
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells]
                extracted_text += " | ".join(cells) + "\n"

        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                img_bytes = rel.target_part.blob
                img = Image.open(io.BytesIO(img_bytes))
                extracted_images.append(img)
    except Exception as exc:
        extracted_text += f"\n--- FILE: {file.name} ---\n[ERROR: {exc}]\n"
    return extracted_text, extracted_images

def extract_pdf_details(file):
    extracted_text = ""
    try:
        file.seek(0)
        reader = pypdf.PdfReader(file)
        extracted_text += f"\n--- FILE: {file.name} ---\n"
        for idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text:
                extracted_text += f"[Page {idx}] {text.strip()}\n"
    except Exception as exc:
        extracted_text += f"\n[PDF ERROR: {exc}]\n"
    return extracted_text

def build_multimodal_payload(sow_files, notes_files, media_files, loose_notes):
    payload_parts = []
    text_buffer = ""

    if sow_files:
        for file in sow_files:
            if file.name.lower().endswith(".docx"):
                t, imgs = extract_docx_details(file)
                text_buffer += t
                payload_parts.extend(imgs)
            elif file.name.lower().endswith(".pdf"):
                text_buffer += extract_pdf_details(file)

    if notes_files:
        for file in notes_files:
            file.seek(0)
            text_buffer += f"\n--- FILE: {file.name} ---\n{file.read().decode('utf-8', errors='replace')}\n"

    if loose_notes and loose_notes.strip():
        text_buffer += f"\n--- LOOSE NOTES ---\n{loose_notes.strip()}\n"

    if text_buffer.strip():
        payload_parts.insert(0, text_buffer)

    if media_files:
        for m in media_files:
            m.seek(0)
            b = m.read()
            if m.type.startswith("image/"):
                payload_parts.append(Image.open(io.BytesIO(b)))
            else:
                payload_parts.append(types.Part.from_bytes(data=b, mime_type=m.type))

    return payload_parts

# =============================================================================
# 8. SYSTEM PROMPT
# =============================================================================

SYSTEM_INSTRUCTION_PROMPT = """
You are a Senior IT Delivery Lead and Solution Architect.
Transform unstructured project intake data into a structured JSON scope analysis.

RULES:
1. Do NOT invent requirements. Rely strictly on provided context.
2. Flag missing details as risks, gaps, or assumptions.
3. Trace every item back to its source document tag.

JSON SCHEMA:
{
  "project_summary": { "project_objective": "", "business_goal": "", "overall_scope_summary": "" },
  "extracted_scope": [ { "module": "", "source": "", "scope_type": "FUNCTIONAL/TECHNICAL", "points": [ "" ] } ],
  "gaps_and_risks": [ { "severity": "HIGH/MEDIUM/LOW", "type": "", "description": "", "impact": "", "recommended_action": "" } ],
  "assumptions": [ { "assumption": "", "reason": "", "validation_required": true } ],
  "dependencies": [ { "dependency": "", "owner": "", "impact": "" } ],
  "conflicts": [ { "topic": "", "source_a": "", "statement_a": "", "source_b": "", "statement_b": "", "resolution_needed": "" } ],
  "jira_user_stories": [ { "title": "", "user_role": "", "want_statement": "", "so_that_statement": "", "acceptance_criteria": [ "" ] } ]
}
"""

# =============================================================================
# 9. GEMINI INFERENCE
# =============================================================================

def analyze_with_gemini(multimodal_payload):
    if not client:
        return None, "GEMINI_API_KEY missing or invalid in Secrets."

    contents = [SYSTEM_INSTRUCTION_PROMPT] + multimodal_payload

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.15,
            )
        )
        return json.loads(response.text), None
    except Exception as exc:
        return None, f"Gemini API Error: {exc}"

# =============================================================================
# 10. MOCK DATA
# =============================================================================

MOCK_ANALYSIS = {
    "project_summary": {
        "project_objective": "Transform pitch materials into actionable scope.",
        "business_goal": "Accelerate project handover and eliminate scope ambiguity.",
        "overall_scope_summary": "Extracted user stories, identified missing SLAs, and cataloged cross-document risks."
    },
    "extracted_scope": [
        {
            "module": "AUTHENTICATION & ACCESS",
            "source": "SOW Page 3",
            "scope_type": "FUNCTIONAL",
            "points": ["Domain restriction to @hurix.com users.", "Role-based authorization."]
        }
    ],
    "gaps_and_risks": [
        {
            "severity": "HIGH",
            "type": "Missing SLA",
            "description": "No execution latency threshold defined.",
            "impact": "Unclear performance targets.",
            "recommended_action": "Align on latency criteria with client."
        }
    ],
    "assumptions": [],
    "dependencies": [],
    "conflicts": [],
    "jira_user_stories": [
        {
            "title": "OAuth Access Control",
            "user_role": "Delivery Lead",
            "want_statement": "restrict application login to authorized domains",
            "so_that_statement": "unauthorized external users cannot process project intake files",
            "acceptance_criteria": [
                "Given a user attempts to sign in",
                "When their email matches @hurix.com",
                "Then access is granted."
            ]
        }
    ]
}

# =============================================================================
# 11. DOCX EXPORT GENERATOR
# =============================================================================

def build_docx_report(data):
    doc = docx.Document()
    doc.add_heading("Pitch to Project - Handover Scope Analysis", 0)

    summary = data.get("project_summary", {})
    doc.add_heading("Project Summary", level=1)
    doc.add_paragraph(f"Objective: {summary.get('project_objective', '')}")
    doc.add_paragraph(f"Business Goal: {summary.get('business_goal', '')}")

    doc.add_heading("Extracted Scope", level=1)
    for mod in data.get("extracted_scope", []):
        doc.add_heading(f"Module: {mod.get('module', '')}", level=2)
        for pt in mod.get("points", []):
            doc.add_paragraph(f"• {pt}")

    doc.add_heading("Jira User Stories", level=1)
    for story in data.get("jira_user_stories", []):
        doc.add_heading(story.get("title", ""), level=2)
        doc.add_paragraph(f"As a {story.get('user_role')}, I want to {story.get('want_statement')} so that {story.get('so_that_statement')}.")
        for ac in story.get("acceptance_criteria", []):
            doc.add_paragraph(f"  - {ac}")

    target_stream = io.BytesIO()
    doc.save(target_stream)
    target_stream.seek(0)
    return target_stream.getvalue()

# =============================================================================
# 12. UI & MAIN LAYOUT
# =============================================================================

st.title("Pitch to Project")
st.subheader("🚀 AI-Powered Scope Intelligence & Handover Engine")

demo_mode = st.toggle("Demo Mode (Safe Pitch)", value=True)

left_col, right_col = st.columns([1, 1], gap="medium")

with left_col:
    st.header("1. Intake Materials")
    sow_files = st.file_uploader("Proposals / SOWs (.docx, .pdf)", type=["docx", "pdf"], accept_multiple_files=True)
    notes_files = st.file_uploader("Transcripts (.txt)", type=["txt"], accept_multiple_files=True)
    media_files = st.file_uploader("Media / Diagrams (.png, .jpg, .mp3, .mp4)", type=["png", "jpg", "mp3", "mp4"], accept_multiple_files=True)
    loose_notes = st.text_area("Paste Notes / Emails:", height=100)
    generate_btn = st.button("⚡ GENERATE SMART SCOPE")

with right_col:
    st.header("2. AI Scope Analysis")

    if generate_btn:
        if demo_mode:
            st.session_state["analysis_data"] = MOCK_ANALYSIS
            st.success("✅ Demo Analysis Loaded!")
        else:
            payload = build_multimodal_payload(sow_files, notes_files, media_files, loose_notes)
            if not payload:
                st.warning("Please upload files or enter text before running analysis.")
            else:
                result, error_msg = analyze_with_gemini(payload)
                if result:
                    st.session_state["analysis_data"] = result
                    st.success("✅ Gemini Analysis Complete!")
                else:
                    st.error(f"🚨 {error_msg}")

    data = st.session_state.get("analysis_data", MOCK_ANALYSIS)

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary", "📌 Scope", "🚨 Risks", "🚀 Jira Stories"])

    with tab1:
        s = data.get("project_summary", {})
        st.write(f"**Objective:** {s.get('project_objective')}")
        st.write(f"**Goal:** {s.get('business_goal')}")

    with tab2:
        for item in data.get("extracted_scope", []):
            st.markdown(f"### {item.get('module')}")
            st.caption(f"Source: {item.get('source')}")
            for p in item.get("points", []):
                st.write(f"• {p}")

    with tab3:
        for r in data.get("gaps_and_risks", []):
            st.error(f"[{r.get('severity')}] {r.get('description')}")

    with tab4:
        for story in data.get("jira_user_stories", []):
            st.markdown(f"### 🚀 {story.get('title')}")
            st.write(f"**As a** `{story.get('user_role')}`, **I want to** {story.get('want_statement')} **so that** {story.get('so_that_statement')}.")
            for ac in story.get("acceptance_criteria", []):
                st.code(ac)

    st.divider()
    st.download_button(
        label="📄 Export Handover Report (.docx)",
        data=build_docx_report(data),
        file_name="Pitch_to_Project_Handover_Report.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
