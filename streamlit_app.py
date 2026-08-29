import os
import json
import time
import io
import re

import streamlit as st
import streamlit.components.v1 as components
import docx

from dotenv import load_dotenv
from google import genai
from google.genai import types


# =============================================================================
# 1. LOAD ENVIRONMENT
# =============================================================================

load_dotenv()


# =============================================================================
# 2. PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Pitch to Project | Smart Scope Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# 3. CUSTOM CSS
# =============================================================================

st.markdown(
    """
    <style>

    /* ---------------------------------------------------------------------
       GLOBAL
    --------------------------------------------------------------------- */

    .stApp {
        background:
            radial-gradient(
                circle at top left,
                rgba(6, 182, 212, 0.08),
                transparent 32%
            ),
            radial-gradient(
                circle at top right,
                rgba(59, 130, 246, 0.07),
                transparent 30%
            ),
            #020617;
        color: #e2e8f0;
    }

    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    /* ---------------------------------------------------------------------
       SIDEBAR
    --------------------------------------------------------------------- */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #020617 0%,
                #07111f 100%
            );
        border-right: 1px solid rgba(6, 182, 212, 0.18);
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #06b6d4;
    }

    /* ---------------------------------------------------------------------
       HEADINGS
    --------------------------------------------------------------------- */

    h1, h2, h3 {
        color: #f8fafc;
    }

    /* ---------------------------------------------------------------------
       STREAMLIT BUTTONS
    --------------------------------------------------------------------- */

    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid rgba(6, 182, 212, 0.35);
        background:
            linear-gradient(
                135deg,
                rgba(6, 182, 212, 0.16),
                rgba(59, 130, 246, 0.14)
            );
        color: #e0f2fe;
        font-weight: 800;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #06b6d4;
        box-shadow:
            0 0 20px rgba(6, 182, 212, 0.25);
        transform: translateY(-1px);
    }

    /* ---------------------------------------------------------------------
       FILE UPLOADER
    --------------------------------------------------------------------- */

    [data-testid="stFileUploader"] {
        border-radius: 14px;
    }

    [data-testid="stFileUploaderDropzone"] {
        background:
            rgba(15, 23, 42, 0.72);
        border:
            1px dashed rgba(6, 182, 212, 0.45);
        border-radius: 14px;
    }

    /* ---------------------------------------------------------------------
       METRIC CARDS
    --------------------------------------------------------------------- */

    .metric-card {
        background:
            linear-gradient(
                135deg,
                rgba(15, 23, 42, 0.96),
                rgba(8, 47, 73, 0.55)
            );
        border:
            1px solid rgba(6, 182, 212, 0.22);
        border-radius: 14px;
        padding: 18px;
        min-height: 105px;
        box-shadow:
            0 8px 25px rgba(0, 0, 0, 0.22);
    }

    .metric-number {
        font-size: 1.8rem;
        font-weight: 900;
        color: #06b6d4;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 700;
        margin-top: 3px;
    }

    /* ---------------------------------------------------------------------
       RESULT CARDS
    --------------------------------------------------------------------- */

    .result-card {
        background:
            rgba(15, 23, 42, 0.82);
        border:
            1px solid rgba(148, 163, 184, 0.12);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow:
            0 8px 30px rgba(0, 0, 0, 0.18);
    }

    .result-title {
        color: #06b6d4;
        font-size: 1.05rem;
        font-weight: 900;
        margin-bottom: 10px;
    }

    .result-item {
        padding: 10px 12px;
        margin: 7px 0;
        background: rgba(2, 6, 23, 0.55);
        border-left: 3px solid #06b6d4;
        border-radius: 7px;
        color: #cbd5e1;
        line-height: 1.5;
    }

    /* ---------------------------------------------------------------------
       JIRA
    --------------------------------------------------------------------- */

    .jira-card {
        background:
            linear-gradient(
                135deg,
                rgba(15, 23, 42, 0.96),
                rgba(30, 41, 59, 0.75)
            );
        border:
            1px solid rgba(59, 130, 246, 0.25);
        border-radius: 13px;
        padding: 16px;
        margin-bottom: 12px;
    }

    .jira-key {
        color: #3b82f6;
        font-weight: 900;
        font-size: 0.82rem;
        letter-spacing: 0.5px;
    }

    .jira-title {
        color: #f8fafc;
        font-size: 1rem;
        font-weight: 850;
        margin-top: 4px;
    }

    .jira-meta {
        color: #94a3b8;
        font-size: 0.82rem;
        margin-top: 8px;
    }

    /* ---------------------------------------------------------------------
       WARNING / RISK
    --------------------------------------------------------------------- */

    .risk-card {
        background:
            rgba(120, 53, 15, 0.18);
        border:
            1px solid rgba(245, 158, 11, 0.25);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 10px;
    }

    .conflict-card {
        background:
            rgba(127, 29, 29, 0.16);
        border:
            1px solid rgba(239, 68, 68, 0.28);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 10px;
    }

    /* ---------------------------------------------------------------------
       SCROLLING SMART BANNER
    --------------------------------------------------------------------- */

    .smart-banner-wrapper {
        width: 100%;
        overflow: hidden;
        border:
            1px solid rgba(6, 182, 212, 0.25);
        border-radius: 12px;
        background:
            linear-gradient(
                90deg,
                rgba(6, 182, 212, 0.08),
                rgba(59, 130, 246, 0.08)
            );
        margin-bottom: 18px;
        box-shadow:
            0 0 20px rgba(6, 182, 212, 0.08);
    }

    .smart-banner-track {
        display: flex;
        width: max-content;
        animation:
            smartBannerScroll 18s linear infinite;
    }

    .smart-banner-text {
        display: inline-block;
        padding: 10px 35px;
        white-space: nowrap;
        color: #67e8f9;
        font-size: 0.9rem;
        font-weight: 800;
        letter-spacing: 0.3px;
    }

    @keyframes smartBannerScroll {
        from {
            transform: translateX(0);
        }

        to {
            transform: translateX(-50%);
        }
    }

    /* ---------------------------------------------------------------------
       SMALL TEXT
    --------------------------------------------------------------------- */

    .muted {
        color: #64748b;
        font-size: 0.8rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# 4. SESSION STATE
# =============================================================================

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "source_text" not in st.session_state:
    st.session_state.source_text = ""

if "source_files" not in st.session_state:
    st.session_state.source_files = []

if "raw_response" not in st.session_state:
    st.session_state.raw_response = ""


# =============================================================================
# 5. HELPER FUNCTIONS
# =============================================================================

def clean_text(text):
    """Normalize extracted document text."""
    if not text:
        return ""

    text = text.replace("\x00", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_docx_text(uploaded_file):
    """Extract paragraphs and table content from a DOCX file."""

    try:
        uploaded_file.seek(0)

        document = docx.Document(uploaded_file)

        parts = []

        # Paragraphs
        for paragraph in document.paragraphs:
            text = paragraph.text.strip()

            if text:
                parts.append(text)

        # Tables
        for table_index, table in enumerate(document.tables, start=1):

            parts.append(f"\n[TABLE {table_index}]")

            for row in table.rows:
                cells = []

                for cell in row.cells:
                    cell_text = " ".join(
                        line.strip()
                        for line in cell.text.splitlines()
                        if line.strip()
                    )

                    cells.append(cell_text)

                if any(cells):
                    parts.append(" | ".join(cells))

        return clean_text("\n".join(parts))

    except Exception as exc:
        raise RuntimeError(
            f"Unable to read '{uploaded_file.name}': {exc}"
        )


def safe_list(value):
    """Always return a list."""
    if isinstance(value, list):
        return value

    if value is None:
        return []

    return [value]


def safe_dict(value):
    """Always return a dictionary."""
    if isinstance(value, dict):
        return value

    return {}


def extract_json_from_response(response_text):
    """
    Extract JSON even if Gemini surrounds it with markdown fences
    or explanatory text.
    """

    if not response_text:
        raise ValueError("Gemini returned an empty response.")

    cleaned = response_text.strip()

    # Markdown JSON block
    cleaned = re.sub(
        r"^```json\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"^```\s*",
        "",
        cleaned,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    cleaned = cleaned.strip()

    # Direct JSON
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try extracting the largest JSON object
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1 and end > start:

        candidate = cleaned[start:end + 1]

        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    raise ValueError(
        "Gemini response did not contain valid JSON."
    )


def normalize_analysis(data):
    """
    Ensure all expected Project Intelligence fields exist.
    """

    data = safe_dict(data)

    defaults = {
        "project": {},
        "sources": [],
        "scope": {},
        "requirements": [],
        "commitments": [],
        "deliverables": [],
        "dependencies": [],
        "assumptions": [],
        "risks": [],
        "conflicts": [],
        "gaps": [],
        "changes": [],
        "actions": [],
        "jira_stories": [],
    }

    for key, default in defaults.items():

        if key not in data:
            data[key] = default

        elif isinstance(default, list):
            data[key] = safe_list(data[key])

        elif isinstance(default, dict):
            data[key] = safe_dict(data[key])

    return data


def get_gemini_client():
    """Create Gemini client from environment/secrets."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:

        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            api_key = None

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Add it to your .env file or Streamlit secrets."
        )

    return genai.Client(api_key=api_key)


# =============================================================================
# 6. GEMINI SYSTEM PROMPT
# =============================================================================

SYSTEM_PROMPT = r"""
You are the Smart Scope Handover Engine.

Your job is to convert project-related source documents into a reliable,
structured Project Intelligence Package.

You are NOT a generic summarizer.

You must behave like a senior:
- Business Analyst
- Project Manager
- Solution Analyst
- Delivery Manager
- QA reviewer
- Jira story analyst

Your primary objective is to identify what the project actually requires,
what has been committed, what must be delivered, what is missing, what
conflicts with other information, what creates delivery risk, and what
should become actionable Jira work.

============================================================
CORE PRINCIPLES
============================================================

1. Use ONLY information contained in the supplied source material.

2. NEVER invent requirements, deadlines, technologies, people, budgets,
   integrations, features, or commitments.

3. Clearly distinguish:
   - Explicit information
   - Reasonable interpretation
   - Missing information

4. When information is unclear, say that it is unclear.

5. Preserve important wording from the source when accuracy matters.

6. Detect contradictions between documents.

7. Detect duplicate or overlapping requirements.

8. Identify missing information that could affect delivery.

9. Do not convert every sentence into a requirement.

10. Do not create Jira stories for unsupported assumptions.

============================================================
ANALYSIS AREAS
============================================================

Analyze the documents for:

PROJECT
- project name
- client
- business objective
- project type
- stakeholders
- timeline
- technology
- platform

SOURCES
- filename
- source type
- important evidence

SCOPE
- in scope
- out of scope
- scope boundaries
- scope notes

REQUIREMENTS
- functional requirements
- non-functional requirements
- business requirements
- technical requirements
- editorial/content requirements

COMMITMENTS
- explicit promises
- agreed deliverables
- deadlines
- responsibilities
- client/vendor commitments

DELIVERABLES
- documents
- software/features
- reports
- content
- integrations
- outputs

DEPENDENCIES
- people
- systems
- vendors
- content
- approvals
- external services
- technical dependencies

ASSUMPTIONS
Only identify assumptions that are genuinely implied by the source.
Do not manufacture assumptions.

RISKS
Identify:
- scope risks
- schedule risks
- technical risks
- resource risks
- dependency risks
- quality risks
- communication risks

For each important risk provide:
- risk
- impact
- likelihood
- severity
- mitigation

CONFLICTS
Find contradictions such as:
- different dates
- different quantities
- conflicting requirements
- conflicting technologies
- conflicting responsibilities
- contradictory scope

For each conflict provide:
- issue
- source_a
- source_b
- why_it_conflicts
- recommended_resolution

GAPS
Identify information that is required for successful execution but is
not sufficiently specified.

CHANGES
Identify explicit or implied changes to:
- scope
- requirements
- delivery
- technology
- schedule
- responsibilities

ACTIONS
Identify concrete next actions.

JIRA STORIES
Create Jira-ready user stories ONLY from sufficiently supported
requirements.

Each Jira story should contain:
- key
- title
- user_story
- description
- acceptance_criteria
- priority
- story_points
- dependencies

Use keys such as:
PTP-001
PTP-002
PTP-003

Do not use random project keys.

============================================================
JIRA STORY QUALITY
============================================================

Every story must be independently understandable.

Use:

"As a <role>, I want <capability>, so that <business value>."

Acceptance criteria should be testable.

Do not create vague stories such as:
- "Implement project"
- "Complete requirements"
- "Develop feature"

Instead describe the actual supported capability.

If the source does not provide enough information to create a reliable
story, put the item into gaps/actions instead.

============================================================
CONFIDENCE
============================================================

Where useful, include:
- confidence
- evidence
- source

Use:
HIGH
MEDIUM
LOW

Do not create false precision.

============================================================
OUTPUT FORMAT
============================================================

Return ONLY valid JSON.

Do not use markdown.

Do not use code fences.

Do not include explanatory text outside JSON.

Use exactly this top-level structure:

{
  "project": {},
  "sources": [],
  "scope": {},
  "requirements": [],
  "commitments": [],
  "deliverables": [],
  "dependencies": [],
  "assumptions": [],
  "risks": [],
  "conflicts": [],
  "gaps": [],
  "changes": [],
  "actions": [],
  "jira_stories": []
}

The JSON must be syntactically valid and parseable by Python json.loads().
"""


# =============================================================================
# 7. BUILD GEMINI PROMPT
# =============================================================================

def build_analysis_prompt(source_documents):
    return f"""
Analyze the following project source documents using the Smart Scope
Handover Engine rules.

============================================================
SOURCE DOCUMENTS
============================================================

{source_documents}

============================================================
FINAL INSTRUCTION
============================================================

Return ONLY valid JSON matching the exact schema defined in the system
instructions.

Do not omit important information.

Do not invent information.
"""


# =============================================================================
# 8. GEMINI ANALYSIS
# =============================================================================

def analyze_with_gemini(source_documents):

    client = get_gemini_client()

    prompt = build_analysis_prompt(source_documents)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.1,
            response_mime_type="application/json",
        ),
    )

    response_text = response.text or ""

    st.session_state.raw_response = response_text

    result = extract_json_from_response(response_text)

    return normalize_analysis(result)


# =============================================================================
# 9. PROGRESS BAR
# =============================================================================

def render_progress(placeholder, progress, message):

    progress = max(0, min(100, int(progress)))

    html = f"""
    <div style="
        width: 100%;
        margin-top: 8px;
        margin-bottom: 14px;
        box-sizing: border-box;
    ">

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
                {message}
            </span>

            <span style="
                color: #f59e0b;
                font-weight: 900;
                font-size: 1.05rem;
                text-shadow:
                    0 0 10px rgba(245, 158, 11, 0.5);
                min-width: 45px;
                text-align: right;
            ">
                {progress}%
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
                width: {progress}%;
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

    placeholder.markdown(
        html,
        unsafe_allow_html=True,
    )


# =============================================================================
# 10. DOCX EXPORT
# =============================================================================

def create_docx_report(data):

    document = docx.Document()

    document.add_heading(
        "Smart Scope Handover Report",
        level=0,
    )

    project = safe_dict(data.get("project"))

    if project:

        document.add_heading(
            "Project Overview",
            level=1,
        )

        for key, value in project.items():

            if isinstance(value, (dict, list)):
                value = json.dumps(
                    value,
                    ensure_ascii=False,
                    indent=2,
                )

            document.add_paragraph(
                f"{key.replace('_', ' ').title()}: {value}"
            )

    sections = [
        ("Scope", data.get("scope", {})),
        ("Requirements", data.get("requirements", [])),
        ("Commitments", data.get("commitments", [])),
        ("Deliverables", data.get("deliverables", [])),
        ("Dependencies", data.get("dependencies", [])),
        ("Assumptions", data.get("assumptions", [])),
        ("Risks", data.get("risks", [])),
        ("Conflicts", data.get("conflicts", [])),
        ("Gaps", data.get("gaps", [])),
        ("Changes", data.get("changes", [])),
        ("Actions", data.get("actions", [])),
        ("Jira Stories", data.get("jira_stories", [])),
    ]

    for title, content in sections:

        document.add_heading(
            title,
            level=1,
        )

        if isinstance(content, dict):

            for key, value in content.items():

                document.add_heading(
                    key.replace("_", " ").title(),
                    level=2,
                )

                if isinstance(value, list):

                    for item in value:

                        if isinstance(item, dict):

                            document.add_paragraph(
                                json.dumps(
                                    item,
                                    ensure_ascii=False,
                                    indent=2,
                                )
                            )

                        else:
                            document.add_paragraph(
                                str(item),
                                style="List Bullet",
                            )

                elif isinstance(value, dict):

                    document.add_paragraph(
                        json.dumps(
                            value,
                            ensure_ascii=False,
                            indent=2,
                        )
                    )

                else:
                    document.add_paragraph(str(value))

        elif isinstance(content, list):

            for item in content:

                if isinstance(item, dict):

                    document.add_paragraph(
                        json.dumps(
                            item,
                            ensure_ascii=False,
                            indent=2,
                        )
                    )

                else:

                    document.add_paragraph(
                        str(item),
                        style="List Bullet",
                    )

        else:

            document.add_paragraph(
                str(content)
            )

    output = io.BytesIO()

    document.save(output)

    output.seek(0)

    return output


# =============================================================================
# 11. DISPLAY HELPERS
# =============================================================================

def display_list_section(title, items, icon="•"):

    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-title">
                {icon} {title}
            </div>
        """,
        unsafe_allow_html=True,
    )

    if not items:

        st.markdown(
            '<div class="muted">No items identified.</div>',
            unsafe_allow_html=True,
        )

    else:

        for item in items:

            if isinstance(item, dict):

                # Prefer common readable fields
                primary = (
                    item.get("title")
                    or item.get("name")
                    or item.get("requirement")
                    or item.get("action")
                    or item.get("deliverable")
                    or item.get("risk")
                    or item.get("issue")
                    or item.get("gap")
                )

                if primary:

                    st.markdown(
                        f"""
                        <div class="result-item">
                            <strong>{primary}</strong>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    details = []

                    for key, value in item.items():

                        if key in {
                            "title",
                            "name",
                            "requirement",
                            "action",
                            "deliverable",
                            "risk",
                            "issue",
                            "gap",
                        }:
                            continue

                        if isinstance(value, list):

                            formatted = "<br>".join(
                                f"• {str(v)}"
                                for v in value
                            )

                        elif isinstance(value, dict):

                            formatted = json.dumps(
                                value,
                                ensure_ascii=False,
                                indent=2,
                            )

                        else:
                            formatted = str(value)

                        details.append(
                            f"<strong>{key.replace('_', ' ').title()}:</strong> "
                            f"{formatted}"
                        )

                    if details:

                        st.markdown(
                            '<div class="result-item">'
                            + "<br>".join(details)
                            + "</div>",
                            unsafe_allow_html=True,
                        )

                else:

                    st.markdown(
                        f"""
                        <div class="result-item">
                            {json.dumps(
                                item,
                                ensure_ascii=False,
                                indent=2
                            )}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            else:

                st.markdown(
                    f"""
                    <div class="result-item">
                        {icon} {item}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


def display_jira_stories(stories):

    st.markdown(
        """
        <div class="result-card">
            <div class="result-title">
                🎯 Jira User Stories
            </div>
        """,
        unsafe_allow_html=True,
    )

    if not stories:

        st.markdown(
            '<div class="muted">No Jira stories identified.</div>',
            unsafe_allow_html=True,
        )

    for index, story in enumerate(stories, start=1):

        if not isinstance(story, dict):
            story = {
                "title": str(story)
            }

        key = story.get(
            "key",
            f"PTP-{index:03d}",
        )

        title = story.get(
            "title",
            "Untitled story",
        )

        user_story = story.get(
            "user_story",
            "",
        )

        priority = story.get(
            "priority",
            "Not specified",
        )

        points = story.get(
            "story_points",
            "Not specified",
        )

        description = story.get(
            "description",
            "",
        )

        acceptance = safe_list(
            story.get(
                "acceptance_criteria",
                [],
            )
        )

        st.markdown(
            f"""
            <div class="jira-card">

                <div class="jira-key">
                    {key}
                </div>

                <div class="jira-title">
                    {title}
                </div>

                <div class="jira-meta">
                    Priority: {priority}
                    &nbsp; | &nbsp;
                    Story Points: {points}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if user_story:

            st.markdown(
                f"**User Story:** {user_story}"
            )

        if description:

            st.markdown(
                f"**Description:** {description}"
            )

        if acceptance:

            st.markdown(
                "**Acceptance Criteria:**"
            )

            for criterion in acceptance:

                st.markdown(
                    f"- {criterion}"
                )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# =============================================================================
# 12. HEADER
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


st.markdown(
    """
    <div style="
        margin-bottom: 6px;
    ">
        <div style="
            color: #f8fafc;
            font-size: 2.05rem;
            font-weight: 950;
            letter-spacing: -0.8px;
        ">
            ⚡ Smart Scope Handover Engine
        </div>

        <div style="
            color: #06b6d4;
            font-size: 1rem;
            font-weight: 750;
            margin-top: 3px;
        ">
            Turn project pitches and documents into actionable project intelligence.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# 13. SIDEBAR
# =============================================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            font-size: 1.25rem;
            font-weight: 900;
            color: #06b6d4;
            margin-bottom: 15px;
        ">
            ⚡ Project Intelligence
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="
            color: #94a3b8;
            font-size: 0.85rem;
            line-height: 1.6;
        ">
            Upload project source documents and let the Smart Scope Engine
            identify scope, requirements, commitments, risks, conflicts,
            gaps and Jira-ready stories.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown(
        "### Supported input"
    )

    st.markdown(
        """
        - Word documents (.docx)
        - Multiple documents
        - Paragraphs
        - Tables
        """
    )

    st.divider()

    st.markdown(
        "### Intelligence layers"
    )

    st.markdown(
        """
        ✓ Scope discovery  
        ✓ Requirement extraction  
        ✓ Commitment detection  
        ✓ Deliverable mapping  
        ✓ Dependency analysis  
        ✓ Risk detection  
        ✓ Conflict detection  
        ✓ Gap analysis  
        ✓ Change detection  
        ✓ Action identification  
        ✓ Jira story generation
        """
    )


# =============================================================================
# 14. DOCUMENT UPLOAD
# =============================================================================

st.markdown(
    "### 📄 Project Source Documents"
)

uploaded_files = st.file_uploader(
    "Upload one or more project documents",
    type=["docx"],
    accept_multiple_files=True,
    help="Upload pitch documents, proposals, requirement documents, emails exported to Word, specifications, or other project source material.",
)


# =============================================================================
# 15. FILE PREVIEW
# =============================================================================

if uploaded_files:

    st.markdown(
        f"""
        <div style="
            color: #94a3b8;
            margin: 8px 0 12px 0;
            font-size: 0.88rem;
        ">
            {len(uploaded_files)} document(s) selected for analysis.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander(
        "📂 View selected documents",
        expanded=False,
    ):

        for file in uploaded_files:

            st.markdown(
                f"**📄 {file.name}** — "
                f"{file.size / 1024:.1f} KB"
            )


# =============================================================================
# 16. GENERATE BUTTON
# =============================================================================

generate_clicked = st.button(
    "⚡ GENERATE SMART SCOPE",
    type="primary",
    use_container_width=True,
)


# =============================================================================
# 17. GENERATION PIPELINE
# =============================================================================

if generate_clicked:

    if not uploaded_files:

        st.error(
            "Please upload at least one DOCX project document."
        )

        st.stop()

    progress_placeholder = st.empty()

    try:

        # ---------------------------------------------------------------------
        # STEP 1
        # ---------------------------------------------------------------------

        render_progress(
            progress_placeholder,
            15,
            "📄 Step 1/3: Reading project documents..."
        )

        extracted_documents = []

        total_files = len(uploaded_files)

        for index, uploaded_file in enumerate(
            uploaded_files,
            start=1,
        ):

            text = extract_docx_text(
                uploaded_file
            )

            if text:

                extracted_documents.append(
                    f"""
============================================================
SOURCE FILE: {uploaded_file.name}
============================================================

{text}
"""
                )

            progress = 15 + int(
                (index / total_files) * 20
            )

            render_progress(
                progress_placeholder,
                progress,
                f"📄 Step 1/3: Reading document {index}/{total_files}..."
            )

            time.sleep(0.08)

        if not extracted_documents:

            raise RuntimeError(
                "No readable text was found in the uploaded DOCX files."
            )

        combined_text = "\n\n".join(
            extracted_documents
        )

        st.session_state.source_text = combined_text

        st.session_state.source_files = [
            file.name
            for file in uploaded_files
        ]

        # ---------------------------------------------------------------------
        # STEP 2
        # ---------------------------------------------------------------------

        render_progress(
            progress_placeholder,
            40,
            "🧠 Step 2/3: Building project intelligence..."
        )

        time.sleep(0.25)

        # ---------------------------------------------------------------------
        # STEP 3
        # ---------------------------------------------------------------------

        render_progress(
            progress_placeholder,
            65,
            "🔍 Step 3/3: Auditing scope, conflicts, risks & Jira stories..."
        )

        # Actual Gemini call
        result = analyze_with_gemini(
            combined_text
        )

        # Give the user a visible final auditing state
        render_progress(
            progress_placeholder,
            80,
            "🔍 Step 3/3: Auditing scope, conflicts, risks & Jira stories..."
        )

        time.sleep(0.15)

        render_progress(
            progress_placeholder,
            90,
            "🔍 Step 3/3: Validating project intelligence..."
        )

        time.sleep(0.15)

        st.session_state.analysis = result

        render_progress(
            progress_placeholder,
            100,
            "✅ Step 3/3: Smart Scope analysis completed."
        )

        time.sleep(0.35)

        progress_placeholder.empty()

        st.success(
            "Smart Scope generated successfully."
        )

    except Exception as exc:

        progress_placeholder.empty()

        st.error(
            f"Smart Scope generation failed: {exc}"
        )

        with st.expander(
            "Technical details",
            expanded=False,
        ):
            st.exception(exc)


# =============================================================================
# 18. DISPLAY RESULTS
# =============================================================================

analysis = st.session_state.analysis

if analysis:

    # -------------------------------------------------------------------------
    # METRICS
    # -------------------------------------------------------------------------

    project = safe_dict(
        analysis.get("project")
    )

    requirements = safe_list(
        analysis.get("requirements")
    )

    risks = safe_list(
        analysis.get("risks")
    )

    conflicts = safe_list(
        analysis.get("conflicts")
    )

    gaps = safe_list(
        analysis.get("gaps")
    )

    jira_stories = safe_list(
        analysis.get("jira_stories")
    )

    deliverables = safe_list(
        analysis.get("deliverables")
    )

    st.markdown(
        "## 📊 Project Intelligence Summary"
    )

    metric_columns = st.columns(6)

    metrics = [
        (
            len(requirements),
            "Requirements",
        ),
        (
            len(deliverables),
            "Deliverables",
        ),
        (
            len(risks),
            "Risks",
        ),
        (
            len(conflicts),
            "Conflicts",
        ),
        (
            len(gaps),
            "Gaps",
        ),
        (
            len(jira_stories),
            "Jira Stories",
        ),
    ]

    for column, (number, label) in zip(
        metric_columns,
        metrics,
    ):

        with column:

            st.markdown(
                f"""
                <div class="metric-card">

                    <div class="metric-number">
                        {number}
                    </div>

                    <div class="metric-label">
                        {label}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


    # -------------------------------------------------------------------------
    # PROJECT OVERVIEW
    # -------------------------------------------------------------------------

    if project:

        st.markdown(
            "## 🧭 Project Overview"
        )

        st.markdown(
            '<div class="result-card">',
            unsafe_allow_html=True,
        )

        for key, value in project.items():

            label = key.replace(
                "_",
                " "
            ).title()

            if isinstance(value, (dict, list)):

                value = json.dumps(
                    value,
                    ensure_ascii=False,
                    indent=2,
                )

            st.markdown(
                f"""
                <div class="result-item">
                    <strong>{label}:</strong> {value}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


    # -------------------------------------------------------------------------
    # SCOPE
    # -------------------------------------------------------------------------

    scope = safe_dict(
        analysis.get("scope")
    )

    if scope:

        st.markdown(
            "## 🎯 Scope"
        )

        scope_columns = st.columns(2)

        with scope_columns[0]:

            st.markdown(
                "### ✅ In Scope"
            )

            in_scope = safe_list(
                scope.get(
                    "in_scope",
                    []
                )
            )

            if in_scope:

                for item in in_scope:

                    st.markdown(
                        f"- {item}"
                    )

            else:

                st.info(
                    "No explicit in-scope items identified."
                )

        with scope_columns[1]:

            st.markdown(
                "### 🚫 Out of Scope"
            )

            out_scope = safe_list(
                scope.get(
                    "out_of_scope",
                    []
                )
            )

            if out_scope:

                for item in out_scope:

                    st.markdown(
                        f"- {item}"
                    )

            else:

                st.info(
                    "No explicit out-of-scope items identified."
                )


    # -------------------------------------------------------------------------
    # REQUIREMENTS
    # -------------------------------------------------------------------------

    display_list_section(
        "Requirements",
        requirements,
        "📋",
    )


    # -------------------------------------------------------------------------
    # COMMITMENTS
    # -------------------------------------------------------------------------

    display_list_section(
        "Commitments",
        safe_list(
            analysis.get("commitments")
        ),
        "🤝",
    )


    # -------------------------------------------------------------------------
    # DELIVERABLES
    # -------------------------------------------------------------------------

    display_list_section(
        "Deliverables",
        deliverables,
        "📦",
    )


    # -------------------------------------------------------------------------
    # DEPENDENCIES
    # -------------------------------------------------------------------------

    display_list_section(
        "Dependencies",
        safe_list(
            analysis.get("dependencies")
        ),
        "🔗",
    )


    # -------------------------------------------------------------------------
    # ASSUMPTIONS
    # -------------------------------------------------------------------------

    display_list_section(
        "Assumptions",
        safe_list(
            analysis.get("assumptions")
        ),
        "💭",
    )


    # -------------------------------------------------------------------------
    # RISKS
    # -------------------------------------------------------------------------

    if risks:

        st.markdown(
            "## ⚠️ Risks"
        )

        for risk in risks:

            if isinstance(risk, dict):

                risk_text = risk.get(
                    "risk",
                    risk.get(
                        "title",
                        "Risk identified"
                    )
                )

                impact = risk.get(
                    "impact",
                    ""
                )

                likelihood = risk.get(
                    "likelihood",
                    ""
                )

                severity = risk.get(
                    "severity",
                    ""
                )

                mitigation = risk.get(
                    "mitigation",
                    ""
                )

                st.markdown(
                    f"""
                    <div class="risk-card">

                        <strong>
                            ⚠️ {risk_text}
                        </strong>

                        <br><br>

                        <strong>Impact:</strong>
                        {impact}

                        <br>

                        <strong>Likelihood:</strong>
                        {likelihood}

                        <br>

                        <strong>Severity:</strong>
                        {severity}

                        <br>

                        <strong>Mitigation:</strong>
                        {mitigation}

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            else:

                st.markdown(
                    f"""
                    <div class="risk-card">
                        ⚠️ {risk}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


    # -------------------------------------------------------------------------
    # CONFLICTS
    # -------------------------------------------------------------------------

    if conflicts:

        st.markdown(
            "## 🚨 Conflicts"
        )

        for conflict in conflicts:

            if isinstance(conflict, dict):

                issue = conflict.get(
                    "issue",
                    "Conflict identified"
                )

                source_a = conflict.get(
                    "source_a",
                    ""
                )

                source_b = conflict.get(
                    "source_b",
                    ""
                )

                why = conflict.get(
                    "why_it_conflicts",
                    ""
                )

                resolution = conflict.get(
                    "recommended_resolution",
                    ""
                )

                st.markdown(
                    f"""
                    <div class="conflict-card">

                        <strong>
                            🚨 {issue}
                        </strong>

                        <br><br>

                        <strong>Source A:</strong>
                        {source_a}

                        <br>

                        <strong>Source B:</strong>
                        {source_b}

                        <br>

                        <strong>Why it conflicts:</strong>
                        {why}

                        <br>

                        <strong>Recommended resolution:</strong>
                        {resolution}

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            else:

                st.markdown(
                    f"""
                    <div class="conflict-card">
                        🚨 {conflict}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


    # -------------------------------------------------------------------------
    # GAPS
    # -------------------------------------------------------------------------

    display_list_section(
        "Gaps / Missing Information",
        gaps,
        "🔎",
    )


    # -------------------------------------------------------------------------
    # CHANGES
    # -------------------------------------------------------------------------

    display_list_section(
        "Changes",
        safe_list(
            analysis.get("changes")
        ),
        "🔄",
    )


    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------

    display_list_section(
        "Recommended Actions",
        safe_list(
            analysis.get("actions")
        ),
        "✅",
    )


    # -------------------------------------------------------------------------
    # JIRA
    # -------------------------------------------------------------------------

    st.markdown(
        "## 🎯 Jira Handover"
    )

    display_jira_stories(
        jira_stories
    )


    # -------------------------------------------------------------------------
    # EXPORT
    # -------------------------------------------------------------------------

    st.markdown(
        "## 📤 Export"
    )

    export_columns = st.columns(2)

    json_data = json.dumps(
        analysis,
        ensure_ascii=False,
        indent=2,
    )

    with export_columns[0]:

        st.download_button(
            label="⬇️ Download JSON",
            data=json_data,
            file_name="smart_scope_analysis.json",
            mime="application/json",
            use_container_width=True,
        )

    with export_columns[1]:

        try:

            docx_data = create_docx_report(
                analysis
            )

            st.download_button(
                label="⬇️ Download Word Report",
                data=docx_data,
                file_name="smart_scope_handover_report.docx",
                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.wordprocessingml.document"
                ),
                use_container_width=True,
            )

        except Exception as exc:

            st.error(
                f"Unable to create Word report: {exc}"
            )


    # -------------------------------------------------------------------------
    # SOURCE DOCUMENTS
    # -------------------------------------------------------------------------

    if st.session_state.source_files:

        with st.expander(
            "📚 Source Documents",
            expanded=False,
        ):

            for filename in st.session_state.source_files:

                st.markdown(
                    f"- 📄 {filename}"
                )


    # -------------------------------------------------------------------------
    # RAW JSON
    # -------------------------------------------------------------------------

    with st.expander(
        "🔧 View structured JSON",
        expanded=False,
    ):

        st.json(
            analysis
        )


# =============================================================================
# 19. INITIAL EMPTY STATE
# =============================================================================

else:

    st.markdown(
        """
        <div style="
            margin-top: 25px;
            padding: 30px;
            border-radius: 16px;
            background: rgba(15, 23, 42, 0.65);
            border: 1px solid rgba(6, 182, 212, 0.15);
            text-align: center;
        ">

            <div style="
                font-size: 2.5rem;
                margin-bottom: 10px;
            ">
                ⚡
            </div>

            <div style="
                color: #e2e8f0;
                font-size: 1.15rem;
                font-weight: 850;
            ">
                Ready for Project Intelligence
            </div>

            <div style="
                color: #64748b;
                margin-top: 8px;
                font-size: 0.9rem;
            ">
                Upload your project documents and click
                <strong>GENERATE SMART SCOPE</strong>.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )
