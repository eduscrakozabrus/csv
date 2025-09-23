#!/usr/bin/env python3
import json
import os
import sys
import pdfplumber
from pathlib import Path
import re

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file using pdfplumber"""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return None
    return text

def parse_technical_skills(text):
    """Parse technical skills table from resume"""
    skills = {}
    
    # Find the technical skills section
    tech_start = text.find("TECHNICAL SKILLS")
    if tech_start == -1:
        return skills
    
    # Find the end (usually next major section)
    tech_end = len(text)
    for section in ["EDUCATION", "CERTIFICATIONS", "LANGUAGES"]:
        pos = text.find(section, tech_start)
        if pos != -1 and pos < tech_end:
            tech_end = pos
    
    tech_text = text[tech_start:tech_end]
    
    # Look for Category/Technologies pattern
    lines = tech_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and the header
        if not line or "TECHNICAL SKILLS" in line or "Category" in line:
            i += 1
            continue
        
        # Check if this could be a category (single word or short phrase)
        # followed by technologies on the same or next line
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            
            # Pattern 1: Category and technologies on same line with clear separator
            if '(' in line or 'AWS' in line or len(line.split()) <= 3:
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    category = parts[0]
                    techs = parts[1]
                elif next_line and not any(word in next_line.lower() for word in ['category', 'cloud', 'kubernetes', 'monitoring']):
                    category = line
                    techs = next_line
                    i += 1
                else:
                    i += 1
                    continue
                
                # Clean up category name
                category = category.replace(':', '').strip()
                
                # Parse technologies
                tech_list = []
                # Remove parentheses and split by comma
                techs = techs.replace('(', '').replace(')', '')
                for tech in re.split(r'[,;]', techs):
                    tech = tech.strip()
                    if tech and len(tech) > 1:
                        tech_list.append(tech)
                
                if tech_list:
                    skills[category] = tech_list
        
        i += 1
    
    # Manual parsing for specific format from the provided resume
    if not skills:
        # Try line-by-line parsing
        skill_patterns = {
            "Cloud": r"AWS.*?(?=\n|$)",
            "Kubernetes": r"Kubernetes.*?(?=\n|$)",
            "CI/CD": r"CI/CD.*?(?=\n|$)",
            "IaC": r"IaC.*?(?=\n|$)",
            "Monitoring": r"Monitoring.*?(?=\n|$)",
            "Programming": r"Programming.*?(?=\n|$)",
            "Frontend": r"Frontend.*?(?=\n|$)",
            "Backend": r"Backend.*?(?=\n|$)",
            "Databases": r"Databases.*?(?=\n|$)|PostgreSQL.*?(?=\n|$)",
            "Operating Systems": r"Operating.*?Systems.*?(?=\n|$)|Linux.*?(?=\n|$)"
        }
        
        for category, pattern in skill_patterns.items():
            match = re.search(pattern, tech_text, re.IGNORECASE | re.DOTALL)
            if match:
                tech_line = match.group(0)
                # Remove the category name from the beginning
                tech_line = re.sub(r'^[^:]+:\s*', '', tech_line)
                tech_line = re.sub(r'^[^\(]+\s+', '', tech_line)
                
                # Split technologies
                techs = []
                for tech in re.split(r'[,;]', tech_line):
                    tech = tech.strip().replace('(', '').replace(')', '')
                    if tech and len(tech) > 1 and not tech.lower() in ['systems', 'category', 'technologies']:
                        techs.append(tech)
                
                if techs:
                    skills[category] = techs
    
    return skills

def parse_resume_text(text):
    """Parse resume text and extract structured data"""
    if not text:
        return None
    
    data = {
        "personal_info": {},
        "professional_profile": "",
        "skills": {},
        "experience": [],
        "education": [],
        "certifications": [],
        "languages": [],
        "technical_skills": {},
        "raw_text": text
    }
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        data["personal_info"]["email"] = emails[0]
    
    # Extract phone
    phone_pattern = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
    phones = re.findall(phone_pattern, text)
    if phones and len(phones[0]) > 6:
        data["personal_info"]["phone"] = phones[0]
    
    # Extract Telegram
    telegram_pattern = r'@[a-zA-Z0-9_]+'
    telegrams = re.findall(telegram_pattern, text)
    if telegrams:
        data["personal_info"]["telegram"] = telegrams[0]
    
    # Extract location
    location_pattern = r'📍\s*([^|]+)'
    locations = re.findall(location_pattern, text)
    if locations:
        data["personal_info"]["location"] = locations[0].strip()
    
    # Extract name (usually at the beginning)
    lines = text.split('\n')
    for i, line in enumerate(lines[:5]):
        if line.strip() and len(line.strip()) < 50:
            # Likely a name if it's short and at the beginning
            if not any(char.isdigit() for char in line) and '@' not in line and '|' not in line and '📍' not in line:
                data["personal_info"]["name"] = line.strip()
                break
    
    # Extract professional profile
    profile_start = text.find("PROFESSIONAL PROFILE")
    work_start = text.find("WORK EXPERIENCE")
    if profile_start != -1 and work_start != -1:
        profile_text = text[profile_start:work_start].strip()
        profile_lines = [line.strip() for line in profile_text.split('\n') if line.strip() and line.strip() != "PROFESSIONAL PROFILE"]
        data["professional_profile"] = " ".join(profile_lines)
    
    # Extract work experience
    work_pattern = r'WORK EXPERIENCE(.*?)(?:TECHNICAL SKILLS|EDUCATION|$)'
    work_match = re.search(work_pattern, text, re.DOTALL)
    if work_match:
        work_text = work_match.group(1)
        
        # Split by job titles
        job_entries = []
        current_job = None
        
        for line in work_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if it's a job title
            title_keywords = ['Engineer', 'Developer', 'DevOps', 'Lead', 'Senior', 'Manager', 'Specialist']
            is_title = any(keyword in line for keyword in title_keywords) and '•' not in line and '|' not in line and len(line) < 60
            
            # Check if it's a company line
            has_date = bool(re.search(r'\d{4}', line)) and '|' in line
            
            if is_title:
                if current_job:
                    job_entries.append(current_job)
                current_job = {
                    "title": line,
                    "company": "",
                    "period": "",
                    "responsibilities": []
                }
            elif current_job and has_date:
                parts = line.split('|')
                current_job["company"] = parts[0].strip()
                if len(parts) > 1:
                    current_job["period"] = parts[1].strip()
            elif current_job and line.startswith('•'):
                current_job["responsibilities"].append(line)
        
        if current_job:
            job_entries.append(current_job)
        
        data["experience"] = job_entries
    
    # Extract technical skills
    data["technical_skills"] = parse_technical_skills(text)
    
    # Copy technical skills to skills section for compatibility
    data["skills"] = data["technical_skills"].copy()
    
    return data

def process_pdf_files(input_dir, output_dir):
    """Process all PDF files in input directory and save as JSON"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all PDF files
    pdf_files = list(input_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return
    
    results = []
    
    for pdf_file in pdf_files:
        print(f"\nProcessing {pdf_file.name}...")
        
        # Extract text
        text = extract_text_from_pdf(pdf_file)
        
        if text:
            # Parse resume data
            resume_data = parse_resume_text(text)
            
            if resume_data:
                resume_data["source_file"] = pdf_file.name
                
                # Save individual JSON file
                json_filename = output_path / f"{pdf_file.stem}_final.json"
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(resume_data, f, ensure_ascii=False, indent=2)
                
                print(f"✅ Saved {json_filename}")
                
                # Print summary
                print(f"  - Name: {resume_data['personal_info'].get('name', 'Not found')}")
                print(f"  - Location: {resume_data['personal_info'].get('location', 'Not found')}")
                print(f"  - Contact: {resume_data['personal_info'].get('telegram', 'Not found')}")
                print(f"  - Experience entries: {len(resume_data['experience'])}")
                print(f"  - Skill categories: {len(resume_data['technical_skills'])}")
                
                results.append(resume_data)
            else:
                print(f"❌ Failed to parse {pdf_file.name}")
        else:
            print(f"❌ Failed to extract text from {pdf_file.name}")
    
    # Save combined results
    if results:
        combined_file = output_path / "all_resumes_final.json"
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Saved combined results to {combined_file}")
        print(f"✅ Processed {len(results)} PDF files successfully")

if __name__ == "__main__":
    # Set paths
    input_directory = "/Users/schekin/Documents/cvs/older"
    output_directory = "/Users/schekin/Documents/cvs/sources/devops"
    
    # Process PDFs
    process_pdf_files(input_directory, output_directory)