import os
import io
import json
import tempfile
import re
import streamlit as st
from typing import Optional, Tuple
import sys

# Ensure project root is on PYTHONPATH so `utils` can be imported when running from src/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Local imports
from utils.text_extractor import extract_text_from_pdf, extract_text_from_docx
from utils.load_text_file import load_text_file
from utils.llm_information_extractor import skills_extractor, personal_information_extractor
from utils.embedder import text_embedding
from sentence_transformers import util


def read_uploaded_resume(file) -> Tuple[str, str]:
    """Return (raw_text, file_ext) from an uploaded resume file (.pdf/.docx)."""
    file_ext = os.path.splitext(file.name)[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name

    try:
        if file_ext == ".pdf":
            text = extract_text_from_pdf(tmp_path)
        elif file_ext == ".docx":
            text = extract_text_from_docx(tmp_path)
        else:
            raise ValueError("Unsupported file type. Please upload a PDF or DOCX.")
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    return text.strip() if text else "", file_ext


def safe_json_load(maybe_json: str):
    try:
        return json.loads(maybe_json)
    except Exception:
        return maybe_json


def render_personal_info(personal_info_json_like: str):
    data = safe_json_load(personal_info_json_like)
    if isinstance(data, dict):
        cols = st.columns(2)
        with cols[0]:
            st.metric("Name", data.get("name") or "-")
            st.write(f"Email: {data.get('email') or '-'}")
            st.write(f"Phone: {data.get('phone') or '-'}")
        with cols[1]:
            st.write(f"Location: {data.get('location') or '-'}")
            st.write(f"LinkedIn: {data.get('linkedin') or '-'}")
            st.write(f"GitHub: {data.get('github') or '-'}")
            st.write(f"Portfolio: {data.get('portfolio') or '-'}")
    else:
        st.code(str(personal_info_json_like))


def compute_similarity(jd_skills_text: str, resume_skills_text: str) -> float:
    if not jd_skills_text or not resume_skills_text:
        return 0.0
    jd_emb = text_embedding(jd_skills_text)
    res_emb = text_embedding(resume_skills_text)
    return float(util.cos_sim(jd_emb, res_emb)) * 100


def parse_skills_to_list(skills_text: str):
    if not skills_text:
        return []
    # Prefer quoted items
    quoted = re.findall(r'"([^"]+)"', skills_text)
    if quoted:
        return [s.strip() for s in quoted if s.strip()]
    # Fallback: remove braces and split by comma
    cleaned = skills_text.strip().strip('{}[]')
    parts = [p.strip().strip('"\'"\'') for p in cleaned.split(',')]
    return [p for p in parts if p]


def main():
    st.set_page_config(page_title="Resume Parser & JD Matcher", layout="wide")
    st.title("Resume Parser & JD Matcher")
    st.caption("Upload resume, paste JD, extract skills & personal info, and get a match score.")

    if not os.getenv("GROQ_API_KEY"):
        st.warning("GROQ_API_KEY is not set. LLM features will fail. Create a .env with GROQ_API_KEY.")

    with st.sidebar:
        st.header("Job Description")
        jd_text = st.text_area("Paste JD here", value="", height=200, key="jd_text_area")
        if st.button("Save JD to file"):
            os.makedirs("data/jd", exist_ok=True)
            path = os.path.join("data", "jd", "posted_jd.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(jd_text)
            st.success("JD saved to data/jd/posted_jd.txt")

        st.divider()
        st.header("Resume Upload")
        resume_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"], accept_multiple_files=False)

    tab_resume, tab_jd, tab_compare = st.tabs(["Resume Details", "JD Skills", "Compare & Score"])

    resume_text: Optional[str] = None
    resume_skills_text: Optional[str] = None
    personal_info_json_like: Optional[str] = None
    jd_skills_text: Optional[str] = None

    if resume_file is not None:
        with st.spinner("Reading resume..."):
            resume_text, _ = read_uploaded_resume(resume_file)

        if resume_text:
            with st.spinner("Extracting personal info and skills from resume via LLM..."):
                try:
                    personal_info_json_like = personal_information_extractor(resume_text)
                except Exception as e:
                    st.error(f"Failed to extract personal information: {e}")
                try:
                    resume_skills_text = skills_extractor(resume_text)
                except Exception as e:
                    st.error(f"Failed to extract resume skills: {e}")

    if jd_text:
        with st.spinner("Extracting JD skills via LLM..."):
            try:
                jd_skills_text = skills_extractor(jd_text)
            except Exception as e:
                st.error(f"Failed to extract JD skills: {e}")

    with tab_resume:
        st.subheader("Personal Information")
        if personal_info_json_like:
            render_personal_info(personal_info_json_like)
        else:
            st.info("Upload a resume to extract personal info.")

        st.subheader("Resume Skills")
        if resume_skills_text:
            skills = parse_skills_to_list(resume_skills_text)
            if skills:
                st.markdown(" ".join([f"`{s}`" for s in skills]))
            else:
                st.code(resume_skills_text, language="json")
        else:
            st.info("Upload a resume to extract skills.")

        st.subheader("Resume Text (preview)")
        if resume_text:
            with st.expander("Show resume text"):
                st.markdown(f"```text\n{resume_text[:4000]}\n```")

    with tab_jd:
        st.subheader("JD Skills")
        if jd_skills_text:
            jd_skills_list = parse_skills_to_list(jd_skills_text)
            if jd_skills_list:
                st.markdown(" ".join([f"`{s}`" for s in jd_skills_list]))
            else:
                st.code(jd_skills_text, language="json")
        else:
            st.info("Paste JD in the sidebar to extract skills.")

        st.subheader("Saved JD Files")
        jd_dir = os.path.join("data", "jd")
        if os.path.isdir(jd_dir):
            files = [f for f in os.listdir(jd_dir) if f.endswith(".txt")]
            if files:
                selected = st.selectbox("View a saved JD", files, index=0)
                if selected:
                    path = os.path.join(jd_dir, selected)
                    jd_loaded = load_text_file(path)
                    st.markdown(f"```text\n{jd_loaded}\n```")
            else:
                st.info("No JD files found in data/jd.")
        else:
            st.info("Folder data/jd not found.")

    with tab_compare:
        st.subheader("Match Score")
        if jd_skills_text and resume_skills_text:
            score = compute_similarity(jd_skills_text, resume_skills_text)
            st.metric("Resume ↔ JD Skill Match", f"{score:.2f}%")

            col1, col2 = st.columns(2)
            with col1:
                st.caption("JD Skills")
                jd_skills_list = parse_skills_to_list(jd_skills_text)
                if jd_skills_list:
                    st.markdown(" ".join([f"`{s}`" for s in jd_skills_list]))
                else:
                    st.code(jd_skills_text, language="json")
            with col2:
                st.caption("Resume Skills")
                res_skills_list = parse_skills_to_list(resume_skills_text)
                if res_skills_list:
                    st.markdown(" ".join([f"`{s}`" for s in res_skills_list]))
                else:
                    st.code(resume_skills_text, language="json")
        else:
            st.info("Provide both JD and resume to compute match score.")


if __name__ == "__main__":
    main()


