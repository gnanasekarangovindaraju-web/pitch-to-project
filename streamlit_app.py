import io
import json
import time

import docx
import jwt
import pypdf
import streamlit as st
import streamlit.components.v1 as components

from PIL import Image
from google import genai
from google.genai import types
from streamlit_oauth import OAuth2Component


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Pitch to Project | Smart Scope Engine",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- Main background ---------- */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(0, 255, 255, 0.08),
                transparent 25%
            ),
            radial-gradient(
                circle at 90% 20%,
                rgba(130, 80, 255, 0.10),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #050816 0%,
                #08101f 50%,
                #050816 100%
            );
        color: #ffffff;
    }

    /* ---------- Main container ---------- */

    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    /* ---------- Text ---------- */

    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }

    p, span, label, div {
        font-family:
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            sans-serif;
    }

    /* ---------- Sidebar ---------- */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #07101d 0%,
                #050914 100%
            );
        border-right: 1px solid rgba(0, 255, 255, 0.15);
    }

    /* ---------- Buttons ---------- */

    .stButton > button {
        border-radius: 10px;
        border: 1px solid rgba(0, 255, 255, 0.35);
        background:
            linear-gradient(
                135deg,
                rgba(0, 220, 255, 0.18),
                rgba(100, 70, 255, 0.18)
            );
        color: white;
        font-weight: 700;
        min-height: 44px;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #00ffff;
        box-shadow:
            0 0 15px rgba(0, 255, 255, 0.25);
        transform: translateY(-1px);
    }

    /* ---------- Download button ---------- */

    .stDownloadButton > button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid rgba(0, 255, 255, 0.4);
        background:
            linear-gradient(
                135deg,
                rgba(0, 220, 255, 0.15),
                rgba(110, 70, 255, 0.20)
            );
        color: white;
        font-weight: 700;
    }

    /* ---------- File uploader ---------- */

    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.025);
        border-radius: 12px;
        padding: 5px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* ---------- Metrics ---------- */

    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.025);
        border: 1px solid rgba(0, 255, 255, 0.12);
        border-radius: 12px;
        padding: 12px;
    }

    /* ---------- Tabs ---------- */

    button[data-baseweb="tab"] {
        color: #b8c7d9;
        font-weight: 600;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #00ffff;
    }

    /* ---------- Expanders ---------- */

    [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.025);
        border: 1px solid rgba(0, 255, 255, 0.10);
        border-radius: 10px;
    }

    /* ---------- Cards ---------- */

    .scope-card {
        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,0.045),
                rgba(255,255,255,0.015)
            );
        border: 1px solid rgba(0,255,255,0.12);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 14px;
    }

    .scope-title {
        color: #00ffff;
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .scope-text {
        color: #d5deea;
        line-height: 1.6;
    }

    .risk-high {
        border-left: 4px solid #ff4d6d;
    }

    .risk-medium {
        border-left: 4px solid #ffb703;
    }

    .risk-low {
        border-left: 4px solid #06d6a0;
    }

    .jira-card {
        background: rgba(255,255,255,0.025);
        border: 1px solid rgba(130,100,255,0.20);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
    }

    .small-muted {
        color: #8fa2b8;
        font-size: 13px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_SESSION_STATE = {
    "authenticated": False,
    "current_user": None,
    "analysis_data": None,
    "last_error": None,
    "processing": False,
}

for key, value in DEFAULT_SESSION_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# GOOGLE SSO
# ============================================================

def check_google_sso():
    """
    Google OAuth authentication.

    Required secrets:

    [oauth]
    client_id = "..."
    client_secret = "..."
    redirect_uri = "http://localhost:8501"

    COMPANY_DOMAIN = "hurix.com"
    """

    if st.session_state.get("authenticated"):
        return True

    try:
        oauth_config = st.secrets["oauth"]

        client_id = oauth_config["client_id"]
        client_secret = oauth_config["client_secret"]
        redirect_uri = oauth_config["redirect_uri"]

        allowed_domain = st.secrets.get(
            "COMPANY_DOMAIN",
            "hurix.com"
        ).lower().strip()

    except Exception as exc:
        st.error("Google OAuth configuration is missing.")
        st.code(
            f"{type(exc).__name__}: {exc}",
            language="text"
        )
        return False

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:35px 10px 15px 10px;
        ">
            <div style="
                font-size:48px;
                font-weight:900;
                background:
                    linear-gradient(
                        90deg,
                        #00ffff,
                        #7c5cff
                    );
                -webkit-background-clip:text;
                -webkit-text-fill-color:transparent;
            ">
                PITCH TO PROJECT
            </div>

            <div style="
                color:#9fb0c3;
                font-size:17px;
                margin-top:8px;
            ">
                Smart Scope Engine
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='text-align:center; color:#b8c7d9;'>"
        "Sign in with your company Google account"
        "</div>",
        unsafe_allow_html=True,
    )

    try:
        oauth2 = OAuth2Component(
            client_id,
            client_secret,
            authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
            token_endpoint="https://oauth2.googleapis.com/token",
        )

        result = oauth2.authorize_button(
            name="🔑 Login with Hurix Google Account",
            redirect_uri=redirect_uri,
            scope="openid email profile",
            key="google_sso",
            extras_params={
                "prompt": "select_account"
            },
        )

    except Exception as exc:
        st.error("Google login could not be initialized.")
        st.code(
            f"{type(exc).__name__}: {exc}",
            language="text"
        )
        return False

    if not result:
        return False

    try:
        token = result.get("token", {})

        id_token = token.get("id_token")

        if not id_token:
            st.error("Google did not return an ID token.")
            return False

        # Decode only.
        # Production authentication should additionally
        # verify the token signature and issuer.
        user_info = jwt.decode(
            id_token,
            options={
                "verify_signature": False,
                "verify_aud": False,
            },
        )

        email = (
            user_info.get("email", "")
            .lower()
            .strip()
        )

        email_verified = user_info.get(
            "email_verified",
            False
        )

        if not email:
            st.error("Google account email was not returned.")
            return False

        if not email_verified:
            st.error("Google account email is not verified.")
            return False

        if not email.endswith("@" + allowed_domain):
            st.error(
                f"Access denied. Please use your @{allowed_domain} "
                "Google account."
            )
            return False

        st.session_state["authenticated"] = True
        st.session_state["current_user"] = email
        st.session_state["last_error"] = None

        st.toast(
            f"Welcome {email}",
            icon="✅"
        )

        try:
            st.query_params.clear()
        except Exception:
            pass

        st.rerun()

    except Exception as exc:
        st.error("Google login response could not be processed.")
        st.code(
            f"{type(exc).__name__}: {exc}",
            language="text"
        )
        return False

    return False


# ============================================================
# LOGIN CHECK
# ============================================================

if not check_google_sso():
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            padding:10px 0 20px 0;
            text-align:center;
        ">
            <div style="
                font-size:24px;
                font-weight:900;
                color:#00ffff;
            ">
                🚀 Smart Scope
            </div>

            <div style="
                color:#7f91a6;
                font-size:12px;
                margin-top:4px;
            ">
                Pitch to Project
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    current_user = st.session_state.get(
        "current_user",
        "Unknown"
    )

    st.markdown("### 👤 Signed in")
    st.caption(current_user)

    st.divider()

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = None
        st.session_state["analysis_data"] = None

        try:
            st.query_params.clear()
        except Exception:
            pass

        st.rerun()


# ============================================================
# GEMINI CLIENT
# ============================================================

@st.cache_resource
def get_gemini_client():

    try:
        api_key = st.secrets["GEMINI_API_KEY"]

        if not api_key:
            return None, "GEMINI_API_KEY is empty."

        client = genai.Client(
            api_key=api_key
        )

        return client, None

    except Exception as exc:

        return (
            None,
            f"{type(exc).__name__}: {exc}"
        )


client, gemini_init_error = get_gemini_client()


# ============================================================
# PROGRESS DISPLAY
# ============================================================

def render_stylish_progress(
    current_step,
    total_steps,
    message
):

    percentage = int(
        (current_step / total_steps) * 100
    )

    st.markdown(
        f"""
        <div style="
            background:rgba(255,255,255,0.035);
            border:1px solid rgba(0,255,255,0.18);
            border-radius:14px;
            padding:18px;
            margin:10px 0 20px 0;
        ">

            <div style="
                display:flex;
                justify-content:space-between;
                margin-bottom:10px;
            ">
                <span style="
                    color:#ffffff;
                    font-weight:700;
                ">
                    {message}
                </span>

                <span style="
                    color:#00ffff;
                    font-weight:800;
                ">
                    {percentage}%
                </span>
            </div>

            <div style="
                width:100%;
                height:8px;
                background:#182335;
                border-radius:20px;
                overflow:hidden;
            ">

                <div style="
                    width:{percentage}%;
                    height:100%;
                    background:
                        linear-gradient(
                            90deg,
                            #00ffff,
                            #7c5cff
                        );
                    border-radius:20px;
                    transition:width 0.3s ease;
                ">
                </div>

            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DOCX EXTRACTION
# ============================================================

def extract_docx_details(file):

    result = {
        "filename": file.name,
        "text": "",
        "tables": [],
        "images": [],
    }

    try:

        file.seek(0)

        document = docx.Document(file)

        text_parts = []

        # Paragraphs
        for paragraph in document.paragraphs:

            text = paragraph.text.strip()

            if text:
                text_parts.append(text)

        # Headers
        for section in document.sections:

            try:
                header_text = []

                for paragraph in section.header.paragraphs:
                    if paragraph.text.strip():
                        header_text.append(
                            paragraph.text.strip()
                        )

                if header_text:
                    text_parts.extend(header_text)

            except Exception:
                pass

        # Footers
        for section in document.sections:

            try:
                footer_text = []

                for paragraph in section.footer.paragraphs:
                    if paragraph.text.strip():
                        footer_text.append(
                            paragraph.text.strip()
                        )

                if footer_text:
                    text_parts.extend(footer_text)

            except Exception:
                pass

        # Tables
        for table in document.tables:

            table_data = []

            for row in table.rows:

                row_data = []

                for cell in row.cells:

                    row_data.append(
                        cell.text.strip()
                    )

                table_data.append(row_data)

            if table_data:
                result["tables"].append(
                    table_data
                )

                # Also include table text
                for row in table_data:
                    text_parts.append(
                        " | ".join(row)
                    )

        # Images
        for rel in document.part.rels.values():

            try:

                target_ref = getattr(
                    rel,
                    "target_ref",
                    ""
                )

                if "image" not in target_ref:
                    continue

                img_part = rel.target_part
                img_bytes = img_part.blob

                content_type = getattr(
                    img_part,
                    "content_type",
                    ""
                )

                img_ext = content_type.split("/")[-1]

                if img_ext in [
                    "png",
                    "jpeg",
                    "jpg",
                ]:

                    img = Image.open(
                        io.BytesIO(img_bytes)
                    )

                    result["images"].append(img)

            except Exception:
                continue

        result["text"] = "\n".join(
            text_parts
        )

        return result

    except Exception as exc:

        raise RuntimeError(
            f"Failed to read DOCX '{file.name}': "
            f"{type(exc).__name__}: {exc}"
        )


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_pdf_details(file):

    result = {
        "filename": file.name,
        "text": "",
        "pages": 0,
    }

    try:

        file.seek(0)

        reader = pypdf.PdfReader(file)

        result["pages"] = len(
            reader.pages
        )

        text_parts = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            try:
                page_text = (
                    page.extract_text()
                    or ""
                )

                if page_text.strip():

                    text_parts.append(
                        f"--- Page {page_number} ---\n"
                        f"{page_text}"
                    )

            except Exception:
                continue

        result["text"] = "\n\n".join(
            text_parts
        )

        return result

    except Exception as exc:

        raise RuntimeError(
            f"Failed to read PDF '{file.name}': "
            f"{type(exc).__name__}: {exc}"
        )


# ============================================================
# BUILD MULTIMODAL PAYLOAD
# ============================================================

def build_multimodal_payload(
    sow_files=None,
    proposal_files=None,
    meeting_files=None,
    direct_media_files=None,
    loose_notes="",
):

    payload_parts = []

    # --------------------------------------------------------
    # Intro
    # --------------------------------------------------------

    payload_parts.append(
        """
PROJECT INPUTS BEGIN

The following content is supplied by the client/project team.
Analyze all relevant information together.

Do not invent facts that are not present in the input.

PROJECT INPUTS END
"""
    )

    # --------------------------------------------------------
    # DOCX
    # --------------------------------------------------------

    all_docx_files = []

    if sow_files:
        all_docx_files.extend(
            sow_files
        )

    if proposal_files:
        all_docx_files.extend(
            proposal_files
        )

    for file in all_docx_files:

        try:

            details = extract_docx_details(
                file
            )

            label = (
                "STATEMENT OF WORK"
                if sow_files
                and file in sow_files
                else "PROPOSAL"
            )

            payload_parts.append(
                f"""
===== {label}: {file.name} =====

{details["text"]}
"""
            )

            # Add extracted images
            for img in details["images"]:

                payload_parts.append(img)

        except Exception as exc:

            payload_parts.append(
                f"""
===== FILE ERROR: {file.name} =====

Unable to extract this file.

Error:
{type(exc).__name__}: {exc}
"""
            )

    # --------------------------------------------------------
    # Meeting notes / TXT / PDF
    # --------------------------------------------------------

    if meeting_files:

        for file in meeting_files:

            filename = file.name.lower()

            try:

                file.seek(0)

                if filename.endswith(".docx"):

                    details = extract_docx_details(
                        file
                    )

                    payload_parts.append(
                        f"""
===== MEETING DOCUMENT: {file.name} =====

{details["text"]}
"""
                    )

                    for img in details["images"]:
                        payload_parts.append(img)

                elif filename.endswith(".pdf"):

                    details = extract_pdf_details(
                        file
                    )

                    payload_parts.append(
                        f"""
===== MEETING PDF: {file.name} =====

{details["text"]}
"""
                    )

                else:

                    raw = file.read()

                    text = raw.decode(
                        "utf-8",
                        errors="replace"
                    )

                    payload_parts.append(
                        f"""
===== MEETING NOTES: {file.name} =====

{text}
"""
                    )

            except Exception as exc:

                payload_parts.append(
                    f"""
===== FILE ERROR: {file.name} =====

{type(exc).__name__}: {exc}
"""
                )

    # --------------------------------------------------------
    # Direct media
    # --------------------------------------------------------

    if direct_media_files:

        for file in direct_media_files:

            try:

                file.seek(0)

                bytes_data = file.read()

                mime_type = (
                    file.type
                    or ""
                )

                if mime_type.startswith(
                    "image/"
                ):

                    img = Image.open(
                        io.BytesIO(bytes_data)
                    )

                    payload_parts.append(
                        f"""
===== IMAGE: {file.name} =====
"""
                    )

                    payload_parts.append(img)

                elif (
                    mime_type.startswith("audio/")
                    or mime_type.startswith("video/")
                ):

                    media_part = (
                        types.Part.from_bytes(
                            data=bytes_data,
                            mime_type=mime_type,
                        )
                    )

                    payload_parts.append(
                        f"""
===== MEDIA: {file.name} =====
"""
                    )

                    payload_parts.append(
                        media_part
                    )

                else:

                    payload_parts.append(
                        f"""
===== MEDIA FILE: {file.name} =====
Unsupported media type: {mime_type}
"""
                    )

            except Exception as exc:

                payload_parts.append(
                    f"""
===== MEDIA ERROR: {file.name} =====

{type(exc).__name__}: {exc}
"""
                )

    # --------------------------------------------------------
    # Loose notes
    # --------------------------------------------------------

    if loose_notes and loose_notes.strip():

        payload_parts.append(
            f"""
===== ADDITIONAL CLIENT NOTES =====

{loose_notes.strip()}
"""
        )

    return payload_parts


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_INSTRUCTION_PROMPT = """
You are an expert Project Delivery Architect and Scope Analyst.

Your job is to analyze client project information and convert it into
a structured implementation-ready delivery scope.

Read ALL supplied project inputs.

The input may contain:

- Proposals
- Statements of Work
- Client emails
- Meeting notes
- Kickoff notes
- Requirements
- PDF documents
- Images
- Audio
- Video
- Additional notes

IMPORTANT RULES:

1. Do not invent requirements.
2. Separate explicit requirements from assumptions.
3. Identify missing information.
4. Identify risks and dependencies.
5. Identify SLA or acceptance gaps.
6. Convert functional requirements into clear modules.
7. Provide useful implementation-level information.
8. Keep the response strictly valid JSON.
9. Do not use Markdown fences.
10. Do not add text before or after the JSON.

Return exactly this structure:

{
  "executive_summary": {
    "project_name": "",
    "objective": "",
    "summary": "",
    "business_value": ""
  },

  "scope": {
    "in_scope": [],
    "out_of_scope": [],
    "functional_modules": [
      {
        "module": "",
        "description": "",
        "requirements": [],
        "dependencies": [],
        "acceptance_criteria": []
      }
    ]
  },

  "assumptions": [],

  "open_questions": [],

  "risks": [
    {
      "risk": "",
      "severity": "High|Medium|Low",
      "impact": "",
      "mitigation": ""
    }
  ],

  "sla_gaps": [
    {
      "area": "",
      "gap": "",
      "impact": "",
      "recommendation": ""
    }
  ],

  "dependencies": [],

  "deliverables": [],

  "jira_epics": [
    {
      "epic": "",
      "description": "",
      "stories": [
        {
          "title": "",
          "description": "",
          "acceptance_criteria": []
        }
      ]
    }
  ],

  "implementation_plan": {
    "phases": [],
    "recommended_next_steps": []
  },

  "confidence": {
    "score": 0,
    "reason": ""
  }
}

The confidence score must be between 0 and 100.
"""


# ============================================================
# GEMINI ANALYSIS
# ============================================================

def analyze_with_gemini(
    multimodal_payload
):

    if client is None:

        return (
            None,
            "Gemini client is not available. "
            f"{gemini_init_error}"
        )

    if not multimodal_payload:

        return (
            None,
            "No project input was supplied."
        )

    contents = [
        SYSTEM_INSTRUCTION_PROMPT
    ]

    contents.extend(
        multimodal_payload
    )

    # Current stable model.
    # Gemini 3.6 Flash is also currently listed
    # as a stable model by Google.
    model_name = "gemini-3.6-flash"

    last_error = None

    for attempt in range(1, 4):

        try:

            response = (
                client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.15,
                    ),
                )
            )

            response_text = (
                response.text
                if response
                else ""
            )

            if not response_text:
                return (
                    None,
                    "Gemini returned an empty response."
                )

            try:

                data = json.loads(
                    response_text
                )

            except json.JSONDecodeError as exc:

                return (
                    None,
                    "Gemini returned invalid JSON.\n\n"
                    f"JSON error: {exc}\n\n"
                    f"Response:\n{response_text[:5000]}"
                )

            return data, None

        except Exception as exc:

            last_error = (
                f"{type(exc).__name__}: {exc}"
            )

            error_text = str(exc).lower()

            retryable = any(
                keyword in error_text
                for keyword in [
                    "503",
                    "unavailable",
                    "overloaded",
                    "high demand",
                    "429",
                    "resource exhausted",
                ]
            )

            if retryable and attempt < 3:

                time.sleep(
                    attempt * 2
                )

                continue

            return (
                None,
                f"Gemini API error:\n\n"
                f"{last_error}"
            )

    return (
        None,
        last_error or "Unknown Gemini error."
    )


# ============================================================
# MOCK ANALYSIS
# ============================================================

MOCK_ANALYSIS = {

    "executive_summary": {
        "project_name": "Customer Digital Transformation",
        "objective": (
            "Create a centralized digital platform "
            "to improve customer engagement and "
            "operational visibility."
        ),
        "summary": (
            "The project requires a modern digital "
            "solution covering customer-facing "
            "experiences, workflow automation, "
            "reporting and integrations."
        ),
        "business_value": (
            "Improved customer experience, reduced "
            "manual processing and better management "
            "visibility."
        ),
    },

    "scope": {

        "in_scope": [
            "Customer-facing application",
            "Authentication",
            "Workflow management",
            "Reporting dashboard",
            "Notifications",
            "Third-party integrations",
        ],

        "out_of_scope": [
            "Infrastructure procurement",
            "Legacy system replacement",
            "Third-party licensing costs",
        ],

        "functional_modules": [

            {
                "module": "User Management",
                "description": (
                    "Manage users, authentication "
                    "and access permissions."
                ),
                "requirements": [
                    "User login",
                    "Role-based access",
                    "Profile management",
                ],
                "dependencies": [
                    "Identity provider"
                ],
                "acceptance_criteria": [
                    "Authorized users can log in.",
                    "Roles control access.",
                ],
            },

            {
                "module": "Dashboard",
                "description": (
                    "Provide operational and "
                    "business visibility."
                ),
                "requirements": [
                    "Summary metrics",
                    "Filtering",
                    "Status indicators",
                ],
                "dependencies": [
                    "Reporting data"
                ],
                "acceptance_criteria": [
                    "Dashboard displays current data.",
                    "Users can filter results.",
                ],
            },

            {
                "module": "Workflow",
                "description": (
                    "Automate key business processes."
                ),
                "requirements": [
                    "Create requests",
                    "Track status",
                    "Approval workflow",
                ],
                "dependencies": [
                    "Business rules"
                ],
                "acceptance_criteria": [
                    "Requests can be created.",
                    "Approvals can be tracked.",
                ],
            },
        ],
    },

    "assumptions": [
        "Client will provide required API specifications.",
        "Client will provide branding assets.",
        "Required test users will be available.",
    ],

    "open_questions": [
        "What are the final user roles?",
        "What systems require integration?",
        "What are the SLA response requirements?",
        "What are the production deployment requirements?",
    ],

    "risks": [

        {
            "risk": "Integration requirements are not finalized.",
            "severity": "High",
            "impact": (
                "Development estimates may change."
            ),
            "mitigation": (
                "Finalize integration inventory "
                "before development."
            ),
        },

        {
            "risk": "Acceptance criteria are incomplete.",
            "severity": "Medium",
            "impact": (
                "Testing and sign-off may be delayed."
            ),
            "mitigation": (
                "Define measurable acceptance criteria."
            ),
        },

    ],

    "sla_gaps": [

        {
            "area": "Support",
            "gap": "Support response time is not defined.",
            "impact": (
                "Operational expectations may be unclear."
            ),
            "recommendation": (
                "Define support priority levels "
                "and response targets."
            ),
        },

        {
            "area": "Availability",
            "gap": "Production availability target is not specified.",
            "impact": (
                "Infrastructure design cannot be finalized."
            ),
            "recommendation": (
                "Define uptime and recovery targets."
            ),
        },

    ],

    "dependencies": [
        "Client API access",
        "Identity provider configuration",
        "Test data",
        "Branding assets",
    ],

    "deliverables": [
        "Solution design",
        "Application UI",
        "Backend services",
        "Integration services",
        "Testing",
        "Deployment package",
        "Documentation",
    ],

    "jira_epics": [

        {
            "epic": "Authentication & User Management",
            "description": (
                "Implement authentication and authorization."
            ),
            "stories": [

                {
                    "title": "Implement user login",
                    "description": (
                        "Provide secure user authentication."
                    ),
                    "acceptance_criteria": [
                        "User can authenticate.",
                        "Invalid credentials are rejected.",
                    ],
                },

                {
                    "title": "Implement role-based access",
                    "description": (
                        "Restrict functionality according to roles."
                    ),
                    "acceptance_criteria": [
                        "Roles are configurable.",
                        "Unauthorized functions are blocked.",
                    ],
                },
            ],
        },

        {
            "epic": "Dashboard",
            "description": (
                "Build operational dashboard."
            ),
            "stories": [

                {
                    "title": "Create dashboard metrics",
                    "description": (
                        "Display key project metrics."
                    ),
                    "acceptance_criteria": [
                        "Metrics are visible.",
                        "Data is refreshed correctly.",
                    ],
                },
            ],
        },

    ],

    "implementation_plan": {

        "phases": [
            "Discovery and requirement validation",
            "Solution design",
            "UI and backend development",
            "Integration",
            "Testing",
            "User acceptance testing",
            "Production deployment",
        ],

        "recommended_next_steps": [
            "Finalize requirements.",
            "Confirm integrations.",
            "Define SLA targets.",
            "Approve solution architecture.",
            "Confirm delivery milestones.",
        ],
    },

    "confidence": {
        "score": 86,
        "reason": (
            "The major functional areas are identifiable, "
            "but integration and SLA details require "
            "additional confirmation."
        ),
    },
}


# ============================================================
# DOCX REPORT
# ============================================================

def build_docx_report(data):

    document = docx.Document()

    # Title
    title = document.add_heading(
        "Pitch to Project",
        level=0
    )

    document.add_paragraph(
        "Smart Scope Engine – Project Scope Report"
    )

    # --------------------------------------------------------
    # Executive Summary
    # --------------------------------------------------------

    document.add_heading(
        "1. Executive Summary",
        level=1
    )

    summary = data.get(
        "executive_summary",
        {}
    )

    fields = [
        ("Project Name", "project_name"),
        ("Objective", "objective"),
        ("Summary", "summary"),
        ("Business Value", "business_value"),
    ]

    for label, key in fields:

        document.add_heading(
            label,
            level=2
        )

        document.add_paragraph(
            str(summary.get(key, ""))
        )

    # --------------------------------------------------------
    # Scope
    # --------------------------------------------------------

    document.add_heading(
        "2. Scope",
        level=1
    )

    scope = data.get(
        "scope",
        {}
    )

    document.add_heading(
        "In Scope",
        level=2
    )

    for item in scope.get(
        "in_scope",
        []
    ):
        document.add_paragraph(
            str(item),
            style="List Bullet"
        )

    document.add_heading(
        "Out of Scope",
        level=2
    )

    for item in scope.get(
        "out_of_scope",
        []
    ):
        document.add_paragraph(
            str(item),
            style="List Bullet"
        )

    document.add_heading(
        "Functional Modules",
        level=2
    )

    for module in scope.get(
        "functional_modules",
        []
    ):

        document.add_heading(
            module.get(
                "module",
                "Module"
            ),
            level=3
        )

        document.add_paragraph(
            module.get(
                "description",
                ""
            )
        )

        document.add_paragraph(
            "Requirements"
        )

        for item in module.get(
            "requirements",
            []
        ):
            document.add_paragraph(
                str(item),
                style="List Bullet"
            )

        document.add_paragraph(
            "Acceptance Criteria"
        )

        for item in module.get(
            "acceptance_criteria",
            []
        ):
            document.add_paragraph(
                str(item),
                style="List Bullet"
            )

    # --------------------------------------------------------
    # Assumptions
    # --------------------------------------------------------

    document.add_heading(
        "3. Assumptions",
        level=1
    )

    for item in data.get(
        "assumptions",
        []
    ):
        document.add_paragraph(
            str(item),
            style="List Bullet"
        )

    # --------------------------------------------------------
    # Open Questions
    # --------------------------------------------------------

    document.add_heading(
        "4. Open Questions",
        level=1
    )

    for item in data.get(
        "open_questions",
        []
    ):
        document.add_paragraph(
            str(item),
            style="List Bullet"
        )

    # --------------------------------------------------------
    # Risks
    # --------------------------------------------------------

    document.add_heading(
        "5. Risks",
        level=1
    )

    for risk in data.get(
        "risks",
        []
    ):

        document.add_heading(
            risk.get(
                "risk",
                "Risk"
            ),
            level=2
        )

        document.add_paragraph(
            f"Severity: {risk.get('severity', '')}"
        )

        document.add_paragraph(
            f"Impact: {risk.get('impact', '')}"
        )

        document.add_paragraph(
            f"Mitigation: {risk.get('mitigation', '')}"
        )

    # --------------------------------------------------------
    # SLA Gaps
    # --------------------------------------------------------

    document.add_heading(
        "6. SLA Gaps",
        level=1
    )

    for gap in data.get(
        "sla_gaps",
        []
    ):

        document.add_heading(
            gap.get(
                "area",
                "SLA"
            ),
            level=2
        )

        document.add_paragraph(
            f"Gap: {gap.get('gap', '')}"
        )

        document.add_paragraph(
            f"Impact: {gap.get('impact', '')}"
        )

        document.add_paragraph(
            f"Recommendation: "
            f"{gap.get('recommendation', '')}"
        )

    # --------------------------------------------------------
    # Dependencies
    # --------------------------------------------------------

    document.add_heading(
        "7. Dependencies",
        level=1
    )

    for item in data.get(
        "dependencies",
        []
    ):
        document.add_paragraph(
            str(item),
            style="List Bullet"
        )

    # --------------------------------------------------------
    # Deliverables
    # --------------------------------------------------------

    document.add_heading(
        "8. Deliverables",
        level=1
    )

    for item in data.get(
        "deliverables",
        []
    ):
        document.add_paragraph(
            str(item),
            style="List Bullet"
        )

    # --------------------------------------------------------
    # Jira
    # --------------------------------------------------------

    document.add_heading(
        "9. Jira Epics & Stories",
        level=1
    )

    for epic in data.get(
        "jira_epics",
        []
    ):

        document.add_heading(
            epic.get(
                "epic",
                "Epic"
            ),
            level=2
        )

        document.add_paragraph(
            epic.get(
                "description",
                ""
            )
        )

        for story in epic.get(
            "stories",
            []
        ):

            document.add_heading(
                story.get(
                    "title",
                    "Story"
                ),
                level=3
            )

            document.add_paragraph(
                story.get(
                    "description",
                    ""
                )
            )

            document.add_paragraph(
                "Acceptance Criteria"
            )

            for criterion in story.get(
                "acceptance_criteria",
                []
            ):
                document.add_paragraph(
                    str(criterion),
                    style="List Bullet"
                )

    # --------------------------------------------------------
    # Implementation
    # --------------------------------------------------------

    document.add_heading(
        "10. Implementation Plan",
        level=1
    )

    implementation = data.get(
        "implementation_plan",
        {}
    )

    document.add_heading(
        "Phases",
        level=2
    )

    for phase in implementation.get(
        "phases",
        []
    ):
        document.add_paragraph(
            str(phase),
            style="List Number"
        )

    document.add_heading(
        "Recommended Next Steps",
        level=2
    )

    for step in implementation.get(
        "recommended_next_steps",
        []
    ):
        document.add_paragraph(
            str(step),
            style="List Bullet"
        )

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    document.add_heading(
        "11. Confidence",
        level=1
    )

    confidence = data.get(
        "confidence",
        {}
    )

    document.add_paragraph(
        f"Score: "
        f"{confidence.get('score', 0)}/100"
    )

    document.add_paragraph(
        confidence.get(
            "reason",
            ""
        )
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    output = io.BytesIO()

    document.save(output)

    output.seek(0)

    return output.getvalue()


# ============================================================
# HEADER / BANNER
# ============================================================

components.html(
    """
    <div style="
        width:100%;
        overflow:hidden;
        background:
            linear-gradient(
                90deg,
                rgba(0,255,255,.10),
                rgba(120,80,255,.10)
            );
        border-top:1px solid rgba(0,255,255,.15);
        border-bottom:1px solid rgba(0,255,255,.15);
        padding:9px 0;
        white-space:nowrap;
    ">

        <div style="
            display:inline-block;
            padding-left:100%;
            animation:scrollBanner 18s linear infinite;
            color:#9eefff;
            font-size:13px;
            font-weight:700;
            letter-spacing:.5px;
        ">

            🚀 AI-POWERED PROJECT SCOPE ANALYSIS
            &nbsp;&nbsp;&nbsp; • &nbsp;&nbsp;&nbsp;
            📄 READ PROPOSALS
            &nbsp;&nbsp;&nbsp; • &nbsp;&nbsp;&nbsp;
            🎯 IDENTIFY SCOPE
            &nbsp;&nbsp;&nbsp; • &nbsp;&nbsp;&nbsp;
            ⚠️ DETECT RISKS
            &nbsp;&nbsp;&nbsp; • &nbsp;&nbsp;&nbsp;
            📋 GENERATE JIRA STORIES

        </div>
    </div>

    <style>
    @keyframes scrollBanner {
        0% {
            transform:translateX(0);
        }

        100% {
            transform:translateX(-100%);
        }
    }
    </style>
    """,
    height=45,
)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        margin:15px 0 5px 0;
    ">

        <div style="
            font-size:42px;
            font-weight:900;
            background:
                linear-gradient(
                    90deg,
                    #00ffff,
                    #ffffff,
                    #8a6cff
                );
            -webkit-background-clip:text;
            -webkit-text-fill-color:transparent;
        ">
            Pitch to Project
        </div>

        <div style="
            font-size:19px;
            color:#9fb0c3;
            margin-top:5px;
        ">
            Smart Scope Engine
        </div>

        <div style="
            color:#6f8299;
            font-size:13px;
            margin-top:5px;
        ">
            Turn unstructured client inputs into a clear delivery plan
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DEMO MODE
# ============================================================

demo_mode = st.toggle(
    "🎬 Demo Mode (Safe Pitch)",
    value=True,
)

if demo_mode:

    st.info(
        "Demo Mode is ON. "
        "The application will use sample analysis and "
        "will not call Gemini."
    )

else:

    if client is None:

        st.error(
            "Gemini is not available."
        )

        st.code(
            gemini_init_error or
            "Unknown Gemini initialization error.",
            language="text"
        )


# ============================================================
# MAIN COLUMNS
# ============================================================

left_col, right_col = st.columns(
    [0.85, 1.55],
    gap="large"
)


# ============================================================
# LEFT SIDE - INPUT
# ============================================================

with left_col:

    st.markdown(
        "## 📥 Project Inputs"
    )

    st.caption(
        "Upload the available client/project information."
    )

    sow_files = st.file_uploader(
        "📑 Statement of Work",
        type=[
            "docx",
            "pdf",
        ],
        accept_multiple_files=True,
        key="sow_upload",
    )

    proposal_files = st.file_uploader(
        "📄 Proposal / Project Documents",
        type=[
            "docx",
            "pdf",
        ],
        accept_multiple_files=True,
        key="proposal_upload",
    )

    meeting_files = st.file_uploader(
        "📝 Meeting Notes / Transcripts",
        type=[
            "txt",
            "docx",
            "pdf",
        ],
        accept_multiple_files=True,
        key="meeting_upload",
    )

    direct_media_files = st.file_uploader(
        "🎥 Images / Audio / Video",
        type=[
            "png",
            "jpg",
            "jpeg",
            "mp3",
            "wav",
            "mp4",
            "mov",
            "m4a",
        ],
        accept_multiple_files=True,
        key="media_upload",
    )

    loose_notes = st.text_area(
        "✍️ Additional Client Notes",
        height=150,
        placeholder=(
            "Paste client emails, requirements, "
            "meeting notes or additional context..."
        ),
    )

    st.markdown("---")

    generate_clicked = st.button(
        "🚀 GENERATE SMART SCOPE",
        use_container_width=True,
    )


# ============================================================
# GENERATE
# ============================================================

if generate_clicked:

    st.session_state["last_error"] = None

    total_files = (
        len(sow_files or [])
        + len(proposal_files or [])
        + len(meeting_files or [])
        + len(direct_media_files or [])
    )

    has_notes = bool(
        loose_notes
        and loose_notes.strip()
    )

    if (
        total_files == 0
        and not has_notes
    ):

        st.warning(
            "Please upload at least one file "
            "or enter additional client notes."
        )

    else:

        progress_area = st.empty()

        try:

            if demo_mode:

                for step in range(1, 11):

                    render_stylish_progress(
                        step,
                        10,
                        "Analyzing project inputs..."
                    )

                    time.sleep(0.08)

                analysis_data = MOCK_ANALYSIS

            else:

                render_stylish_progress(
                    1,
                    4,
                    "Reading project files..."
                )

                payload = (
                    build_multimodal_payload(
                        sow_files=sow_files,
                        proposal_files=proposal_files,
                        meeting_files=meeting_files,
                        direct_media_files=direct_media_files,
                        loose_notes=loose_notes,
                    )
                )

                render_stylish_progress(
                    2,
                    4,
                    "Preparing AI analysis..."
                )

                analysis_data, error = (
                    analyze_with_gemini(
                        payload
                    )
                )

                if error:

                    raise RuntimeError(
                        error
                    )

                render_stylish_progress(
                    3,
                    4,
                    "Building delivery scope..."
                )

                time.sleep(0.3)

                render_stylish_progress(
                    4,
                    4,
                    "Analysis complete"
                )

            st.session_state[
                "analysis_data"
            ] = analysis_data

            st.session_state[
                "last_error"
            ] = None

            time.sleep(0.3)

            st.rerun()

        except Exception as exc:

            error_message = (
                f"{type(exc).__name__}: {exc}"
            )

            st.session_state[
                "last_error"
            ] = error_message

            progress_area.empty()

            st.error(
                "❌ Analysis failed."
            )

            st.code(
                error_message,
                language="text"
            )


# ============================================================
# RIGHT SIDE - ANALYSIS
# ============================================================

with right_col:

    st.markdown(
        "## 🎯 Smart Scope Analysis"
    )

    analysis_data = st.session_state.get(
        "analysis_data"
    )

    last_error = st.session_state.get(
        "last_error"
    )

    if last_error:

        st.error(
            "The previous analysis failed."
        )

        st.code(
            last_error,
            language="text"
        )

    if not analysis_data:

        st.markdown(
            """
            <div class="scope-card"
                 style="text-align:center; padding:60px 20px;">

                <div style="
                    font-size:55px;
                    margin-bottom:15px;
                ">
                    🧠
                </div>

                <div style="
                    font-size:22px;
                    font-weight:800;
                    color:#00ffff;
                ">
                    Ready for Analysis
                </div>

                <div style="
                    color:#8fa2b8;
                    margin-top:8px;
                ">
                    Upload your project inputs and click
                    <b>GENERATE SMART SCOPE</b>.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        # ----------------------------------------------------
        # Summary metrics
        # ----------------------------------------------------

        summary = analysis_data.get(
            "executive_summary",
            {}
        )

        scope = analysis_data.get(
            "scope",
            {}
        )

        risks = analysis_data.get(
            "risks",
            []
        )

        questions = analysis_data.get(
            "open_questions",
            []
        )

        confidence = analysis_data.get(
            "confidence",
            {}
        )

        functional_modules = scope.get(
            "functional_modules",
            []
        )

        jira_epics = analysis_data.get(
            "jira_epics",
            []
        )

        metric1, metric2, metric3, metric4 = (
            st.columns(4)
        )

        with metric1:
            st.metric(
                "Modules",
                len(functional_modules)
            )

        with metric2:
            st.metric(
                "Risks",
                len(risks)
            )

        with metric3:
            st.metric(
                "Open Questions",
                len(questions)
            )

        with metric4:
            st.metric(
                "Confidence",
                f"{confidence.get('score', 0)}%"
            )

        # ----------------------------------------------------
        # Tabs
        # ----------------------------------------------------

        (
            tab_summary,
            tab_scope,
            tab_risks,
            tab_jira,
        ) = st.tabs(
            [
                "📌 Summary",
                "🎯 Scope",
                "⚠️ Risks & Gaps",
                "📋 Jira",
            ]
        )

        # ----------------------------------------------------
        # SUMMARY TAB
        # ----------------------------------------------------

        with tab_summary:

            st.markdown(
                f"""
                <div class="scope-card">

                    <div class="scope-title">
                        {summary.get(
                            "project_name",
                            "Project"
                        )}
                    </div>

                    <div class="scope-text">
                        <b>Objective:</b><br>
                        {summary.get(
                            "objective",
                            ""
                        )}
                    </div>

                    <br>

                    <div class="scope-text">
                        <b>Summary:</b><br>
                        {summary.get(
                            "summary",
                            ""
                        )}
                    </div>

                    <br>

                    <div class="scope-text">
                        <b>Business Value:</b><br>
                        {summary.get(
                            "business_value",
                            ""
                        )}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            st.subheader(
                "Recommended Next Steps"
            )

            for step in analysis_data.get(
                "implementation_plan",
                {}
            ).get(
                "recommended_next_steps",
                []
            ):

                st.markdown(
                    f"☑️ {step}"
                )

        # ----------------------------------------------------
        # SCOPE TAB
        # ----------------------------------------------------

        with tab_scope:

            col_a, col_b = st.columns(2)

            with col_a:

                st.subheader(
                    "✅ In Scope"
                )

                for item in scope.get(
                    "in_scope",
                    []
                ):
                    st.markdown(
                        f"• {item}"
                    )

            with col_b:

                st.subheader(
                    "🚫 Out of Scope"
                )

                for item in scope.get(
                    "out_of_scope",
                    []
                ):
                    st.markdown(
                        f"• {item}"
                    )

            st.markdown("---")

            st.subheader(
                "Functional Modules"
            )

            for module in functional_modules:

                with st.expander(
                    module.get(
                        "module",
                        "Module"
                    ),
                    expanded=False,
                ):

                    st.write(
                        module.get(
                            "description",
                            ""
                        )
                    )

                    st.markdown(
                        "**Requirements**"
                    )

                    for requirement in module.get(
                        "requirements",
                        []
                    ):
                        st.markdown(
                            f"• {requirement}"
                        )

                    st.markdown(
                        "**Dependencies**"
                    )

                    for dependency in module.get(
                        "dependencies",
                        []
                    ):
                        st.markdown(
                            f"• {dependency}"
                        )

                    st.markdown(
                        "**Acceptance Criteria**"
                    )

                    for criterion in module.get(
                        "acceptance_criteria",
                        []
                    ):
                        st.markdown(
                            f"☑️ {criterion}"
                        )

        # ----------------------------------------------------
        # RISKS TAB
        # ----------------------------------------------------

        with tab_risks:

            st.subheader(
                "⚠️ Project Risks"
            )

            if not risks:

                st.success(
                    "No major risks identified."
                )

            for risk in risks:

                severity = risk.get(
                    "severity",
                    "Medium"
                )

                severity_class = (
                    "risk-high"
                    if severity.lower() == "high"
                    else
                    "risk-low"
                    if severity.lower() == "low"
                    else
                    "risk-medium"
                )

                st.markdown(
                    f"""
                    <div class="
                        scope-card
                        {severity_class}
                    ">

                        <div class="scope-title">
                            {risk.get(
                                "risk",
                                "Risk"
                            )}
                        </div>

                        <div class="scope-text">

                            <b>Severity:</b>
                            {severity}

                            <br><br>

                            <b>Impact:</b><br>
                            {risk.get(
                                "impact",
                                ""
                            )}

                            <br><br>

                            <b>Mitigation:</b><br>
                            {risk.get(
                                "mitigation",
                                ""
                            )}

                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.subheader(
                "Open Questions"
            )

            for question in questions:

                st.markdown(
                    f"❓ {question}"
                )

            st.subheader(
                "SLA Gaps"
            )

            sla_gaps = analysis_data.get(
                "sla_gaps",
                []
            )

            if not sla_gaps:

                st.success(
                    "No SLA gaps identified."
                )

            for gap in sla_gaps:

                st.markdown(
                    f"""
                    <div class="scope-card">

                        <div class="scope-title">
                            {gap.get(
                                "area",
                                "SLA"
                            )}
                        </div>

                        <div class="scope-text">

                            <b>Gap:</b>
                            {gap.get(
                                "gap",
                                ""
                            )}

                            <br><br>

                            <b>Impact:</b>
                            {gap.get(
                                "impact",
                                ""
                            )}

                            <br><br>

                            <b>Recommendation:</b>
                            {gap.get(
                                "recommendation",
                                ""
                            )}

                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # ----------------------------------------------------
        # JIRA TAB
        # ----------------------------------------------------

        with tab_jira:

            st.subheader(
                "📋 Jira Epics & Stories"
            )

            if not jira_epics:

                st.info(
                    "No Jira epics were generated."
                )

            for epic in jira_epics:

                st.markdown(
                    f"""
                    <div class="jira-card">

                        <div style="
                            color:#00ffff;
                            font-size:18px;
                            font-weight:800;
                        ">
                            {epic.get(
                                "epic",
                                "Epic"
                            )}
                        </div>

                        <div style="
                            color:#b7c4d5;
                            margin-top:5px;
                        ">
                            {epic.get(
                                "description",
                                ""
                            )}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                for story in epic.get(
                    "stories",
                    []
                ):

                    with st.expander(
                        f"📝 {story.get('title', 'Story')}"
                    ):

                        st.write(
                            story.get(
                                "description",
                                ""
                            )
                        )

                        st.markdown(
                            "**Acceptance Criteria**"
                        )

                        for criterion in story.get(
                            "acceptance_criteria",
                            []
                        ):
                            st.markdown(
                                f"☑️ {criterion}"
                            )


# ============================================================
# DOWNLOAD REPORT
# ============================================================

if st.session_state.get(
    "analysis_data"
):

    st.markdown("---")

    st.markdown(
        "## 📥 Export"
    )

    report_bytes = build_docx_report(
        st.session_state[
            "analysis_data"
        ]
    )

    st.download_button(
        label="📄 Download Project Scope Report (.docx)",
        data=report_bytes,
        file_name=(
            "Pitch_to_Project_Smart_Scope_Report.docx"
        ),
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        use_container_width=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#65778d;
        font-size:12px;
        padding:30px 0 10px 0;
    ">
        Pitch to Project | Smart Scope Engine
        <br>
        AI-assisted project scope analysis
    </div>
    """,
    unsafe_allow_html=True,
)
