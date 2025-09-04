# Resume Parser & JD Matcher

Lightweight resume parsing and JD matching app that extracts skills and personal information from resumes (PDF/DOCX) using a Groq LLM (via `langchain_groq`) and computes semantic similarity with job descriptions using sentence-transformers.

- Streamlit web UI: [`src/app.py`](src/app.py) — see [`src.app.main`](src/app.py), [`src.app.read_uploaded_resume`](src/app.py), [`src.app.compute_similarity`](src/app.py), [`src.app.parse_skills_to_list`](src/app.py)
- CLI demo: [`main.py`](main.py)

Core utilities
- Skill & personal-info extraction (LLM): [`utils/llm_information_extractor.py`](utils/llm_information_extractor.py) — functions: [`utils.llm_information_extractor.skills_extractor`](utils/llm_information_extractor.py), [`utils.llm_information_extractor.personal_information_extractor`](utils/llm_information_extractor.py)
- Resume text extraction: [`utils/text_extractor.py`](utils/text_extractor.py) — functions: [`utils.text_extractor.extract_text_from_pdf`](utils/text_extractor.py), [`utils.text_extractor.extract_text_from_docx`](utils/text_extractor.py)
- Load JD text files: [`utils/load_text_file.py`](utils/load_text_file.py) — [`utils.load_text_file.load_text_file`](utils/load_text_file.py)
- Embeddings helper: [`utils/embedder.py`](utils/embedder.py) — [`utils.embedder.text_embedding`](utils/embedder.py)
- Config: [`conifg.py`](conifg.py) — keys: [`conifg.res_file_path`](conifg.py), [`conifg.jd_file_path`](conifg.py), [`conifg.embedding_model_id`](conifg.py), [`conifg.llm_model_id`](conifg.py)

Notebooks and examples
- Example notebooks and saved resume text: `notebooks/` (e.g. [`notebooks/resume_text.txt`](notebooks/resume_text.txt), [`notebooks/bhargavDasRsm.txt`](notebooks/bhargavDasRsm.txt))

Requirements
- Install dependencies:
```sh
pip install -r requirements.txt
```
See: [`requirements.txt`](requirements.txt)

Environment
- Create a `.env` with your Groq key:
  - Key name: `GROQ_API_KEY` (used by the LLM code). Example file: [`.env`](.env)
- The Streamlit app checks for `GROQ_API_KEY` and warns if missing.

Quickstart (Streamlit)
```sh
# from project root
pip install -r requirements.txt
# set GROQ_API_KEY in .env or env vars
streamlit run src/app.py
```

Quickstart (CLI)
```sh
python main.py
```
`main.py` runs a simple pipeline that reads a resume from the path in [`conifg.res_file_path`](conifg.py) and a JD from [`conifg.jd_file_path`](conifg.py), extracts skills & personal info, embeds skills and prints a similarity score.

Data layout
- Job descriptions: `data/jd/` (saved JD files can be written by the UI)
- Resumes: `data/resume/`
- Example JD file: [`data/ai_ml_jd.txt`](data/ai_ml_jd.txt) (referenced by config)

Notes & tips
- The LLM calls use `langchain_groq.ChatGroq` in [`utils/llm_information_extractor.py`](utils/llm_information_extractor.py). Ensure your GROQ API key is valid and set in the environment.
- Embeddings use `sentence-transformers` (model id configured in [`conifg.embedding_model_id`](conifg.py)).
- PDF and DOCX parsing falls back to available libs: [`pdfplumber`], [`pypdf`], [`docx2txt`] as used in [`utils/text_extractor.py`](utils/text_extractor.py).
- If you intend to deploy, avoid committing `.env` (it's in `.gitignore`) and rotate any leaked keys.

Files of interest
- App: [`src/app.py`](src/app.py)
- Config: [`conifg.py`](conifg.py)
- CLI: [`main.py`](main.py)
- LLM extractor: [`utils/llm_information_extractor.py`](utils/llm_information_extractor.py)
- Text extraction: [`utils/text_extractor.py`](utils/text_extractor.py)
- Loader: [`utils/load_text_file.py`](utils/load_text_file.py)
- Embedder: [`utils/embedder.py`](utils/embedder.py)
- Requirements: [`requirements.txt`](requirements.txt)
- Notebooks: [`notebooks/`](notebooks/)

License
- Add a LICENSE file if you plan to open-source this