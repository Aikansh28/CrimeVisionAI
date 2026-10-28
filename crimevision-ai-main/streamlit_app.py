"""
CrimeVision AI - Streamlit Cloud Deployment Application
AI-Assisted Forensic Evidence Analysis System
"""

import os
import io
import json
import base64
from datetime import datetime
from dotenv import load_dotenv

import streamlit as st
from PIL import Image as PILImage
from groq import Groq
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import sessionmaker, declarative_base

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

# Load .env if present (check current dir and backend/ dir)
load_dotenv()
_backend_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", ".env")
if os.path.exists(_backend_env):
    load_dotenv(_backend_env)

# --- Page Configuration ---
st.set_page_config(
    page_title="CrimeVision AI - Forensic Evidence Analysis",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Forensic Dark CSS ---
st.markdown("""
<style>
    .reportview-container {
        background: #0f172a;
    }
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 16px;
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: #1e293b;
        border-radius: 6px 6px 0px 0px;
        color: #94a3b8;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: white !important;
    }
    .badge-image {
        background-color: rgba(168, 85, 247, 0.2);
        color: #c084fc;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-audio {
        background-color: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }
    .witness-quote {
        background: rgba(245, 158, 11, 0.1);
        border-left: 3px solid #f59e0b;
        padding: 10px 14px;
        border-radius: 4px;
        color: #fef3c7;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Database Setup (SQLite + SQLAlchemy) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "crimevision_st.db")
DATABASE_URL = f"sqlite:///{DB_PATH.replace(os.sep, '/')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True, autoincrement=True)
    case_number = Column(String, unique=True, nullable=False)
    case_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # "image" or "audio"
    file_path = Column(String, nullable=False)
    analysis_result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    role = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads_st")
os.makedirs(UPLOAD_DIR, exist_ok=True)
REPORT_DIR = os.path.join(BASE_DIR, "reports_st")
os.makedirs(REPORT_DIR, exist_ok=True)


# --- Groq API Helper ---
def get_groq_api_key():
    """Retrieve Groq API key from Streamlit secrets, environment, or session state"""
    # 1. Streamlit secrets
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

    # 2. Environment variable
    env_key = os.getenv("GROQ_API_KEY")
    if env_key and env_key != "your_groq_api_key_here":
        return env_key

    # 3. Session state user input
    return st.session_state.get("user_groq_api_key", "")


def get_groq_client():
    api_key = get_groq_api_key()
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set. Please provide it in the sidebar or in Streamlit Secrets.")
    return Groq(api_key=api_key)


def parse_llm_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return json.loads(cleaned.strip())


def analyze_image_ai(file_path: str) -> dict:
    client = get_groq_client()
    with open(file_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    ext = file_path.lower().split(".")[-1]
    mime_type = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"

    response = client.chat.completions.create(
        model="llama-3.2-11b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Act as a forensic evidence analyst. Analyze this image and identify: "
                            "people visible, possible weapons, important objects, scene description, "
                            "and observations. Return ONLY valid JSON with keys: "
                            "people (list), weapons (list), objects (list), scene (string), "
                            "observations (list). "
                            'Use careful language like "appears to be", "possible", "visible". '
                            "Never identify anyone as a criminal. Never claim certainty."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{image_data}"},
                    },
                ],
            }
        ],
        max_tokens=1024,
    )
    return parse_llm_json(response.choices[0].message.content)


def transcribe_and_analyze_audio_ai(file_path: str) -> dict:
    client = get_groq_client()

    # Step 1: Transcribe
    with open(file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=audio_file,
        )
    transcript = transcription.text

    # Step 2: Analyze transcript
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a forensic analyst. Analyze this transcript and extract: "
                    "key_events (list of dicts with 'time' and 'event'), "
                    "witness_statements (list of strings), important_information (list of strings), "
                    "and summary (string). Return ONLY valid JSON. "
                    'If no time is mentioned, use "Time unavailable". '
                    "Label witness statements clearly."
                ),
            },
            {
                "role": "user",
                "content": f"Analyze this transcript:\n\n{transcript}",
            },
        ],
        max_tokens=1024,
    )
    result = parse_llm_json(response.choices[0].message.content)
    result["transcript"] = transcript
    return result


def ask_case_ai(evidence_data: list, chat_history: list, question: str) -> str:
    client = get_groq_client()
    context = "CASE EVIDENCE:\n\n"
    for i, e in enumerate(evidence_data, 1):
        context += f"Evidence #{i} ({e.get('file_type')} - {e.get('filename')}):\n{json.dumps(e.get('analysis'), indent=2)}\n\n"

    system_prompt = (
        "You are a forensic AI assistant for CrimeVision AI. "
        "Answer questions ONLY based on the evidence provided. "
        "If the evidence does not contain enough information, say: "
        '"The available evidence does not provide enough information to answer this question." '
        "Use cautious language. Never make accusations.\n\n"
        f"{context}"
    )

    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["message"]})
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1024,
    )
    return response.choices[0].message.content


def generate_case_summary_ai(case_info: dict, evidence_data: list) -> dict:
    client = get_groq_client()
    evidence_text = ""
    for i, e in enumerate(evidence_data, 1):
        evidence_text += f"Evidence #{i}:\n{json.dumps(e.get('analysis'), indent=2)}\n\n"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "Generate a forensic case summary with: "
                    "overview (string), key_observations (list), "
                    "evidence_summary (list), uncertainties (list). "
                    "Use cautious language. Return ONLY valid JSON."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Case Information:\n{json.dumps(case_info, indent=2)}\n\n"
                    f"Evidence Analyses:\n{evidence_text}"
                ),
            },
        ],
        max_tokens=1024,
    )
    return parse_llm_json(response.choices[0].message.content)


def generate_pdf_report(case_obj, evidence_items, summary_dict=None) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("T", parent=styles["Title"], fontSize=22, textColor=HexColor("#1e3a8a"), spaceAfter=14)
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14, textColor=HexColor("#1d4ed8"), spaceBefore=12, spaceAfter=6)
    body_style = styles["BodyText"]
    small_style = ParagraphStyle("S", parent=styles["BodyText"], fontSize=8, textColor=HexColor("#64748b"))

    elements = [
        Paragraph("CrimeVision AI — Forensic Analysis Report", title_style),
        Spacer(1, 10),
        Paragraph("Case Information", h2_style),
    ]

    case_data = [
        ["Case Number:", case_obj.case_number],
        ["Case Name:", case_obj.case_name],
        ["Description:", case_obj.description or "N/A"],
        ["Date Created:", str(case_obj.created_at)],
        ["Report Generated:", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")],
    ]
    t = Table(case_data, colWidths=[1.8 * inch, 4.5 * inch])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.extend([t, Spacer(1, 14), Paragraph("Evidence Findings", h2_style)])

    for e in evidence_items:
        elements.append(Paragraph(f"<b>Evidence #{e.id}</b>: {e.filename} ({e.file_type.upper()})", body_style))
        if e.analysis_result:
            try:
                res = json.loads(e.analysis_result)
                if e.file_type == "image":
                    if res.get("scene"):
                        elements.append(Paragraph(f"<i>Scene:</i> {res['scene']}", body_style))
                    for k in ["people", "weapons", "objects", "observations"]:
                        if res.get(k):
                            elements.append(Paragraph(f"<i>{k.capitalize()}:</i>", body_style))
                            for item in res[k]:
                                elements.append(Paragraph(f"  • {item}", body_style))
                elif e.file_type == "audio":
                    if res.get("transcript"):
                        elements.append(Paragraph(f"<i>Transcript:</i> {res['transcript']}", body_style))
                    if res.get("witness_statements"):
                        elements.append(Paragraph("<i>Witness Statements:</i>", body_style))
                        for ws in res["witness_statements"]:
                            elements.append(Paragraph(f"  • {ws}", body_style))
            except Exception:
                elements.append(Paragraph("Raw analysis stored.", body_style))
        else:
            elements.append(Paragraph("Status: Not yet analyzed.", body_style))
        elements.append(Spacer(1, 8))

    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Disclaimer", h2_style))
    elements.append(Paragraph(
        "CrimeVision AI is an academic demonstration system. Findings are AI-generated observations "
        "and should never be treated as legal or definitive forensic evidence. Human review is required.",
        small_style
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


# --- Database Helpers ---
def load_demo_data(case_id: int):
    db = SessionLocal()
    try:
        # Fictional demo image
        img_analysis = {
            "people": [
                "One individual appears to be standing near the doorway",
                "A second individual appears to be seated at a table",
            ],
            "weapons": ["No weapons visibly identified in the scene"],
            "objects": ["Wooden table with scattered papers", "Open laptop computer", "Two coffee cups", "Backpack near chair"],
            "scene": "Dimly lit indoor room, residential living area with signs of recent disturbance.",
            "observations": [
                "Room appears recently occupied",
                "Papers on table appear disorganized",
                "Timestamp suggests approximately 9:45 PM",
                "[DEMO / FICTIONAL DATA]",
            ],
        }
        e1 = Evidence(
            case_id=case_id,
            filename="demo_room_photo.jpg",
            file_type="image",
            file_path="demo_room_photo.jpg",
            analysis_result=json.dumps(img_analysis),
        )
        db.add(e1)

        # Fictional demo audio
        aud_analysis = {
            "transcript": (
                "At approximately 10:15 PM, I heard loud voices coming from the apartment next door. "
                "Two people were arguing. Around 10:20 PM, I heard what sounded like furniture moving. "
                "Then a door slammed shut at 10:25 PM followed by footsteps running down the stairs."
            ),
            "key_events": [
                {"time": "10:15 PM", "event": "Loud voices heard from adjacent apartment"},
                {"time": "10:20 PM", "event": "Sounds of furniture disturbance"},
                {"time": "10:25 PM", "event": "Door slammed and hurried footsteps heard"},
            ],
            "witness_statements": [
                "Witness reports hearing two individuals arguing intensely",
                "Witness describes hearing furniture being moved violently around 10:20 PM",
                "Witness observed footsteps running down the stairs following a door slam",
            ],
            "important_information": [
                "Incident duration: approximately 10 minutes",
                "Two individuals involved",
                "Disturbance concluded at 10:25 PM",
            ],
            "summary": "Witness heard a 10-minute domestic disturbance ending with an exit at 10:25 PM.",
            "_demo_note": "DEMO / FICTIONAL DATA",
        }
        e2 = Evidence(
            case_id=case_id,
            filename="demo_witness_audio.mp3",
            file_type="audio",
            file_path="demo_witness_audio.mp3",
            analysis_result=json.dumps(aud_analysis),
        )
        db.add(e2)

        # Demo chats
        db.add(ChatMessage(case_id=case_id, role="user", message="Were any weapons visible in the scene?"))
        db.add(ChatMessage(case_id=case_id, role="assistant", message="Based on the analyzed image evidence, no weapons were visibly identified in the scene."))
        db.add(ChatMessage(case_id=case_id, role="user", message="What did the witness report hearing?"))
        db.add(ChatMessage(case_id=case_id, role="assistant", message="The witness reported hearing two people arguing at ~10:15 PM, furniture moving at ~10:20 PM, and a door slam with running footsteps at ~10:25 PM."))

        db.commit()
    finally:
        db.close()


# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("### 🔍 CrimeVision AI")
    st.caption("Forensic Evidence Analysis • BTech Project")
    st.divider()

    # API Key Configuration
    key = get_groq_api_key()
    if not key:
        st.warning("⚠️ Groq API Key required")
        user_key = st.text_input("Enter Groq API Key", type="password", key="user_groq_api_key", help="Get a free key at console.groq.com")
        if user_key:
            st.rerun()
    else:
        st.success("🟢 Groq API Connected")

    st.divider()

    # Case Selection
    db = SessionLocal()
    cases = db.query(Case).order_by(Case.created_at.desc()).all()

    case_options = {f"{c.case_number} — {c.case_name}": c.id for c in cases}

    if not case_options:
        st.info("No cases exist yet. Create a case below or load demo data.")
        current_case_id = None
    else:
        selected_label = st.selectbox("Select Case", list(case_options.keys()))
        current_case_id = case_options[selected_label]

    # Create Case Expander
    with st.expander("➕ Create New Case"):
        new_name = st.text_input("Case Name", placeholder="e.g. Downtown Incident")
        new_desc = st.text_area("Description", placeholder="Case details...")
        if st.button("Create Case", use_container_width=True):
            if new_name.strip():
                year = datetime.utcnow().year
                count = db.query(Case).count()
                c_num = f"CV-{year}-{count + 1:03d}"
                new_case = Case(case_number=c_num, case_name=new_name.strip(), description=new_desc.strip())
                db.add(new_case)
                db.commit()
                st.success(f"Case {c_num} created!")
                st.rerun()
            else:
                st.error("Case name required.")

    # Load Demo Case Button
    if st.button("⚡ Load Demo Case (Fictional)", use_container_width=True, type="secondary"):
        year = datetime.utcnow().year
        count = db.query(Case).count()
        c_num = f"CV-{year}-{count + 1:03d}"
        demo_case = Case(
            case_number=c_num,
            case_name="Demo Incident — Apartment 4B",
            description="Fictional forensic investigation case for demonstration purposes.",
        )
        db.add(demo_case)
        db.commit()
        db.refresh(demo_case)
        load_demo_data(demo_case.id)
        st.success("Demo Case Loaded Successfully!")
        st.rerun()

    db.close()

# ==========================================
# MAIN INTERFACE
# ==========================================
if not current_case_id:
    st.title("🔍 CrimeVision AI")
    st.subheader("AI-Assisted Forensic Evidence Analysis")
    st.write("Welcome to CrimeVision AI. To get started, please **create a new case** or click **⚡ Load Demo Case** in the sidebar.")
    st.stop()

db = SessionLocal()
active_case = db.query(Case).filter(Case.id == current_case_id).first()
evidence_items = db.query(Evidence).filter(Evidence.case_id == current_case_id).order_by(Evidence.created_at.desc()).all()

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.caption(f"CASE ID: {active_case.case_number}")
    st.title(active_case.case_name)
    if active_case.description:
        st.write(active_case.description)
with col2:
    st.metric("Total Evidence", len(evidence_items))

# Tabs
tab_evidence, tab_timeline, tab_summary, tab_chat, tab_report = st.tabs([
    "📁 Evidence", "⏱️ Timeline", "🧠 AI Summary", "💬 AI Chat", "📄 PDF Report"
])

# ------------------------------------------
# TAB 1: EVIDENCE
# ------------------------------------------
with tab_evidence:
    st.subheader("Upload Evidence Files")
    uploaded_files = st.file_uploader(
        "Upload Image (JPG, PNG) or Audio (MP3, WAV)",
        type=["jpg", "jpeg", "png", "mp3", "wav"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        for uf in uploaded_files:
            ext = uf.name.lower().split(".")[-1]
            f_type = "image" if ext in ["jpg", "jpeg", "png"] else "audio"
            save_path = os.path.join(UPLOAD_DIR, f"{active_case.id}_{uf.name}")
            with open(save_path, "wb") as f:
                f.write(uf.getbuffer())

            # Check if already added
            existing = db.query(Evidence).filter(Evidence.case_id == active_case.id, Evidence.filename == uf.name).first()
            if not existing:
                new_e = Evidence(case_id=active_case.id, filename=uf.name, file_type=f_type, file_path=save_path)
                db.add(new_e)
                db.commit()
                st.success(f"Uploaded: {uf.name}")
                st.rerun()

    st.divider()
    st.subheader("Case Evidence Dossier")

    if not evidence_items:
        st.info("No evidence uploaded for this case yet.")
    else:
        for item in evidence_items:
            with st.container(border=True):
                head_col1, head_col2 = st.columns([3, 1])
                with head_col1:
                    badge_class = "badge-image" if item.file_type == "image" else "badge-audio"
                    st.markdown(f"**{item.filename}** <span class='{badge_class}'>{item.file_type.upper()}</span>", unsafe_allow_html=True)
                    st.caption(f"Uploaded: {item.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                with head_col2:
                    if st.button(f"⚡ Analyze #{item.id}", key=f"btn_an_{item.id}", use_container_width=True):
                        with st.spinner("Analyzing with Groq AI..."):
                            try:
                                if item.file_type == "image":
                                    analysis = analyze_image_ai(item.file_path)
                                else:
                                    analysis = transcribe_and_analyze_audio_ai(item.file_path)
                                item.analysis_result = json.dumps(analysis)
                                db.commit()
                                st.success("Analysis Complete!")
                                st.rerun()
                            except Exception as err:
                                st.error(f"Analysis error: {str(err)}")

                # Findings Display
                if item.analysis_result:
                    res = json.loads(item.analysis_result)
                    st.markdown("##### Findings:")
                    if item.file_type == "image":
                        fcol1, fcol2 = st.columns(2)
                        with fcol1:
                            if res.get("scene"):
                                st.write("**Scene:**", res["scene"])
                            if res.get("people"):
                                st.write("**People Visible:**")
                                for p in res["people"]:
                                    st.write(f"- {p}")
                        with fcol2:
                            if res.get("weapons"):
                                st.write("**Possible Weapons:**")
                                for w in res["weapons"]:
                                    st.write(f"- ⚠️ {w}")
                            if res.get("objects"):
                                st.write("**Objects Identified:**", ", ".join(res["objects"]))
                        if res.get("observations"):
                            st.write("**Observations:**")
                            for obs in res["observations"]:
                                st.write(f"- {obs}")
                    elif item.file_type == "audio":
                        if res.get("transcript"):
                            st.write("**Transcript:**")
                            st.text_area("Full Audio Transcript", res["transcript"], height=90, key=f"tr_{item.id}", disabled=True)
                        if res.get("witness_statements"):
                            st.write("**Witness Statements:**")
                            for ws in res["witness_statements"]:
                                st.markdown(f"<div class='witness-quote'>“{ws}”</div>", unsafe_allow_html=True)
                        if res.get("key_events"):
                            st.write("**Key Events:**")
                            for ke in res["key_events"]:
                                if isinstance(ke, dict):
                                    st.write(f"- **[{ke.get('time', 'N/A')}]** {ke.get('event', '')}")
                                else:
                                    st.write(f"- {ke}")

# ------------------------------------------
# TAB 2: TIMELINE
# ------------------------------------------
with tab_timeline:
    st.subheader("Chronological Event Timeline")
    timeline_entries = []

    for item in evidence_items:
        if item.analysis_result:
            try:
                res = json.loads(item.analysis_result)
                if item.file_type == "image":
                    for obs in res.get("observations", []):
                        t_str = "Time unavailable"
                        for kw in ["pm", "am", "o'clock", "timestamp", "approximately"]:
                            if kw in obs.lower():
                                t_str = obs
                                break
                        timeline_entries.append({"time": t_str, "event": obs, "source": "Image", "id": item.id})
                elif item.file_type == "audio":
                    for ke in res.get("key_events", []):
                        if isinstance(ke, dict):
                            timeline_entries.append({"time": ke.get("time", "Time unavailable"), "event": ke.get("event", "Event"), "source": "Audio", "id": item.id})
            except Exception:
                pass

    if not timeline_entries:
        st.info("No timeline events extracted yet. Upload and analyze evidence to generate a chronological timeline.")
    else:
        for idx, entry in enumerate(timeline_entries, 1):
            badge = "badge-image" if entry["source"] == "Image" else "badge-audio"
            with st.container(border=True):
                st.markdown(f"**⏱️ {entry['time']}** &nbsp; <span class='{badge}'>{entry['source']}</span>", unsafe_allow_html=True)
                st.write(entry["event"])

# ------------------------------------------
# TAB 3: AI CASE SUMMARY
# ------------------------------------------
with tab_summary:
    st.subheader("AI Case Summary & Forensic Synthesis")
    if st.button("🧠 Generate Comprehensive AI Summary", type="primary", use_container_width=False):
        analyzed_data = [
            {"filename": e.filename, "file_type": e.file_type, "analysis": json.loads(e.analysis_result)}
            for e in evidence_items if e.analysis_result
        ]
        if not analyzed_data:
            st.warning("Please analyze at least one piece of evidence first.")
        else:
            with st.spinner("Synthesizing forensic evidence with Groq AI..."):
                try:
                    c_info = {"case_number": active_case.case_number, "case_name": active_case.case_name, "description": active_case.description}
                    summary = generate_case_summary_ai(c_info, analyzed_data)
                    st.session_state[f"summary_{active_case.id}"] = summary
                except Exception as e:
                    st.error(f"Failed to generate summary: {str(e)}")

    cached_summary = st.session_state.get(f"summary_{active_case.id}")
    if cached_summary:
        if cached_summary.get("overview"):
            with st.container(border=True):
                st.markdown("#### Overview")
                st.write(cached_summary["overview"])
        if cached_summary.get("key_observations"):
            with st.container(border=True):
                st.markdown("#### Key Observations")
                for obs in cached_summary["key_observations"]:
                    st.write(f"- {obs}")
        if cached_summary.get("evidence_summary"):
            with st.container(border=True):
                st.markdown("#### Evidence Synthesis")
                for es in cached_summary["evidence_summary"]:
                    st.write(f"- {es}")
        if cached_summary.get("uncertainties"):
            with st.container(border=True):
                st.markdown("#### Uncertainties & Caveats")
                for u in cached_summary["uncertainties"]:
                    st.write(f"- ⚠️ {u}")

# ------------------------------------------
# TAB 4: AI CHAT
# ------------------------------------------
with tab_chat:
    st.subheader("Forensic AI Assistant")
    st.caption("Ask questions strictly constrained to the evidence gathered in this case.")

    chat_history = db.query(ChatMessage).filter(ChatMessage.case_id == active_case.id).order_by(ChatMessage.created_at).all()
    for cm in chat_history:
        with st.chat_message(cm.role):
            st.write(cm.message)

    user_query = st.chat_input("Ask a forensic question (e.g. 'What objects were found?' or 'What did the witness state?')")
    if user_query:
        # Display user message
        with st.chat_message("user"):
            st.write(user_query)

        # Save user message
        db.add(ChatMessage(case_id=active_case.id, role="user", message=user_query))
        db.commit()

        # Build context
        analyzed_data = [
            {"filename": e.filename, "file_type": e.file_type, "analysis": json.loads(e.analysis_result)}
            for e in evidence_items if e.analysis_result
        ]
        history_list = [{"role": m.role, "message": m.message} for m in chat_history]

        with st.chat_message("assistant"):
            with st.spinner("Analyzing evidence..."):
                try:
                    ai_reply = ask_case_ai(analyzed_data, history_list, user_query)
                except Exception as e:
                    ai_reply = f"Error: {str(e)}"
                st.write(ai_reply)

        # Save assistant reply
        db.add(ChatMessage(case_id=active_case.id, role="assistant", message=ai_reply))
        db.commit()

# ------------------------------------------
# TAB 5: PDF REPORT
# ------------------------------------------
with tab_report:
    st.subheader("Forensic Dossier PDF Generation")
    st.write("Generate and download an official ReportLab forensic analysis dossier containing all metadata, evidence findings, and disclaimers.")

    if st.button("📄 Build PDF Report", type="primary"):
        pdf_bytes = generate_pdf_report(active_case, evidence_items)
        st.download_button(
            label="⬇️ Download Official Forensic PDF",
            data=pdf_bytes,
            file_name=f"CrimeVision_{active_case.case_number}.pdf",
            mime="application/pdf",
        )
        st.success("PDF Dossier Generated Successfully!")

db.close()
