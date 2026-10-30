"""
TalentIQ AI - Resume Builder & PDF Generation Engine
Enables recruiters and candidates to compose, edit, pre-populate, and export
high-fidelity professional PDF resumes utilizing ReportLab typography and layouts.
"""

import io
import re
from xml.sax.saxutils import escape as xml_escape
from typing import Dict, List, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def sanitize_xml(text: str) -> str:
    """Escapes special characters for ReportLab XML paragraph rendering."""
    if not text:
        return ""
    return xml_escape(str(text))


def prefill_resume_from_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts structured fields from an indexed candidate profile to pre-fill the Resume Builder.
    """
    contact = candidate.get("contact", {})
    sections = candidate.get("sections", {})
    skills = candidate.get("all_skills", [])

    # Extract summary
    summary = sections.get("summary", "")
    if not summary and candidate.get("raw_text"):
        lines = [line.strip() for line in candidate["raw_text"].split("\n") if line.strip()]
        if len(lines) > 2:
            summary = lines[1] if len(lines[1]) > 30 else " ".join(lines[1:3])

    # Extract education entries
    edu_list = candidate.get("education", [])
    education_records = []
    if edu_list:
        for e in edu_list:
            education_records.append({
                "degree": e,
                "institution": "University / College",
                "year": "2020 - 2024"
            })
    else:
        education_records.append({
            "degree": "B.S. in Computer Science",
            "institution": "Accredited University",
            "year": "2019 - 2023"
        })

    # Default experience entry from candidate experience
    exp_years = candidate.get("years_of_experience", 0.0)
    exp_text = sections.get("experience", "")
    exp_bullets = []
    if exp_text:
        lines = [l.strip("-•* ") for l in exp_text.split("\n") if len(l.strip()) > 15][:3]
        exp_bullets = lines if lines else ["Spearheaded core software feature engineering and distributed workflows."]
    else:
        exp_bullets = [
            f"Demonstrated {exp_years:.1f} years of professional engineering expertise.",
            "Designed and shipped production features collaborating with cross-functional teams."
        ]

    # Projects
    proj_text = sections.get("projects", "")
    projects_list = []
    if proj_text:
        proj_lines = [p.strip("-•* ") for p in proj_text.split("\n") if len(p.strip()) > 15][:2]
        for p in proj_lines:
            projects_list.append({"name": "Key Project", "description": p})
    else:
        projects_list.append({
            "name": "Cloud Microservices Platform",
            "description": "Architected high-throughput REST APIs and containerized Docker services."
        })

    # Certifications
    cert_text = sections.get("certifications", "")
    certs_list = []
    if cert_text:
        for c in cert_text.split("\n")[:2]:
            clean_c = c.strip("-•* ")
            if clean_c:
                certs_list.append(clean_c)

    return {
        "full_name": candidate.get("candidate_name", "Alex Mercer"),
        "job_title": "Software Engineer",
        "email": contact.get("email") or "candidate@example.com",
        "phone": contact.get("phone") or "+1 (555) 019-2834",
        "location": "San Francisco, CA",
        "linkedin": contact.get("linkedin") or "linkedin.com/in/profile",
        "github": contact.get("github") or "github.com/profile",
        "summary": summary[:450] if summary else "Results-driven engineer with a proven track record of architecting scalable applications and high-availability cloud systems.",
        "skills": ", ".join(skills[:16]) if skills else "Python, React, Node.js, Docker, AWS, PostgreSQL, Git",
        "experience": [
            {
                "role": "Senior Engineer",
                "company": "Tech Innovations Inc.",
                "duration": "2022 - Present",
                "bullets": "\n".join(exp_bullets)
            }
        ],
        "education": education_records,
        "projects": projects_list,
        "certifications": certs_list
    }


def generate_resume_pdf(resume_data: Dict[str, Any]) -> bytes:
    """
    Renders an enterprise-grade, styled PDF resume into in-memory bytes using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    color_primary = colors.HexColor("#1E3A8A")   # Royal navy
    color_accent = colors.HexColor("#4F46E5")    # Electric indigo
    color_dark = colors.HexColor("#0F172A")      # Dark slate
    color_muted = colors.HexColor("#64748B")     # Secondary muted

    name_style = ParagraphStyle(
        "ResumeName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=color_primary,
        spaceAfter=3
    )

    title_style = ParagraphStyle(
        "ResumeTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=color_accent,
        spaceAfter=5
    )

    contact_style = ParagraphStyle(
        "ResumeContact",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=color_muted,
        spaceAfter=10
    )

    section_heading = ParagraphStyle(
        "ResumeSection",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=color_primary,
        spaceBefore=8,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        "ResumeBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=color_dark,
        spaceAfter=4
    )

    bold_body_style = ParagraphStyle(
        "ResumeBoldBody",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=color_dark
    )

    bullet_style = ParagraphStyle(
        "ResumeBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=color_dark,
        leftIndent=14,
        spaceAfter=2
    )

    story = []

    # 1. Header: Name & Title
    full_name = sanitize_xml(resume_data.get("full_name", "Professional Resume"))
    job_title = sanitize_xml(resume_data.get("job_title", "Software Developer"))
    story.append(Paragraph(full_name, name_style))
    if job_title:
        story.append(Paragraph(job_title.upper(), title_style))

    # Contact line
    contacts = []
    if resume_data.get("email"):
        contacts.append(resume_data["email"])
    if resume_data.get("phone"):
        contacts.append(resume_data["phone"])
    if resume_data.get("location"):
        contacts.append(resume_data["location"])
    if resume_data.get("linkedin"):
        contacts.append(resume_data["linkedin"])
    if resume_data.get("github"):
        contacts.append(resume_data["github"])

    contact_line = " &nbsp;&middot;&nbsp; ".join([sanitize_xml(c) for c in contacts])
    story.append(Paragraph(contact_line, contact_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=color_accent, spaceBefore=0, spaceAfter=8))

    # 2. Professional Summary
    summary = resume_data.get("summary", "").strip()
    if summary:
        story.append(Paragraph("PROFESSIONAL SUMMARY", section_heading))
        story.append(Paragraph(sanitize_xml(summary), body_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=3, spaceAfter=6))

    # 3. Technical Skills
    skills_text = resume_data.get("skills", "").strip()
    if skills_text:
        story.append(Paragraph("TECHNICAL SKILLS", section_heading))
        story.append(Paragraph(f"<b>Core Competencies:</b> {sanitize_xml(skills_text)}", body_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=3, spaceAfter=6))

    # 4. Professional Experience
    experiences = resume_data.get("experience", [])
    if experiences:
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", section_heading))
        for exp in experiences:
            role = sanitize_xml(exp.get("role", "Role"))
            company = sanitize_xml(exp.get("company", "Company"))
            duration = sanitize_xml(exp.get("duration", "Dates"))
            
            # Subheader table for Role | Company | Dates
            exp_table = Table(
                [[Paragraph(f"<b>{role}</b> &mdash; <i>{company}</i>", bold_body_style), Paragraph(duration, contact_style)]],
                colWidths=[400, 140]
            )
            exp_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (1,0), (1,0), 'RIGHT'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2)
            ]))
            story.append(exp_table)

            # Bullets
            bullets = exp.get("bullets", "")
            if isinstance(bullets, list):
                bullet_lines = bullets
            else:
                bullet_lines = [b.strip() for b in bullets.split("\n") if b.strip()]
            
            for b in bullet_lines:
                clean_b = sanitize_xml(re.sub(r"^[-•* ]+", "", b))
                story.append(Paragraph(f"&bull; {clean_b}", bullet_style))
            story.append(Spacer(1, 4))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=3, spaceAfter=6))

    # 5. Education
    educations = resume_data.get("education", [])
    if educations:
        story.append(Paragraph("EDUCATION", section_heading))
        for edu in educations:
            deg = sanitize_xml(edu.get("degree", "Degree"))
            inst = sanitize_xml(edu.get("institution", "Institution"))
            yr = sanitize_xml(edu.get("year", ""))
            edu_table = Table(
                [[Paragraph(f"<b>{deg}</b> &mdash; {inst}", body_style), Paragraph(yr, contact_style)]],
                colWidths=[400, 140]
            )
            edu_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (1,0), (1,0), 'RIGHT'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2)
            ]))
            story.append(edu_table)
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=3, spaceAfter=6))

    # 6. Projects (Optional)
    projects = resume_data.get("projects", [])
    if projects:
        story.append(Paragraph("KEY PROJECTS", section_heading))
        for p in projects:
            p_name = sanitize_xml(p.get("name", "Project"))
            p_desc = sanitize_xml(p.get("description", ""))
            story.append(Paragraph(f"<b>{p_name}:</b> {p_desc}", body_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=3, spaceAfter=6))

    # 7. Certifications (Optional)
    certs = resume_data.get("certifications", [])
    if certs:
        story.append(Paragraph("CERTIFICATIONS", section_heading))
        for c in certs:
            story.append(Paragraph(f"&bull; {sanitize_xml(c)}", bullet_style))

    # Build PDF doc
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

