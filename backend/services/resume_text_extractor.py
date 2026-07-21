import os
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = 5 * 1024 * 1024


class TextExtractionResult:
    def __init__(self, text: str, character_count: int, page_count: Optional[int], file_type: str):
        self.text = text
        self.character_count = character_count
        self.page_count = page_count
        self.file_type = file_type


class ResumeTextExtractor:

    @staticmethod
    def validate_file(filename: str, file_size: Optional[int] = None) -> str:
        ext = os.path.splitext(filename or "")[1].lower()
        if not ext:
            raise ValueError("File must have an extension")
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext}. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")
        if file_size is not None and file_size <= 0:
            raise ValueError("File is empty")
        if file_size is not None and file_size > MAX_FILE_SIZE:
            raise ValueError(f"File exceeds maximum size of {MAX_FILE_SIZE // (1024 * 1024)}MB")
        return ext

    @staticmethod
    def extract(file_path: str) -> TextExtractionResult:
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            return ResumeTextExtractor._extract_pdf(file_path)
        elif ext == ".docx":
            return ResumeTextExtractor._extract_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type for extraction: {ext}")

    @staticmethod
    def _extract_pdf(file_path: str) -> TextExtractionResult:
        try:
            from pdfminer.high_level import extract_text, extract_pages
            from pdfminer.layout import LAParams

            text = extract_text(file_path, laparams=LAParams())
            text = ResumeTextExtractor._normalize(text)

            page_count = None
            try:
                pages = list(extract_pages(file_path))
                page_count = len(pages)
            except Exception:
                pass

            return TextExtractionResult(
                text=text,
                character_count=len(text),
                page_count=page_count,
                file_type="pdf",
            )
        except ImportError:
            logger.error("pdfminer.six not installed")
            raise ValueError("PDF extraction library not available")
        except Exception as e:
            logger.error("PDF extraction failed: %s", e)
            raise ValueError(f"Failed to extract text from PDF: {e}")

    @staticmethod
    def _extract_docx(file_path: str) -> TextExtractionResult:
        try:
            import docx

            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            text = "\n".join(paragraphs)
            text = ResumeTextExtractor._normalize(text)

            return TextExtractionResult(
                text=text,
                character_count=len(text),
                page_count=None,
                file_type="docx",
            )
        except ImportError:
            logger.error("python-docx not installed")
            raise ValueError("DOCX extraction library not available")
        except Exception as e:
            logger.error("DOCX extraction failed: %s", e)
            raise ValueError(f"Failed to extract text from DOCX: {e}")

    @staticmethod
    def _normalize(text: str) -> str:
        if not text:
            return ""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
