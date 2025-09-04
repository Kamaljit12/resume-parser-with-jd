from utils.llm_information_extractor import skills_extractor, personal_information_extractor
from utils.text_extractor import extract_text_from_pdf, extract_text_from_docx
from utils.load_text_file import load_text_file
from utils.embedder import text_embedding
from conifg import *
from sentence_transformers import util

# extrac the text from the docs
resume_text = extract_text_from_pdf(res_file_path) if res_file_path.endswith(".pdf") else extract_text_from_docx(res_file_path)
# job description text
jd_text = load_text_file(jd_file_path)

# ------------------- resume skills -------------------
resume_skills = skills_extractor(resume_text)

#  --------------------- jd skills ---------------------
jd_skills = skills_extractor(jd_text)

# ------------- resume personal information -------------
resume_personal_info = personal_information_extractor(resume_text)

resume_skills_embedding = text_embedding(resume_skills)
jd_skills_embedding = text_embedding(jd_skills)

simi_score = float(util.cos_sim(jd_skills_embedding, resume_skills_embedding))*100
print(f"Score: {simi_score:.2f}%")