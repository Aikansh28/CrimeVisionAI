"""
report.py - PDF report generation route for CrimeVision AI
Generates downloadable forensic analysis reports using ReportLab.
"""

import os
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from app.database import get_db
from app.models import Case, Evidence
from app.services import groq_service

router = APIRouter(prefix="/api", tags=["Report"])

# Base and Report directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORT_DIR = os.path.join(BASE_DIR, "reports")


@router.get("/cases/{case_id}/report")
def generate_report(case_id: int, db: Session = Depends(get_db)):
    """
    Generate a PDF forensic analysis report for a case.
    Includes case info, evidence analyses, timeline, and AI summary.
    Returns the PDF as a downloadable file.
    """
    # Check that the case exists
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Ensure the reports directory exists
    os.makedirs(REPORT_DIR, exist_ok=True)

    # Build filename and path
    report_filename = f"report_{case.case_number}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    report_path = os.path.join(REPORT_DIR, report_filename)

    # Gather evidence data
    evidence_list = db.query(Evidence).filter(Evidence.case_id == case_id).all()
    evidence_analyses = []
    for e in evidence_list:
        entry = {
            "id": e.id,
            "filename": e.filename,
            "file_type": e.file_type,
            "analysis": None,
        }
        if e.analysis_result:
            try:
                entry["analysis"] = json.loads(e.analysis_result)
            except json.JSONDecodeError:
                pass
        evidence_analyses.append(entry)

    # Generate AI summary
    case_info = {
        "case_number": case.case_number,
        "case_name": case.case_name,
        "description": case.description,
        "created_at": str(case.created_at),
    }
    analyses_for_summary = [
        {"evidence_id": ea["id"], "filename": ea["filename"], "file_type": ea["file_type"], "analysis": ea["analysis"]}
        for ea in evidence_analyses if ea["analysis"]
    ]
    ai_summary = groq_service.generate_summary(case_info, analyses_for_summary) if analyses_for_summary else {}

    # --- Build the PDF ---
    doc = SimpleDocTemplate(report_path, pagesize=A4,
                            topMargin=0.75 * inch, bottomMargin=0.75 * inch)

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Title"],
        fontSize=22, textColor=HexColor("#1a237e"), spaceAfter=20,
    )
    heading_style = ParagraphStyle(
        "CustomHeading", parent=styles["Heading2"],
        fontSize=14, textColor=HexColor("#283593"), spaceBefore=16, spaceAfter=8,
    )
    body_style = styles["BodyText"]
    small_style = ParagraphStyle(
        "SmallText", parent=styles["BodyText"],
        fontSize=8, textColor=HexColor("#666666"),
    )

    elements = []

    # --- Title ---
    elements.append(Paragraph("CrimeVision AI - Forensic Analysis Report", title_style))
    elements.append(Spacer(1, 12))

    # --- Case Information ---
    elements.append(Paragraph("Case Information", heading_style))
    case_data = [
        ["Case Number:", case.case_number],
        ["Case Name:", case.case_name],
        ["Description:", case.description or "N/A"],
        ["Created:", str(case.created_at)],
        ["Report Generated:", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")],
    ]
    case_table = Table(case_data, colWidths=[1.8 * inch, 4.5 * inch])
    case_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(case_table)
    elements.append(Spacer(1, 16))

    # --- Evidence List ---
    elements.append(Paragraph("Evidence Files", heading_style))
    if not evidence_analyses:
        elements.append(Paragraph("No evidence files uploaded.", body_style))
    else:
        for ea in evidence_analyses:
            elements.append(Paragraph(
                f"<b>Evidence #{ea['id']}</b> — {ea['filename']} ({ea['file_type'].upper()})",
                body_style,
            ))

            if ea["analysis"]:
                analysis = ea["analysis"]

                if ea["file_type"] == "image":
                    # Show image analysis findings
                    for key in ["people", "weapons", "objects"]:
                        items = analysis.get(key, [])
                        if items:
                            elements.append(Paragraph(f"<i>{key.capitalize()}:</i>", body_style))
                            for item in items:
                                elements.append(Paragraph(f"  • {item}", body_style))

                    scene = analysis.get("scene", "")
                    if scene:
                        elements.append(Paragraph(f"<i>Scene:</i> {scene}", body_style))

                    observations = analysis.get("observations", [])
                    if observations:
                        elements.append(Paragraph("<i>Observations:</i>", body_style))
                        for obs in observations:
                            elements.append(Paragraph(f"  • {obs}", body_style))

                elif ea["file_type"] == "audio":
                    # Show transcript and key information
                    transcript = analysis.get("transcript", "")
                    if transcript:
                        elements.append(Paragraph(f"<i>Transcript:</i> {transcript}", body_style))

                    key_events = analysis.get("key_events", [])
                    if key_events:
                        elements.append(Paragraph("<i>Key Events:</i>", body_style))
                        for event in key_events:
                            if isinstance(event, dict):
                                elements.append(Paragraph(
                                    f"  • [{event.get('time', 'N/A')}] {event.get('event', '')}",
                                    body_style,
                                ))
                            else:
                                elements.append(Paragraph(f"  • {event}", body_style))

                    important = analysis.get("important_information", [])
                    if important:
                        elements.append(Paragraph("<i>Important Information:</i>", body_style))
                        for info in important:
                            elements.append(Paragraph(f"  • {info}", body_style))
            else:
                elements.append(Paragraph("  (Not yet analyzed)", body_style))

            elements.append(Spacer(1, 10))

    # --- Timeline ---
    elements.append(Paragraph("Timeline", heading_style))
    timeline_entries = _build_timeline(evidence_analyses)
    if timeline_entries:
        for entry in timeline_entries:
            elements.append(Paragraph(
                f"<b>[{entry['time']}]</b> {entry['event']} <i>({entry['source']})</i>",
                body_style,
            ))
    else:
        elements.append(Paragraph("No timeline data available.", body_style))
    elements.append(Spacer(1, 12))

    # --- AI Case Summary ---
    elements.append(Paragraph("AI Case Summary", heading_style))
    if ai_summary and "error" not in ai_summary:
        overview = ai_summary.get("overview", "")
        if overview:
            elements.append(Paragraph(f"<b>Overview:</b> {overview}", body_style))

        key_obs = ai_summary.get("key_observations", [])
        if key_obs:
            elements.append(Paragraph("<b>Key Observations:</b>", body_style))
            for obs in key_obs:
                elements.append(Paragraph(f"  • {obs}", body_style))

        evidence_summary = ai_summary.get("evidence_summary", [])
        if evidence_summary:
            elements.append(Paragraph("<b>Evidence Summary:</b>", body_style))
            for es in evidence_summary:
                elements.append(Paragraph(f"  • {es}", body_style))

        uncertainties = ai_summary.get("uncertainties", [])
        if uncertainties:
            elements.append(Paragraph("<b>Uncertainties:</b>", body_style))
            for u in uncertainties:
                elements.append(Paragraph(f"  • {u}", body_style))
    else:
        error_msg = ai_summary.get("error", "Summary could not be generated.") if ai_summary else "No analyzed evidence available."
        elements.append(Paragraph(error_msg, body_style))

    elements.append(Spacer(1, 20))

    # --- Disclaimer ---
    elements.append(Paragraph("Disclaimer", heading_style))
    disclaimer_text = (
        "This report was generated by CrimeVision AI, an artificial intelligence-assisted "
        "forensic analysis tool. The findings, observations, and conclusions presented in "
        "this report are generated by AI models and should NOT be considered as definitive "
        "forensic evidence. All AI-generated analysis uses cautious language and does not "
        "make accusations or claims of certainty. This report is intended to assist human "
        "investigators and should be reviewed by qualified forensic professionals before "
        "being used in any legal or investigative capacity. AI analysis may contain errors, "
        "misinterpretations, or miss important details."
    )
    elements.append(Paragraph(disclaimer_text, small_style))

    # Build the PDF
    doc.build(elements)

    # Return the PDF as a downloadable file
    return FileResponse(
        path=report_path,
        filename=report_filename,
        media_type="application/pdf",
    )


def _build_timeline(evidence_analyses: list) -> list:
    """
    Helper to build timeline entries from evidence analyses.
    Same logic as the timeline route, extracted here for reuse.
    """
    timeline = []

    for ea in evidence_analyses:
        if not ea.get("analysis"):
            continue

        analysis = ea["analysis"]
        file_type = ea["file_type"]

        if file_type == "image":
            observations = analysis.get("observations", [])
            for obs in observations:
                time_str = "Time unavailable"
                obs_lower = obs.lower()
                for keyword in ["pm", "am", "o'clock", "timestamp"]:
                    if keyword in obs_lower:
                        time_str = obs
                        break
                timeline.append({
                    "time": time_str,
                    "event": obs,
                    "source": "Image",
                })

        elif file_type == "audio":
            key_events = analysis.get("key_events", [])
            for event in key_events:
                if isinstance(event, dict):
                    timeline.append({
                        "time": event.get("time", "Time unavailable"),
                        "event": event.get("event", "Unknown event"),
                        "source": "Audio",
                    })
                elif isinstance(event, str):
                    timeline.append({
                        "time": "Time unavailable",
                        "event": event,
                        "source": "Audio",
                    })

    return timeline
