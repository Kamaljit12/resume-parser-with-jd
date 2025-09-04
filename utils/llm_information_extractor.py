import re
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv
load_dotenv()

# accesss the groq api key
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# # Save the extracted text
# with open("resume_text_file/resumes/bhargavDasRsm.txt", "w", encoding="utf-8") as f:
#     f.write(resume_text)


# Create a llm model
def get_llm_model(model_id: str = "llama-3.1-8b-instant"):
    llm = ChatGroq(model=model_id,
               temperature=0,
               verbose=True)
    return llm

# Extract information from the resume
def skills_extractor(text: str, llm: str = get_llm_model()):

    # ---------- Step 2: Prompt for Skill Extraction ----------
    skill_prompt = PromptTemplate.from_template("""
            You are an expert HR assistant that extracts technical and professional skills from resumes and job descriptions.

            Instructions:
            - Extract only SKILLS from the given text.
            - Normalize variations into a common standard (e.g., VLOOKUP → Excel, Random Forest → Machine Learning).
            - Return output strictly in JSON format like:
            {{"Skill1", "Skill2", "Skill3"}}
            - Don't return any additional text or explanations.

            Text:
            {context}
            """)

    prompt = skill_prompt.format(context=text)
    response = llm.invoke(prompt)
    jd_skills = response.content.strip()
    
    match = re.search(r"\{.*\}", jd_skills, re.DOTALL)
    if match:
        raw = match.group(0)

    return raw

# Personal Information Extraction
def personal_information_extractor(text: str, model_id: str = "llama-3.1-8b-instant"):
      
      """ Model id is the identifier for the specific LLM version to use."""

      llm = ChatGroq(model=model_id,
          temperature=0,
          verbose=True
          )
      personal_info_prompt = PromptTemplate.from_template("""
          You are an expert Resume Parser.

          Task:
          - Extract the candidate's personal information from the given resume text.
          - Return the information in valid JSON format with these keys:
          - name
          - email
          - phone
          - location
          - linkedin
          - github
          - portfolio

          If any field is missing, return it as null.

          Resume Text:
          {resume_text}

          Return strictly in JSON format:
          {{
            "name": "...",
            "email": "...",
            "phone": "...",
            "location": "...",
            "linkedin": "...",
            "github": "...",
            "portfolio": "..."
          }}
          Don't include any explanations or additional text.
          """)

      response = llm.invoke(input = personal_info_prompt.format(resume_text=text)).content

      return response
