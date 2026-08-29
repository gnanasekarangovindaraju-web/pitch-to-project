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

/* =========================================================
   GLOBAL APPLICATION BACKGROUND
   ========================================================= */

.stApp {
    background:
        linear-gradient(
            125deg,
            #0f172a 0%,
            #1e1b4b 35%,
            #311042 70%,
            #0284c7 100%
        ) !important;

    background-attachment: fixed !important;
}


/* =========================================================
   LOGIN FORM
   ========================================================= */

div[data-testid="stForm"] {
    background: rgba(15, 23, 42, 0.95) !important;
    border: 2.5px solid #a855f7 !important;
    border-radius: 18px !important;
    padding: 36px !important;
    box-shadow: 0 0 40px rgba(168, 85, 247, 0.5) !important;
}


/* =========================================================
   LOGIN LABELS
   ========================================================= */

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


/* =========================================================
   INPUT FIELDS
   ========================================================= */

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


/* =========================================================
   AUTOFILL
   ========================================================= */

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


/* =========================================================
   PLACEHOLDER
   ========================================================= */

div[data-testid="stTextInput"] input::placeholder,
input::placeholder {

    color: #94a3b8 !important;
    -webkit-text-fill-color: #94a3b8 !important;

    font-weight: 700 !important;
    font-size: 1.25rem !important;

    opacity: 1 !important;
    text-align: left !important;
}


/* =========================================================
   PASSWORD ICON
   ========================================================= */

div[data-testid="stTextInput"] button svg,
div[data-testid="stForm"] svg {

    fill: #38bdf8 !important;
    stroke: #38bdf8 !important;

    width: 26px !important;
    height: 26px !important;
}


/* =========================================================
   LOGIN BUTTON
   ========================================================= */

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


/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {

    background:
        rgba(15, 23, 42, 0.95) !important;

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
    border: none !important;

    box-shadow:
        0 0 15px rgba(244, 63, 94, 0.5) !important;

    margin-top: 10px !important;
}


/* =========================================================
   HEADINGS
   ========================================================= */

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


/* =========================================================
   FILE UPLOADER
   ========================================================= */

div[data-testid="stFileUploader"] {

    background:
        rgba(15, 23, 42, 0.95) !important;

    border:
        2px solid #a855f7 !important;

    border-radius: 14px !important;

    padding: 12px !important;
}


div[data-testid="stFileUploader"] section,
div[data-testid="stFileUploaderDropzone"],
div[data-testid="stFileUploader"]
[data-testid="stFileUploaderDropzone"] {

    background: #1e1b4b !important;

    border:
        2px dashed #38bdf8 !important;

    border-radius: 10px !important;
}


div[data-testid="stFileUploaderDropzone"] *,
div[data-testid="stFileUploaderDropzone"] span,
div[data-testid="stFileUploaderDropzone"] small,
div[data-testid="stFileUploaderDropzone"] p {

    color: #ffffff !important;

    font-weight: 700 !important;
}


/* =========================================================
   TOAST
   ========================================================= */

div[data-testid="stToast"],
div[data-testid="stToast"] > div {

    background-color: #1e1b4b !important;
    background: #1e1b4b !important;

    border:
        2px solid #38bdf8 !important;

    border-radius: 12px !important;

    box-shadow:
        0 0 20px rgba(56, 189, 248, 0.5) !important;
}


div[data-testid="stToast"] * {

    color: #ffffff !important;

    font-weight: 800 !important;
}


/* =========================================================
   DOWNLOAD BUTTON
   ========================================================= */

div[data-testid="stDownloadButton"] > button {

    background:
        linear-gradient(
            135deg,
            #10b981 0%,
            #059669 100%
        ) !important;

    border-radius: 12px !important;

    border: none !important;

    box-shadow:
        0 0 18px rgba(16, 185, 129, 0.5) !important;

    width: 100%;
}


div[data-testid="stDownloadButton"] > button * {

    color: #ffffff !important;

    font-weight: 900 !important;
}


/* =========================================================
   TEXT AREA
   ========================================================= */

div[data-testid="stTextArea"] textarea {

    background:
        rgba(15, 23, 42, 0.85) !important;

    border:
        2px solid #a855f7 !important;

    border-radius: 14px !important;

    color: #ffffff !important;
}


/* =========================================================
   GENERAL BUTTON
   ========================================================= */

div.stButton > button {

    background:
        linear-gradient(
            90deg,
            #ec4899 0%,
            #8b5cf6 50%,
            #3b82f6 100%
        ) !important;

    color: #ffffff !important;

    font-weight: 800 !important;
    font-size: 1.05rem !important;

    border-radius: 12px !important;
    border: none !important;

    padding: 14px 28px !important;

    box-shadow:
        0 0 20px rgba(139, 92, 246, 0.5) !important;

    width: 100%;
}


button[aria-selected="true"] {

    background:
        linear-gradient(
            135deg,
            #8b5cf6 0%,
            #ec4899 100%
        ) !important;

    color: #ffffff !important;
}


/* =========================================================
   RESULT CARDS
   ========================================================= */

div[data-testid="stVerticalBlockBorderWrapper"] > div {

    background:
        rgba(15, 23, 42, 0.8) !important;

    backdrop-filter:
        blur(10px) !important;

    border-left:
        6px solid #06b6d4 !important;

    border-radius: 14px !important;

    padding: 20px !important;
}


/* =========================================================
   CODE
   ========================================================= */

code {

    background-color:
        rgba(30, 27, 75, 0.95) !important;

    color: #38bdf8 !important;

    border:
        1px solid #a855f7 !important;

    border-radius: 6px !important;

    padding: 3px 8px !important;
}


/* =========================================================
   SMART TOP BANNER
   ========================================================= */

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

    border-radius: 10px;

    padding: 10px 0;

    margin-bottom: 24px;

    box-shadow:
        0 0 20px rgba(139, 92, 246, 0.45);

    font-weight: 800;

    font-size: 1.05rem;

    white-space: nowrap;
}


.smart-banner-inner {

    display: inline-block;

    padding-left: 100%;

    animation:
        smartBannerScroll 18s linear infinite;
}


.smart-banner-text {

    display: inline-block;

    margin-right: 180px;

    color: #ffffff;

    font-weight: 800;
}


@keyframes smartBannerScroll {

    0% {
        transform: translateX(0);
    }

    100% {
        transform: translateX(-100%);
    }
}

</style>
"""

st.markdown(css_code, unsafe_allow_html=True)


# =============================================================================
# 3. AUTHENTICATION
# =============================================================================

def check_password():
    """Display login screen and return True after successful authentication."""

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
                            0 3px 12px rgba(0,0,0,0.8);
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
                            0 2px 8px rgba(0,0,0,0.8);
                    ">
                        ⚡ Scope Intelligence Engine Access
                    </div>

                </div>
                """,
                height=140,
            )

            username = st.text_input(
                "Username",
                placeholder="Enter username",
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter password",
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
    <div style="
        margin: 10px 0 18px 0;
    ">

        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        ">

            <span style="
                color: #06b6d4;
                font-weight: 800;
                font-size: 0.95rem;
            ">
                {status_text}
            </span>

            <span style="
                color: #f59e0b;
                font-weight: 900;
                font-size: 1.05rem;
                text-shadow:
                    0 0 10px rgba(245,158,11,0.5);
            ">
                {percentage}%
            </span>

        </div>

        <div style="
            background: rgba(15,23,42,0.9);
            border: 2px solid #10b981;
            border-radius: 12px;
            padding: 3px;
            box-shadow:
                0 0 15px rgba(16,185,129,0.3);
            position: relative;
            overflow: hidden;
        ">

            <div style="
                width: {percentage}%;
                height: 18px;

                background:
                    linear-gradient(
                        90deg,
                        #10b981 0%,
                        #3b82f6 50%,
                        #f59e0b 100%
                    );

                border-radius: 8px;

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
# 7. FILE EXTRACTION
# =============================================================================

def extract_text_from_uploads(
    sow_files,
    notes_files,
    loose_notes
):
    """
    Extract textual content from uploaded documents.

    Supports:
        DOCX
        TXT
        pasted notes
    """

    combined_text = ""

    # ---------------------------------------------------------
    # DOCX
    # ---------------------------------------------------------

    if sow_files:

        for file in sow_files:

            try:

                doc = docx.Document(file)

                combined_text += (
                    f"\n--- FILE: {file.name} ---\n"
                )

                for para in doc.paragraphs:

                    text = para.text.strip()

                    if text:
                        combined_text += (
                            text + "\n"
                        )

                # Extract table content
                for table_index, table in enumerate(
                    doc.tables,
                    start=1
                ):

                    combined_text += (
                        f"\n[TABLE {table_index}]\n"
                    )

                    for row in table.rows:

                        row_values = [
                            cell.text.strip()
                            for cell in row.cells
                        ]

                        combined_text += (
                            " | ".join(row_values)
                            + "\n"
                        )

            except Exception as exc:

                combined_text += (
                    f"\n[ERROR READING {file.name}: "
                    f"{exc}]\n"
                )

    # ---------------------------------------------------------
    # TXT
    # ---------------------------------------------------------

    if notes_files:

        for file in notes_files:

            try:

                file.seek(0)

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

            except Exception as exc:

                combined_text += (
                    f"\n[ERROR READING {file.name}: "
                    f"{exc}]\n"
                )

    # ---------------------------------------------------------
    # Loose notes
    # ---------------------------------------------------------

    if loose_notes and loose_notes.strip():

        combined_text += (
            "\n--- LOOSE NOTES / CLIENT EMAILS ---\n"
        )

        combined_text += (
            loose_notes.strip()
            + "\n"
        )

    return combined_text


# =============================================================================
# 8. PROFESSIONAL SMART SCOPE ENGINE PROMPT
# =============================================================================

SMART_SCOPE_PROMPT = """
You are "Smart Scope Engine", an expert AI Delivery Lead,
Business Analyst, Solution Analyst, and Project Handover Specialist.

Your job is to transform unstructured project intake material
into a professional, delivery-ready scope analysis.

The source material may contain:

- Proposals
- Statements of Work (SOW)
- Requirements
- Meeting notes
- Kickoff transcripts
- Client emails
- Functional requirements
- Technical requirements
- Tables
- Constraints
- Assumptions
- Deadlines
- SLAs
- Integrations
- User roles
- Business rules
- Open questions

IMPORTANT OBJECTIVE:

Do NOT simply summarize the documents.

Instead:

1. Extract concrete requirements.
2. Group requirements into meaningful functional modules.
3. Preserve the source of every important requirement.
4. Identify missing information that could block delivery.
5. Identify contradictions between documents.
6. Identify assumptions that have not been formally confirmed.
7. Identify technical, operational, security, integration,
   timeline, data, and dependency risks.
8. Convert sufficiently defined requirements into Jira-ready
   user stories.
9. Write measurable acceptance criteria.
10. Never invent project facts.

SOURCE TRACEABILITY:

For every extracted scope item, identify where it came from.

Use the filename and the closest available section,
heading, paragraph, table, or line reference.

If exact location cannot be determined, use:

"Source file: <filename>"

Do not fabricate page or paragraph numbers.

REQUIREMENT CLASSIFICATION:

Think carefully about:

- Functional requirements
- Non-functional requirements
- Business rules
- User roles
- Workflow
- Data requirements
- Integrations
- Security
- Authentication
- Authorization
- Reporting
- Notifications
- Performance
- Availability
- Scalability
- Audit/logging
- Compliance
- Migration
- Deployment
- Support
- SLA
- Dependencies
- Assumptions

GAP AND RISK ANALYSIS:

Look specifically for:

- Missing acceptance criteria
- Missing business rules
- Missing user roles
- Missing permissions
- Missing validation rules
- Missing error handling
- Missing notification behavior
- Missing integration details
- Missing API specifications
- Missing data definitions
- Missing migration requirements
- Missing security requirements
- Missing performance targets
- Missing SLA
- Missing availability requirements
- Missing backup/recovery requirements
- Missing audit requirements
- Missing reporting requirements
- Missing deployment information
- Missing support model
- Missing ownership
- Missing timelines
- Missing dependencies
- Conflicting requirements
- Ambiguous requirements
- Unsupported assumptions

SEVERITY:

HIGH:
Could significantly block delivery, cause major rework,
create security/compliance exposure, or affect project viability.

MEDIUM:
Important clarification or dependency that may cause rework
or schedule impact.

LOW:
Minor clarification, optimization, or documentation issue.

CONTRADICTIONS:

When two source documents disagree, explicitly identify:

- What Document A says
- What Document B says
- Why the conflict matters
- What decision/clarification is required

DO NOT decide which document is correct unless the source
material explicitly establishes priority.

USER STORIES:

Create stories only when there is enough information.

Use this conceptual format:

As a <user role>,
I want to <action>,
so that <business value>.

Acceptance criteria must be:

- Specific
- Testable
- Observable
- Business meaningful

Prefer Given / When / Then style.

Avoid vague acceptance criteria such as:

"The system should work correctly."

Instead provide measurable behavior.

IMPORTANT:

Do not invent:

- Technologies
- APIs
- Databases
- Cloud providers
- SLAs
- Deadlines
- User roles
- Business rules
- Security requirements
- Integrations

If information is absent, classify it as a gap or assumption.

OUTPUT:

Return ONLY valid JSON.

Use exactly this structure:

{
  "project_summary": {
    "project_name": "",
    "business_objective": "",
    "overall_scope_summary": "",
    "delivery_complexity": "LOW/MEDIUM/HIGH"
  },

  "extracted_scope": [
    {
      "module": "",
      "requirement_type": "FUNCTIONAL/NON_FUNCTIONAL/BUSINESS_RULE/DATA/INTEGRATION/SECURITY/OTHER",
      "source": "",
      "points": [
        ""
      ]
    }
  ],

  "gaps_and_risks": [
    {
      "severity": "HIGH/MEDIUM/LOW",
      "type": "",
      "description": "",
      "impact": "",
      "recommended_action": "",
      "source": ""
    }
  ],

  "assumptions_and_dependencies": [
    {
      "category": "ASSUMPTION/DEPENDENCY",
      "description": "",
      "owner_or_dependency": "",
      "status": "OPEN/CONFIRMED/UNKNOWN",
      "source": ""
    }
  ],

  "clarification_questions": [
    {
      "priority": "HIGH/MEDIUM/LOW",
      "question": "",
      "reason": ""
    }
  ],

  "jira_user_stories": [
    {
      "title": "",
      "user_role": "",
      "want_statement": "",
      "so_that_statement": "",
      "acceptance_criteria": [
        "Given ... When ... Then ..."
      ],
      "source": ""
    }
  ]
}

QUALITY RULES:

- Be precise.
- Be professional.
- Be conservative.
- Maintain source traceability.
- Do not hallucinate.
- Do not duplicate requirements unnecessarily.
- Combine closely related requirements into the same module.
- Separate unrelated requirements.
- Identify ambiguity instead of guessing.
- Prefer actionable delivery language.
- Return JSON only.
"""


# =============================================================================
# 9. GEMINI ANALYSIS
# =============================================================================

def analyze_with_gemini(raw_text):

    if not client:

        st.error(
            "GEMINI_API_KEY is missing in "
            "Streamlit Secrets!"
        )

        return None

    prompt = (
        SMART_SCOPE_PROMPT
        + "\n\n"
        + "==============================\n"
        + "PROJECT INTAKE MATERIALS\n"
        + "==============================\n\n"
        + raw_text
    )

    try:

        response = client.models.generate_content(

            model="gemini-3.6-flash",

            contents=prompt,

            config=types.GenerateContentConfig(

                response_mime_type="application/json",

                temperature=0.2,
            ),
        )

        response_text = response.text.strip()

        # -----------------------------------------------------
        # Remove accidental markdown fences
        # -----------------------------------------------------

        if response_text.startswith("```"):

            response_text = (
                response_text
                .replace("```json", "", 1)
                .replace("```", "")
                .strip()
            )

        data = json.loads(response_text)

        # -----------------------------------------------------
        # Ensure expected keys exist
        # -----------------------------------------------------

        data.setdefault(
            "project_summary",
            {
                "project_name": "Unknown",
                "business_objective": "",
                "overall_scope_summary": "",
                "delivery_complexity": "UNKNOWN",
            },
        )

        data.setdefault(
            "extracted_scope",
            []
        )

        data.setdefault(
            "gaps_and_risks",
            []
        )

        data.setdefault(
            "assumptions_and_dependencies",
            []
        )

        data.setdefault(
            "clarification_questions",
            []
        )

        data.setdefault(
            "jira_user_stories",
            []
        )

        return data

    except json.JSONDecodeError as exc:

        st.error(
            "❌ Gemini returned invalid JSON."
        )

        st.exception(exc)

        return None

    except Exception as exc:

        st.error(
            f"❌ Gemini API Error: {exc}"
        )

        return None


# =============================================================================
# 10. DEMO DATA
# =============================================================================

MOCK_ANALYSIS = {

    "project_summary": {

        "project_name":
            "Smart Scope Handover Platform",

        "business_objective":
            "Convert project intake material into "
            "delivery-ready scope and Jira stories.",

        "overall_scope_summary":
            "The platform analyzes project intake documents, "
            "identifies scope, gaps, risks and creates "
            "structured user stories.",

        "delivery_complexity":
            "MEDIUM",
    },

    "extracted_scope": [

        {

            "module":
                "AUTHENTICATION & SECURITY",

            "requirement_type":
                "SECURITY",

            "source":
                "Proposal Page 4, Section 2",

            "points": [

                "Multi-factor authentication "
                "via SMS or email.",

                "Role-based access control for "
                "Admin and Client roles.",
            ],
        },

        {

            "module":
                "HANDOVER INTELLIGENCE ENGINE",

            "requirement_type":
                "FUNCTIONAL",

            "source":
                "Kickoff Transcript Lines 12-45",

            "points": [

                "Multi-format document parsing.",

                "Automated gap auditing.",

                "Structured scope extraction.",

                "Jira-ready user story generation.",
            ],
        },
    ],

    "gaps_and_risks": [

        {

            "severity":
                "HIGH",

            "type":
                "Missing SLA",

            "description":
                "No processing-time SLA has been defined.",

            "impact":
                "Delivery and operational expectations "
                "cannot be validated.",

            "recommended_action":
                "Define measurable processing-time targets "
                "for supported document sizes.",

            "source":
                "Project intake materials",
        },

        {

            "severity":
                "MEDIUM",

            "type":
                "Cross-Document Conflict",

            "description":
                "Different upload size limits are mentioned "
                "in the intake material.",

            "impact":
                "Implementation and testing requirements "
                "may conflict.",

            "recommended_action":
                "Confirm the authoritative maximum "
                "upload size.",

            "source":
                "SOW / Kickoff transcript",
        },
    ],

    "assumptions_and_dependencies": [

        {

            "category":
                "ASSUMPTION",

            "description":
                "Users are expected to provide "
                "readable source documents.",

            "owner_or_dependency":
                "Project user",

            "status":
                "OPEN",

            "source":
                "Project intake materials",
        }
    ],

    "clarification_questions": [

        {

            "priority":
                "HIGH",

            "question":
                "What is the maximum supported document size?",

            "reason":
                "Different limits appear in the source material.",
        },

        {

            "priority":
                "MEDIUM",

            "question":
                "What processing time is considered acceptable?",

            "reason":
                "No SLA target has been defined.",
        },
    ],

    "jira_user_stories": [

        {

            "title":
                "Configurable Document Processing Engine",

            "user_role":
                "Delivery Lead",

            "want_statement":
                "ingest intake documents",

            "so_that_statement":
                "I can automatically extract "
                "delivery requirements",

            "acceptance_criteria": [

                "Given a user uploads a supported document, "
                "When the user selects Generate Smart Scope, "
                "Then the system extracts structured "
                "scope information.",

                "Given the document contains multiple modules, "
                "When analysis completes, "
                "Then requirements are grouped into "
                "logical modules.",
            ],

            "source":
                "Project intake materials",
        }
    ],
}


# =============================================================================
# 11. DOCX REPORT GENERATOR
# =============================================================================

def build_docx_report(data):

    doc = docx.Document()

    doc.add_heading(
        "Pitch to Project - Smart Scope Handover Analysis",
        0
    )

    # ---------------------------------------------------------
    # Project Summary
    # ---------------------------------------------------------

    doc.add_heading(
        "1. Project Summary",
        level=1
    )

    summary = data.get(
        "project_summary",
        {}
    )

    doc.add_paragraph(
        f"Project Name: "
        f"{summary.get('project_name', 'Unknown')}"
    )

    doc.add_paragraph(
        f"Business Objective: "
        f"{summary.get('business_objective', '')}"
    )

    doc.add_paragraph(
        f"Overall Scope: "
        f"{summary.get('overall_scope_summary', '')}"
    )

    doc.add_paragraph(
        f"Delivery Complexity: "
        f"{summary.get('delivery_complexity', 'UNKNOWN')}"
    )

    # ---------------------------------------------------------
    # Extracted Scope
    # ---------------------------------------------------------

    doc.add_heading(
        "2. Extracted Scope",
        level=1
    )

    for mod in data.get(
        "extracted_scope",
        []
    ):

        doc.add_heading(
            mod.get(
                "module",
                "General"
            ),
            level=2
        )

        doc.add_paragraph(
            "Requirement Type: "
            + mod.get(
                "requirement_type",
                "OTHER"
            )
        )

        doc.add_paragraph(
            "Source: "
            + mod.get(
                "source",
                "Uploaded Documents"
            )
        )

        for point in mod.get(
            "points",
            []
        ):

            doc.add_paragraph(
                point,
                style="List Bullet"
            )

    # ---------------------------------------------------------
    # Risks
    # ---------------------------------------------------------

    doc.add_heading(
        "3. Gaps & Risk Audit",
        level=1
    )

    for risk in data.get(
        "gaps_and_risks",
        []
    ):

        severity = risk.get(
            "severity",
            "INFO"
        )

        risk_type = risk.get(
            "type",
            "Risk"
        )

        doc.add_heading(
            f"[{severity}] {risk_type}",
            level=2
        )

        doc.add_paragraph(
            "Description: "
            + risk.get(
                "description",
                ""
            )
        )

        doc.add_paragraph(
            "Impact: "
            + risk.get(
                "impact",
                ""
            )
        )

        doc.add_paragraph(
            "Recommended Action: "
            + risk.get(
                "recommended_action",
                ""
            )
        )

        doc.add_paragraph(
            "Source: "
            + risk.get(
                "source",
                ""
            )
        )

    # ---------------------------------------------------------
    # Assumptions / Dependencies
    # ---------------------------------------------------------

    doc.add_heading(
        "4. Assumptions & Dependencies",
        level=1
    )

    for item in data.get(
        "assumptions_and_dependencies",
        []
    ):

        doc.add_paragraph(
            f"[{item.get('category', '')}] "
            f"{item.get('description', '')}"
        )

        doc.add_paragraph(
            "Owner / Dependency: "
            + item.get(
                "owner_or_dependency",
                ""
            )
        )

        doc.add_paragraph(
            "Status: "
            + item.get(
                "status",
                ""
            )
        )

        doc.add_paragraph(
            "Source: "
            + item.get(
                "source",
                ""
            )
        )

    # ---------------------------------------------------------
    # Questions
    # ---------------------------------------------------------

    doc.add_heading(
        "5. Clarification Questions",
        level=1
    )

    for question in data.get(
        "clarification_questions",
        []
    ):

        doc.add_paragraph(
            f"[{question.get('priority', 'MEDIUM')}] "
            f"{question.get('question', '')}"
        )

        doc.add_paragraph(
            "Reason: "
            + question.get(
                "reason",
                ""
            )
        )

    # ---------------------------------------------------------
    # Jira Stories
    # ---------------------------------------------------------

    doc.add_heading(
        "6. Jira User Stories",
        level=1
    )

    for story in data.get(
        "jira_user_stories",
        []
    ):

        doc.add_heading(
            story.get(
                "title",
                "User Story"
            ),
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
            "Acceptance Criteria:"
        )

        for ac in story.get(
            "acceptance_criteria",
            []
        ):

            doc.add_paragraph(
                ac,
                style="List Bullet"
            )

        doc.add_paragraph(
            "Source: "
            + story.get(
                "source",
                ""
            )
        )

    # ---------------------------------------------------------
    # Save in memory
    # ---------------------------------------------------------

    target_stream = io.BytesIO()

    doc.save(target_stream)

    target_stream.seek(0)

    return target_stream.getvalue()


# =============================================================================
# 12. TOP SMART BANNER
# =============================================================================
#
# IMPORTANT:
# We intentionally use ONLY st.markdown() here.
#
# The previous problem happened because the banner HTML was being
# inserted/rendered incorrectly and appeared as literal HTML text.
#
# This version uses a single self-contained HTML block.
# =============================================================================

st.markdown(
    """
    <div class="smart-banner">
        <div class="smart-banner-inner">

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
    unsafe_allow_html=True,
)


# =============================================================================
# 13. MAIN TITLE
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
                color: #ffffff;
                font-size: 2.8rem;
                font-weight: 900;
                margin: 0;
                line-height: 1.2;
                text-shadow:
                    0 0 15px rgba(56,189,248,0.6);
            ">
                Pitch to Project
            </div>

            <div style="
                color: #38bdf8;
                font-size: 1.05rem;
                font-weight: 700;
                margin-top: 6px;
                line-height: 1.3;
            ">
                🚀 AI-Powered Scope Intelligence & Handover Engine
            </div>

        </div>
        """,
        height=120,
    )


with col_toggle:

    demo_mode = st.toggle(
        "Demo Mode (Safe Pitch)",
        value=True
    )


# =============================================================================
# 14. TWO-COLUMN MAIN APPLICATION
# =============================================================================

left_col, right_col = st.columns(
    [1, 1],
    gap="medium"
)


# =============================================================================
# LEFT SIDE - INTAKE
# =============================================================================

with left_col:

    st.header(
        "1. Intake Documents & Media"
    )

    sow_files = st.file_uploader(
        "Proposals / SOWs (.docx)",
        type=["docx"],
        accept_multiple_files=True,
    )

    notes_files = st.file_uploader(
        "Transcripts / Notes (.txt)",
        type=["txt"],
        accept_multiple_files=True,
    )

    media_files = st.file_uploader(
        "Diagrams & Media (.png, .jpg, .mp4, .mp3)",
        type=[
            "png",
            "jpg",
            "mp4",
            "mp3"
        ],
        accept_multiple_files=True,
    )

    loose_notes = st.text_area(
        "Or Paste Loose Client Emails / Notes:",
        height=120,
        placeholder=(
            "Paste kickoff notes or "
            "client requirements here..."
        ),
    )

    generate_btn = st.button(
        "⚡ GENERATE SMART SCOPE"
    )


# =============================================================================
# RIGHT SIDE - ANALYSIS
# =============================================================================

with right_col:

    st.header(
        "2. AI Scope & Handover Analysis"
    )

    # ---------------------------------------------------------
    # GENERATE
    # ---------------------------------------------------------

    if generate_btn:

        progress_card = st.empty()

        # =====================================================
        # DEMO MODE
        # =====================================================

        if demo_mode:

            with progress_card.container(
                border=True
            ):

                st.markdown(
                    "### 🧠 Running Scope Analysis"
                )

                bar_ph = st.empty()

                for i in range(101):

                    time.sleep(0.01)

                    bar_ph.markdown(
                        render_stylish_progress(
                            i,
                            "⚙️ Processing intake materials & generating user stories..."
                        ),
                        unsafe_allow_html=True,
                    )

                st.success(
                    "✅ Demo Analysis Loaded Successfully!"
                )

                time.sleep(0.4)

            progress_card.empty()

            st.session_state[
                "analysis_data"
            ] = MOCK_ANALYSIS

            st.toast(
                "⚡ Demo Analysis Loaded!",
                icon="✅"
            )

        # =====================================================
        # LIVE GEMINI MODE
        # =====================================================

        else:

            raw_text = extract_text_from_uploads(
                sow_files,
                notes_files,
                loose_notes
            )

            if not raw_text.strip():

                st.warning(
                    "Please upload at least one "
                    "document or paste text before analyzing."
                )

            else:

                with progress_card.container(
                    border=True
                ):

                    st.markdown(
                        "### 🧠 Live Gemini Scope Extraction"
                    )

                    bar_ph = st.empty()

                    # -----------------------------------------
                    # STEP 1
                    # -----------------------------------------

                    bar_ph.markdown(
                        render_stylish_progress(
                            20,
                            "📄 Step 1/3: Extracting and structuring intake material..."
                        ),
                        unsafe_allow_html=True,
                    )

                    time.sleep(0.3)

                    # -----------------------------------------
                    # STEP 2
                    # -----------------------------------------

                    bar_ph.markdown(
                        render_stylish_progress(
                            50,
                            "⚡ Step 2/3: Sending structured project context to Gemini..."
                        ),
                        unsafe_allow_html=True,
                    )

                    time.sleep(0.3)

                    # -----------------------------------------
                    # STEP 3
                    # -----------------------------------------

                    bar_ph.markdown(
                        render_stylish_progress(
                            80,
                            "🔍 Step 3/3: Auditing scope, gaps, risks & Jira stories..."
                        ),
                        unsafe_allow_html=True,
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
                            unsafe_allow_html=True,
                        )

                        st.success(
                            "✅ Scope Successfully Extracted!"
                        )

                        time.sleep(0.5)

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


    # =============================================================================
    # 15. DEFAULT DATA
    # =============================================================================

    if (
        "analysis_data"
        not in st.session_state
    ):

        st.session_state[
            "analysis_data"
        ] = MOCK_ANALYSIS


    data = st.session_state[
        "analysis_data"
    ]


    # =============================================================================
    # 16. PROJECT SUMMARY
    # =============================================================================

    summary = data.get(
        "project_summary",
        {}
    )

    with st.container(
        border=True
    ):

        st.markdown(
            "### 📊 Project Intelligence Summary"
        )

        project_name = summary.get(
            "project_name",
            "Unknown"
        )

        complexity = summary.get(
            "delivery_complexity",
            "UNKNOWN"
        )

        st.markdown(
            f"**Project:** `{project_name}`"
        )

        st.markdown(
            f"**Delivery Complexity:** `{complexity}`"
        )

        objective = summary.get(
            "business_objective",
            ""
        )

        if objective:

            st.markdown(
                f"**Business Objective:** {objective}"
            )

        scope_summary = summary.get(
            "overall_scope_summary",
            ""
        )

        if scope_summary:

            st.markdown(
                f"**Scope Summary:** {scope_summary}"
            )


    # =============================================================================
    # 17. TABS
    # =============================================================================

    (
        tab_scope,
        tab_risks,
        tab_questions,
        tab_jira
    ) = st.tabs(
        [
            "📌 Extracted Scope",
            "🚨 Missing Items & Risks",
            "❓ Clarifications",
            "🚀 Jira User Stories",
        ]
    )


    # =============================================================================
    # TAB 1 - SCOPE
    # =============================================================================

    with tab_scope:

        scope_items = data.get(
            "extracted_scope",
            []
        )

        if not scope_items:

            st.info(
                "No scope items were extracted."
            )

        for item in scope_items:

            with st.container(
                border=True
            ):

                st.markdown(
                    "### 📌 MODULE: "
                    + item.get(
                        "module",
                        "General Scope"
                    )
                )

                requirement_type = item.get(
                    "requirement_type",
                    "OTHER"
                )

                st.caption(
                    "Requirement Type: "
                    + requirement_type
                )

                st.caption(
                    "Source: "
                    + item.get(
                        "source",
                        "Uploaded Files"
                    )
                )

                for point in item.get(
                    "points",
                    []
                ):

                    st.markdown(
                        f"• {point}"
                    )


    # =============================================================================
    # TAB 2 - RISKS
    # =============================================================================

    with tab_risks:

        risks = data.get(
            "gaps_and_risks",
            []
        )

        if not risks:

            st.success(
                "✅ No significant gaps or risks identified."
            )

        for risk in risks:

            with st.container(
                border=True
            ):

                severity = risk.get(
                    "severity",
                    "INFO"
                ).upper()

                if severity == "HIGH":
                    badge = "🔴"

                elif severity == "MEDIUM":
                    badge = "🟡"

                else:
                    badge = "🔵"

                st.markdown(
                    f"### {badge} "
                    f"[{severity}] "
                    f"{risk.get('type', 'Risk')}"
                )

                st.write(
                    risk.get(
                        "description",
                        ""
                    )
                )

                impact = risk.get(
                    "impact",
                    ""
                )

                if impact:

                    st.markdown(
                        f"**Impact:** {impact}"
                    )

                recommendation = risk.get(
                    "recommended_action",
                    ""
                )

                if recommendation:

                    st.markdown(
                        f"**Recommended Action:** "
                        f"{recommendation}"
                    )

                source = risk.get(
                    "source",
                    ""
                )

                if source:

                    st.caption(
                        "Source: " + source
                    )


    # =============================================================================
    # TAB 3 - QUESTIONS
    # =============================================================================

    with tab_questions:

        questions = data.get(
            "clarification_questions",
            []
        )

        if not questions:

            st.success(
                "✅ No clarification questions identified."
            )

        for question in questions:

            with st.container(
                border=True
            ):

                priority = question.get(
                    "priority",
                    "MEDIUM"
                ).upper()

                icon = (
                    "🔴"
                    if priority == "HIGH"
                    else "🟡"
                    if priority == "MEDIUM"
                    else "🔵"
                )

                st.markdown(
                    f"### {icon} "
                    f"[{priority}]"
                )

                st.markdown(
                    f"**Question:** "
                    f"{question.get('question', '')}"
                )

                st.markdown(
                    f"**Why it matters:** "
                    f"{question.get('reason', '')}"
                )


    # =============================================================================
    # TAB 4 - JIRA STORIES
    # =============================================================================

    with tab_jira:

        stories = data.get(
            "jira_user_stories",
            []
        )

        if not stories:

            st.info(
                "No sufficiently defined Jira stories "
                "were identified."
            )

        for story in stories:

            with st.container(
                border=True
            ):

                st.markdown(
                    "### 🚀 "
                    + story.get(
                        "title",
                        "User Story"
                    )
                )

                st.markdown(
                    f"**As a** "
                    f"`{story.get('user_role', 'User')}`, "
                    f"**I want to** "
                    f"{story.get('want_statement', '')} "
                    f"**so that** "
                    f"{story.get('so_that_statement', '')}."
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

                source = story.get(
                    "source",
                    ""
                )

                if source:

                    st.caption(
                        "Source: " + source
                    )


    # =============================================================================
    # 18. ASSUMPTIONS & DEPENDENCIES
    # =============================================================================

    assumptions = data.get(
        "assumptions_and_dependencies",
        []
    )

    if assumptions:

        st.divider()

        st.subheader(
            "🔗 Assumptions & Dependencies"
        )

        for item in assumptions:

            with st.container(
                border=True
            ):

                st.markdown(
                    f"**[{item.get('category', 'ITEM')}]** "
                    f"{item.get('description', '')}"
                )

                st.caption(
                    f"Status: "
                    f"{item.get('status', 'UNKNOWN')} "
                    f"| Owner/Dependency: "
                    f"{item.get('owner_or_dependency', 'N/A')}"
                )


    # =============================================================================
    # 19. EXPORT REPORT
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

        use_container_width=True,
    )
