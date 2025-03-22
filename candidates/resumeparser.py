from openai import OpenAI
import docx2txt
from . import utils
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = OpenAI(
    api_key = os.getenv('OPEN_AI_KEY',)
)


def get_resume_raw_text(file_path):
    text = ""
    if file_path.endswith('.pdf'):
        for page in utils.extract_text_from_pdf(file_path):
            text += ' ' + page
    elif file_path.endswith('.docx'):
        text = docx2txt.process(file_path)
    return text.strip()


class ResumeParser:
    def __init__(self, resume_file_path):
        self.resume = resume_file_path 
        self.raw_text = get_resume_raw_text(resume_file_path)
        self.sections = utils.extract_sections(self.raw_text)
        self.details = self.get_details()
        self.data = {
            "full_name": self.details['full_name'],
            "email": self.details['email'],
            "sections": self.sections,
            "details": self.details,
            "raw_text": self.raw_text
        }
    def get_details(self):
        prompt = self.get_prompt()
        response = self.call_chat_api(prompt)
        raw_content = response.choices[0].message.content
        
        cleaned_json = raw_content.strip("```json").strip("```").strip()
        try:
            data = json.loads(cleaned_json)
        except json.JSONDecodeError:
            data = {"error": "Malformed JSON in response"}
        
        return data 
    
    def get_prompt(self):
        prompt = f"""
        You are an intelligent resume parser. Analyze the resume text below and extract the following fields into a JSON object:
        if field does not found mark as "Not found"
        - full_name
        - job title
        - email
        - phone
        - location
        - statement
        - education (as a list of dictionary with this fields College Name, degree, date, location)
        - skills (as a list)
        - experience (as a list of dictionary with this fields Company Name, job_title, date, location, responsibilities)
        - total_experience_year 
        - projects (as a list of dictionary with this fields title, tech_used as a list, description, link)
        - awards (as a list of dictionary with this fields title, description, link)
        - languages (as a list)

        Resume:
        \"\"\"
        {self.raw_text}
        \"\"\"

        Return only the JSON format with keys and values.

        """
        return prompt    
    
    def call_chat_api(self, prompt):
        return client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant skilled in parsing resumes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
    def get_extracted_data(self):
        return self.data