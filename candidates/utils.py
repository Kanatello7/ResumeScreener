import re 
import pandas as pd 
import os 
import spacy
from spacy.matcher import PhraseMatcher, Matcher
from datetime import datetime
from dateutil import relativedelta
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFSyntaxError
import io

def extract_text_from_pdf(pdf_path):
    if not isinstance(pdf_path, io.BytesIO):
        # extract text from local pdf file
        with open(pdf_path, 'rb') as fh:
            try:
                for page in PDFPage.get_pages(
                        fh,
                        caching=True,
                        check_extractable=True
                ):
                    resource_manager = PDFResourceManager()
                    fake_file_handle = io.StringIO()
                    converter = TextConverter(
                        resource_manager,
                        fake_file_handle,
                        codec='utf-8',
                        laparams=LAParams()
                    )
                    page_interpreter = PDFPageInterpreter(
                        resource_manager,
                        converter
                    )
                    page_interpreter.process_page(page)

                    text = fake_file_handle.getvalue()
                    yield text

                    # close open handles
                    converter.close()
                    fake_file_handle.close()
            except PDFSyntaxError:
                return
    else:
        # extract text from remote pdf file
        try:
            for page in PDFPage.get_pages(
                    pdf_path,
                    caching=True,
                    check_extractable=True
            ):
                resource_manager = PDFResourceManager()
                fake_file_handle = io.StringIO()
                converter = TextConverter(
                    resource_manager,
                    fake_file_handle,
                    codec='utf-8',
                    laparams=LAParams()
                )
                page_interpreter = PDFPageInterpreter(
                    resource_manager,
                    converter
                )
                page_interpreter.process_page(page)

                text = fake_file_handle.getvalue()
                yield text

                # close open handles
                converter.close()
                fake_file_handle.close()
        except PDFSyntaxError:
            return

RESUME_SECTIONS_GRAD = [
                    'profile',
                    'contact',
                    'hello',
                    'about me',
                    'statement',
                    'summary',
                    'work experience',
                    'experience',
                    'education',
                    'skills',
                    'interests',
                    'projects',
                    'professional experience',
                    'publications',
                    'certifications',
                    'objective',
                    'career objective',
                    'leadership',
                    'reference',
                    'languages',
                    'awards'
                ]


def extract_entity(text):
    text_split = [i.strip() for i in text.split('\n')]

    entities = {}
    key = False
    for phrase in text_split:
        if len(phrase) == 1:
            p_key = phrase
        else:
            p_key = set(phrase.lower().split()) & set(RESUME_SECTIONS_GRAD)
        try:
            p_key = list(p_key)[0]
        except IndexError:
            pass
        if p_key in RESUME_SECTIONS_GRAD:
            entities[p_key] = []
            key = p_key
        elif key and phrase.strip():
            entities[key].append(phrase)
    return entities

synonym_mapping = {
    "work experience": "experience",
    "professional experience": "experience",
    "experience": "experience",
    "profile": "statement",
    "statement": "statement",
    "summary": "statement",
    "about me": "statement",
    "hello": "contact"
}
def convert_to_text(lis):
    return " ".join(e for e in lis)

def extract_sections(text):
    entities = extract_entity(text)
    normalized = {}
    for key, value in entities.items():
        normalized_key = synonym_mapping.get(key.lower(), key.lower())
        normalized[normalized_key] = convert_to_text(value) 
    return normalized

def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)
def extract_full_name(text):
    text = preprocess_text(text)
    doc = nlp(text)
    patterns = [
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}],  # First name and Last name
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}],  # First name, Middle name, and Last name
    ]

    for pattern in patterns:
        matcher.add('NAME', patterns=[pattern])
    matches = matcher(doc)

    for match_id, start, end in matches:
        span = doc[start:end]
        return span.text

    return "Unknown"

def extract_email(text):
    matches = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)
     
    return matches[0] if matches else 'Unknown'

def extract_phone_number(text):
    phone_number = 'Unknown'
    pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    match = re.search(pattern, text)
    if match:
        phone_number = match.group()
    return phone_number

def extract_location(text):
    doc = nlp(text)
    location = ""
    cnt = 0
    for ent in doc.ents:
        if ent.label_ == 'GPE':
            location += ent.text + " "
            cnt += 1
            if cnt > 2:
                break
    return location  if location != "" else 'Unknown'

def extract_statement(text):
    lines = text.split('\n')
    b = True
    res = ""
    for line in lines:
        if (len(line.split()) <= 1 and b) or not re.search(r"[a-z]", line.lower()):
           continue
        b = False
        res += line + "\n"
    return res


SKILLS_PATH = os.path.join(os.path.dirname(__file__), 'skillset.csv')
skills_df = pd.read_csv(SKILLS_PATH)
skills_df = skills_df.apply(lambda x: x.str.lower())
skills_list = skills_df.stack().tolist()
 
def extract_skills(text):
    skills_set = set()
    for i in re.split(r'[,\s]+',text):
        if i.lower() in skills_list:
            skills_set.add(i)
    return ", ".join(list(skills_set))

def extract_experience_section(text):
    start_pattern = re.compile(r'(?i)(work\s*experience|professional\s*experience|employment\s*history|experience)')
    start_match = start_pattern.search(text)
    if not start_match:
        return None
    next_section_pattern = re.compile(r'(?i)(education|projects|skills|references|achievements)')
    next_section_match = next_section_pattern.search(text[start_match.end():])

    if next_section_match:
        experience_text = text[start_match.end():start_match.end() + next_section_match.start()]
    else:
        experience_text = text[start_match.end():]

    return experience_text.strip()

def extract_work_experience_year(text):
    dates = re.findall(
        r'(?P<fmonth>\w+[\s/-]+\d+)\s*([^\w\s]|to)\s*(?P<smonth>\w+[\s/-]+\d+|present|ongoing)',
        text,
        re.IGNORECASE
    )
    total_exp = sum(
        [get_number_of_months_from_dates(i[0], i[2]) for i in dates]
    )
    experience_year = round(total_exp / 12, 2)
    return experience_year

def get_month_name(month_ind):
    d = {
        "01": "Jan",
        "02": "Feb",
        "03": "Mar",
        "04": "Apr",
        "05": "May",
        "06": "Jun",
        "07": "Jul",
        "08": "Aug",
        "09": "Sep",
        "10": "Oct",
        "11": "Nov",
        "12": "Dec"
    }
    return d[month_ind]

def parse_date_string(date_str):
    if date_str.strip().lower() == 'present' or date_str.strip().lower() == 'ongoing':
        return datetime.now()

    date_str = re.sub(r"([A-Za-z]+)(\d{4})", r"\1 \2", date_str)
    parts = date_str.split()
    if len(parts) == 1:

        if parts[0].isdigit() and len(parts[0]) == 4:
            date_str = f"Jan {parts[0]}"
        elif '/' in parts[0] and len(parts[0]) == 7:
            tmp = parts[0].split('/')
            date_str = f"{get_month_name(tmp[0])} {tmp[1]}"
        else:
            raise ValueError(f"Unrecognized date format: {date_str}")
    elif len(parts) >= 2:

        month_part, year_part = parts[0], parts[1]
        if year_part == '/' or year_part == '-':
            year_part = parts[2]
        # e.g. "September" -> "Sep", "JUNE" -> "JUN"
        if len(month_part) > 3:
            month_part = month_part[:3]

        date_str = month_part.capitalize() + " " + year_part
    else:
        raise ValueError(f"Could not parse date: {date_str}")

    return datetime.strptime(date_str, '%b %Y')


def get_number_of_months_from_dates(date1, date2):
    try:
        dt1 = parse_date_string(date1)
        dt2 = parse_date_string(date2)
    except ValueError:

        return 0

    rd = relativedelta.relativedelta(dt2, dt1)
    months_of_experience = rd.years * 12 + rd.months

    return max(months_of_experience, 0)

def extract_work_experience(text):
    text = " ".join(text.split("\n"))
    temp = re.split(r'[●•-][^●^.]*', text)
    job_titles = []
    for i, title in enumerate(temp[:-1]):
        if title != '.' and title != '. ':
            job_titles.append(title.replace('.', ' ').strip())
    if job_titles:
        res = ""
        for i, title in enumerate(job_titles):
            res += str(i + 1) + ") " + title + "\n"
        return res
    return 'Unknown'

def extract_education(text):
    degrees = []
    
    pattern = r"(?i)(?:Bsc|\bB\.\w+|\bM\.\w+|\bPh\.D\.\w+|\bBachelor(?:'s)?|\bMaster(?:'s)?|\bPh\.D)\s(?:\w+\s)*\w+"
    matches = re.findall(pattern, text)
    for match in matches:
        degree = match.strip()
        res = []
        for token in nlp(degree):
            if token.ent_type_ != 'DATE' and token.ent_type_ != 'GPE':
                res.append(token.text)
        degree = " ".join(res)
        degrees.append(degree)
    doc = nlp(text)
    orgs = []
    dates = []
    for ent in doc.ents:
        if ent.label_ == 'DATE':
            dates.append(ent.text)
        elif ent.label_ == 'ORG' and 'university' in ent.text.lower():
            orgs.append(ent.text)
    educations = ""
    for i, degree in enumerate(degrees):
        try:
            educations += orgs[i] + "\n"
            educations += degree + "\n"
            educations += dates[i] + "\n\n"
        except:
            break
        
    return  educations