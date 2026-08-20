import os
import json
import time
import streamlit as st
import docx
from docx.shared import Inches, Pt, RGBColor
from dotenv import load_dotenv
st.set_page_config(page_title="Pitch to Project", layout="wide")

# Inject CSS cleanly using triple quotescss_code = """
<style>
/* 1. Page Background & Font Baseline */
.stApp {
    background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%) !important;
}

/* 2. Rich Top Navigation / Header Styling */
h1, h2, h3 {
    color: #0f172a !important;
    font-weight: 800 !important;
    letter-spacing: -0.025em !important;
}

/* 3. High-Contrast Labels & Text Visibility Fix */
div[data-testid="stMarkdownContainer"] p, 
label[data-testid="stWidgetLabel"] p,
div[data-testid="stToggle"] span {
    color: #0f172a !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    text-shadow: 0 1px 1px rgba(255, 255, 255, 0.8);
}

/* 4. Glassmorphism Card Wrapper for Demo Mode Toggle */
div[data-testid="stToggle"] {
    background: rgba(255, 255, 255, 0.85) !important;
    backdrop-filter: blur(8px) !important;
    padding: 10px 18px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(203, 213, 225, 0.6) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
}

/* 5. Rich Input Cards (File Uploaders & Text Areas) */
div[data-testid="stFileUploader"], 
div[data-testid="stTextArea"] textarea {
    background: #ffffff !important;
    border: 2px solid #6366f1 !important; /* Soft Indigo border */
    border-radius: 14px !important;
    padding: 14px !important;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.04), 0 4px 6px -2px rgba(0, 0, 0, 0.02) !important;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* Dropzone Interior Styling */
div[data-testid="stFileUploaderDropzone"] {
    background: #f8fafc !important;
    border: 1px dashed #cbd5e1 !important;
    border-radius: 10px !important;
}

/* 6. Glowing Hover & Focus Micro-Animations */
div[data-testid="stFileUploader"]:hover, 
div[data-testid="stTextArea"] textarea:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 12px 20px -5px rgba(99, 102, 241, 0.25), 0 0 0 4px rgba(99, 102, 241, 0.15) !important;
    transform: translateY(-3px) scale(1.005) !important;
}

/* 7. Gradient Primary Action Button with Pulse Hover */
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
}

div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(79, 70, 229, 0.55) !important;
    background: linear-gradient(135deg, #4338ca 0%, #1d4ed8 100%) !important;
}

/* 8. Container Cards for Extracted Output Sections */
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-left: 5px solid #6366f1 !important; /* Left highlight bar */
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
# Load environment variables
load_dotenv()

# Page Setup
st.set_page_config(
    page_title="Pitch To Project — Smart Scope Handover Engine",
    page_icon="⚡",
    layout="wide"
)

# --- GEMINI SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are an expert Delivery Manager and Solution Architect. Analyze the provided project input text, tables, visual diagrams, and meeting media to generate a structured JSON output with strictly three root keys:

1. "extracted_scope": Array of objects, each containing:
   - "module": Name of the functional area (e.g., Auth, Payments, UI/UX, Admin)
   - "requirements": Array of functional requirement strings
   - "source_citation": String citing the document/section/media (e.g., "Proposal Page 4 Table 2" or "Architecture Diagram PNG")

2. "risks_and_gaps": Array of objects, each containing:
   - "type": Category ("Missing SLA", "Unstated Assumption", "Cross-Document Conflict", "Scope Drift")
   - "description": Explicit callout of what is missing, vague, contradictory, or conflicting across files
   - "severity": String ("HIGH", "MEDIUM", "LOW")

3. "user_stories": Array of objects, each containing:
   - "title": Short story title
   - "as_a": User role
   - "i_want": Feature / Capability
   - "so_that": Business value
   - "acceptance_criteria": Array of acceptance criteria strings

CRITICAL AUDIT RULES:
- Actively search for MISSING non-functional requirements (e.g., unstated uptime SLAs, missing performance bounds, undefined maintenance windows, unmentioned security compliance).
- Cross-check conflicts between proposal promises, SOW tables, diagrams, and audio notes.
- If details are not explicitly present, DO NOT invent them—flag them explicitly under 'risks_and_gaps'.
- Return ONLY valid raw JSON with no Markdown wrapping.
"""

# --- DEMO DATA (SAFE PITCH MODE) ---
DEMO_DATA = {
    "extracted_scope": [
        {
            "module": "Authentication & Security",
            "requirements": [
                "Multi-factor authentication (MFA) via SMS/Email.",
                "Role-based access control (RBAC) for Admin and Client roles."
            ],
            "source_citation": "Proposal Page 4, Section 2"
        },
        {
            "module": "Handover Intelligence Engine",
            "requirements": [
                "Multi-format document parsing (.docx, .txt, tables, media).",
                "Automated gap auditing and structured JSON extraction."
            ],
            "source_citation": "Kickoff Transcript Lines 12-45"
        }
    ],
    "risks_and_gaps": [
        {
            "type": "Missing SLA",
            "description": "System requests 99.9% availability, but maintenance windows and downtime penalties are undefined.",
            "severity": "HIGH"
        },
        {
            "type": "Unstated Assumption",
            "description": "Third-party payment API keys are assumed to be provided by the client prior to Sprint 1.",
            "severity": "MEDIUM"
        },
        {
            "type": "Cross-Document Conflict",
            "description": "Proposal promises a 2-week QA phase, but the Meeting Transcript specifies a requested 1-week timeline.",
            "severity": "HIGH"
        }
    ],
    "user_stories": [
        {
            "title": "Automated Scope Parsing",
            "as_a": "Delivery Lead",
            "i_want": "to convert unstructured SOW text into categorized requirements",
            "so_that": "I can establish project readiness in seconds",
            "acceptance_criteria": [
                "Support multi-.docx, tables, and media ingestion",
                "Categorize output by functional module",
                "Include source citations for extracted points"
            ]
        }
    ]
}

# --- DOCUMENT & TEXT PARSER ---
def read_uploaded_sources(proposal_files, transcript_files, pasted_notes):
    combined_text = []

    # Process .docx files
    for file in proposal_files:
        try:
            doc = docx.Document(file)
            doc_content = []
            for p in doc.paragraphs:
                if p.text.strip():
                    doc_content.append(p.text.strip())
            for t_idx, table in enumerate(doc.tables):
                doc_content.append(f"\n[TABLE {t_idx + 1} DATA]:")
                for row in table.rows:
                    row_vals = [cell.text.strip().replace("\n", " ") for cell in row.cells if cell.text.strip()]
                    if row_vals:
                        doc_content.append(" | ".join(row_vals))
            combined_text.append(f"--- DOCUMENT: {file.name} ---\n" + "\n".join(doc_content))
        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")

    # Process .txt files
    for file in transcript_files:
        try:
            content = file.read().decode("utf-8")
            combined_text.append(f"--- TRANSCRIPT: {file.name} ---\n{content}")
        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")

    # Process pasted text
    if pasted_notes.strip():
        combined_text.append(f"--- PASTED NOTES ---\n{pasted_notes.strip()}")

    return "\n\n".join(combined_text)

# --- WORD REPORT GENERATOR ---
def generate_word_report(data):
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    p_title = doc.add_paragraph()
    r_title = p_title.add_run("PITCH TO PROJECT — HANDOVER REPORT")
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(31, 78, 121)

    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("Smart Scope Handover Analysis & Gap Audit")
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(100, 100, 100)

    # Section 1: Scope
    h1 = doc.add_heading(level=1)
    h1.add_run("1. Extracted Functional Scope").font.color.rgb = RGBColor(31, 78, 121)
    for item in data.get("extracted_scope", []):
        p = doc.add_paragraph()
        p.add_run(f"Module: {item.get('module')}\n").bold = True
        p.add_run(f"Source: {item.get('source_citation', 'N/A')}\n").font.italic = True
        for req in item.get("requirements", []):
            doc.add_paragraph(f"{req}", style="List Bullet")

    # Section 2: Risks
    h2 = doc.add_heading(level=1)
    h2.add_run("2. Missing Items, Gaps & Risk Audit").font.color.rgb = RGBColor(31, 78, 121)
    for risk in data.get("risks_and_gaps", []):
        p = doc.add_paragraph()
        r_r = p.add_run(f"⚠️ [{risk.get('severity')}] {risk.get('type')}\n")
        r_r.bold = True
        r_r.font.color.rgb = RGBColor(192, 57, 43)
        p.add_run(f"{risk.get('description')}")

    # Section 3: Stories
    h3 = doc.add_heading(level=1)
    h3.add_run("3. Jira User Stories").font.color.rgb = RGBColor(31, 78, 121)
    for story in data.get("user_stories", []):
        p = doc.add_paragraph()
        p.add_run(f"Story: {story.get('title')}\n").bold = True
        clean_want = story.get('i_want', '').replace('to ', '', 1)
        p.add_run(f"As a {story.get('as_a')}, I want to {clean_want} so that {story.get('so_that')}.\n")
        p.add_run("Acceptance Criteria:\n").font.italic = True
        for ac in story.get("acceptance_criteria", []):
            doc.add_paragraph(f"☐ {ac}", style="List Bullet")

    out_path = f"Pitch_To_Project_Handover_Report_{time.strftime('%Y%m%d_%H%M%S')}.docx"
    doc.save(out_path)
    return out_path

# --- UI HEADER ---
st.title("⚡ PITCH TO PROJECT")
st.caption("Smart Scope Handover Engine | Project Intelligence Layer")

# Demo Mode Toggle
demo_mode = st.toggle("Demo Mode (Safe Pitch)", value=True)

# Main Two-Column Layout
col_input, col_output = st.columns([1, 1.3], gap="large")

with col_input:
    st.subheader("1. Intake Documents & Media")

    proposals = st.file_uploader("📁 Proposals / SOWs (.docx)", type=["docx"], accept_multiple_files=True)
    transcripts = st.file_uploader("📁 Transcripts / Notes (.txt)", type=["txt"], accept_multiple_files=True)
    media = st.file_uploader("🖼️ Diagrams & Media (.png, .jpg, .mp4, .mp3)", type=["png", "jpg", "jpeg", "mp4", "mp3", "wav"], accept_multiple_files=True)

    raw_notes = st.text_area("Or Paste Loose Client Emails / Notes:", height=120)

    generate_btn = st.button("⚡ GENERATE SMART SCOPE", type="primary", use_container_width=True)

# Execution Logic
if generate_btn:
    if demo_mode:
        st.session_state["analysis_data"] = DEMO_DATA
        st.toast("Loaded local sample scope data (Demo Mode).")
    else:
        combined_text = read_uploaded_sources(proposals, transcripts, raw_notes)

        if not combined_text and not media:
            st.warning("Please upload files or paste text before generating scope.")
        else:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                st.error("GEMINI_API_KEY not found in environment. Falling back to Demo Mode.")
                st.session_state["analysis_data"] = DEMO_DATA
            else:
                with st.spinner("Analyzing Scope & Running Gap Audit..."):
                    try:
                        from google import genai
                        from google.genai import types

                        client = genai.Client(api_key=api_key)

                        # Handle Media Uploads
                        media_handles = []
                        for m_file in media:
                            temp_path = f"temp_{m_file.name}"
                            with open(temp_path, "wb") as f:
                                f.write(m_file.getbuffer())
                            handle = client.files.upload(file=temp_path)
                            media_handles.append(handle)
                            os.remove(temp_path)

                        # Dynamic Model Check
                        available_models = []
                        try:
                            for m in client.models.list():
                                if hasattr(m, "supported_generation_methods") and "generateContent" in m.supported_generation_methods:
                                    available_models.append(m.name.replace("models/", ""))
                        except Exception:
                            pass

                        preferred = ["gemini-3.6-flash", "gemini-3.1-pro-preview", "gemini-2.5-flash"]
                        candidates = [m for m in preferred if m in available_models] or available_models or ["gemini-3.6-flash"]

                        payload = [SYSTEM_PROMPT] + media_handles + [f"PROJECT INPUT TEXT AND TABLES:\n{combined_text}"]

                        response = None
                        for model_name in candidates:
                            try:
                                response = client.models.generate_content(
                                    model=model_name,
                                    contents=payload,
                                    config=types.GenerateContentConfig(response_mime_type="application/json")
                                )
                                if response and response.text:
                                    break
                            except Exception:
                                continue

                        if response and response.text:
                            clean_text = response.text.strip()
                            if clean_text.startswith("```json"):
                                clean_text = clean_text.replace("```json", "", 1).rstrip("`")
                            if clean_text.endswith("```"):
                                clean_text = clean_text[:-3].strip()

                            data = json.loads(clean_text)

                            # Scope Validation Check
                            if not (data.get("extracted_scope") or data.get("risks_and_gaps") or data.get("user_stories")):
                                st.warning("Uploaded document does not contain software requirements.")
                            else:
                                st.session_state["analysis_data"] = data
                                st.success("✨ Smart scope analysis has been successfully generated!")
                        else:
                            st.session_state["analysis_data"] = DEMO_DATA

                    except Exception as e:
                        st.error(f"API Error: {e}")
                        st.session_state["analysis_data"] = DEMO_DATA

# Display Results
with col_output:
    st.subheader("2. AI Scope & Handover Analysis")

    data = st.session_state.get("analysis_data", None)

    if data:
        tab1, tab2, tab3 = st.tabs(["Extracted Scope", "Missing Items & Risks", "Jira User Stories"])

        with tab1:
            for item in data.get("extracted_scope", []):
                st.markdown(f"**📌 MODULE: {item.get('module', '').upper()}**")
                st.caption(f"Source: {item.get('source_citation', '')}")
                for req in item.get("requirements", []):
                    st.markdown(f"- {req}")
                st.divider()

        with tab2:
            for risk in data.get("risks_and_gaps", []):
                sev = risk.get("severity", "MEDIUM")
                icon = "🔴" if sev == "HIGH" else "🟠"
                st.markdown(f"**{icon} [{sev}] {risk.get('type', '').upper()}**")
                st.write(risk.get("description", ""))
                st.divider()

        with tab3:
            for story in data.get("user_stories", []):
                st.markdown(f"**🔷 STORY: {story.get('title')}**")
                clean_want = story.get("i_want", "").replace("to ", "", 1)
                st.write(f"As a **{story.get('as_a')}**, I want to **{clean_want}** so that **{story.get('so_that')}**.")
                st.caption("Acceptance Criteria:")
                for ac in story.get("acceptance_criteria", []):
                    st.markdown(f"- [ ] {ac}")
                st.divider()

        # Word Document Download Button
        docx_path = generate_word_report(data)
        with open(docx_path, "rb") as file:
            st.download_button(
                label="📄 Export Handover Report (.docx)",
                data=file,
                file_name=os.path.basename(docx_path),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
