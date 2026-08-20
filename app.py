import os
import json
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import docx
from docx.shared import Inches, Pt, RGBColor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize CustomTkinter Appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- GEMINI SYSTEM PROMPT (STRICT GAP & RISK AUDIT ENGINE) ---
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

# --- DEMO FALLBACK DATA (SAFE PITCH MODE) ---
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


class PitchToProjectApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Pitch To Project — Smart Scope Handover Engine")
        self.geometry("1100x780")
        self.minsize(950, 700)

        self.proposal_files = []
        self.transcript_files = []
        self.media_files = []
        self.current_analysis_data = None

        self._build_ui()

    def _build_ui(self):
        # Header Frame
        header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#1E293B")
        header_frame.pack(fill="x", side="top")

        title_label = ctk.CTkLabel(
            header_frame,
            text="PITCH TO PROJECT",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#38BDF8",
        )
        title_label.pack(side="left", padx=20, pady=12)

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Smart Scope Handover Engine | Project Intelligence Layer",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="#94A3B8",
        )
        subtitle_label.pack(side="left", padx=0, pady=12)

        # Demo Mode Switch
        self.demo_mode_switch = ctk.CTkSwitch(
            header_frame,
            text="Demo Mode (Safe Pitch)",
            font=ctk.CTkFont(size=12, weight="bold"),
            progress_color="#0EA5E9",
        )
        self.demo_mode_switch.pack(side="right", padx=20, pady=12)
        self.demo_mode_switch.select()

        # Main Layout (2 Columns)
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Left Panel - Inputs
        left_panel = ctk.CTkFrame(main_container, width=380, corner_radius=8)
        left_panel.pack(side="left", fill="both", padx=(0, 10), pady=0)

        ctk.CTkLabel(
            left_panel,
            text="1. Intake Documents & Media",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Multi-File Pickers
        self.btn_proposal = ctk.CTkButton(
            left_panel,
            text="📁 Proposals / SOWs (.docx)",
            command=self._select_proposals,
            fg_color="#334155",
            hover_color="#475569",
        )
        self.btn_proposal.pack(fill="x", padx=15, pady=4)

        self.lbl_proposal = ctk.CTkLabel(
            left_panel,
            text="No files selected",
            font=ctk.CTkFont(size=11),
            text_color="#64748B",
            anchor="w",
        )
        self.lbl_proposal.pack(fill="x", padx=15, pady=(0, 6))

        self.btn_transcript = ctk.CTkButton(
            left_panel,
            text="📁 Transcripts / Notes (.txt)",
            command=self._select_transcripts,
            fg_color="#334155",
            hover_color="#475569",
        )
        self.btn_transcript.pack(fill="x", padx=15, pady=4)

        self.lbl_transcript = ctk.CTkLabel(
            left_panel,
            text="No files selected",
            font=ctk.CTkFont(size=11),
            text_color="#64748B",
            anchor="w",
        )
        self.lbl_transcript.pack(fill="x", padx=15, pady=(0, 6))

        self.btn_media = ctk.CTkButton(
            left_panel,
            text="🖼️ Diagrams & Media (.png, .mp4, .mp3)",
            command=self._select_media,
            fg_color="#334155",
            hover_color="#475569",
        )
        self.btn_media.pack(fill="x", padx=15, pady=4)

        self.lbl_media = ctk.CTkLabel(
            left_panel,
            text="No media selected",
            font=ctk.CTkFont(size=11),
            text_color="#64748B",
            anchor="w",
        )
        self.lbl_media.pack(fill="x", padx=15, pady=(0, 6))

        # Raw Text Box
        ctk.CTkLabel(
            left_panel,
            text="Or Paste Loose Client Emails / Notes:",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w", padx=15, pady=(5, 5))

        self.txt_raw_input = ctk.CTkTextbox(
            left_panel, height=140, font=ctk.CTkFont(size=12)
        )
        self.txt_raw_input.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # Progress Bar Indicator (Hidden by default)
        self.progress_bar = ctk.CTkProgressBar(
            left_panel, mode="indeterminate", progress_color="#38BDF8"
        )
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 10))
        self.progress_bar.pack_forget()

        # Generate Button
        self.btn_generate = ctk.CTkButton(
            left_panel,
            text="⚡ GENERATE SMART SCOPE",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#0284C7",
            hover_color="#0369A1",
            height=42,
            command=self._start_generation_thread,
        )
        self.btn_generate.pack(fill="x", padx=15, pady=(0, 15))

        # Right Panel - Output Tabs
        right_panel = ctk.CTkFrame(main_container, corner_radius=8)
        right_panel.pack(side="right", fill="both", expand=True, padx=0, pady=0)

        ctk.CTkLabel(
            right_panel,
            text="2. AI Scope & Handover Analysis",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=15, pady=(15, 5))

        # Tabview
        self.tabview = ctk.CTkTabview(right_panel)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self.tab_scope = self.tabview.add("Extracted Scope")
        self.tab_risks = self.tabview.add("Missing Items & Risks")
        self.tab_jira = self.tabview.add("Jira User Stories")

        # Text Views in Tabs
        self.view_scope = ctk.CTkTextbox(
            self.tab_scope, font=ctk.CTkFont(size=12)
        )
        self.view_scope.pack(fill="both", expand=True, padx=5, pady=5)

        self.view_risks = ctk.CTkTextbox(
            self.tab_risks, font=ctk.CTkFont(size=12)
        )
        self.view_risks.pack(fill="both", expand=True, padx=5, pady=5)

        self.view_jira = ctk.CTkTextbox(
            self.tab_jira, font=ctk.CTkFont(size=12)
        )
        self.view_jira.pack(fill="both", expand=True, padx=5, pady=5)

        # Export Button
        self.btn_export = ctk.CTkButton(
            right_panel,
            text="📄 Export Handover Report (.docx)",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#16A34A",
            hover_color="#15803D",
            height=36,
            command=self._export_word_doc,
        )
        self.btn_export.pack(anchor="e", padx=15, pady=(0, 15))

    # --- MULTI-FILE SELECTION METHODS ---
    def _select_proposals(self):
        paths = filedialog.askopenfilenames(
            title="Select Proposals / SOWs", filetypes=[("Word Files", "*.docx")]
        )
        if paths:
            self.proposal_files = list(paths)
            cnt = len(self.proposal_files)
            txt = f"{cnt} Word file(s) selected" if cnt > 1 else os.path.basename(self.proposal_files[0])
            self.lbl_proposal.configure(text=txt, text_color="#38BDF8")

    def _select_transcripts(self):
        paths = filedialog.askopenfilenames(
            title="Select Transcripts", filetypes=[("Text Files", "*.txt")]
        )
        if paths:
            self.transcript_files = list(paths)
            cnt = len(self.transcript_files)
            txt = f"{cnt} Text file(s) selected" if cnt > 1 else os.path.basename(self.transcript_files[0])
            self.lbl_transcript.configure(text=txt, text_color="#38BDF8")

    def _select_media(self):
        paths = filedialog.askopenfilenames(
            title="Select Diagrams or Audio/Video",
            filetypes=[("Media Files", "*.png *.jpg *.jpeg *.mp4 *.mp3 *.wav")]
        )
        if paths:
            self.media_files = list(paths)
            cnt = len(self.media_files)
            txt = f"{cnt} Media file(s) selected" if cnt > 1 else os.path.basename(self.media_files[0])
            self.lbl_media.configure(text=txt, text_color="#38BDF8")

    # --- PARSING PARAGRAPHS & TABLES IN DOCX ---
    def _read_input_sources(self):
        combined_text = []

        for path in self.proposal_files:
            if os.path.exists(path):
                try:
                    doc = docx.Document(path)
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
                    
                    combined_text.append(
                        f"--- DOCUMENT: {os.path.basename(path)} ---\n" + "\n".join(doc_content)
                    )
                except Exception as e:
                    print(f"Error reading docx ({path}): {e}")

        for path in self.transcript_files:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        t_text = f.read()
                    combined_text.append(
                        f"--- TRANSCRIPT FILE: {os.path.basename(path)} ---\n{t_text}"
                    )
                except Exception as e:
                    print(f"Error reading txt ({path}): {e}")

        pasted_text = self.txt_raw_input.get("1.0", "end").strip()
        if pasted_text:
            combined_text.append(f"--- PASTED NOTES ---\n{pasted_text}")

        return "\n\n".join(combined_text)

    # --- THREAD & LOADING CONTROLLERS ---
    def _start_generation_thread(self):
        self.btn_generate.configure(
            state="disabled", text="⏳ ANALYZING SCOPE...", fg_color="#475569"
        )
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 10))
        self.progress_bar.start()

        thread = threading.Thread(target=self._run_async_handover, daemon=True)
        thread.start()

    def _run_async_handover(self):
        try:
            self._process_handover()
        finally:
            self.after(0, self._stop_loading_animation)

    # --- DOCUMENT VALIDATION HELPER ---
    def _validate_analysis_data(self, data):
        has_scope = bool(data.get("extracted_scope"))
        has_risks = bool(data.get("risks_and_gaps"))
        has_stories = bool(data.get("user_stories"))

        if not (has_scope or has_risks or has_stories):
            messagebox.showwarning(
                "Non-Technical Document",
                "The uploaded document does not contain software requirements or SOW scope.\n\n"
                "Please upload a Software Proposal, SOW, or Technical Requirements document."
            )
            return False
        return True

    def _stop_loading_animation(self):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.btn_generate.configure(
            state="normal", text="⚡ GENERATE SMART SCOPE", fg_color="#0284C7"
        )

        messagebox.showinfo(
            "Completed",
            "✨ Smart scope analysis has been successfully generated!"
        )

    # --- API CALL & MULTIMODAL MEDIA PROCESSING ---
    def _process_handover(self):
        is_demo_mode = self.demo_mode_switch.get() == 1

        if is_demo_mode:
            self.current_analysis_data = DEMO_DATA
            self._render_output_tabs(DEMO_DATA)
            return

        combined_raw = self._read_input_sources()
        if not combined_raw.strip() and not self.media_files:
            messagebox.showwarning(
                "No Input",
                "Please select files or paste text before generating scope.",
            )
            return

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            messagebox.showerror(
                "API Key Missing",
                "GEMINI_API_KEY not found in .env file. Falling back to Demo Mode.",
            )
            self.current_analysis_data = DEMO_DATA
            self._render_output_tabs(DEMO_DATA)
            return

        uploaded_media_handles = []
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)

            for media_path in self.media_files:
                if os.path.exists(media_path):
                    try:
                        print(f"Uploading media file to Gemini API: {os.path.basename(media_path)}...")
                        f_handle = client.files.upload(file=media_path)
                        uploaded_media_handles.append(f_handle)
                    except Exception as upload_err:
                        print(f"Failed to upload media file ({media_path}): {upload_err}")

            available_models = []
            try:
                for m in client.models.list():
                    if hasattr(m, "supported_generation_methods") and "generateContent" in m.supported_generation_methods:
                        name = m.name.replace("models/", "")
                        available_models.append(name)
            except Exception as list_err:
                print(f"Model listing skipped: {list_err}")

            preferred_models = [
                "gemini-3.6-flash",
                "gemini-3.1-pro-preview",
                "gemini-2.5-flash"
            ]

            candidate_models = [m for m in preferred_models if m in available_models]
            if not candidate_models:
                candidate_models = available_models if available_models else ["gemini-3.6-flash"]

            contents_payload = [SYSTEM_PROMPT] + uploaded_media_handles + [f"PROJECT INPUT TEXT AND TABLES:\n{combined_raw}"]

            response = None
            last_error = None

            for model_name in candidate_models:
                try:
                    print(f"Executing scope analysis with model: {model_name}...")
                    
                    response = client.models.generate_content(
                        model=model_name,
                        contents=contents_payload,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        )
                    )

                    if response and response.text:
                        print(f"Successfully generated response using {model_name}!")
                        break
                except Exception as model_err:
                    print(f"Model {model_name} execution failed: {model_err}")
                    last_error = model_err
                    continue

            if not response or not response.text:
                raise last_error or Exception("All candidate Gemini models were unavailable.")

            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text.replace("```json", "", 1).rstrip("`")
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3].strip()

            data = json.loads(clean_text)

            # Validate input matches software SOW requirements
            if not self._validate_analysis_data(data):
                return

            self.current_analysis_data = data
            self._render_output_tabs(data)

        except Exception as e:
            print(f"[API Fallback]: {e}")
            self.current_analysis_data = DEMO_DATA
            self._render_output_tabs(DEMO_DATA)

    # --- TAB RENDERING ---
    def _render_output_tabs(self, data):
        # Render Scope
        self.view_scope.delete("1.0", "end")
        for item in data.get("extracted_scope", []):
            module = item.get("module", "General")
            citation = item.get("source_citation", "Document Reference")
            self.view_scope.insert("end", f"📌 MODULE: {module.upper()}\n")
            self.view_scope.insert("end", f"   Source: {citation}\n")
            for req in item.get("requirements", []):
                self.view_scope.insert("end", f"   • {req}\n")
            self.view_scope.insert("end", "\n")

        # Render Risks & Gaps
        self.view_risks.delete("1.0", "end")
        for risk in data.get("risks_and_gaps", []):
            r_type = risk.get("type", "Gap")
            sev = risk.get("severity", "MEDIUM")
            desc = risk.get("description", "")
            icon = "🔴" if sev == "HIGH" else "🟠"
            self.view_risks.insert(
                "end", f"{icon} [{sev}] {r_type.upper()}\n"
            )
            self.view_risks.insert("end", f"   {desc}\n\n")

        # Render User Stories
        self.view_jira.delete("1.0", "end")
        for story in data.get("user_stories", []):
            title = story.get("title", "User Story")
            as_a = story.get("as_a", "User")
            i_want = story.get("i_want", "Feature").replace("to ", "", 1)
            so_that = story.get("so_that", "Benefit")

            self.view_jira.insert("end", f"🔷 STORY: {title}\n")
            self.view_jira.insert(
                "end",
                f"   As a {as_a}, I want to {i_want} so that {so_that}.\n",
            )
            self.view_jira.insert("end", "   Acceptance Criteria:\n")
            for ac in story.get("acceptance_criteria", []):
                self.view_jira.insert("end", f"     [ ] {ac}\n")
            self.view_jira.insert("end", "\n")

    # --- WORD REPORT EXPORT ---
    def _export_word_doc(self):
        if not self.current_analysis_data:
            messagebox.showwarning(
                "Export Error", "Please generate scope analysis first!"
            )
            return

        try:
            doc = docx.Document()

            for section in doc.sections:
                section.top_margin = Inches(0.8)
                section.bottom_margin = Inches(0.8)
                section.left_margin = Inches(0.8)
                section.right_margin = Inches(0.8)

            # Title Header
            p_title = doc.add_paragraph()
            r_title = p_title.add_run("PITCH TO PROJECT — HANDOVER REPORT")
            r_title.font.size = Pt(22)
            r_title.font.bold = True
            r_title.font.color.rgb = RGBColor(31, 78, 121)

            p_sub = doc.add_paragraph()
            r_sub = p_sub.add_run(
                "Smart Scope Handover Analysis & Gap Audit"
            )
            r_sub.font.italic = True
            r_sub.font.color.rgb = RGBColor(100, 100, 100)

            # Section 1: Scope
            h1 = doc.add_heading(level=1)
            h1.add_run("1. Extracted Functional Scope").font.color.rgb = (
                RGBColor(31, 78, 121)
            )

            for item in self.current_analysis_data.get("extracted_scope", []):
                p = doc.add_paragraph()
                r_mod = p.add_run(f"Module: {item.get('module')}\n")
                r_mod.bold = True
                p.add_run(
                    f"Source: {item.get('source_citation', 'N/A')}\n"
                ).font.italic = True
                for req in item.get("requirements", []):
                    doc.add_paragraph(f"{req}", style="List Bullet")

            # Section 2: Risks
            h2 = doc.add_heading(level=1)
            h2.add_run(
                "2. Missing Items, Gaps & Risk Audit"
            ).font.color.rgb = RGBColor(31, 78, 121)

            for risk in self.current_analysis_data.get("risks_and_gaps", []):
                p = doc.add_paragraph()
                r_r = p.add_run(
                    f"⚠️ [{risk.get('severity')}] {risk.get('type')}\n"
                )
                r_r.bold = True
                r_r.font.color.rgb = RGBColor(192, 57, 43)
                p.add_run(f"{risk.get('description')}")

            # Section 3: Stories
            h3 = doc.add_heading(level=1)
            h3.add_run("3. Jira User Stories").font.color.rgb = RGBColor(
                31, 78, 121)

            for story in self.current_analysis_data.get("user_stories", []):
                p = doc.add_paragraph()
                p.add_run(f"Story: {story.get('title')}\n").bold = True
                clean_want = story.get('i_want', '').replace('to ', '', 1)
                p.add_run(
                    f"As a {story.get('as_a')}, I want to {clean_want} so that {story.get('so_that')}.\n"
                )
                p.add_run("Acceptance Criteria:\n").font.italic = True
                for ac in story.get("acceptance_criteria", []):
                    doc.add_paragraph(f"☐ {ac}", style="List Bullet")

            # Timestamped output file to prevent permission lock errors
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            out_file = f"Pitch_To_Project_Handover_Report_{timestamp}.docx"
            
            doc.save(out_file)
            abs_path = os.path.abspath(out_file)

            messagebox.showinfo(
                "Export Success", f"Word Document created at:\n{abs_path}"
            )
            os.startfile(abs_path)

        except Exception as e:
            messagebox.showerror(
                "Export Error", f"Failed to export Word document:\n{str(e)}"
            )


if __name__ == "__main__":
    app = PitchToProjectApp()
    app.mainloop()