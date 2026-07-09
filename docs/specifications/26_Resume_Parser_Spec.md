# Resume Parser Specification

## Purpose

Convert an uploaded resume into a structured cybersecurity profile.

---

# Inputs

Supported Formats

- PDF
- DOCX
- TXT

Maximum Size

5 MB

---

# Output

{
    "name": "",
    "email": "",
    "skills": [],
    "projects": [],
    "certifications": [],
    "education": [],
    "experience": []
}

---

# Processing Pipeline

Resume Upload

↓

Text Extraction

↓

Section Detection

↓

Skill Extraction

↓

Skill Normalization

↓

Structured JSON

---

# Responsibilities

Extract

- Technical Skills
- Projects
- Certifications
- Education
- Experience

Ignore

- Styling
- Images
- Headers
- Footers

---

# Validation

Duplicate Skills

↓

Remove

Unknown Skills

↓

Ignore

Empty Resume

↓

Return Error

---

# Acceptance Criteria

✓ PDF supported

✓ DOCX supported

✓ JSON returned

✓ No duplicate skills