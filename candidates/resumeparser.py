from PyPDF2 import PdfReader
import docx2txt
import re 
import spacy
from spacy.matcher import Matcher
from . import utils

def get_resume_raw_text(file_path):
    text = ""
    if file_path.endswith('.pdf'):
        reader = PdfReader(file_path)
        text = "\n".join([page.extract_text().strip() for page in reader.pages if page.extract_text()])
    elif file_path.endswith('.docx'):
        text = docx2txt.process(file_path)
    return text.strip()


class ResumeParser:
    def __init__(self, resume_file_path):
        nlp = spacy.load('en_core_web_sm')
        self.details = {
            'personal information': None,
            'full_name': None,
            'email': None,
            'phone_number': None,
            'location': None,
            'role': None,
            'statement':None,
            'skills': None,
            'work_experience': None,
            'education': None,
            'projects': None,
            'certifications': None,
            'awards': None,
            'languages': None,
            'experience_year': None,
            'raw_text': None,
            'sections': None,
        }
        self.resume = resume_file_path 
        self.raw_text = get_resume_raw_text(resume_file_path)
        self.doc = nlp(self.raw_text)
        self.noun_chunks = list(self.doc.noun_chunks)
        self.sections = utils.extract_sections(self.raw_text)
        self.matcher_ = Matcher(nlp.vocab)
        self.get_details()
    
    def get_details(self):
        self.details['full_name'] = utils.extract_full_name(self.raw_text)
        if self.sections.get('contact', False):
            contact_text = self.sections.get('contact')
            self.details['email'] = utils.extract_email(contact_text)
            self.details['phone_number'] = utils.extract_phone_number(contact_text)
            self.details['location'] = utils.extract_location(contact_text)
        else:
            self.details['email'] = utils.extract_email(self.raw_text)
            self.details['phone_number'] = utils.extract_phone_number(self.raw_text)
            self.details['location'] = utils.extract_location(self.raw_text)
        
        if self.sections.get('statement', False):      
            self.details['statement'] = self.sections.get('statement')
        
        if self.sections.get('skills', False):
            self.details['skills'] = utils.extract_skills(self.sections.get('skills'))
        
        if self.sections.get('experience', False):
            experience_text = self.sections.get('experience')
            work_experience = utils.extract_work_experience(experience_text)
            exp_year = utils.extract_work_experience_year(experience_text)
            self.details['work_experience'] = f"Professional Experience ({exp_year} years) \n" + work_experience
        
        if self.sections.get('education', False):
            education_text = self.sections.get('education')
            self.details['education'] = utils.extract_education(education_text)
        
        if self.sections.get('languages', False):
            language_text = self.sections.get('languages')
            self.details['languages'] = language_text
   
        self.details['sections'] = self.sections
        self.details['raw_text'] = self.raw_text
        
    def get_extracted_data(self):
        return self.details