#!/usr/bin/env python3
"""
Генерация всех основных шаблонов резюме
Автор: Pavel Schekin
"""

from resume_builder import ResumeBuilder

def main():
    """Генерирует все основные шаблоны резюме"""
    builder = ResumeBuilder()
    
    # Основные шаблоны для отправки
    templates = [
        'blockchain_startup',     # Web3/Blockchain позиции
        'fintech_focused',        # FinTech компании
        'ai_startup_modern',      # AI/ML стартапы 
        'startup_friendly',       # Обычные стартапы
        'sre_position',          # SRE позиции
        'senior_devops_standard', # Стандартные Senior DevOps
        'junior_mid_devops'       # Mid-level позиции
    ]
    
    print("🚀 Генерация всех шаблонов резюме...")
    print("=" * 50)
    
    for template in templates:
        try:
            builder.create_pdf(template)
            print(f"✅ {template}")
        except Exception as e:
            print(f"❌ {template}: {e}")
    
    print("\n" + "=" * 50)
    print("📁 Файлы сохранены в generated/2025/[категория]/")
    print("📋 Готово для отправки работодателям!")

if __name__ == "__main__":
    main()