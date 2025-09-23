#!/usr/bin/env python3
"""
Resume Builder - Компоновка PDF резюме из JSON блоков
Автор: Pavel Schekin
"""

import json
import os
from pathlib import Path
from datetime import datetime
import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import argparse

class ResumeBuilder:
    def __init__(self, blocks_dir="resume_blocks"):
        self.blocks_dir = Path(blocks_dir)
        self.load_all_blocks()
        
    def load_all_blocks(self):
        """Загрузка всех JSON блоков"""
        self.personal_info = self.load_json("personal_info.json")
        self.summaries = self.load_json("professional_summaries.json")
        self.experience = self.load_json("experience_blocks.json")
        self.skills = self.load_json("technical_skills.json")
        self.templates = self.load_json("resume_templates.json")
        
    def load_json(self, filename):
        """Загрузка отдельного JSON файла"""
        filepath = self.blocks_dir / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def filter_experience(self, template_config):
        """Фильтрация опыта работы согласно шаблону"""
        experience_filter = template_config.get('experience_filter', {})
        filtered_exp = []
        
        for exp in self.experience['experience_blocks']:
            # Проверка на исключающие теги
            if 'exclude_tags' in experience_filter:
                if any(tag in exp['tags'] for tag in experience_filter['exclude_tags']):
                    continue
            
            # Проверка на скрытие для определенных уровней
            if 'hidden_for' in exp:
                if template_config['name'].lower() in exp['hidden_for']:
                    continue
            
            # Ограничение по годам опыта
            if 'limit_years' in experience_filter:
                # Надёжный парсинг начального года периода (поддержка разных тире и форматов)
                years = re.findall(r'(?:19|20)\d{2}', exp.get('period', ''))
                if years:
                    try:
                        start_year = int(years[0])
                        current_year = datetime.now().year
                        if current_year - start_year > experience_filter['limit_years']:
                            continue
                    except ValueError:
                        pass
            
            filtered_exp.append(exp)
        
        # Сортировка по приоритетным тегам
        if 'priority_tags' in experience_filter:
            priority_tags = experience_filter['priority_tags']
            filtered_exp.sort(
                key=lambda x: sum(tag in priority_tags for tag in x['tags']),
                reverse=True
            )
        
        return filtered_exp
    
    def get_skills_for_preset(self, preset_name, level_filter=None):
        """Получение навыков для заданного пресета"""
        preset = self.skills['skill_presets'].get(preset_name, [])
        result_skills = {}
        
        for category_key in preset:
            category = self.skills['technical_skills'].get(category_key, {})
            if category:
                skills_by_level = category.get('skills', {})
                
                if level_filter:
                    # Фильтруем по уровням
                    filtered_skills = []
                    for level in level_filter:
                        filtered_skills.extend(skills_by_level.get(level, []))
                    
                    if filtered_skills:
                        result_skills[category['category']] = filtered_skills
                else:
                    # Берем все уровни
                    all_skills = []
                    for level in ['expert', 'proficient', 'familiar']:
                        all_skills.extend(skills_by_level.get(level, []))
                    
                    if all_skills:
                        result_skills[category['category']] = all_skills
        
        return result_skills
    
    def create_pdf(self, template_name, output_filename=None):
        """Создание PDF резюме по шаблону"""
        if template_name not in self.templates['resume_templates']:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.templates['resume_templates'][template_name]
        
        # Определяем папку и имя выходного файла
        if not output_filename:
            # Маппинг шаблонов к папкам
            folder_mapping = {
                'blockchain_startup': 'blockchain',
                'fintech_focused': 'fintech', 
                'startup_friendly': 'startup',
                'ai_startup_modern': 'ai',
                'sre_position': 'sre',
                'senior_devops_standard': 'senior',
                'lead_position': 'senior',
                'junior_mid_devops': 'startup'
            }
            
            folder = folder_mapping.get(template_name, 'senior')
            current_year = datetime.now().year
            
            # Создаем папку если не существует
            output_dir = Path(f"generated/{current_year}/{folder}")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Красивое имя файла без timestamp
            clean_names = {
                'blockchain_startup': 'Blockchain_DevOps',
                'fintech_focused': 'FinTech_DevOps',
                'startup_friendly': 'Startup_DevOps', 
                'ai_startup_modern': 'AI_DevOps',
                'sre_position': 'SRE',
                'senior_devops_standard': 'Senior_DevOps',
                'lead_position': 'Lead_DevOps',
                'junior_mid_devops': 'Mid_DevOps'
            }
            
            clean_name = clean_names.get(template_name, template_name.replace('_', '_').title())
            output_filename = str(output_dir / f"Pavel_Schekin_{clean_name}_{current_year}.pdf")
        
        # Создаем документ
        doc = SimpleDocTemplate(
            output_filename,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Стили
        styles = getSampleStyleSheet()
        self.create_custom_styles(styles)
        
        # Элементы документа
        story = []
        
        # Персональная информация
        story.extend(self.add_personal_info(template, styles))
        story.append(Spacer(1, 10*mm))
        
        # Professional Summary
        story.extend(self.add_summary(template, styles))
        story.append(Spacer(1, 8*mm))
        
        # Технические навыки
        # Явная настройка уровней в шаблоне через skills_levels, иначе разумные значения по умолчанию
        skills_level_filter = template.get('skills_levels')
        if skills_level_filter is None:
            if template_name == 'junior_mid_devops':
                skills_level_filter = None  # показать все уровни для mid/junior
            else:
                skills_level_filter = ['expert', 'proficient']
        story.extend(self.add_skills(template, styles, skills_level_filter))
        story.append(Spacer(1, 8*mm))
        
        # Опыт работы
        story.extend(self.add_experience(template, styles))
        
        # Генерация PDF
        doc.build(story)
        print(f"✅ Resume created: {output_filename}")
        
        return output_filename
    
    def create_custom_styles(self, styles):
        """Создание кастомных стилей"""
        styles.add(ParagraphStyle(
            name='Name',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_CENTER,
            spaceAfter=6
        ))
        
        styles.add(ParagraphStyle(
            name='JobTitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            alignment=TA_CENTER,
            spaceAfter=12
        ))
        
        styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=8,
            borderColor=colors.HexColor('#2c3e50'),
            borderWidth=0,
            borderPadding=0
        ))
        
        styles.add(ParagraphStyle(
            name='ExperienceTitle',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=4
        ))
    
    def add_personal_info(self, template, styles):
        """Добавление персональной информации"""
        elements = []
        info = self.personal_info['personal_info']
        
        # Имя
        elements.append(Paragraph(info['name'], styles['Name']))
        
        # Должность
        title_key = template['profile'].replace('_focused', '').replace('_position', '')
        title = info['title_variants'].get(title_key, info['title_variants']['senior'])
        elements.append(Paragraph(title, styles['JobTitle']))
        
        # Контакты
        contacts = []
        contacts.append(f"📱 Telegram: {info['contacts']['telegram']}")
        if 'linkedin' in info['contacts']:
            contacts.append(f"🔗 {info['contacts']['linkedin']}")
        
        contact_text = " | ".join(contacts)
        elements.append(Paragraph(contact_text, styles['Normal']))
        
        return elements
    
    def add_summary(self, template, styles):
        """Добавление professional summary"""
        elements = []
        
        summary_data = self.summaries['professional_summaries'].get(template['profile'])
        if summary_data:
            elements.append(Paragraph("PROFESSIONAL PROFILE", styles['SectionHeading']))
            elements.append(Paragraph(summary_data['content'], styles['BodyText']))
        
        return elements
    
    def add_skills(self, template, styles, level_filter=None):
        """Добавление технических навыков"""
        elements = []
        
        elements.append(Paragraph("TECHNICAL SKILLS", styles['SectionHeading']))
        
        skills_data = self.get_skills_for_preset(template['skills_preset'], level_filter)
        
        # Создаем таблицу навыков
        table_data = []
        for category, skills_list in sorted(skills_data.items(), key=lambda x: x[0].lower()):
            # Стабильный порядок и внутри категорий
            sorted_skills = sorted(skills_list, key=lambda s: s.lower())
            skills_text = ", ".join(sorted_skills)
            table_data.append([
                Paragraph(f"<b>{category}</b>", styles['Normal']),
                Paragraph(skills_text, styles['Normal'])
            ])
        
        if table_data:
            table = Table(table_data, colWidths=[50*mm, 120*mm])
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(table)
        
        return elements
    
    def add_experience(self, template, styles):
        """Добавление опыта работы"""
        elements = []
        
        elements.append(Paragraph("WORK EXPERIENCE", styles['SectionHeading']))
        
        filtered_experience = self.filter_experience(template)
        
        for i, exp in enumerate(filtered_experience):
            # Заголовок позиции
            title_text = f"<b>{exp['title']}</b>"
            elements.append(Paragraph(title_text, styles['ExperienceTitle']))
            
            # Компания и период
            company_text = f"{exp['company']} | {exp['period']}"
            elements.append(Paragraph(company_text, styles['Normal']))
            elements.append(Spacer(1, 2*mm))
            
            # Обязанности
            for responsibility in exp['responsibilities']:
                elements.append(Paragraph(responsibility, styles['BodyText']))
            
            # Достижения (если есть и если нужно выделить)
            if 'achievements' in exp and template.get('highlight_achievements', True):
                elements.append(Spacer(1, 2*mm))
                for achievement in exp['achievements']:
                    achievement_text = f"<i>→ {achievement}</i>"
                    elements.append(Paragraph(achievement_text, styles['BodyText']))
            
            if i < len(filtered_experience) - 1:
                elements.append(Spacer(1, 6*mm))
        
        return elements

def main():
    parser = argparse.ArgumentParser(description='Build PDF resume from JSON blocks')
    parser.add_argument('template', help='Template name to use')
    parser.add_argument('-o', '--output', help='Output filename')
    parser.add_argument('-d', '--dir', default='resume_blocks', help='Blocks directory')
    
    args = parser.parse_args()
    
    builder = ResumeBuilder(args.dir)
    builder.create_pdf(args.template, args.output)

if __name__ == "__main__":
    # Делегируем в CLI обработчик аргументов
    main()
