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
# 2. CUSTOM CSS
# =============================================================================

css_code = """
<style>

/* ========================================================================
   GLOBAL BACKGROUND
   ======================================================================== */

.stApp {
    background: linear-gradient(
        125deg,
        #0f172a 0%,
        #1e1b4b 35%,
        #311042 70%,
        #0284c7 100%
    ) !important;

    background-attachment: fixed;
}


/* ========================================================================
   LOGIN FORM
   ======================================================================== */

div[data-testid="stForm"] {
    background: rgba(15, 23, 42, 0.95) !important;
    border: 2.5px solid #a855f7 !important;
    border-radius: 18px !important;
    padding: 36px !important;
    box-shadow: 0 0 40px rgba(168, 85, 247, 0.5) !important;
}


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


/* ========================================================================
   INPUTS
   ======================================================================== */

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


/* ========================================================================
   AUTOFILL
   ======================================================================== */

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


/* ========================================================================
   PLACEHOLDER
   ======================================================================== */

div[data-testid="stTextInput"] input::placeholder,
input::placeholder {

    color: #94a3b8 !important;

    -webkit-text-fill-color: #94a3b8 !important;

    font-weight: 700 !important;

    font-size: 1.25rem !important;

    opacity: 1 !important;

    text-align: left !important;
}


/* ========================================================================
   PASSWORD ICON
   ======================================================================== */

div[data-testid="stTextInput"] button svg,
div[data-testid="stForm"] svg {

    fill: #38bdf8 !important;

    stroke: #38bdf8 !important;

    width: 26px !important;

    height: 26px !important;
}


/* ========================================================================
   LOGIN BUTTON
   ======================================================================== */

div[data-testid="stForm"] button[type="submit"],
div[data-testid="stForm"] button[data-testid="stFormSubmitButton"],
div[data-testid="stForm"] button {

    background: linear-gradient(
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


/* ========================================================================
   SIDEBAR
   ======================================================================== */

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

    background: linear-gradient(
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


/* ========================================================================
   MAIN HEADINGS
   ======================================================================== */

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


/* ========================================================================
   FILE UPLOADER
   ======================================================================== */

div[data-testid="stFileUploader"] {

    background: rgba(15, 23, 42, 0.95) !important;

    border: 2px solid #a855f7 !important;

    border-radius: 14px !important;

    padding: 12px !important;
}


div[data-testid="stFileUploader"] section,
div[data-testid="stFileUploaderDropzone"],
div[data-testid="stFileUploader"]
[data-testid="stFileUploaderDropzone"] {

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


/* ========================================================================
   TOAST
   ======================================================================== */

div[data-testid="stToast"],
div[data-testid="stToast"] > div {

    background-color: #1e1b4b !important;

    background: #1e1b4b !important;

    border: 2px solid #38bdf8 !important;

    border-radius: 12px !important;

    box-shadow:
        0 0 20px rgba(56, 189, 248, 0.5) !important;
}


div[data-testid="stToast"] * {

    color: #ffffff !important;

    font-weight: 800 !important;
}


/* ========================================================================
   DOWNLOAD BUTTON
   ======================================================================== */

div[data-testid="stDownloadButton"] > button {

    background: linear-gradient(
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


/* ========================================================================
   TEXT AREA
   ======================================================================== */

div[data-testid="stTextArea"] textarea {

    background: rgba(15, 23, 42, 0.85) !important;

    border: 2px solid #a855f7 !important;

    border-radius: 14px !important;

    color: #ffffff !important;
}


/* ========================================================================
   GENERAL BUTTONS
   ======================================================================== */

div.stButton > button {

    background: linear-gradient(
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

    background: linear-gradient(
        135deg,
        #8b5cf6 0%,
        #ec4899 100%
    ) !important;

    color: #ffffff !important;
}


/* ========================================================================
   RESULT CARDS
   ======================================================================== */

div[data-testid="stVerticalBlockBorderWrapper"] > div {

    background: rgba(15, 23, 42, 0.8) !important;

    backdrop-filter: blur(10px) !important;

    border-left: 6px solid #06b6d4 !important;

    border-radius: 14px !important;

    padding: 20px !important;
}


/* ========================================================================
   CODE
   ======================================================================== */

code {

    background-color:
        rgba(30, 27, 75, 0.95) !important;

    color: #38bdf8 !important;

    border: 1px solid #a855f7 !important;

    border-radius: 6px !important;

    padding: 3px 8px !important;
}

</style>
"""

st.markdown(
    css_code,
    unsafe_allow_html=True
)


# =============================================================================
# 3. AUTHENTICATION
# =============================================================================

def check_password():

    if st.session_state.get(
        "authenticated",
        False
    ):
        return True

    st.markdown(
        "<br><br>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(
        [1, 2.4, 1]
    )

    with col2:

        with st.form("login_form"):

            components.html(
                """
                <div style="
                    background: linear-gradient(
                        135deg,
                        #ec4899 0%,
                        #8b5cf6 50%,
                        #06b6d4 100%
                    );
                    border-radius: 14px;
                    padding: 24px 10px;
                    box-shadow:
                        0 0 25px
                        rgba(236, 72, 153, 0.6);
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
                            0 3px 12px
                            rgba(0, 0, 0, 0.8);
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
                            0 2px 8px
                            rgba(0, 0, 0, 0.8);
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

                    st.session_state[
                        "authenticated"
                    ] = True

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
# 4. SIDEBAR LOGOUT
# =============================================================================

with st.sidebar:

    st.markdown(
        "### 👤 User Session"
    )

    st.write(
        "Logged in as **Admin**"
    )

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state[
            "authenticated"
        ] = False

        st.rerun()


# =============================================================================
# 5. GEMINI CLIENT
# =============================================================================

GEMINI_MODEL = "gemini-3.6-flash"


@st.cache_resource
def get_gemini_client():

    try:

        api_key = st.secrets[
            "GEMINI_API_KEY"
        ]

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
                    0 0 10px
                    rgba(245, 158, 11, 0.5);
            ">
                {percentage}%
            </span>

        </div>

        <div style="
            background: rgba(15, 23, 42, 0.9);
            border: 2px solid #10b981;
            border-radius: 12px;
            padding: 3px;
            box-shadow:
                0 0 15px
                rgba(16, 185, 129, 0.3);
            position: relative;
            overflow: hidden;
        ">

            <div style="
                width: {percentage}%;
                height: 18px;
                background: linear-gradient(
                    90deg,
                    #10b981 0%,
                    #3b82f6 50%,
                    #f59e0b 100%
                );
                border-radius: 8px;
                box-shadow:
                    0 0 20px
                    rgba(245, 158, 11, 0.8);
                transition:
                    width 0.2s ease-in-out;
            ">
            </div>

        </div>

    </div>
    """


# =============================================================================
# 7. DOCX EXTRACTION
# =============================================================================

def extract_docx_content(file):

    content = []

    try:

        document = docx.Document(
            file
        )

        # -------------------------------------------------------------
        # Paragraphs
        # -------------------------------------------------------------

        paragraph_number = 0

        for paragraph in document.paragraphs:

            text = paragraph.text.strip()

            if text:

                paragraph_number += 1

                content.append(
                    f"[Paragraph {paragraph_number}] "
                    f"{text}"
                )

        # -------------------------------------------------------------
        # Tables
        # -------------------------------------------------------------

        for table_index, table in enumerate(
            document.tables,
            start=1
        ):

            content.append(
                f"[TABLE {table_index}]"
            )

            for row_index, row in enumerate(
                table.rows,
                start=1
            ):

                cells = []

                for cell in row.cells:

                    cells.append(
                        cell.text.strip()
                    )

                row_text = " | ".join(
                    cells
                )

                if row_text.strip():

                    content.append(
                        f"[Table {table_index} "
                        f"Row {row_index}] "
                        f"{row_text}"
                    )

    except Exception as exc:

        content.append(
            "[DOCX EXTRACTION ERROR] "
            f"{str(exc)}"
        )

    return "\n".join(
        content
    )


# =============================================================================
# 8. INTAKE EXTRACTION
# =============================================================================

def extract_text_from_uploads(
    sow_files,
    notes_files,
    loose_notes,
    media_files=None
):

    combined_sections = []

    # -----------------------------------------------------------------
    # DOCX
    # -----------------------------------------------------------------

    if sow_files:

        for file in sow_files:

            content = extract_docx_content(
                file
            )

            combined_sections.append(
                "\n".join(
                    [
                        f"--- SOURCE FILE: {file.name} ---",
                        "SOURCE TYPE: DOCX / SOW / PROPOSAL",
                        content,
                        "--- END SOURCE FILE ---"
                    ]
                )
            )

    # -----------------------------------------------------------------
    # TXT
    # -----------------------------------------------------------------

    if notes_files:

        for file in notes_files:

            try:

                raw_bytes = file.read()

                text = raw_bytes.decode(
                    "utf-8",
                    errors="replace"
                )

                combined_sections.append(
                    "\n".join(
                        [
                            f"--- SOURCE FILE: {file.name} ---",
                            "SOURCE TYPE: TXT / TRANSCRIPT / NOTES",
                            text,
                            "--- END SOURCE FILE ---"
                        ]
                    )
                )

            except Exception as exc:

                combined_sections.append(
                    "\n".join(
                        [
                            f"--- SOURCE FILE: {file.name} ---",
                            "SOURCE TYPE: TXT",
                            f"EXTRACTION ERROR: {str(exc)}",
                            "--- END SOURCE FILE ---"
                        ]
                    )
                )

    # -----------------------------------------------------------------
    # Pasted notes
    # -----------------------------------------------------------------

    if loose_notes and loose_notes.strip():

        combined_sections.append(
            "\n".join(
                [
                    "--- SOURCE: USER PASTED NOTES / CLIENT EMAILS ---",
                    "SOURCE TYPE: USER PROVIDED TEXT",
                    loose_notes.strip(),
                    "--- END PASTED NOTES ---"
                ]
            )
        )

    # -----------------------------------------------------------------
    # Media inventory
    # -----------------------------------------------------------------

    if media_files:

        media_lines = [
            "--- MEDIA / VISUAL EVIDENCE INVENTORY ---"
        ]

        for media in media_files:

            media_type = getattr(
                media,
                "type",
                "unknown"
            )

            media_size = getattr(
                media,
                "size",
                0
            )

            media_lines.append(
                f"File: {media.name} | "
                f"Type: {media_type} | "
                f"Size: {media_size} bytes"
            )

        media_lines.append(
            "--- END MEDIA INVENTORY ---"
        )

        combined_sections.append(
            "\n".join(
                media_lines
            )
        )

    return "\n\n".join(
        combined_sections
    )


# =============================================================================
# 9. GEMINI RESPONSE SCHEMA
# =============================================================================

SMART_SCOPE_SCHEMA = {

    "type": "object",

    "properties": {

        "executive_summary": {
            "type": "string"
        },

        "project_objectives": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },

        "extracted_scope": {

            "type": "array",

            "items": {

                "type": "object",

                "properties": {

                    "module": {
                        "type": "string"
                    },

                    "requirement_type": {
                        "type": "string"
                    },

                    "source": {
                        "type": "string"
                    },

                    "confidence": {
                        "type": "string"
                    },

                    "points": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }

                },

                "required": [
                    "module",
                    "requirement_type",
                    "source",
                    "confidence",
                    "points"
                ]
            }
        },

        "functional_requirements": {

            "type": "array",

            "items": {
                "type": "string"
            }
        },

        "non_functional_requirements": {

            "type": "array",

            "items": {
                "type": "string"
            }
        },

        "integrations_and_dependencies": {

            "type": "array",

            "items": {
                "type": "string"
            }
        },

        "assumptions": {

            "type": "array",

            "items": {
                "type": "string"
            }
        },

        "gaps_and_risks": {

            "type": "array",

            "items": {

                "type": "object",

                "properties": {

                    "severity": {
                        "type": "string"
                    },

                    "type": {
                        "type": "string"
                    },

                    "description": {
                        "type": "string"
                    },

                    "source": {
                        "type": "string"
                    },

                    "recommended_action": {
                        "type": "string"
                    }

                },

                "required": [
                    "severity",
                    "type",
                    "description",
                    "source",
                    "recommended_action"
                ]
            }
        },

        "open_questions": {

            "type": "array",

            "items": {
                "type": "string"
            }
        },

        "jira_user_stories": {

            "type": "array",

            "items": {

                "type": "object",

                "properties": {

                    "title": {
                        "type": "string"
                    },

                    "priority": {
                        "type": "string"
                    },

                    "user_role": {
                        "type": "string"
                    },

                    "want_statement": {
                        "type": "string"
                    },

                    "so_that_statement": {
                        "type": "string"
                    },

                    "source": {
                        "type": "string"
                    },

                    "acceptance_criteria": {

                        "type": "array",

                        "items": {
                            "type": "string"
                        }
                    }

                },

                "required": [
                    "title",
                    "priority",
                    "user_role",
                    "want_statement",
                    "so_that_statement",
                    "source",
                    "acceptance_criteria"
                ]
            }
        }
    },

    "required": [
        "executive_summary",
        "project_objectives",
        "extracted_scope",
        "functional_requirements",
        "non_functional_requirements",
        "integrations_and_dependencies",
        "assumptions",
        "gaps_and_risks",
        "open_questions",
        "jira_user_stories"
    ]
}


# =============================================================================
# 10. PROFESSIONAL SMART SCOPE PROMPT
# =============================================================================

SMART_SCOPE_SYSTEM_PROMPT = """

You are the Smart Scope Intelligence Engine for an enterprise IT
delivery organization.

You operate as:

- Senior Business Analyst
- IT Delivery Lead
- Systems Analyst
- Solution Consultant
- Product Owner
- QA Lead
- Technical Project Manager

Your job is to transform project intake material into a reliable,
source-traceable implementation scope.

The supplied material may include:

- SOWs
- Proposals
- Client emails
- Meeting notes
- Kickoff transcripts
- Functional requirements
- Technical requirements
- Tables
- Media inventories


===============================================================================
1. EVIDENCE-FIRST PRINCIPLE
===============================================================================

Use ONLY information supported by the supplied intake.

Never invent:

- features
- business rules
- APIs
- integrations
- technologies
- databases
- user roles
- SLAs
- deadlines
- budgets
- security controls
- compliance requirements
- performance targets

If information is missing, classify it as:

- GAP
- OPEN QUESTION
- ASSUMPTION

Never silently convert missing information into a requirement.


===============================================================================
2. REQUIREMENT CLASSIFICATION
===============================================================================

Identify and classify requirements as appropriate.

FUNCTIONAL examples:

- Login
- Upload
- Search
- Approval
- Workflow
- Reporting
- Notifications
- Import/export

NON-FUNCTIONAL examples:

- Performance
- Availability
- Scalability
- Security
- Accessibility
- Reliability
- Auditability
- Backup/recovery

TECHNICAL examples:

- APIs
- Integrations
- Database
- Authentication
- File formats
- Hosting
- Infrastructure

BUSINESS examples:

- Business objectives
- Business rules
- Policies
- Operational processes


===============================================================================
3. SOURCE TRACEABILITY
===============================================================================

Every extracted scope module must identify the source.

Use the actual supplied filename and available paragraph/table
references.

Examples:

Proposal.docx - Paragraph 12

SOW.docx - Table 3 Row 4

Kickoff.txt - Transcript section

Client Email - Pasted Notes

Never invent page or line numbers.


===============================================================================
4. CONFIDENCE
===============================================================================

HIGH:

Explicitly stated and unambiguous.

MEDIUM:

Strongly implied by the supplied material.

LOW:

Ambiguous and requiring confirmation.


===============================================================================
5. CROSS-DOCUMENT CONFLICT DETECTION
===============================================================================

Compare all sources.

Look for conflicts involving:

- file sizes
- user roles
- functionality
- workflows
- deadlines
- environments
- integrations
- platforms
- response times
- SLAs
- responsibilities
- security
- data ownership
- scope boundaries

If conflicting information exists:

Explain:

1. Source A
2. Source B
3. Why the conflict matters
4. Recommended resolution


===============================================================================
6. GAP AUDIT
===============================================================================

Audit for missing information in:

- Business objective
- Target users
- User roles
- Functional requirements
- Non-functional requirements
- Authentication
- Authorization
- Data ownership
- Data retention
- Integrations
- APIs
- Error handling
- Notifications
- Reporting
- Audit logging
- Security
- Privacy
- Compliance
- Performance
- Availability
- Scalability
- Backup
- Disaster recovery
- Deployment
- Environments
- Monitoring
- Support
- SLA
- Acceptance criteria
- UAT
- Training
- Migration
- Rollback
- Dependencies
- Constraints


===============================================================================
7. RISK SEVERITY
===============================================================================

HIGH:

Potentially affects architecture, cost, security, timeline,
contractual scope, or production readiness.

MEDIUM:

May cause rework, delays, ambiguity, or testing issues.

LOW:

Minor clarification or manageable uncertainty.


===============================================================================
8. JIRA USER STORIES
===============================================================================

Generate Jira stories ONLY from confirmed or strongly supported
requirements.

Use:

As a [user role],
I want to [specific action],
so that [business value].

Acceptance criteria must be testable.

Prefer:

Given ...
When ...
Then ...

Never use vague criteria such as:

"The feature should work correctly."


===============================================================================
9. PRIORITY
===============================================================================

HIGH:

Core business capability, blocker, critical security requirement,
or contractual requirement.

MEDIUM:

Important capability but not an immediate blocker.

LOW:

Enhancement or convenience functionality.


===============================================================================
10. ANTI-HALLUCINATION RULE
===============================================================================

Example:

If the source says:

"System should support reports."

Do NOT assume:

- PDF
- Excel
- CSV
- dashboards
- scheduled reports
- email delivery

unless explicitly stated.

Instead identify these as missing details.


===============================================================================
11. FINAL QUALITY CHECK
===============================================================================

Before returning JSON, verify:

1. All meaningful requirements were captured.
2. Source traceability is preserved.
3. Confirmed requirements are separated from assumptions.
4. Contradictions are identified.
5. Missing SLAs are identified.
6. Security gaps are identified.
7. Integration dependencies are identified.
8. Missing acceptance criteria are identified.
9. No unsupported features were invented.
10. Jira stories are testable.
11. Risks contain recommended actions.
12. Open questions are useful for delivery teams.

Return ONLY the JSON object matching the response schema.

No markdown.
No explanation outside JSON.

"""


# =============================================================================
# 11. GEMINI ANALYSIS
# =============================================================================

def analyze_with_gemini(raw_text):

    if not client:

        st.error(
            "GEMINI_API_KEY is missing in Streamlit Secrets!"
        )

        return None

    if not raw_text.strip():

        st.warning(
            "No intake content was available for analysis."
        )

        return None

    prompt = f"""
{SMART_SCOPE_SYSTEM_PROMPT}

===============================================================================
PROJECT INTAKE MATERIAL
===============================================================================

{raw_text}

===============================================================================
FINAL INSTRUCTION
===============================================================================

Analyze the complete project intake.

Cross-reference all available sources.

Preserve source traceability.

Identify confirmed requirements, gaps, assumptions, conflicts,
dependencies, risks and open questions.

Generate only implementation-ready Jira stories supported by the
source material.

Return ONLY valid JSON.
"""

    try:

        response = client.models.generate_content(

            model=GEMINI_MODEL,

            contents=prompt,

            config=types.GenerateContentConfig(

                response_mime_type="application/json",

                response_schema=SMART_SCOPE_SCHEMA,
            ),
        )

        if not response:

            st.error(
                "Gemini returned an empty response."
            )

            return None

        response_text = getattr(
            response,
            "text",
            None
        )

        if not response_text:

            st.error(
                "Gemini response did not contain usable text."
            )

            return None

        result = json.loads(
            response_text
        )

        return normalize_analysis_result(
            result
        )

    except json.JSONDecodeError as exc:

        st.error(
            "Gemini returned invalid JSON."
        )

        st.code(
            response_text
            if "response_text" in locals()
            else "No response text"
        )

        st.caption(
            f"JSON parsing error: {str(exc)}"
        )

        return None

    except Exception as exc:

        st.error(
            f"Gemini API Error: {str(exc)}"
        )

        return None


# =============================================================================
# 12. NORMALIZE RESULT
# =============================================================================

def normalize_analysis_result(data):

    if not isinstance(
        data,
        dict
    ):

        return None

    list_fields = [

        "project_objectives",

        "extracted_scope",

        "functional_requirements",

        "non_functional_requirements",

        "integrations_and_dependencies",

        "assumptions",

        "gaps_and_risks",

        "open_questions",

        "jira_user_stories",
    ]

    for field in list_fields:

        if field not in data:

            data[field] = []

        elif not isinstance(
            data[field],
            list
        ):

            data[field] = []

    if not isinstance(
        data.get("executive_summary"),
        str
    ):

        data[
            "executive_summary"
        ] = "Smart Scope analysis completed."

    return data


# =============================================================================
# 13. DEMO ANALYSIS
# =============================================================================

MOCK_ANALYSIS = {

    "executive_summary":
        "The intake describes an AI-powered scope intelligence "
        "platform designed to convert project handover material "
        "into structured requirements, risks and Jira-ready "
        "user stories.",

    "project_objectives": [

        "Convert project intake material into structured scope.",

        "Identify missing requirements and delivery risks.",

        "Generate implementation-ready Jira user stories."
    ],

    "extracted_scope": [

        {

            "module":
                "AUTHENTICATION & SECURITY",

            "requirement_type":
                "FUNCTIONAL",

            "source":
                "Proposal.docx - Page 4 / Section 2",

            "confidence":
                "HIGH",

            "points": [

                "Multi-factor authentication is required.",

                "Role-based access control is required for "
                "Admin and Client roles."
            ]
        },

        {

            "module":
                "HANDOVER INTELLIGENCE ENGINE",

            "requirement_type":
                "FUNCTIONAL",

            "source":
                "Kickoff Transcript - Lines 12-45",

            "confidence":
                "HIGH",

            "points": [

                "The platform should ingest project intake material.",

                "The platform should identify scope gaps and risks.",

                "The platform should generate structured user stories."
            ]
        }
    ],

    "functional_requirements": [

        "Users can provide project intake material.",

        "The system extracts project requirements.",

        "The system identifies scope gaps and risks.",

        "The system generates structured user stories."
    ],

    "non_functional_requirements": [

        "Processing performance expectations should be defined.",

        "Security requirements should be documented."
    ],

    "integrations_and_dependencies": [

        "Gemini API is required for AI-based analysis."
    ],

    "assumptions": [

        "Uploaded project material is assumed to be authoritative "
        "unless conflicting sources are identified."
    ],

    "gaps_and_risks": [

        {

            "severity":
                "HIGH",

            "type":
                "Missing SLA",

            "description":
                "No operational SLA is defined for document "
                "processing or AI response time.",

            "source":
                "Provided intake material",

            "recommended_action":
                "Define expected response time, maximum processing "
                "time and acceptable timeout behavior."
        },

        {

            "severity":
                "MEDIUM",

            "type":
                "Cross-Document Conflict",

            "description":
                "Different intake sources may specify different "
                "upload limits.",

            "source":
                "Multiple project sources",

            "recommended_action":
                "Confirm the authoritative maximum upload size."
        }
    ],

    "open_questions": [

        "What are the complete user roles?",

        "What are the supported file-size limits?",

        "What response-time SLA is required?",

        "What integrations are required?",

        "What security and retention policies apply?"
    ],

    "jira_user_stories": [

        {

            "title":
                "Structured Intake Analysis",

            "priority":
                "HIGH",

            "user_role":
                "Delivery Lead",

            "want_statement":
                "upload project intake material and generate "
                "structured scope",

            "so_that_statement":
                "I can identify project requirements without "
                "manually reviewing every document",

            "source":
                "Kickoff Transcript - Lines 12-45",

            "acceptance_criteria": [

                "Given a supported project document is uploaded",

                "When the user selects Generate Smart Scope",

                "Then the system extracts the available "
                "project requirements",

                "And the system identifies gaps and risks",

                "And the system generates structured user stories"
            ]
        }
    ]
}


# =============================================================================
# 14. DOCX REPORT
# =============================================================================

def build_docx_report(data):

    doc = docx.Document()

    # -----------------------------------------------------------------
    # TITLE
    # -----------------------------------------------------------------

    doc.add_heading(
        "Pitch to Project - Handover Scope Analysis",
        0
    )

    # -----------------------------------------------------------------
    # EXECUTIVE SUMMARY
    # -----------------------------------------------------------------

    doc.add_heading(
        "Executive Summary",
        level=1
    )

    doc.add_paragraph(
        data.get(
            "executive_summary",
            ""
        )
    )

    # -----------------------------------------------------------------
    # OBJECTIVES
    # -----------------------------------------------------------------

    doc.add_heading(
        "Project Objectives",
        level=1
    )

    for objective in data.get(
        "project_objectives",
        []
    ):

        doc.add_paragraph(
            f"• {objective}"
        )

    # -----------------------------------------------------------------
    # SCOPE
    # -----------------------------------------------------------------

    doc.add_heading(
        "1. Extracted Scope",
        level=1
    )

    for mod in data.get(
        "extracted_scope",
        []
    ):

        doc.add_heading(
            f"Module: {mod.get('module', 'General')}",
            level=2
        )

        doc.add_paragraph(
            "Requirement Type: "
            f"{mod.get('requirement_type', 'Unknown')}"
        )

        doc.add_paragraph(
            "Source: "
            f"{mod.get('source', 'Uploaded Documents')}"
        )

        doc.add_paragraph(
            "Confidence: "
            f"{mod.get('confidence', 'Unknown')}"
        )

        for point in mod.get(
            "points",
            []
        ):

            doc.add_paragraph(
                f"• {point}"
            )

    # -----------------------------------------------------------------
    # FUNCTIONAL
    # -----------------------------------------------------------------

    doc.add_heading(
        "2. Functional Requirements",
        level=1
    )

    for requirement in data.get(
        "functional_requirements",
        []
    ):

        doc.add_paragraph(
            f"• {requirement}"
        )

    # -----------------------------------------------------------------
    # NON-FUNCTIONAL
    # -----------------------------------------------------------------

    doc.add_heading(
        "3. Non-Functional Requirements",
        level=1
    )

    for requirement in data.get(
        "non_functional_requirements",
        []
    ):

        doc.add_paragraph(
            f"• {requirement}"
        )

    # -----------------------------------------------------------------
    # DEPENDENCIES
    # -----------------------------------------------------------------

    doc.add_heading(
        "4. Integrations & Dependencies",
        level=1
    )

    for dependency in data.get(
        "integrations_and_dependencies",
        []
    ):

        doc.add_paragraph(
            f"• {dependency}"
        )

    # -----------------------------------------------------------------
    # ASSUMPTIONS
    # -----------------------------------------------------------------

    doc.add_heading(
        "5. Assumptions",
        level=1
    )

    for assumption in data.get(
        "assumptions",
        []
    ):

        doc.add_paragraph(
            f"• {assumption}"
        )

    # -----------------------------------------------------------------
    # RISKS
    # -----------------------------------------------------------------

    doc.add_heading(
        "6. Gaps & Risk Audit",
        level=1
    )

    for gap in data.get(
        "gaps_and_risks",
        []
    ):

        severity = gap.get(
            "severity",
            "INFO"
        )

        risk_type = gap.get(
            "type",
            "Risk"
        )

        description = gap.get(
            "description",
            ""
        )

        source = gap.get(
            "source",
            ""
        )

        action = gap.get(
            "recommended_action",
            ""
        )

        doc.add_heading(
            f"[{severity}] {risk_type}",
            level=2
        )

        doc.add_paragraph(
            f"Description: {description}"
        )

        doc.add_paragraph(
            f"Source: {source}"
        )

        doc.add_paragraph(
            f"Recommended Action: {action}"
        )

    # -----------------------------------------------------------------
    # OPEN QUESTIONS
    # -----------------------------------------------------------------

    doc.add_heading(
        "7. Open Questions",
        level=1
    )

    for question in data.get(
        "open_questions",
        []
    ):

        doc.add_paragraph(
            f"• {question}"
        )

    # -----------------------------------------------------------------
    # JIRA
    # -----------------------------------------------------------------

    doc.add_heading(
        "8. Jira User Stories",
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
            "Priority: "
            f"{story.get('priority', 'MEDIUM')}"
        )

        doc.add_paragraph(
            "Source: "
            f"{story.get('source', '')}"
        )

        doc.add_paragraph(
            "As a "
            f"{story.get('user_role', 'User')}, "
            "I want to "
            f"{story.get('want_statement', '')} "
            "so that "
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
                f"  - {ac}"
            )

    # -----------------------------------------------------------------
    # RETURN BYTES
    # -----------------------------------------------------------------

    target_stream = io.BytesIO()

    doc.save(
        target_stream
    )

    return target_stream.getvalue()


# =============================================================================
# 15. MAIN HEADER BANNER
#    FIXED: No <marquee> HTML
# =============================================================================

st.markdown(
    """
    <div style="
        background: linear-gradient(
            90deg,
            #ec4899 0%,
            #8b5cf6 33%,
            #06b6d4 66%,
            #10b981 100%
        );

        color: #ffffff;

        padding: 10px 0px;

        border-radius: 10px;

        font-weight: 800;

        font-size: 1.05rem;

        box-shadow:
            0 0 20px rgba(139, 92, 246, 0.4);

        margin-bottom: 24px;

        overflow: hidden;

        white-space: nowrap;
    ">

        <div style="
            display: inline-block;

            padding-left: 100%;

            animation:
                pitch_project_marquee
                20s linear infinite;
        ">

            ⚡ Smart Scope Handover Engine
            &nbsp;|&nbsp;
            Project Intelligence Layer

            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;

            ⚡ Smart Scope Handover Engine
            &nbsp;|&nbsp;
            Project Intelligence Layer

        </div>

    </div>

    <style>

        @keyframes pitch_project_marquee {

            0% {
                transform: translateX(0%);
            }

            100% {
                transform: translateX(-100%);
            }

        }

    </style>
    """,
    unsafe_allow_html=True
)


# =============================================================================
# 16. TITLE + DEMO TOGGLE
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
                    0 0 15px
                    rgba(56, 189, 248, 0.6);
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
        height=120
    )


with col_toggle:

    demo_mode = st.toggle(
        "Demo Mode (Safe Pitch)",
        value=True
    )


# =============================================================================
# 17. DUAL COLUMN LAYOUT
# =============================================================================

left_col, right_col = st.columns(
    [1, 1],
    gap="medium"
)


# =============================================================================
# 18. LEFT COLUMN
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
        placeholder=(
            "Paste kickoff notes or client requirements here..."
        )
    )

    generate_btn = st.button(
        "⚡ GENERATE SMART SCOPE"
    )


# =============================================================================
# 19. RIGHT COLUMN
# =============================================================================

with right_col:

    st.header(
        "2. AI Scope & Handover Analysis"
    )

    # -----------------------------------------------------------------
    # GENERATE
    # -----------------------------------------------------------------

    if generate_btn:

        progress_card = st.empty()

        # =============================================================
        # DEMO MODE
        # =============================================================

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

        # =============================================================
        # LIVE GEMINI
        # =============================================================

        else:

            raw_text = extract_text_from_uploads(
                sow_files,
                notes_files,
                loose_notes,
                media_files
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

                    # -------------------------------------------------
                    # STEP 1
                    # -------------------------------------------------

                    bar_ph.markdown(
                        render_stylish_progress(
                            20,
                            "📄 Step 1/4: Extracting and structuring intake material..."
                        ),
                        unsafe_allow_html=True
                    )

                    time.sleep(
                        0.3
                    )

                    # -------------------------------------------------
                    # STEP 2
                    # -------------------------------------------------

                    bar_ph.markdown(
                        render_stylish_progress(
                            40,
                            "🔎 Step 2/4: Building source-traceable requirements..."
                        ),
                        unsafe_allow_html=True
                    )

                    time.sleep(
                        0.3
                    )

                    # -------------------------------------------------
                    # STEP 3
                    # -------------------------------------------------

                    bar_ph.markdown(
                        render_stylish_progress(
                            65,
                            "🧠 Step 3/4: Auditing scope, gaps, conflicts & dependencies..."
                        ),
                        unsafe_allow_html=True
                    )

                    time.sleep(
                        0.3
                    )

                    # -------------------------------------------------
                    # CALL GEMINI
                    # -------------------------------------------------

                    result = analyze_with_gemini(
                        raw_text
                    )

                    # -------------------------------------------------
                    # STEP 4
                    # -------------------------------------------------

                    if result:

                        bar_ph.markdown(
                            render_stylish_progress(
                                100,
                                "✅ Step 4/4: Smart Scope Handover Analysis Complete!"
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


    # =============================================================================
    # 20. DEFAULT ANALYSIS
    # =============================================================================

    if "analysis_data" not in st.session_state:

        st.session_state[
            "analysis_data"
        ] = MOCK_ANALYSIS


    data = st.session_state[
        "analysis_data"
    ]


    # =============================================================================
    # 21. EXECUTIVE SUMMARY
    # =============================================================================

    if data.get(
        "executive_summary"
    ):

        with st.container(
            border=True
        ):

            st.markdown(
                "### 🧠 Executive Summary"
            )

            st.write(
                data.get(
                    "executive_summary",
                    ""
                )
            )


    # =============================================================================
    # 22. TABS
    # =============================================================================

    tab_scope, tab_risks, tab_jira = st.tabs(
        [
            "📌 Extracted Scope",
            "🚨 Missing Items & Risks",
            "🚀 Jira User Stories"
        ]
    )


    # =============================================================================
    # TAB 1 — SCOPE
    # =============================================================================

    with tab_scope:

        objectives = data.get(
            "project_objectives",
            []
        )

        if objectives:

            with st.container(
                border=True
            ):

                st.markdown(
                    "### 🎯 Project Objectives"
                )

                for objective in objectives:

                    st.markdown(
                        f"• {objective}"
                    )


        scope_items = data.get(
            "extracted_scope",
            []
        )

        if not scope_items:

            st.info(
                "No extracted scope items available."
            )

        for item in scope_items:

            with st.container(
                border=True
            ):

                st.markdown(
                    "### 📌 MODULE: "
                    f"{item.get('module', 'General Scope')}"
                )

                st.caption(
                    "Source: "
                    f"{item.get('source', 'Uploaded Files')}"
                )

                st.caption(
                    "Type: "
                    f"{item.get('requirement_type', 'Unknown')}"
                    " | Confidence: "
                    f"{item.get('confidence', 'Unknown')}"
                )

                for pt in item.get(
                    "points",
                    []
                ):

                    st.markdown(
                        f"• {pt}"
                    )


        functional_requirements = data.get(
            "functional_requirements",
            []
        )

        if functional_requirements:

            with st.container(
                border=True
            ):

                st.markdown(
                    "### ⚙️ Functional Requirements"
                )

                for requirement in functional_requirements:

                    st.markdown(
                        f"• {requirement}"
                    )


        non_functional_requirements = data.get(
            "non_functional_requirements",
            []
        )

        if non_functional_requirements:

            with st.container(
                border=True
            ):

                st.markdown(
                    "### 🛡️ Non-Functional Requirements"
                )

                for requirement in non_functional_requirements:

                    st.markdown(
                        f"• {requirement}"
                    )


        dependencies = data.get(
            "integrations_and_dependencies",
            []
        )

        if dependencies:

            with st.container(
                border=True
            ):

                st.markdown(
                    "### 🔗 Integrations & Dependencies"
                )

                for dependency in dependencies:

                    st.markdown(
                        f"• {dependency}"
                    )


        assumptions = data.get(
            "assumptions",
            []
        )

        if assumptions:

            with st.container(
                border=True
            ):

                st.markdown(
                    "### 💡 Assumptions"
                )

                for assumption in assumptions:

                    st.markdown(
                        f"• {assumption}"
                    )


    # =============================================================================
    # TAB 2 — RISKS
    # =============================================================================

    with tab_risks:

        risks = data.get(
            "gaps_and_risks",
            []
        )

        if not risks:

            st.success(
                "✅ No significant gaps or risks were identified."
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

                    badge_color = "🔴"

                elif severity == "MEDIUM":

                    badge_color = "🟡"

                else:

                    badge_color = "🔵"

                st.markdown(
                    f"### {badge_color} "
                    f"[{severity}] "
                    f"{risk.get('type', 'Risk')}"
                )

                st.write(
                    risk.get(
                        "description",
                        ""
                    )
                )

                source = risk.get(
                    "source",
                    ""
                )

                if source:

                    st.caption(
                        f"Source: {source}"
                    )

                action = risk.get(
                    "recommended_action",
                    ""
                )

                if action:

                    st.markdown(
                        "**Recommended Action:** "
                        f"{action}"
                    )


        questions = data.get(
            "open_questions",
            []
        )

        if questions:

            st.markdown(
                "### ❓ Open Questions"
            )

            for question in questions:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"❓ {question}"
                    )


    # =============================================================================
    # TAB 3 — JIRA
    # =============================================================================

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
                    "### 🚀 "
                    f"{story.get('title', 'User Story')}"
                )

                priority = story.get(
                    "priority",
                    "MEDIUM"
                ).upper()

                st.caption(
                    f"Priority: {priority}"
                )

                st.markdown(
                    f"**As a** "
                    f"`{story.get('user_role', 'User')}`, "
                    f"**I want to** "
                    f"{story.get('want_statement', '')} "
                    f"**so that** "
                    f"{story.get('so_that_statement', '')}."
                )

                source = story.get(
                    "source",
                    ""
                )

                if source:

                    st.caption(
                        f"Source: {source}"
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
    # 23. EXPORT
    # =============================================================================

    st.divider()

    docx_bytes = build_docx_report(
        data
    )

    st.download_button(

        label="📄 Export Handover Report (.docx)",

        data=docx_bytes,

        file_name=(
            "Pitch_to_Project_Handover_Report.docx"
        ),

        mime=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),

        use_container_width=True
    )
