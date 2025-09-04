try:
    import pdfplumber
    _HAVE_PDFPLUMBER = True
except Exception:
    _HAVE_PDFPLUMBER = False

try:
    import docx2txt
except Exception as _e:
    docx2txt = None
from pypdf import PdfReader
from conifg import *

# extract text from pdf files
def extract_text_from_pdf(file_path):
    text = ""
    if _HAVE_PDFPLUMBER:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
        return text
    # Fallback to pypdf
    reader = PdfReader(file_path)
    for page in reader.pages:
        txt = page.extract_text() or ""
        text += txt + "\n"
    return text

# extract text from docx files
def extract_text_from_docx(file_path):
    if docx2txt is None:
        raise ImportError("docx2txt is not installed. Please install it to parse DOCX resumes.")
    return docx2txt.process(file_path)
