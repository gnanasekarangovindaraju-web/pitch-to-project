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

# Initialize Gemini Client (Uses GEMINI_API_KEY from st.secrets)
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
    """Calls Gemini API (gemini-3.6-flash) to perform live scope analysis."""
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
        cleaned_json = response.text.strip().replace("json", "").replace("