"""
TalentIQ AI - Resume Parser Module
Extracts structured data, sections, education, and contact information from PDF and DOCX files.
"""

import io
import re
import hashlib
from typing import Dict, Any, List, Optional


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts raw text from a PDF file using pypdf with fallback."""
    text_content = []
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_content.append(t)
    except Exception:
        # Fallback to pure regex byte scanning for text streams if pypdf fails
        try:
            raw_str = file_bytes.decode("latin-1", errors="ignore")
            matches = re.findall(r"\(([^\(\)]+)\)\s*Tj", raw_str)
            if matches:
                text_content.append(" ".join(matches))
        except Exception:
            pass
    return "\n".join(text_content).strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extracts text from a DOCX file using python-docx with fallback."""
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        paragraphs.append(cell.text.strip())
        return "\n".join(paragraphs).strip()
    except Exception:
        # Fallback using zipfile to read word/document.xml
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                xml_content = z.read("word/document.xml")
                root = ET.fromstring(xml_content)
                namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                texts = [elem.text for elem in root.findall(".//w:t", namespaces) if elem.text]
                return " ".join(texts).strip()
        except Exception:
            return ""


def clean_text(text: str) -> str:
    """Cleans and standardizes extracted resume text."""
    if not text:
        return ""
    # Normalize carriage returns and tabs
    text = re.sub(r"[\r\t\f\v]", " ", text)
    # Normalize line-by-line whitespace
    lines = [re.sub(r" +", " ", line).strip() for line in text.split("\n")]
    text = "\n".join(lines)
    # Normalize excessive consecutive newlines to double newline
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_contact_info(text: str) -> Dict[str, Any]:
    """Extracts email, phone, LinkedIn, and GitHub links from resume text."""
    info = {
        "email": None,
        "phone": None,
        "linkedin": None,
        "github": None,
        "portfolio": None
    }
    if not text:
        return info

    # Email
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    if email_match:
        info["email"] = email_match.group(0).lower()

    # Phone numbers (standard non-backtracking bounded regex)
    phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    if phone_match:
        info["phone"] = phone_match.group(0).strip()

    # LinkedIn
    linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/(?:in|profile)/[a-zA-Z0-9_-]+", text, re.IGNORECASE)
    if linkedin_match:
        info["linkedin"] = linkedin_match.group(0)

    # GitHub
    github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+", text, re.IGNORECASE)
    if github_match:
        info["github"] = github_match.group(0)

    return info


def extract_candidate_name(text: str, filename: str = "") -> str:
    """Infers candidate name from first lines or filename."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if lines:
        first_line = lines[0]
        # Ignore lines with common headers or symbols
        if len(first_line) < 40 and not any(k in first_line.lower() for k in ["resume", "curriculum", "cv", "page", "phone", "email"]):
            cleaned = re.sub(r"[^a-zA-Z\s]", "", first_line).strip()
            if len(cleaned.split()) in [2, 3, 4]:
                return cleaned.title()

    # Fallback to filename cleanup
    if filename:
        clean_fn = re.sub(r"\.(pdf|docx|doc|txt)$", "", filename, flags=re.IGNORECASE)
        clean_fn = re.sub(r"[-_]", " ", clean_fn)
        clean_fn = re.sub(r"(resume|cv|profile|updated|202[0-9])", "", clean_fn, flags=re.IGNORECASE).strip()
        if clean_fn:
            return clean_fn.title()

    return "Candidate"


def extract_education(text: str, education_section: str = "") -> List[str]:
    """
    Extracts degrees and educational qualifications from the resume.
    Checks the education section first, then scans the entire text.
    """
    target_text = education_section if education_section else text
    if not target_text:
        return []

    degree_patterns = [
        r"(?:Ph\.?D\.?|Doctorate|Doctor\s+of\s+Philosophy)(?:\s+(?:in|of)\s+[^,\n]+)?",
        r"(?:M\.?S\.?|M\.?Sc\.?|M\.?Tech\.?|M\.?E\.?|Master(?:'s)?(?:\s+of\s+Science)?)(?:\s+(?:in|of)\s+[^,\n]+)?",
        r"(?:B\.?S\.?|B\.?Sc\.?|B\.?Tech\.?|B\.?E\.?|Bachelor(?:'s)?(?:\s+of\s+Science)?)(?:\s+(?:in|of)\s+[^,\n]+)?",
        r"(?:MBA|Master\s+of\s+Business\s+Administration)",
        r"(?:Associate(?:'s)?\s+Degree|Diploma)(?:\s+(?:in|of)\s+[^,\n]+)?"
    ]

    found_degrees = []
    for pat in degree_patterns:
        matches = re.findall(pat, target_text, re.IGNORECASE)
        for m in matches:
            clean_m = re.sub(r"\s+", " ", m).strip()
            # Clean trailing punctuation
            clean_m = re.sub(r"[,;:\.]$", "", clean_m)
            if clean_m and len(clean_m) > 2 and clean_m not in found_degrees:
                found_degrees.append(clean_m)

    return found_degrees


def extract_sections(text: str) -> Dict[str, str]:
    """Splits resume text into logical sections."""
    section_patterns = {
        "summary": r"(?:professional\s+summary|summary|profile|about\s+me|objective)",
        "skills": r"(?:technical\s+skills|skills|technologies|core\s+competencies|tools)",
        "experience": r"(?:work\s+experience|professional\s+experience|experience|employment\s+history)",
        "education": r"(?:education|academic\s+background|academics|qualifications)",
        "projects": r"(?:projects|key\s+projects|academic\s+projects|personal\s+projects)",
        "certifications": r"(?:certifications|certificates|licenses|courses)"
    }

    sections: Dict[str, str] = {k: "" for k in section_patterns}
    sections["raw"] = text

    # Find heading positions
    positions = []
    for sec_name, pattern in section_patterns.items():
        for match in re.finditer(rf"\b{pattern}\b", text, re.IGNORECASE):
            positions.append((match.start(), sec_name))

    positions.sort(key=lambda x: x[0])

    if not positions:
        return sections

    for i in range(len(positions)):
        start_pos, sec_name = positions[i]
        end_pos = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        sections[sec_name] = text[start_pos:end_pos].strip()

    return sections


def parse_resume(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """Main parsing orchestrator that extracts full profile from file with validation."""
    error_msg = None
    raw_text = ""
    file_size = len(file_bytes) if file_bytes else 0
    file_hash = hashlib.sha256(file_bytes).hexdigest() if file_bytes else ""

    if not file_bytes or file_size == 0:
        return {
            "filename": filename,
            "candidate_name": "Unknown Candidate",
            "contact": {"email": None, "phone": None, "linkedin": None, "github": None},
            "raw_text": "",
            "sections": {},
            "education": [],
            "word_count": 0,
            "char_count": 0,
            "file_size": 0,
            "file_hash": "",
            "is_valid": False,
            "error_message": "Uploaded file is empty (0 bytes).",
            "status": "Failed"
        }

    try:
        lower_fn = filename.lower()
        if lower_fn.endswith(".pdf"):
            raw_text = extract_text_from_pdf(file_bytes)
        elif lower_fn.endswith(".docx"):
            raw_text = extract_text_from_docx(file_bytes)
        elif lower_fn.endswith(".txt"):
            raw_text = file_bytes.decode("utf-8", errors="ignore")
        else:
            try:
                raw_text = file_bytes.decode("utf-8", errors="ignore")
            except Exception:
                raw_text = ""
                error_msg = f"Unsupported file extension: {filename}."
    except Exception as e:
        error_msg = f"Parsing error for {filename}: {str(e)}"
        raw_text = ""

    cleaned = clean_text(raw_text)
    contact = extract_contact_info(cleaned)
    name = extract_candidate_name(cleaned, filename)
    sections = extract_sections(cleaned)
    education = extract_education(cleaned, sections.get("education", ""))

    words = cleaned.split()
    word_count = len(words)
    is_valid = len(cleaned.strip()) >= 30 and error_msg is None

    if not is_valid and error_msg is None:
        error_msg = "Insufficient readable text extracted from document."

    return {
        "filename": filename,
        "candidate_name": name,
        "contact": contact,
        "raw_text": cleaned,
        "sections": sections,
        "education": education,
        "word_count": word_count,
        "char_count": len(cleaned),
        "file_size": file_size,
        "file_hash": file_hash,
        "is_valid": is_valid,
        "error_message": error_msg,
        "status": "Indexed" if is_valid else "Failed"
    }
