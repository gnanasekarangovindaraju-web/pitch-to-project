import json
import time
import io
import docx
import streamlit as st
import streamlit.components.v1 as components
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
# 2. GLOBAL NEON UI CSS
# =============================================================================

css_code = """
<style>

/* -------------------------------------------------------------------------
   GLOBAL APPLICATION BACKGROUND
   ------------------------------------------------------------------------- */

.stApp {
    background:
        linear-gradient(
            125deg,
            #0f172a 0%,
            #1e1b4b 35%,
            #311042 70%,
            #0284c7 100%
        ) !important;

    background-attachment: fixed;
}


/* -------------------------------------------------------------------------
   LOGIN FORM
   ------------------------------------------------------------------------- */

div[data-testid="stForm"] {
    background: rgba(15, 23, 42, 0.95) !important;
    border: 2.5px solid #a855f7 !important;
    border-radius: 18px !important;
    padding: 36px !important;
    box-shadow: 0 0 40px rgba(168, 85, 247, 0.5) !important;
}


/* LOGIN LABELS */

div[data-testid="stForm"] label,
div[data-testid="stForm"] label p,
div[data-testid="stTextInput"] label p {
    color: #38bdf8 !important;
    font-weight: 900 !important;
    font-size: 1.4rem !important;
    letter-spacing: 0.5px !important;
    margin-bottom: 8px !important;
    text-align: left !important;
    width: 100% !important;
    display: block !important;
}


/* LOGIN INPUTS */

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

    text-align: left !important;

    box-shadow:
        0 0 14px rgba(56, 189, 248, 0.3) !important;
}


/* AUTOFILL */

input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
input:-webkit-autofill:active {

    -webkit-box-shadow:
        0 0 0 1000px #0f172a inset !important;

    -webkit-text-fill-color: #ffffff !important;

    caret-color: #ffffff !important;

    border: 2.5px solid #38bdf8 !important;
}


/* PLACEHOLDER */

div[data-testid="stTextInput"] input::placeholder,
input::placeholder {

    color: #94a3b8 !important;

    -webkit-text-fill-color: #94a3b8 !important;

    font-weight: 700 !important;

    font-size: 1.25rem !important;

    opacity: 1 !important;

    text-align: left !important;
}


/* PASSWORD ICON */

div[data-testid="stTextInput"] button svg,
div[data-testid="stForm"] svg {

    fill: #38bdf8 !important;

    stroke: #38bdf8 !important;

    width: 26px !important;

    height: 26px !important;
}


/* LOGIN BUTTON */

div[data-testid="stForm"] button[type="submit"],
div[data-testid="stForm"] button[data-testid="stFormSubmitButton"],
div[data-testid="stForm"] button {

    background:
        linear-gradient(
            90deg,
            #ec4899 0%,
            #8b5cf6 50%,
            #06b6d4 100%
        ) !important;

    border: none !important;

    border-radius: 14px !important;

    padding: 18px 32px !important;

    box-shadow:
        0 0 30px rgba(236, 72, 153, 0.7) !important;

    transition: all 0.3s ease !important;

    margin-top: 22px !important;

    width: 100% !important;
}


div[data-testid="stForm"] button[type="submit"] *,
div[data-testid="stForm"] button[type="submit"] p,
div[data-testid="stForm"] button[type="submit"] span {

    color: #ffffff !important;

    -webkit-text-fill-color: #ffffff !important;

    font-weight: 900 !important;

    font-size: 1.5rem !important;

    letter-spacing: 1.2px !important;
}


/* -------------------------------------------------------------------------
   SIDEBAR
   ------------------------------------------------------------------------- */

section[data-testid="stSidebar"] {

    background: rgba(15, 23, 42, 0.95) !important;

    border-right:
        1.5px solid #a855f7 !important;
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

    background:
        linear-gradient(
            90deg,
            #ec4899 0%,
            #f43f5e 100%
        ) !important;

    color: #ffffff !important;

    font-weight: 800 !important;

    font-size: 1.1rem !important;

    border-radius: 10px !important;

    box-shadow:
        0 0 15px rgba(244, 63, 94, 0.5) !important;

    border: none !important;

    margin-top: 10px !important;
}


/* -------------------------------------------------------------------------
   HEADINGS
   ------------------------------------------------------------------------- */

h1,
h2,
h3 {

    color: #f8fafc !important;

    font-weight: 800 !important;

    text-shadow:
        0 0 10px rgba(168, 85, 247, 0.3) !important;
}


div[data-testid="stMarkdownContainer"] p,
label[data-testid="stWidgetLabel"] p,
div[data-testid="stToggle"] span {

    color: #f8fafc !important;

    font-weight: 700 !important;
}


/* -------------------------------------------------------------------------
   FILE UPLOADER
   ------------------------------------------------------------------------- */

div[data-testid="stFileUploader"] {

    background:
        rgba(15, 23, 42, 0.95) !important;

    border:
        2px solid #a855f7 !important;

    border-radius:
        14px !important;

    padding:
        12px !important;
}


div[data-testid="stFileUploader"] section,
div[data-testid="stFileUploaderDropzone"],
div[data-testid="stFileUploader"]
[data-testid="stFileUploaderDropzone"] {

    background:
        #1e1b4b !important;

    border:
        2px dashed #38bdf8 !important;

    border-radius:
        10px !important;
}


div[data-testid="stFileUploaderDropzone"] *,
div[data-testid="stFileUploaderDropzone"] span,
div[data-testid="stFileUploaderDropzone"] small,
div[data-testid="stFileUploaderDropzone"] p {

    color:
        #ffffff !important;

    font-weight:
        700 !important;
}


/* -------------------------------------------------------------------------
   TOAST
   ------------------------------------------------------------------------- */

div[data-testid="stToast"],
div[data-testid="stToast"] > div {

    background-color:
        #1e1b4b !important;

    background:
        #1e1b4b !important;

    border:
        2px solid #38bdf8 !important;

    border-radius:
        12px !important;

    box-shadow:
        0 0 20px rgba(56, 189, 248, 0.5) !important;
}


div[data-testid="stToast"] * {

    color:
        #ffffff !important;

    font-weight:
        800 !important;
}


/* -------------------------------------------------------------------------
   DOWNLOAD BUTTON
   ------------------------------------------------------------------------- */

div[data-testid="stDownloadButton"] > button {

    background:
        linear-gradient(
            135deg,
            #10b981 0%,
            #059669 100%
        ) !important;

    border-radius:
        12px !important;

    border:
        none !important;

    box-shadow:
        0 0 18px rgba(16, 185, 129, 0.5) !important;

    width:
        100%;
}


div[data-testid="stDownloadButton"] > button * {

    color:
        #ffffff !important;

    font-weight:
        900 !important;
}


/* -------------------------------------------------------------------------
   TEXT AREA
   ------------------------------------------------------------------------- */

div[data-testid="stTextArea"] textarea {

    background:
        rgba(15, 23, 42, 0.85) !important;

    border:
        2px solid #a855f7 !important;

    border-radius:
        14px !important;

    color:
        #ffffff !important;
}


/* -------------------------------------------------------------------------
   NORMAL BUTTONS
   ------------------------------------------------------------------------- */

div.stButton > button {

    background:
        linear-gradient(
            90deg,
            #ec4899 0%,
            #8b5cf6 50%,
            #3b82f6 100%
        ) !important;

    color:
        #ffffff !important;

    font-weight:
        800 !important;

    font-size:
        1.05rem !important;

    border-radius:
        12px !important;

    border:
        none !important;

    padding:
        14px 28px !important;

    box-shadow:
        0 0 20px rgba(139, 92, 246, 0.5) !important;

    width:
        100%;
}


button[aria-selected="true"] {

    background:
        linear-gradient(
            135deg,
            #8b5cf6 0%,
            #ec4899 100%
        ) !important;

    color:
        #ffffff !important;
}


/* -------------------------------------------------------------------------
   CONTAINER CARDS
   ------------------------------------------------------------------------- */

div[data-testid="stVerticalBlockBorderWrapper"] > div {

    background:
        rgba(15, 23, 42, 0.8) !important;

    backdrop-filter:
        blur(10px) !important;

    border-left:
        6px solid #06b6d4 !important;

    border-radius:
        14px !important;

    padding:
        20px !important;
}


/* -------------------------------------------------------------------------
   CODE
   ------------------------------------------------------------------------- */

code {

    background-color:
        rgba(30, 27, 75, 0.95) !important;

    color:
        #38bdf8 !important;

    border:
        1px solid #a855f7 !important;

    border-radius:
        6px !important;

    padding:
        3px 8px !important;
}


/* -------------------------------------------------------------------------
   SMART SCOPE ANIMATED BANNER
   IMPORTANT:
   No <marquee> is used.
   ------------------------------------------------------------------------- */

.smart-banner {

    width: 100%;

    overflow: hidden;

    background:
        linear-gradient(
            90deg,
            #ec4899 0%,
            #8b5cf6 33%,
            #06b6d4 66%,
            #10b981 100%
        );

    color: #ffffff;

    padding: 10px 0;

    border-radius: 10px;

    font-weight: 800;

    font-size: 1.05rem;

    box-shadow:
        0 0 20px rgba(139, 92, 246, 0.4);

    margin-bottom: 24px;

    white-space: nowrap;
}


.smart-banner-track {

    display: inline-block;

    padding-left: 100%;

    animation:
        smart-scroll 18s linear infinite;
}


.smart-banner-text {

    display: inline-block;

    margin-right: 100px;
}


@keyframes smart-scroll {

    0% {
        transform: translateX(0%);
    }

    100% {
        transform: translateX(-100%);
    }
}


/* -------------------------------------------------------------------------
   ANALYSIS RESULT TEXT
   ------------------------------------------------------------------------- */

.scope-point {

    color: #f8fafc;

    font-size: 1.02rem;

    line-height: 1.6;

    margin: 6px 0;
}


.risk-description {

    color: #e2e8f0;

    font-size: 1.02rem;

    line-height: 1.6;
}


.story-text {

    color: #e2e8f0;

    font-size: 1.02rem;

    line-height: 1.6;
}

</style>
"""

st.markdown(css_code, unsafe_allow_html=True)


# =============================================================================
# 3. AUTHENTICATION
# =============================================================================

def check_password():

    """Returns True if the user has authenticated successfully."""

    if st.session_state.get("authenticated", False):
        return True

    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2.4, 1])

    with col2:

        with st.form("login_form"):

            components.html(
                """
                <div style="
                    background:
                        linear-gradient(
                            135deg,
                            #ec4899 0%,
                            #8b5cf6 50%,
                            #06b6d4 100%
                        );

                    border-radius: 14px;

                    padding: 24px 10px;

                    box-shadow:
                        0 0 25px rgba(236, 72, 153, 0.6);

                    text-align: center;

                    font-family:
                        system-ui,
                        -apple-system,
                        sans-serif;
                ">

                    <div style="
                        color: #ffffff;
                        font-size: 2.8rem;
                        font-weight: 900;
                        margin-bottom: 6px;
                        text-shadow:
                            0 3px 12px rgba(0, 0, 0, 0.8);
                        letter-spacing: -0.5px;
                    ">
                        🔒 Pitch to Project
                    </div>

                    <div style="
                        color: #ffffff;
                        font-size: 1.35rem;
                        font-weight: 800;
                        letter-spacing: 1px;
                        text-shadow:
                            0 2px 8px rgba(0, 0, 0, 0.8);
                    ">
                        ⚡ Scope Intelligence Engine Access
                    </div>

                </div>
                """,
                height=140
            )

            username = st.text_input(
                "Username",
                placeholder="Enter username"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter password"
            )

            submit = st.form_submit_button(
                "🔑 LOGIN TO ENGINE"
            )

            if submit:

                valid_user = st.secrets.get(
                    "APP_USER",
                    "admin"
                )

                valid_password = st.secrets.get(
                    "APP_PASSWORD",
                    "project2026"
                )

                if (
                    username == valid_user
                    and password == valid_password
                ):

                    st.session_state["authenticated"] = True

                    st.toast(
                        "⚡ Login Successful!",
                        icon="✅"
                    )

                    st.rerun()

                else:

                    st.error(
                        "❌ Invalid Username or Password"
                    )

    return False


# =============================================================================
# STOP IF NOT AUTHENTICATED
# =============================================================================

if not check_password():
    st.stop()


# =============================================================================
# 4. SIDEBAR
# =============================================================================

with st.sidebar:

    st.markdown("### 👤 User Session")

    st.write(
        "Logged in as **Admin**"
    )

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state["authenticated"] = False

        st.rerun()


# =============================================================================
# 5. GEMINI CLIENT
# =============================================================================

@st.cache_resource
def get_gemini_client():

    try:

        api_key = st.secrets["GEMINI_API_KEY"]

        return genai.Client(
            api_key=api_key
        )

    except Exception:

        return None


client = get_gemini_client()


# =============================================================================
# 6. PROGRESS BAR
# =============================================================================

def render_stylish_progress(
    percentage,
    status_text
):

    return f"""
    <div style="margin: 10px 0 18px 0;">

        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            margin-bottom:6px;
        ">

            <span style="
                color:#06b6d4;
                font-weight:800;
                font-size:0.95rem;
            ">
                {status_text}
            </span>

            <span style="
                color:#f59e0b;
                font-weight:900;
                font-size:1.05rem;
                text-shadow:
                    0 0 10px rgba(245,158,11,0.5);
            ">
                {percentage}%
            </span>

        </div>


        <div style="
            background:rgba(15,23,42,0.9);
            border:2px solid #10b981;
            border-radius:12px;
            padding:3px;
            box-shadow:
                0 0 15px rgba(16,185,129,0.3);
            position:relative;
            overflow:hidden;
        ">

            <div style="
                width:{percentage}%;
                height:18px;
                background:
                    linear-gradient(
                        90deg,
                        #10b981 0%,
                        #3b82f6 50%,
                        #f59e0b 100%
                    );
                border-radius:8px;
                box-shadow:
                    0 0 20px rgba(245,158,11,0.8);
                transition:
                    width 0.2s ease-in-out;
            ">
            </div>

        </div>

    </div>
    """


# =============================================================================
# 7. DOCUMENT EXTRACTION
# =============================================================================

def extract_text_from_uploads(
    sow_files,
    notes_files,
    loose_notes
):

    combined_text = ""

    # -------------------------------------------------------------------------
    # DOCX FILES
    # -------------------------------------------------------------------------

    if sow_files:

        for file in sow_files:

            try:

                doc = docx.Document(file)

                combined_text += (
                    f"\n--- FILE: {file.name} ---\n"
                )

                for index, para in enumerate(
                    doc.paragraphs,
                    start=1
                ):

                    text = para.text.strip()

                    if text:

                        combined_text += (
                            f"[Paragraph {index}] "
                            f"{text}\n"
                        )

                # Extract tables as well

                for table_index, table in enumerate(
                    doc.tables,
                    start=1
                ):

                    combined_text += (
                        f"\n[TABLE {table_index}]\n"
                    )

                    for row in table.rows:

                        row_values = []

                        for cell in row.cells:

                            row_values.append(
                                cell.text.strip()
                            )

                        combined_text += (
                            " | ".join(row_values)
                            + "\n"
                        )

            except Exception as e:

                combined_text += (
                    f"\n--- FILE ERROR: {file.name} ---\n"
                    f"{str(e)}\n"
                )


    # -------------------------------------------------------------------------
    # TXT FILES
    # -------------------------------------------------------------------------

    if notes_files:

        for file in notes_files:

            try:

                content = file.read()

                if isinstance(content, bytes):

                    content = content.decode(
                        "utf-8",
                        errors="replace"
                    )

                combined_text += (
                    f"\n--- FILE: {file.name} ---\n"
                )

                combined_text += (
                    content + "\n"
                )

            except Exception as e:

                combined_text += (
                    f"\n--- FILE ERROR: {file.name} ---\n"
                    f"{str(e)}\n"
                )


    # -------------------------------------------------------------------------
    # LOOSE NOTES
    # -------------------------------------------------------------------------

    if loose_notes and loose_notes.strip():

        combined_text += (
            "\n--- LOOSE CLIENT EMAILS / NOTES ---\n"
        )

        combined_text += (
            loose_notes.strip()
            + "\n"
        )


    return combined_text


# =============================================================================
# 8. PROFESSIONAL SMART SCOPE ENGINE PROMPT
# =============================================================================

def build_scope_prompt(raw_text):

    return f"""
You are an expert IT Delivery Lead, Business Analyst,
Systems Analyst, Solution Architect and Project Handover Specialist.

Your job is to transform raw project intake material into a
professional, implementation-ready Smart Scope Analysis.

The input may contain:

- Statements of Work
- Proposals
- Client emails
- Meeting notes
- Kickoff transcripts
- Requirements
- Technical notes
- Tables
- Business requirements
- Functional requirements
- Non-functional requirements
- Constraints
- Assumptions
- Dependencies
- Risks
- Open questions

IMPORTANT PRINCIPLES
====================

1. DO NOT invent requirements.

2. Only extract information that is explicitly stated or can be
   safely inferred from the provided material.

3. Clearly identify ambiguity instead of guessing.

4. Preserve conflicts between documents.

5. Identify missing information that could affect development,
   testing, deployment, cost, schedule or acceptance.

6. Convert requirements into professional Jira-ready user stories.

7. Acceptance criteria must be testable.

8. Distinguish between:
   - confirmed requirement
   - assumption
   - dependency
   - risk
   - missing information
   - open question

9. When multiple documents disagree, report the conflict rather
   than selecting one arbitrarily.

10. Source references must identify the originating file whenever
    possible.

11. Do not generate marketing language.

12. Do not make unsupported technical decisions.

13. Think like a senior delivery professional preparing a project
    for estimation, development, QA, UAT and handover.

ANALYSIS OBJECTIVES
===================

A. Extract the actual project scope.

Group related requirements into logical modules.

Examples:

- Authentication & Security
- User Management
- Administration
- Dashboard
- Workflow
- Notifications
- Reporting
- Integrations
- Data Management
- API
- UI/UX
- Infrastructure
- Deployment
- Testing

Do not create modules that are unsupported by the input.

B. Identify gaps and risks.

Look specifically for:

- Missing acceptance criteria
- Missing SLA
- Missing performance expectations
- Missing security requirements
- Missing roles/permissions
- Missing data definitions
- Missing integrations
- Missing API details
- Missing environments
- Missing deployment requirements
- Missing backup/recovery requirements
- Missing monitoring requirements
- Missing browser/device support
- Missing accessibility requirements
- Missing audit requirements
- Missing reporting definitions
- Missing notification rules
- Missing error handling
- Missing authentication details
- Missing retention requirements
- Missing ownership
- Missing deadlines
- Missing UAT criteria
- Conflicting requirements
- Ambiguous requirements
- Technical dependencies
- External dependencies

C. Generate Jira user stories.

Each story must:

- Have a clear title.
- Identify the correct user role.
- Describe one meaningful capability.
- Explain the business value.
- Contain testable acceptance criteria.
- Avoid combining unrelated capabilities into one story.

Acceptance criteria should preferably follow:

Given ...
When ...
Then ...

D. Detect requirement conflicts.

If one source says one thing and another source says something
different, create a conflict risk and cite both sources.

E. Identify open questions.

These are questions the delivery team should ask the client before
development or estimation.

OUTPUT FORMAT
=============

Return ONLY valid JSON.

Do not return Markdown.

Do not return explanations outside JSON.

Use EXACTLY this structure:

{{
  "project_summary": {{
    "project_name": "",
    "objective": "",
    "primary_users": [],
    "overall_scope_summary": ""
  }},

  "extracted_scope": [
    {{
      "module": "",
      "source": "",
      "confidence": "HIGH/MEDIUM/LOW",
      "points": []
    }}
  ],

  "functional_requirements": [
    {{
      "requirement_id": "FR-001",
      "module": "",
      "requirement": "",
      "source": "",
      "priority": "MUST/SHOULD/COULD/UNKNOWN"
    }}
  ],

  "non_functional_requirements": [
    {{
      "category": "",
      "requirement": "",
      "source": "",
      "priority": "MUST/SHOULD/COULD/UNKNOWN"
    }}
  ],

  "assumptions": [
    {{
      "assumption": "",
      "reason": "",
      "impact": "HIGH/MEDIUM/LOW"
    }}
  ],

  "dependencies": [
    {{
      "dependency": "",
      "owner": "",
      "impact": "HIGH/MEDIUM/LOW"
    }}
  ],

  "gaps_and_risks": [
    {{
      "severity": "HIGH/MEDIUM/LOW",
      "type": "",
      "description": "",
      "impact": "",
      "recommended_action": "",
      "source": ""
    }}
  ],

  "open_questions": [
    {{
      "question": "",
      "reason": "",
      "priority": "HIGH/MEDIUM/LOW"
    }}
  ],

  "jira_user_stories": [
    {{
      "story_id": "US-001",
      "title": "",
      "user_role": "",
      "want_statement": "",
      "so_that_statement": "",
      "priority": "HIGH/MEDIUM/LOW",
      "acceptance_criteria": []
    }}
  ]
}}

INPUT MATERIALS
===============

{raw_text}
"""


# =============================================================================
# 9. GEMINI ANALYSIS
# =============================================================================

def analyze_with_gemini(raw_text):

    if not client:

        st.error(
            "GEMINI_API_KEY is missing in Streamlit Secrets."
        )

        return None


    prompt = build_scope_prompt(
        raw_text
    )


    try:

        response = client.models.generate_content(

            model="gemini-3.6-flash",

            contents=prompt,

            config=types.GenerateContentConfig(

                response_mime_type="application/json",

                temperature=0.2
            )
        )


        response_text = response.text.strip()


        # Remove accidental markdown fences

        if response_text.startswith("```"):

            response_text = (
                response_text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )


        data = json.loads(
            response_text
        )


        return data


    except json.JSONDecodeError as e:

        st.error(
            f"Gemini returned invalid JSON: {str(e)}"
        )

        return None


    except Exception as e:

        st.error(
            f"Gemini API Error: {str(e)}"
        )

        return None


# =============================================================================
# 10. MOCK ANALYSIS
# =============================================================================

MOCK_ANALYSIS = {

    "project_summary": {

        "project_name":
            "Smart Scope Handover Engine",

        "objective":
            "Transform project intake materials into structured delivery scope.",

        "primary_users": [
            "Delivery Lead",
            "Business Analyst",
            "Project Manager"
        ],

        "overall_scope_summary":
            "AI-assisted extraction of project scope, risks, gaps and Jira-ready user stories."
    },


    "extracted_scope": [

        {

            "module":
                "AUTHENTICATION & SECURITY",

            "source":
                "Proposal Page 4, Section 2",

            "confidence":
                "HIGH",

            "points": [

                "Multi-factor authentication (MFA) via SMS/Email.",

                "Role-based access control (RBAC) for Admin and Client roles."
            ]
        },


        {

            "module":
                "HANDOVER INTELLIGENCE ENGINE",

            "source":
                "Kickoff Transcript Lines 12-45",

            "confidence":
                "HIGH",

            "points": [

                "Multi-format document parsing.",

                "Automated gap auditing.",

                "Structured requirement extraction."
            ]
        }
    ],


    "functional_requirements": [

        {

            "requirement_id":
                "FR-001",

            "module":
                "Document Processing",

            "requirement":
                "The system shall ingest project intake documents.",

            "source":
                "Kickoff Transcript",

            "priority":
                "MUST"
        }
    ],


    "non_functional_requirements": [],


    "assumptions": [],


    "dependencies": [],


    "gaps_and_risks": [

        {

            "severity":
                "HIGH",

            "type":
                "Missing SLA",

            "description":
                "No operational SLA is defined for document processing.",

            "impact":
                "Processing expectations cannot be validated.",

            "recommended_action":
                "Define maximum processing time and acceptable timeout behavior.",

            "source":
                "Project intake materials"
        },


        {

            "severity":
                "MEDIUM",

            "type":
                "Cross-Document Conflict",

            "description":
                "Different document sources may specify different upload limits.",

            "impact":
                "Implementation and infrastructure sizing may be affected.",

            "recommended_action":
                "Confirm the final supported upload size with the client.",

            "source":
                "Project intake materials"
        }
    ],


    "open_questions": [

        {

            "question":
                "What is the maximum supported document size?",

            "reason":
                "Required for infrastructure and performance planning.",

            "priority":
                "HIGH"
        }
    ],


    "jira_user_stories": [

        {

            "story_id":
                "US-001",

            "title":
                "Process Project Intake Documents",

            "user_role":
                "Delivery Lead",

            "want_statement":
                "ingest project intake documents",

            "so_that_statement":
                "I can automatically extract structured project requirements",

            "priority":
                "HIGH",

            "acceptance_criteria": [

                "Given a user uploads a supported project document",

                "When the user clicks Generate Smart Scope",

                "Then the system processes the document and generates structured scope information."
            ]
        }
    ]
}


# =============================================================================
# 11. DOCX REPORT GENERATOR
# =============================================================================

def build_docx_report(data):

    doc = docx.Document()


    # -------------------------------------------------------------------------
    # TITLE
    # -------------------------------------------------------------------------

    doc.add_heading(
        "Pitch to Project - Smart Scope Handover Analysis",
        0
    )


    # -------------------------------------------------------------------------
    # PROJECT SUMMARY
    # -------------------------------------------------------------------------

    summary = data.get(
        "project_summary",
        {}
    )

    doc.add_heading(
        "1. Project Summary",
        level=1
    )

    doc.add_paragraph(
        f"Project Name: "
        f"{summary.get('project_name', '')}"
    )

    doc.add_paragraph(
        f"Objective: "
        f"{summary.get('objective', '')}"
    )

    doc.add_paragraph(
        f"Scope Summary: "
        f"{summary.get('overall_scope_summary', '')}"
    )


    # -------------------------------------------------------------------------
    # EXTRACTED SCOPE
    # -------------------------------------------------------------------------

    doc.add_heading(
        "2. Extracted Scope",
        level=1
    )

    for item in data.get(
        "extracted_scope",
        []
    ):

        doc.add_heading(
            f"Module: {item.get('module', 'General')}",
            level=2
        )

        doc.add_paragraph(
            f"Source: {item.get('source', '')}"
        )

        doc.add_paragraph(
            f"Confidence: "
            f"{item.get('confidence', '')}"
        )

        for point in item.get(
            "points",
            []
        ):

            doc.add_paragraph(
                f"• {point}"
            )


    # -------------------------------------------------------------------------
    # FUNCTIONAL REQUIREMENTS
    # -------------------------------------------------------------------------

    doc.add_heading(
        "3. Functional Requirements",
        level=1
    )

    for item in data.get(
        "functional_requirements",
        []
    ):

        doc.add_paragraph(
            f"{item.get('requirement_id', '')} - "
            f"{item.get('requirement', '')}"
        )

        doc.add_paragraph(
            f"Module: {item.get('module', '')}"
        )

        doc.add_paragraph(
            f"Priority: {item.get('priority', '')}"
        )

        doc.add_paragraph(
            f"Source: {item.get('source', '')}"
        )


    # -------------------------------------------------------------------------
    # NON-FUNCTIONAL REQUIREMENTS
    # -------------------------------------------------------------------------

    doc.add_heading(
        "4. Non-Functional Requirements",
        level=1
    )

    for item in data.get(
        "non_functional_requirements",
        []
    ):

        doc.add_paragraph(
            f"[{item.get('category', '')}] "
            f"{item.get('requirement', '')}"
        )


    # -------------------------------------------------------------------------
    # ASSUMPTIONS
    # -------------------------------------------------------------------------

    doc.add_heading(
        "5. Assumptions",
        level=1
    )

    for item in data.get(
        "assumptions",
        []
    ):

        doc.add_paragraph(
            f"{item.get('assumption', '')}"
        )

        doc.add_paragraph(
            f"Reason: {item.get('reason', '')}"
        )


    # -------------------------------------------------------------------------
    # DEPENDENCIES
    # -------------------------------------------------------------------------

    doc.add_heading(
        "6. Dependencies",
        level=1
    )

    for item in data.get(
        "dependencies",
        []
    ):

        doc.add_paragraph(
            f"{item.get('dependency', '')}"
        )


    # -------------------------------------------------------------------------
    # RISKS
    # -------------------------------------------------------------------------

    doc.add_heading(
        "7. Gaps & Risk Audit",
        level=1
    )

    for gap in data.get(
        "gaps_and_risks",
        []
    ):

        doc.add_paragraph(

            f"[{gap.get('severity', 'INFO')}] "
            f"{gap.get('type', 'Risk')}: "
            f"{gap.get('description', '')}"
        )

        doc.add_paragraph(
            f"Impact: {gap.get('impact', '')}"
        )

        doc.add_paragraph(
            f"Recommended Action: "
            f"{gap.get('recommended_action', '')}"
        )


    # -------------------------------------------------------------------------
    # OPEN QUESTIONS
    # -------------------------------------------------------------------------

    doc.add_heading(
        "8. Open Questions",
        level=1
    )

    for question in data.get(
        "open_questions",
        []
    ):

        doc.add_paragraph(
            f"[{question.get('priority', '')}] "
            f"{question.get('question', '')}"
        )

        doc.add_paragraph(
            f"Reason: {question.get('reason', '')}"
        )


    # -------------------------------------------------------------------------
    # JIRA STORIES
    # -------------------------------------------------------------------------

    doc.add_heading(
        "9. Jira User Stories",
        level=1
    )

    for story in data.get(
        "jira_user_stories",
        []
    ):

        doc.add_heading(
            f"{story.get('story_id', '')} - "
            f"{story.get('title', 'User Story')}",
            level=2
        )

        doc.add_paragraph(

            f"As a "
            f"{story.get('user_role', 'User')}, "
            f"I want to "
            f"{story.get('want_statement', '')} "
            f"so that "
            f"{story.get('so_that_statement', '')}."
        )

        doc.add_paragraph(
            f"Priority: "
            f"{story.get('priority', '')}"
        )

        doc.add_paragraph(
            "Acceptance Criteria:"
        )

        for ac in story.get(
            "acceptance_criteria",
            []
        ):

            doc.add_paragraph(
                f"- {ac}"
            )


    # -------------------------------------------------------------------------
    # SAVE IN MEMORY
    # -------------------------------------------------------------------------

    target_stream = io.BytesIO()

    doc.save(
        target_stream
    )

    target_stream.seek(0)

    return target_stream.getvalue()


# =============================================================================
# 12. MAIN ANIMATED BANNER
# =============================================================================

st.markdown(
    """
    <div class="smart-banner">

        <div class="smart-banner-track">

            <span class="smart-banner-text">
                ⚡ Smart Scope Handover Engine
                &nbsp; | &nbsp;
                Project Intelligence Layer
            </span>

            <span class="smart-banner-text">
                ⚡ Smart Scope Handover Engine
                &nbsp; | &nbsp;
                Project Intelligence Layer
            </span>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =============================================================================
# 13. MAIN HEADER
# =============================================================================

col_title, col_toggle = st.columns(
    [3, 1]
)


with col_title:

    components.html(
        """
        <div style="
            font-family:
                system-ui,
                -apple-system,
                sans-serif;
        ">

            <div style="
                color:#ffffff;
                font-size:2.8rem;
                font-weight:900;
                margin:0;
                line-height:1.2;
                text-shadow:
                    0 0 15px rgba(56,189,248,0.6);
            ">
                Pitch to Project
            </div>

            <div style="
                color:#38bdf8;
                font-size:1.05rem;
                font-weight:700;
                margin-top:6px;
                line-height:1.3;
            ">
                🚀 AI-Powered Scope Intelligence & Handover Engine
            </div>

        </div>
        """,
        height=120
    )


with col_toggle:

    demo_mode = st.toggle(
        "Demo Mode (Safe Pitch)",
        value=True
    )


# =============================================================================
# 14. TWO-COLUMN MAIN LAYOUT
# =============================================================================

left_col, right_col = st.columns(
    [1, 1],
    gap="medium"
)


# =============================================================================
# LEFT COLUMN
# =============================================================================

with left_col:

    st.header(
        "1. Intake Documents & Media"
    )


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
        type=[
            "png",
            "jpg",
            "mp4",
            "mp3"
        ],
        accept_multiple_files=True
    )


    loose_notes = st.text_area(

        "Or Paste Loose Client Emails / Notes:",

        height=120,

        placeholder=
            "Paste kickoff notes or client requirements here..."
    )


    generate_btn = st.button(
        "⚡ GENERATE SMART SCOPE"
    )


# =============================================================================
# RIGHT COLUMN
# =============================================================================

with right_col:

    st.header(
        "2. AI Scope & Handover Analysis"
    )


    # -------------------------------------------------------------------------
    # GENERATE
    # -------------------------------------------------------------------------

    if generate_btn:

        progress_card = st.empty()


        # ---------------------------------------------------------------------
        # DEMO MODE
        # ---------------------------------------------------------------------

        if demo_mode:

            with progress_card.container(
                border=True
            ):

                st.markdown(
                    "### 🧠 Running Scope Analysis"
                )

                bar_ph = st.empty()


                for i in range(101):

                    time.sleep(
                        0.01
                    )

                    bar_ph.markdown(

                        render_stylish_progress(

                            i,

                            "⚙️ Processing intake materials & generating user stories..."
                        ),

                        unsafe_allow_html=True
                    )


                st.success(
                    "✅ Demo Analysis Loaded Successfully!"
                )

                time.sleep(
                    0.4
                )


            progress_card.empty()


            st.session_state[
                "analysis_data"
            ] = MOCK_ANALYSIS


            st.toast(
                "⚡ Demo Analysis Loaded!",
                icon="✅"
            )


        # ---------------------------------------------------------------------
        # LIVE GEMINI MODE
        # ---------------------------------------------------------------------

        else:

            raw_text = extract_text_from_uploads(

                sow_files,

                notes_files,

                loose_notes
            )


            if not raw_text.strip():

                st.warning(
                    "Please upload at least one document "
                    "or paste text before analyzing."
                )

            else:

                with progress_card.container(
                    border=True
                ):

                    st.markdown(
                        "### 🧠 Live Gemini Scope Extraction"
                    )


                    bar_ph = st.empty()


                    bar_ph.markdown(

                        render_stylish_progress(

                            20,

                            "📄 Step 1/3: Extracting requirements from intake documents..."
                        ),

                        unsafe_allow_html=True
                    )


                    time.sleep(
                        0.3
                    )


                    bar_ph.markdown(

                        render_stylish_progress(

                            50,

                            "⚡ Step 2/3: Sending structured intake payload to Gemini..."
                        ),

                        unsafe_allow_html=True
                    )


                    time.sleep(
                        0.3
                    )


                    bar_ph.markdown(

                        render_stylish_progress(

                            80,

                            "🔍 Step 3/3: Auditing scope, risks, gaps & Jira stories..."
                        ),

                        unsafe_allow_html=True
                    )


                    result = analyze_with_gemini(
                        raw_text
                    )


                    if result:

                        bar_ph.markdown(

                            render_stylish_progress(

                                100,

                                "✅ Smart Scope Handover Analysis Complete!"
                            ),

                            unsafe_allow_html=True
                        )


                        st.success(
                            "✅ Scope Successfully Extracted!"
                        )


                        time.sleep(
                            0.5
                        )


                        st.session_state[
                            "analysis_data"
                        ] = result


                        st.toast(
                            "⚡ Live Gemini Extraction Complete!",
                            icon="✅"
                        )


                    else:

                        st.error(
                            "❌ Extraction Failed"
                        )


                progress_card.empty()


    # -------------------------------------------------------------------------
    # DEFAULT DATA
    # -------------------------------------------------------------------------

    if "analysis_data" not in st.session_state:

        st.session_state[
            "analysis_data"
        ] = MOCK_ANALYSIS


    data = st.session_state[
        "analysis_data"
    ]


    # =============================================================================
    # TABS
    # =============================================================================

    tab_scope, tab_requirements, tab_risks, tab_questions, tab_jira = st.tabs(

        [
            "📌 Extracted Scope",
            "📋 Requirements",
            "🚨 Missing Items & Risks",
            "❓ Open Questions",
            "🚀 Jira User Stories"
        ]
    )


    # =========================================================================
    # SCOPE TAB
    # =========================================================================

    with tab_scope:

        summary = data.get(
            "project_summary",
            {}
        )

        if summary:

            with st.container(
                border=True
            ):

                st.markdown(
                    "### 🎯 Project Summary"
                )

                st.write(
                    summary.get(
                        "overall_scope_summary",
                        ""
                    )
                )


        for item in data.get(
            "extracted_scope",
            []
        ):

            with st.container(
                border=True
            ):

                st.markdown(
                    f"### 📌 MODULE: "
                    f"{item.get('module', 'General Scope')}"
                )


                st.caption(
                    f"Source: "
                    f"{item.get('source', 'Uploaded Files')} "
                    f"| Confidence: "
                    f"{item.get('confidence', 'UNKNOWN')}"
                )


                for pt in item.get(
                    "points",
                    []
                ):

                    st.markdown(
                        f"• {pt}"
                    )


    # =========================================================================
    # REQUIREMENTS TAB
    # =========================================================================

    with tab_requirements:

        st.markdown(
            "### 📋 Functional Requirements"
        )


        for item in data.get(
            "functional_requirements",
            []
        ):

            with st.container(
                border=True
            ):

                st.markdown(

                    f"### "
                    f"{item.get('requirement_id', '')} "
                    f"| {item.get('module', '')}"
                )


                st.write(
                    item.get(
                        "requirement",
                        ""
                    )
                )


                st.caption(

                    f"Priority: "
                    f"{item.get('priority', '')} "
                    f"| Source: "
                    f"{item.get('source', '')}"
                )


        st.markdown(
            "### ⚙️ Non-Functional Requirements"
        )


        for item in data.get(
            "non_functional_requirements",
            []
        ):

            with st.container(
                border=True
            ):

                st.markdown(

                    f"### "
                    f"{item.get('category', 'General')}"
                )

                st.write(
                    item.get(
                        "requirement",
                        ""
                    )
                )

                st.caption(
                    f"Priority: "
                    f"{item.get('priority', '')} "
                    f"| Source: "
                    f"{item.get('source', '')}"
                )


    # =========================================================================
    # RISKS TAB
    # =========================================================================

    with tab_risks:

        risks = data.get(
            "gaps_and_risks",
            []
        )


        if not risks:

            st.success(
                "✅ No major gaps or risks were identified."
            )


        for risk in risks:

            with st.container(
                border=True
            ):

                severity = risk.get(
                    "severity",
                    "INFO"
                ).upper()


                badge_color = (

                    "🔴"
                    if severity == "HIGH"

                    else "🟡"
                    if severity == "MEDIUM"

                    else "🔵"
                )


                st.markdown(

                    f"### "
                    f"{badge_color} "
                    f"[{severity}] "
                    f"{risk.get('type', 'Risk')}"
                )


                st.write(
                    risk.get(
                        "description",
                        ""
                    )
                )


                if risk.get(
                    "impact"
                ):

                    st.markdown(
                        f"**Impact:** "
                        f"{risk.get('impact')}"
                    )


                if risk.get(
                    "recommended_action"
                ):

                    st.markdown(
                        f"**Recommended Action:** "
                        f"{risk.get('recommended_action')}"
                    )


                if risk.get(
                    "source"
                ):

                    st.caption(
                        f"Source: "
                        f"{risk.get('source')}"
                    )


    # =========================================================================
    # QUESTIONS TAB
    # =========================================================================

    with tab_questions:

        questions = data.get(
            "open_questions",
            []
        )


        if not questions:

            st.success(
                "✅ No open questions were identified."
            )


        for question in questions:

            with st.container(
                border=True
            ):

                priority = question.get(
                    "priority",
                    "MEDIUM"
                )


                st.markdown(
                    f"### ❓ "
                    f"[{priority}] "
                    f"{question.get('question', '')}"
                )


                st.write(
                    question.get(
                        "reason",
                        ""
                    )
                )


    # =========================================================================
    # JIRA TAB
    # =========================================================================

    with tab_jira:

        stories = data.get(
            "jira_user_stories",
            []
        )


        if not stories:

            st.info(
                "No Jira user stories were generated."
            )


        for story in stories:

            with st.container(
                border=True
            ):

                st.markdown(

                    f"### 🚀 "
                    f"{story.get('story_id', '')} "
                    f"| "
                    f"{story.get('title', 'User Story')}"
                )


                st.markdown(

                    f"**As a** "
                    f"`{story.get('user_role', 'User')}`, "
                    f"**I want to** "
                    f"{story.get('want_statement', '')} "
                    f"**so that** "
                    f"{story.get('so_that_statement', '')}."
                )


                st.caption(

                    f"Priority: "
                    f"{story.get('priority', 'UNKNOWN')}"
                )


                st.markdown(
                    "**Acceptance Criteria:**"
                )


                for ac in story.get(
                    "acceptance_criteria",
                    []
                ):

                    st.markdown(
                        f"- `{ac}`"
                    )


    # =============================================================================
    # EXPORT REPORT
    # =============================================================================

    st.divider()


    docx_bytes = build_docx_report(
        data
    )


    st.download_button(

        label=
            "📄 Export Handover Report (.docx)",

        data=
            docx_bytes,

        file_name=
            "Pitch_to_Project_Handover_Report.docx",

        mime=
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",

        use_container_width=True
    )
