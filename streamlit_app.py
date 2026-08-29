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

/* =========================================================================
   GLOBAL APPLICATION BACKGROUND
   ========================================================================= */

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


/* =========================================================================
   LOGIN FORM
   ========================================================================= */

div[data-testid="stForm"] {
    background: rgba(15, 23, 42, 0.95) !important;
    border: 2.5px solid #a855f7 !important;
    border-radius: 18px !important;
    padding: 36px !important;
    box-shadow: 0 0 40px rgba(168, 85, 247, 0.5) !important;
}


/* =========================================================================
   LOGIN LABELS
   ========================================================================= */

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


/* =========================================================================
   TEXT INPUTS
   ========================================================================= */

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


/* =========================================================================
   AUTOFILL
   ========================================================================= */

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


/* =========================================================================
   PLACEHOLDER
   ========================================================================= */

div[data-testid="stTextInput"] input::placeholder,
input::placeholder {

    color: #94a3b8 !important;
    -webkit-text-fill-color: #94a3b8 !important;

    font-weight: 700 !important;
    font-size: 1.25rem !important;

    opacity: 1 !important;
    text-align: left !important;
}


/* =========================================================================
   PASSWORD EYE
   ========================================================================= */

div[data-testid="stTextInput"] button svg,
div[data-testid="stForm"] svg {

    fill: #38bdf8 !important;
    stroke: #38bdf8 !important;

    width: 26px !important;
    height: 26px !important;
}


/* =========================================================================
   LOGIN BUTTON
   ========================================================================= */

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


/* =========================================================================
   SIDEBAR
   ========================================================================= */

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


/* =========================================================================
   MAIN HEADINGS
   ========================================================================= */

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


/* =========================================================================
   FILE UPLOADER
   ========================================================================= */

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


/* =========================================================================
   TOAST
   ========================================================================= */

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


/* =========================================================================
   DOWNLOAD BUTTON
   ========================================================================= */

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


/* =========================================================================
   TEXT AREA
   ========================================================================= */

div[data-testid="stTextArea"] textarea {

    background:
        rgba(15, 23, 42, 0.85) !important;

    border:
        2px solid #a855f7 !important;

    border-radius: 14px !important;

    color: #ffffff !important;
}


/* =========================================================================
   GENERAL BUTTONS
   ========================================================================= */

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


/* =========================================================================
   TABS
   ========================================================================= */

button[aria-selected="true"] {

    background:
        linear-gradient(
            135deg,
            #8b5cf6 0%,
            #ec4899 100%
        ) !important;

    color: #ffffff !important;
}


/* =========================================================================
   RESULT CARDS
   ========================================================================= */

div[data-testid="stVerticalBlockBorderWrapper"] > div {

    background:
        rgba(15, 23, 42, 0.8) !important;

    backdrop-filter: blur(10px) !important;

    border-left:
        6px solid #06b6d4 !important;

    border-radius: 14px !important;

    padding: 20px !important;
}


/* =========================================================================
   CODE
   ========================================================================= */

code {

    background-color:
        rgba(30, 27, 75, 0.95) !important;

    color: #38bdf8 !important;

    border:
        1px solid #a855f7 !important;

    border-radius: 6px !important;

    padding: 3px 8px !important;
}


/* =========================================================================
   SMART MOVING HEADER
   ========================================================================= */

.smart-banner-wrapper {

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

    border-radius: 10px;

    margin-bottom: 24px;

    box-shadow:
        0 0 20px rgba(139, 92, 246, 0.4);

    padding: 10px 0;

    position: relative;
}


.smart-banner-track {

    display: flex;

    width: max-content;

    animation:
        smartBannerScroll 18s linear infinite;
}


.smart-banner-text {

    flex-shrink: 0;

    color: #ffffff;

    font-size: 1.05rem;

    font-weight: 800;

    white-space: nowrap;

    padding-right: 100px;

    text-shadow:
        0 2px 6px rgba(0, 0, 0, 0.4);
}


@keyframes smartBannerScroll {

    0% {
        transform: translateX(0);
    }

    100% {
        transform: translateX(-50%);
    }
}


/* =========================================================================
   ANALYSIS PROGRESS CARD
   ========================================================================= */

.smart-progress-card {

    background:
        rgba(15, 23, 42, 0.88);

    border:
        1.5px solid rgba(56, 189, 248, 0.35);

    border-radius: 14px;

    padding: 16px;

    box-shadow:
        0 0 20px rgba(56, 189, 248, 0.15);
}

</style>
"""

st.markdown(css_code, unsafe_allow_html=True)


# =============================================================================
# 3. AUTHENTICATION
# =============================================================================

def check_password():
    """
    Display login form until valid credentials are entered.
    """

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
                    "admin",
                )

                valid_password = st.secrets.get(
                    "APP_PASSWORD",
                    "project2026",
                )

                if (
                    username == valid_user
                    and password == valid_password
                ):

                    st.session_state["authenticated"] = True

                    st.toast(
                        "⚡ Login Successful!",
                        icon="✅",
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
        use_container_width=True,
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
# 6. SAFE PROGRESS BAR
# =============================================================================

def render_stylish_progress(
    percentage,
    status_text,
):
    """
    Returns HTML for the neon progress bar.

    IMPORTANT:
    The returned HTML must be rendered using:
        st.markdown(..., unsafe_allow_html=True)
    """

    percentage = max(
        0,
        min(
            100,
            int(percentage),
        ),
    )

    return f"""
    <div class="smart-progress-card">

        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
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
                    0 0 10px rgba(245, 158, 11, 0.5);
            ">
                {percentage}%
            </span>

        </div>


        <div style="
            width: 100%;
            background: rgba(15, 23, 42, 0.95);
            border: 2px solid #10b981;
            border-radius: 12px;
            padding: 3px;
            box-shadow:
                0 0 15px rgba(16, 185, 129, 0.3);
            box-sizing: border-box;
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
                    0 0 20px rgba(245, 158, 11, 0.8);

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
    loose_notes,
):
    """
    Extract text from DOCX, TXT and pasted notes.
    """

    combined_text = ""

    # -------------------------------------------------------------------------
    # DOCX
    # -------------------------------------------------------------------------

    if sow_files:

        for file in sow_files:

            try:

                file.seek(0)

                doc = docx.Document(file)

                combined_text += (
                    f"\n--- FILE: {file.name} ---\n"
                )

                for index, para in enumerate(
                    doc.paragraphs,
                    start=1,
                ):

                    text = para.text.strip()

                    if text:

                        combined_text += (
                            f"[Paragraph {index}] "
                            f"{text}\n"
                        )

                # Tables
                for table_index, table in enumerate(
                    doc.tables,
                    start=1,
                ):

                    combined_text += (
                        f"\n[TABLE {table_index}]\n"
                    )

                    for row in table.rows:

                        row_values = []

                        for cell in row.cells:

                            value = cell.text.strip()

                            row_values.append(
                                value
                            )

                        combined_text += (
                            " | ".join(row_values)
                            + "\n"
                        )

            except Exception as e:

                combined_text += (
                    f"\n--- FILE ERROR: {file.name} ---\n"
                    f"Could not read file: {str(e)}\n"
                )


    # -------------------------------------------------------------------------
    # TXT
    # -------------------------------------------------------------------------

    if notes_files:

        for file in notes_files:

            try:

                file.seek(0)

                content = file.read()

                if isinstance(content, bytes):

                    content = content.decode(
                        "utf-8",
                        errors="replace",
                    )

                combined_text += (
                    f"\n--- FILE: {file.name} ---\n"
                )

                combined_text += (
                    content
                    + "\n"
                )

            except Exception as e:

                combined_text += (
                    f"\n--- FILE ERROR: {file.name} ---\n"
                    f"Could not read file: {str(e)}\n"
                )


    # -------------------------------------------------------------------------
    # PASTED NOTES
    # -------------------------------------------------------------------------

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

def build_scope_prompt(raw_text):

    return f"""
You are a Senior IT Delivery Lead, Business Analyst,
Solution Architect and Project Handover Specialist.

Your responsibility is to transform messy project-intake information
into a professional, implementation-ready Smart Scope Analysis.

The input may contain:

- Statements of Work
- Proposals
- Client emails
- Meeting notes
- Kickoff transcripts
- Functional requirements
- Technical requirements
- Business requirements
- Tables
- Constraints
- Assumptions
- Dependencies
- Timelines
- SLA expectations
- Integration requirements
- Security requirements
- User roles
- Acceptance expectations

============================================================
PRIMARY OBJECTIVE
============================================================

Analyze the COMPLETE intake material.

Do NOT merely summarize it.

Extract actionable scope and identify ambiguity, missing information,
contradictions, risks, assumptions, dependencies and implementation
questions.

The final output must help a Delivery Lead understand:

1. What is explicitly in scope?
2. What is implied but not confirmed?
3. What is missing?
4. What conflicts with other information?
5. What risks could affect delivery?
6. What clarification questions should be raised?
7. What Jira-ready user stories should be created?

============================================================
SCOPE EXTRACTION RULES
============================================================

For every meaningful requirement:

- Identify the appropriate module.
- Preserve the actual meaning of the source.
- Do not invent requirements.
- Separate functional and non-functional expectations when useful.
- Capture business rules.
- Capture roles and permissions.
- Capture integrations.
- Capture data requirements.
- Capture workflows.
- Capture reporting requirements.
- Capture security requirements.
- Capture performance requirements.
- Capture SLA expectations.
- Capture deployment/environment expectations.
- Capture constraints and dependencies.

SOURCE TRACEABILITY IS IMPORTANT.

Whenever possible, identify the originating file and paragraph,
section, table or approximate line.

============================================================
GAP AND RISK ANALYSIS
============================================================

Look specifically for:

- Missing requirements
- Ambiguous requirements
- Contradictory requirements
- Missing acceptance criteria
- Missing SLA
- Missing performance targets
- Missing security requirements
- Missing authentication/authorization details
- Missing data retention rules
- Missing backup/recovery requirements
- Missing integration specifications
- Missing API details
- Missing error-handling expectations
- Missing notification rules
- Missing reporting requirements
- Missing ownership
- Missing approval process
- Missing environments
- Missing deployment information
- Missing support model
- Missing monitoring requirements
- Missing scalability requirements
- Timeline conflicts
- Scope conflicts
- Technical constraints
- Dependency risks
- Assumption risks

Severity:

HIGH
= likely to cause significant delivery, cost, security,
timeline or scope impact.

MEDIUM
= important issue that should be clarified before implementation.

LOW
= useful clarification or minor delivery concern.

============================================================
CONFLICT DETECTION
============================================================

Compare information across ALL supplied documents.

Examples:

- Different file size limits
- Different dates
- Different user counts
- Different SLA values
- Different technology expectations
- Different role definitions
- Different workflow descriptions
- Different scope boundaries
- Different integration requirements

Do NOT claim a conflict unless the source material actually supports it.

============================================================
JIRA USER STORIES
============================================================

Create implementation-ready user stories from confirmed or strongly
implied requirements.

Use this structure:

As a <user role>,
I want to <action>,
so that <business value>.

Acceptance criteria should use clear Given / When / Then language.

Acceptance criteria must be testable.

Avoid vague criteria such as:

"System should work correctly."

Prefer:

"Given an authenticated administrator,
When the administrator creates a new client,
Then the system validates mandatory fields and creates the client
with an Active status."

============================================================
IMPORTANT ANTI-HALLUCINATION RULES
============================================================

1. Never invent a requirement.
2. Never invent a source.
3. Never invent a business rule.
4. Never invent a deadline.
5. Never invent an SLA.
6. Never invent a technology.
7. Never invent a user role.
8. Never invent an integration.
9. If information is unavailable, explicitly identify it as missing.
10. Clearly distinguish confirmed requirements from assumptions.

============================================================
OUTPUT FORMAT
============================================================

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "executive_summary": {{
        "project_understanding": "Short professional summary",
        "scope_confidence": "HIGH/MEDIUM/LOW",
        "overall_risk": "HIGH/MEDIUM/LOW"
    }},

    "extracted_scope": [
        {{
            "module": "MODULE NAME",
            "scope_type": "FUNCTIONAL/NON_FUNCTIONAL/TECHNICAL/BUSINESS",
            "source": "File / section / paragraph / table",
            "confidence": "CONFIRMED/IMPLIED",
            "points": [
                "Requirement detail"
            ]
        }}
    ],

    "gaps_and_risks": [
        {{
            "severity": "HIGH/MEDIUM/LOW",
            "type": "Risk category",
            "description": "Detailed explanation",
            "impact": "Potential delivery/business impact",
            "recommended_action": "Recommended clarification or mitigation"
        }}
    ],

    "clarification_questions": [
        {{
            "priority": "HIGH/MEDIUM/LOW",
            "question": "Question that should be asked",
            "reason": "Why this clarification is necessary"
        }}
    ],

    "assumptions": [
        {{
            "assumption": "Potential assumption",
            "validation_required": true
        }}
    ],

    "dependencies": [
        {{
            "dependency": "Dependency",
            "impact": "Potential impact"
        }}
    ],

    "jira_user_stories": [
        {{
            "title": "Short Story Title",
            "user_role": "Target User",
            "want_statement": "Action",
            "so_that_statement": "Business value",
            "priority": "HIGH/MEDIUM/LOW",
            "acceptance_criteria": [
                "Given ... When ... Then ..."
            ]
        }}
    ]
}}

============================================================
PROJECT INTAKE MATERIALS
============================================================

{raw_text}

============================================================
FINAL VALIDATION
============================================================

Before returning the JSON:

- Check that the JSON is valid.
- Check that every scope item is traceable.
- Check that risks are supported by the input.
- Check for cross-document conflicts.
- Check that Jira stories are actionable.
- Check that acceptance criteria are testable.
- Do not add unsupported facts.
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

                temperature=0.15,
            ),
        )

        if not response:

            st.error(
                "Gemini returned an empty response."
            )

            return None

        response_text = (
            response.text
            if hasattr(response, "text")
            else ""
        )

        if not response_text:

            st.error(
                "Gemini returned no usable text."
            )

            return None

        response_text = response_text.strip()

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

        if not isinstance(data, dict):

            st.error(
                "Gemini response is not a JSON object."
            )

            return None

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
# 10. MOCK / DEMO DATA
# =============================================================================

MOCK_ANALYSIS = {

    "executive_summary": {

        "project_understanding":
            "The solution is intended to provide a centralized "
            "scope-intelligence and project-handover workflow.",

        "scope_confidence":
            "MEDIUM",

        "overall_risk":
            "MEDIUM",
    },


    "extracted_scope": [

        {
            "module":
                "AUTHENTICATION & SECURITY",

            "scope_type":
                "FUNCTIONAL",

            "source":
                "Proposal Page 4, Section 2",

            "confidence":
                "CONFIRMED",

            "points": [

                "Multi-factor authentication (MFA) via SMS/Email.",

                "Role-based access control (RBAC) for Admin and Client roles.",
            ],
        },


        {
            "module":
                "HANDOVER INTELLIGENCE ENGINE",

            "scope_type":
                "TECHNICAL",

            "source":
                "Kickoff Transcript Lines 12-45",

            "confidence":
                "CONFIRMED",

            "points": [

                "Multi-format document parsing for supported intake files.",

                "Automated gap auditing and structured requirement extraction.",

                "Generation of implementation-ready Jira user stories.",
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
                "No operational SLA is explicitly defined for "
                "document processing.",

            "impact":
                "Performance expectations may differ between "
                "stakeholders and implementation teams.",

            "recommended_action":
                "Define target processing time by document size "
                "and workload.",
        },


        {
            "severity":
                "MEDIUM",

            "type":
                "Cross-Document Conflict",

            "description":
                "Different document-processing limits may exist "
                "across project materials.",

            "impact":
                "The implementation team may build against "
                "inconsistent limits.",

            "recommended_action":
                "Confirm the authoritative maximum upload size.",
        },
    ],


    "clarification_questions": [

        {
            "priority":
                "HIGH",

            "question":
                "What is the expected maximum document size "
                "and processing SLA?",

            "reason":
                "The implementation requires measurable "
                "performance expectations.",
        },
    ],


    "assumptions": [

        {
            "assumption":
                "Admin and Client are the initial application roles.",

            "validation_required":
                True,
        },
    ],


    "dependencies": [

        {
            "dependency":
                "Gemini API availability and configured API credentials.",

            "impact":
                "AI analysis cannot execute when the API is unavailable.",
        },
    ],


    "jira_user_stories": [

        {
            "title":
                "Configurable Document Processing Engine",

            "user_role":
                "Delivery Lead",

            "want_statement":
                "ingest supported intake documents concurrently",

            "so_that_statement":
                "I can automatically extract project requirements "
                "without manually reviewing every document",

            "priority":
                "HIGH",

            "acceptance_criteria": [

                "Given a user uploads supported intake documents, "
                "When the user clicks Generate Smart Scope, "
                "Then the system analyzes the supplied content.",

                "Given the analysis completes, "
                "When the results are displayed, "
                "Then the system shows extracted scope, risks "
                "and Jira-ready stories.",
            ],
        },
    ],
}


# =============================================================================
# 11. DOCX REPORT GENERATION
# =============================================================================

def build_docx_report(data):

    doc = docx.Document()

    doc.add_heading(
        "Pitch to Project - Smart Scope Handover Analysis",
        0,
    )


    # -------------------------------------------------------------------------
    # Executive Summary
    # -------------------------------------------------------------------------

    doc.add_heading(
        "Executive Summary",
        level=1,
    )

    summary = data.get(
        "executive_summary",
        {},
    )

    doc.add_paragraph(
        "Project Understanding: "
        + summary.get(
            "project_understanding",
            "Not available",
        )
    )

    doc.add_paragraph(
        "Scope Confidence: "
        + summary.get(
            "scope_confidence",
            "UNKNOWN",
        )
    )

    doc.add_paragraph(
        "Overall Risk: "
        + summary.get(
            "overall_risk",
            "UNKNOWN",
        )
    )


    # -------------------------------------------------------------------------
    # Extracted Scope
    # -------------------------------------------------------------------------

    doc.add_heading(
        "1. Extracted Scope",
        level=1,
    )

    for item in data.get(
        "extracted_scope",
        [],
    ):

        doc.add_heading(
            f"Module: {item.get('module', 'General')}",
            level=2,
        )

        doc.add_paragraph(
            f"Type: {item.get('scope_type', 'N/A')}"
        )

        doc.add_paragraph(
            f"Confidence: {item.get('confidence', 'N/A')}"
        )

        doc.add_paragraph(
            f"Source: {item.get('source', 'Uploaded Documents')}"
        )

        for point in item.get(
            "points",
            [],
        ):

            doc.add_paragraph(
                f"• {point}"
            )


    # -------------------------------------------------------------------------
    # Risks
    # -------------------------------------------------------------------------

    doc.add_heading(
        "2. Gaps & Risk Audit",
        level=1,
    )

    for risk in data.get(
        "gaps_and_risks",
        [],
    ):

        doc.add_heading(
            (
                f"[{risk.get('severity', 'INFO')}] "
                f"{risk.get('type', 'Risk')}"
            ),
            level=2,
        )

        doc.add_paragraph(
            "Description: "
            + risk.get(
                "description",
                "",
            )
        )

        doc.add_paragraph(
            "Impact: "
            + risk.get(
                "impact",
                "",
            )
        )

        doc.add_paragraph(
            "Recommended Action: "
            + risk.get(
                "recommended_action",
                "",
            )
        )


    # -------------------------------------------------------------------------
    # Clarification Questions
    # -------------------------------------------------------------------------

    doc.add_heading(
        "3. Clarification Questions",
        level=1,
    )

    for question in data.get(
        "clarification_questions",
        [],
    ):

        doc.add_paragraph(
            (
                f"[{question.get('priority', 'MEDIUM')}] "
                f"{question.get('question', '')}"
            )
        )

        doc.add_paragraph(
            "Reason: "
            + question.get(
                "reason",
                "",
            )
        )


    # -------------------------------------------------------------------------
    # Assumptions
    # -------------------------------------------------------------------------

    doc.add_heading(
        "4. Assumptions",
        level=1,
    )

    for assumption in data.get(
        "assumptions",
        [],
    ):

        doc.add_paragraph(
            (
                f"{assumption.get('assumption', '')} "
                f"(Validation Required: "
                f"{assumption.get('validation_required', False)})"
            )
        )


    # -------------------------------------------------------------------------
    # Dependencies
    # -------------------------------------------------------------------------

    doc.add_heading(
        "5. Dependencies",
        level=1,
    )

    for dependency in data.get(
        "dependencies",
        [],
    ):

        doc.add_paragraph(
            "Dependency: "
            + dependency.get(
                "dependency",
                "",
            )
        )

        doc.add_paragraph(
            "Impact: "
            + dependency.get(
                "impact",
                "",
            )
        )


    # -------------------------------------------------------------------------
    # Jira Stories
    # -------------------------------------------------------------------------

    doc.add_heading(
        "6. Jira User Stories",
        level=1,
    )

    for story in data.get(
        "jira_user_stories",
        [],
    ):

        doc.add_heading(
            story.get(
                "title",
                "User Story",
            ),
            level=2,
        )

        doc.add_paragraph(
            (
                f"As a {story.get('user_role', 'User')}, "
                f"I want to {story.get('want_statement', '')} "
                f"so that {story.get('so_that_statement', '')}."
            )
        )

        doc.add_paragraph(
            "Priority: "
            + story.get(
                "priority",
                "MEDIUM",
            )
        )

        doc.add_paragraph(
            "Acceptance Criteria:"
        )

        for ac in story.get(
            "acceptance_criteria",
            [],
        ):

            doc.add_paragraph(
                f"- {ac}"
            )


    target_stream = io.BytesIO()

    doc.save(
        target_stream
    )

    return target_stream.getvalue()


# =============================================================================
# 12. MOVING TOP BANNER
# =============================================================================

st.markdown(
    """
    <div class="smart-banner-wrapper">

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
    unsafe_allow_html=True,
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
                color: #ffffff;
                font-size: 2.8rem;
                font-weight: 900;
                margin: 0;
                line-height: 1.2;
                text-shadow:
                    0 0 15px rgba(56, 189, 248, 0.6);
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
        value=True,
    )


# =============================================================================
# 14. MAIN TWO-COLUMN LAYOUT
# =============================================================================

left_col, right_col = st.columns(
    [1, 1],
    gap="medium",
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

        type=[
            "docx"
        ],

        accept_multiple_files=True,
    )


    notes_files = st.file_uploader(

        "Transcripts / Notes (.txt)",

        type=[
            "txt"
        ],

        accept_multiple_files=True,
    )


    media_files = st.file_uploader(

        "Diagrams & Media (.png, .jpg, .mp4, .mp3)",

        type=[
            "png",
            "jpg",
            "mp4",
            "mp3",
        ],

        accept_multiple_files=True,
    )


    loose_notes = st.text_area(

        "Or Paste Loose Client Emails / Notes:",

        height=120,

        placeholder=(
            "Paste kickoff notes or client "
            "requirements here..."
        ),
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
    # GENERATE BUTTON
    # -------------------------------------------------------------------------

    if generate_btn:

        progress_card = st.empty()


        # =====================================================================
        # DEMO MODE
        # =====================================================================

        if demo_mode:

            with progress_card.container(
                border=True
            ):

                st.markdown(
                    "### 🧠 Running Scope Analysis"
                )

                bar_ph = st.empty()


                demo_steps = [

                    (
                        15,
                        "📥 Step 1/3: Reading intake materials..."
                    ),

                    (
                        40,
                        "📄 Step 1/3: Extracting requirements..."
                    ),

                    (
                        65,
                        "⚡ Step 2/3: Building project scope model..."
                    ),

                    (
                        80,
                        "🔍 Step 3/3: Auditing scope, conflicts, risks & Jira stories..."
                    ),

                    (
                        100,
                        "✅ Smart Scope Handover Analysis Complete!"
                    ),
                ]


                for percentage, status in demo_steps:

                    bar_ph.markdown(

                        render_stylish_progress(
                            percentage,
                            status,
                        ),

                        unsafe_allow_html=True,
                    )

                    time.sleep(
                        0.25
                    )


                st.success(
                    "✅ Demo Analysis Loaded Successfully!"
                )


            progress_card.empty()


            st.session_state[
                "analysis_data"
            ] = MOCK_ANALYSIS


            st.toast(
                "⚡ Demo Analysis Loaded!",
                icon="✅",
            )


        # =====================================================================
        # LIVE GEMINI MODE
        # =====================================================================

        else:

            raw_text = extract_text_from_uploads(

                sow_files,

                notes_files,

                loose_notes,
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


                    # ---------------------------------------------------------
                    # STEP 1
                    # ---------------------------------------------------------

                    bar_ph.markdown(

                        render_stylish_progress(
                            20,
                            "📄 Step 1/3: Extracting raw text from intake documents...",
                        ),

                        unsafe_allow_html=True,
                    )

                    time.sleep(
                        0.4
                    )


                    # ---------------------------------------------------------
                    # STEP 2
                    # ---------------------------------------------------------

                    bar_ph.markdown(

                        render_stylish_progress(
                            50,
                            "⚡ Step 2/3: Transmitting payload to Gemini API...",
                        ),

                        unsafe_allow_html=True,
                    )

                    time.sleep(
                        0.4
                    )


                    # ---------------------------------------------------------
                    # STEP 3
                    # ---------------------------------------------------------

                    bar_ph.markdown(

                        render_stylish_progress(
                            80,
                            "🔍 Step 3/3: Auditing scope, conflicts, risks & Jira stories...",
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
                                "✅ Smart Scope Handover Analysis Complete!",
                            ),

                            unsafe_allow_html=True,
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
                            icon="✅",
                        )


                    else:

                        st.error(
                            "❌ Extraction Failed"
                        )


                progress_card.empty()


    # =========================================================================
    # DEFAULT DATA
    # =========================================================================

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


    # =========================================================================
    # TABS
    # =========================================================================

    tab_scope, tab_risks, tab_jira = st.tabs(

        [
            "📌 Extracted Scope",
            "🚨 Missing Items & Risks",
            "🚀 Jira User Stories",
        ]
    )


    # =========================================================================
    # SCOPE TAB
    # =========================================================================

    with tab_scope:

        summary = data.get(
            "executive_summary",
            {},
        )


        if summary:

            with st.container(
                border=True
            ):

                st.markdown(
                    "### 🎯 Executive Summary"
                )

                st.write(
                    summary.get(
                        "project_understanding",
                        "",
                    )
                )

                st.markdown(
                    f"**Scope Confidence:** "
                    f"`{summary.get('scope_confidence', 'UNKNOWN')}`"
                )

                st.markdown(
                    f"**Overall Risk:** "
                    f"`{summary.get('overall_risk', 'UNKNOWN')}`"
                )


        for item in data.get(
            "extracted_scope",
            [],
        ):

            with st.container(
                border=True
            ):

                st.markdown(
                    (
                        f"### 📌 MODULE: "
                        f"{item.get('module', 'General Scope')}"
                    )
                )


                st.caption(
                    (
                        f"Source: "
                        f"{item.get('source', 'Uploaded Files')}"
                    )
                )


                st.markdown(
                    (
                        f"**Type:** "
                        f"`{item.get('scope_type', 'N/A')}` "
                        f"&nbsp;&nbsp; "
                        f"**Confidence:** "
                        f"`{item.get('confidence', 'N/A')}`"
                    ),
                    unsafe_allow_html=True,
                )


                for pt in item.get(
                    "points",
                    [],
                ):

                    st.markdown(
                        f"• {pt}"
                    )


    # =========================================================================
    # RISKS TAB
    # =========================================================================

    with tab_risks:

        for risk in data.get(
            "gaps_and_risks",
            [],
        ):

            with st.container(
                border=True
            ):

                severity = (
                    risk.get(
                        "severity",
                        "INFO",
                    )
                    .upper()
                )


                badge_color = (

                    "🔴"
                    if severity == "HIGH"

                    else "🟡"
                    if severity == "MEDIUM"

                    else "🔵"
                )


                st.markdown(
                    (
                        f"### {badge_color} "
                        f"[{severity}] "
                        f"{risk.get('type', 'Risk')}"
                    )
                )


                st.write(
                    risk.get(
                        "description",
                        "",
                    )
                )


                if risk.get(
                    "impact"
                ):

                    st.markdown(
                        (
                            f"**Impact:** "
                            f"{risk.get('impact')}"
                        )
                    )


                if risk.get(
                    "recommended_action"
                ):

                    st.markdown(
                        (
                            f"**Recommended Action:** "
                            f"{risk.get('recommended_action')}"
                        )
                    )


        # ---------------------------------------------------------------------
        # CLARIFICATION QUESTIONS
        # ---------------------------------------------------------------------

        questions = data.get(
            "clarification_questions",
            [],
        )


        if questions:

            st.markdown(
                "### ❓ Clarification Questions"
            )


            for question in questions:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        (
                            f"**[{question.get('priority', 'MEDIUM')}]** "
                            f"{question.get('question', '')}"
                        )
                    )

                    st.caption(
                        (
                            "Reason: "
                            + question.get(
                                "reason",
                                "",
                            )
                        )
                    )


    # =========================================================================
    # JIRA TAB
    # =========================================================================

    with tab_jira:

        for story in data.get(
            "jira_user_stories",
            [],
        ):

            with st.container(
                border=True
            ):

                st.markdown(
                    (
                        f"### 🚀 "
                        f"{story.get('title', 'User Story')}"
                    )
                )


                st.markdown(
                    (
                        f"**Priority:** "
                        f"`{story.get('priority', 'MEDIUM')}`"
                    )
                )


                st.markdown(
                    (
                        f"**As a** "
                        f"`{story.get('user_role', 'User')}`, "
                        f"**I want to** "
                        f"{story.get('want_statement', '')} "
                        f"**so that** "
                        f"{story.get('so_that_statement', '')}."
                    )
                )


                st.markdown(
                    "**Acceptance Criteria:**"
                )


                for ac in story.get(
                    "acceptance_criteria",
                    [],
                ):

                    st.markdown(
                        f"- `{ac}`"
                    )


    # =========================================================================
    # EXPORT
    # =========================================================================

    st.divider()


    docx_bytes = build_docx_report(
        data
    )


    st.download_button(

        label="📄 Export Handover Report (.docx)",

        data=docx_bytes,

        file_name=(
            "Pitch_to_Project_"
            "Handover_Report.docx"
        ),

        mime=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),

        use_container_width=True,
    )
