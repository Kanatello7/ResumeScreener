# ResumeScreener

**ResumeScreener** is an open-source tool designed to streamline the recruitment process by automating the screening of resumes against job descriptions. Built with Python, it uses natural language processing (NLP) to parse resumes, extract key skills and experiences, and match them to job requirements.

Whether you're a recruiter, HR professional, or developer building custom hiring pipelines, this tool helps identify top candidates quickly and efficiently.

## 🚀 Features

- **Resume Parsing**: Supports PDF, DOCX, and ZIP, Rar formats. Extracts structured data like education, work experience, skills, and contact info.
- **Job Description Matching**: Compares resumes to JD using cosine similarity and keyword extraction for accurate scoring.
- **Customizable Scoring**: Adjustable weights for skills, experience, and education to fit your hiring criteria.
- 
## 🛠️ Tech Stack

- **Core Language**: Python 3.8+
- **Libraries**:
  - `PyPDF2` or `pdfplumber` for PDF parsing
  - `python-docx` for DOCX handling
  - `scikit-learn` and `nltk` for NLP and matching algorithms
  - `pandas` for data manipulation
  - `Django` for API serving
  - `OpenAPI` for GPT requests
- **No external dependencies** beyond standard pip-installable packages (see `requirements.txt`).

## 📦 Installation

1. **Clone the Repository**:
   ```
   git clone https://github.com/Kanatello7/ResumeScreener.git
   cd ResumeScreener
   ```

2. **Create a Virtual Environment** (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```
4. **Run Web App**:
   ```
   python manage.py runserver
   ```
