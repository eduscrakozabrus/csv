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

def parse_resume_text(text):
    """Parse resume text and extract structured data"""
    if not text:
        return None
    
    data = {
        "personal_info": {},
        "skills": {
            "cloud": [],
            "kubernetes": [],
            "cicd": [],
            "iac": [],
            "monitoring": [],
            "programming": [],
            "frontend": [],
            "backend": [],
            "databases": [],
            "os": [],
            "other": []
        },
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
    if phones:
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
            if not any(char.isdigit() for char in line) and '@' not in line and '|' not in line:
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
        
        # Split by job titles (look for patterns like "Senior DevOps Engineer" followed by company/date)
        job_entries = []
        current_job = None
        
        for line in work_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if it's a job title (contains common titles)
            title_keywords = ['Engineer', 'Developer', 'DevOps', 'Lead', 'Senior', 'Manager', 'Specialist']
            is_title = any(keyword in line for keyword in title_keywords) and '•' not in line and '|' not in line
            
            # Check if it's a company line (contains date pattern)
            date_pattern = r'\d{4}'
            has_date = re.search(date_pattern, line)
            
            if is_title and len(line) < 60:
                if current_job:
                    job_entries.append(current_job)
                current_job = {
                    "title": line,
                    "company": "",
                    "period": "",
                    "responsibilities": []
                }
            elif current_job and has_date and '|' in line:
                parts = line.split('|')
                current_job["company"] = parts[0].strip()
                if len(parts) > 1:
                    current_job["period"] = parts[1].strip()
            elif current_job and line.startswith('•'):
                current_job["responsibilities"].append(line)
        
        if current_job:
            job_entries.append(current_job)
        
        data["experience"] = job_entries
    
    # Extract technical skills section
    tech_skills_pattern = r'TECHNICAL SKILLS(.*?)(?:EDUCATION|CERTIFICATIONS|$)'
    tech_match = re.search(tech_skills_pattern, text, re.DOTALL)
    if tech_match:
        tech_text = tech_match.group(1)
        
        current_category = None
        for line in tech_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Check if it's a category line
            if 'Category' not in line and not line.startswith('(') and len(line) < 30:
                current_category = line.lower()
                data["technical_skills"][current_category] = []
            elif current_category and line and 'Category' not in line:
                # Clean up the technologies line
                techs = [t.strip() for t in re.split(r'[,;]', line) if t.strip()]
                data["technical_skills"][current_category].extend(techs)
    
    # Organize skills into categories based on technical skills section
    if data["technical_skills"]:
        for category, techs in data["technical_skills"].items():
            category_lower = category.lower()
            if 'cloud' in category_lower:
                data["skills"]["cloud"] = techs
            elif 'kubernetes' in category_lower:
                data["skills"]["kubernetes"] = techs
            elif 'ci/cd' in category_lower or 'cicd' in category_lower:
                data["skills"]["cicd"] = techs
            elif 'iac' in category_lower or 'infrastructure' in category_lower:
                data["skills"]["iac"] = techs
            elif 'monitoring' in category_lower:
                data["skills"]["monitoring"] = techs
            elif 'programming' in category_lower:
                data["skills"]["programming"] = techs
            elif 'frontend' in category_lower:
                data["skills"]["frontend"] = techs
            elif 'backend' in category_lower:
                data["skills"]["backend"] = techs
            elif 'database' in category_lower:
                data["skills"]["databases"] = techs
            elif 'operating' in category_lower or 'os' in category_lower or 'system' in category_lower:
                data["skills"]["os"] = techs
    
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
        print(f"Processing {pdf_file.name}...")
        
        # Extract text
        text = extract_text_from_pdf(pdf_file)
        
        if text:
            # Parse resume data
            resume_data = parse_resume_text(text)
            
            if resume_data:
                resume_data["source_file"] = pdf_file.name
                
                # Save individual JSON file
                json_filename = output_path / f"{pdf_file.stem}_improved.json"
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(resume_data, f, ensure_ascii=False, indent=2)
                
                print(f"Saved {json_filename}")
                results.append(resume_data)
            else:
                print(f"Failed to parse {pdf_file.name}")
        else:
            print(f"Failed to extract text from {pdf_file.name}")
    
    # Save combined results
    if results:
        combined_file = output_path / "all_resumes_improved.json"
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\nSaved combined results to {combined_file}")
        print(f"Processed {len(results)} PDF files successfully")

if __name__ == "__main__":
    # Set paths
    input_directory = "/Users/schekin/Documents/cvs/older"
    output_directory = "/Users/schekin/Documents/cvs/sources/devops"
    
    # Process PDFs
    process_pdf_files(input_directory, output_directory)