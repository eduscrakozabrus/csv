# Resume Builder System

Модульная система для создания PDF резюме из JSON блоков с автоматической адаптацией под разные типы вакансий.

## 🚀 Быстрый старт

### 1. Активация виртуального окружения
```bash
source venv/bin/activate
```

### 2. Генерация всех шаблонов
```bash
python generate_all.py
```

### 3. Создание отдельного шаблона
```bash
python -c "from resume_builder import ResumeBuilder; builder = ResumeBuilder(); builder.create_pdf('blockchain_startup')"
```

## 📁 Структура проекта

```
cvs/
├── resume_blocks/              # JSON блоки данных
│   ├── personal_info.json      # Личная информация и контакты
│   ├── experience_blocks.json  # Опыт работы с тегами
│   ├── technical_skills.json   # Технические навыки по категориям
│   ├── professional_summaries.json # Professional summary варианты
│   └── resume_templates.json   # Конфигурация шаблонов
├── generated/2025/             # Сгенерированные PDF
│   ├── blockchain/            # Web3/Blockchain позиции
│   ├── fintech/              # FinTech компании
│   ├── ai/                   # AI/ML стартапы
│   ├── startup/              # Стартапы
│   ├── sre/                  # SRE позиции
│   └── senior/               # Senior DevOps
├── resume_builder.py          # Основной класс для генерации
├── generate_all.py           # Скрипт генерации всех шаблонов
└── venv/                     # Виртуальное окружение
```

## 🎯 Доступные шаблоны

| Шаблон | Описание | Файл | Целевые вакансии |
|--------|----------|------|------------------|
| `blockchain_startup` | Blockchain/Web3 | `Pavel_Schekin_Blockchain_DevOps_2025.pdf` | Web3 стартапы, DeFi, криптопроекты |
| `fintech_focused` | FinTech | `Pavel_Schekin_FinTech_DevOps_2025.pdf` | Банки, платежные системы |
| `ai_startup_modern` | AI/ML | `Pavel_Schekin_AI_DevOps_2025.pdf` | AI стартапы, ML платформы |
| `startup_friendly` | Стартапы | `Pavel_Schekin_Startup_DevOps_2025.pdf` | Обычные стартапы |
| `sre_position` | SRE | `Pavel_Schekin_SRE_2025.pdf` | Site Reliability Engineer |
| `senior_devops_standard` | Senior | `Pavel_Schekin_Senior_DevOps_2025.pdf` | Корпорации, крупные компании |
| `junior_mid_devops` | Mid-level | `Pavel_Schekin_Mid_DevOps_2025.pdf` | Mid/Junior позиции |

## 🔧 Команды

### Генерация всех шаблонов
```bash
source venv/bin/activate
python generate_all.py
```

### Создание отдельного шаблона
```bash
source venv/bin/activate
python -c "from resume_builder import ResumeBuilder; builder = ResumeBuilder(); builder.create_pdf('TEMPLATE_NAME')"
```

### Примеры для конкретных шаблонов
```bash
# Blockchain/Web3 позиции
python -c "from resume_builder import ResumeBuilder; builder = ResumeBuilder(); builder.create_pdf('blockchain_startup')"

# FinTech компании
python -c "from resume_builder import ResumeBuilder; builder = ResumeBuilder(); builder.create_pdf('fintech_focused')"

# AI/ML стартапы
python -c "from resume_builder import ResumeBuilder; builder = ResumeBuilder(); builder.create_pdf('ai_startup_modern')"

# SRE позиции
python -c "from resume_builder import ResumeBuilder; builder = ResumeBuilder(); builder.create_pdf('sre_position')"
```

## 📝 Настройка и кастомизация

### Личная информация
Редактируй `resume_blocks/personal_info.json`:
```json
{
  "name": "Pavel Schekin",
  "contacts": {
    "telegram": "@cqrsdevops",
    "linkedin": "linkedin.com/in/pavelschekin"
  },
  "title_variants": {
    "senior": "Senior DevOps Engineer",
    "lead": "Lead DevOps Engineer",
    "sre": "Site Reliability Engineer"
  }
}
```

### Опыт работы
Управляй опытом через теги в `resume_blocks/experience_blocks.json`:
```json
{
  "id": "exp_blockchain_2023",
  "title": "Lead DevOps",
  "company": "Blockchain Service Provider",
  "period": "2023 – 2024",
  "tags": ["blockchain", "terraform", "ansible", "startup", "web3"],
  "responsibilities": [...],
  "achievements": [...]
}
```

### Технические навыки
Добавляй/изменяй навыки в `resume_blocks/technical_skills.json`:
```json
"blockchain": {
  "category": "Blockchain Infrastructure",
  "skills": {
    "expert": ["Multi-chain Network Orchestration"],
    "proficient": ["High-RPS Distributed Systems"],
    "familiar": ["Validator Management"]
  }
}
```

### Создание нового шаблона
1. Добавь шаблон в `resume_blocks/resume_templates.json`
2. Опционально укажи `skills_levels` для контроля глубины навыков (например: ["expert","proficient"] или ["expert","proficient","familiar"]).
3. Обнови `folder_mapping` и `clean_names` в `resume_builder.py`
4. Добавь в список `templates` в `generate_all.py`

## 🎨 Логика фильтрации

### Теги для опыта работы
- **`blockchain`** - блокчейн проекты
- **`fintech`** - финтех/банки
- **`ai`** - AI/ML проекты
- **`startup`** - стартапы
- **`kubernetes`** - K8s опыт
- **`high-scale`** - высоконагруженные системы
- **`legacy`** - старый опыт (исключается для senior позиций)

### Пример фильтрации шаблона
```json
"blockchain_startup": {
  "experience_filter": {
    "priority_tags": ["blockchain", "microservices", "high-scale"],
    "exclude_tags": ["legacy", "fintech"],
    "limit_years": 5
  }
}
```

## 🔍 Какой шаблон выбрать?

### Для отклика на вакансию
1. **Blockchain/Web3** → `blockchain_startup`
2. **Банк/FinTech** → `fintech_focused`  
3. **AI/ML компания** → `ai_startup_modern`
4. **Обычный стартап** → `startup_friendly`
5. **SRE позиция** → `sre_position`
6. **Крупная корпорация** → `senior_devops_standard`
7. **Mid-level позиция** → `junior_mid_devops`

### Универсальная отправка
Используй `generate_all.py` и выбирай нужный файл из `generated/2025/[категория]/`

## 🛠️ Установка зависимостей

Если нужно переустановить окружение:
```bash
python3 -m venv venv
source venv/bin/activate
pip install reportlab pdfplumber
```

## 📋 Результат

После генерации получаешь готовые PDF файлы:
- Красивое форматирование
- Адаптация под тип вакансии  
- Удобные имена файлов
- Организованная структура папок
- Без "overqualification" проблем

**Готово для отправки работодателям!** 🚀

## Изменения CLI

Теперь `resume_builder.py` использует аргументы командной строки (через `argparse`). Примеры:
```bash
python resume_builder.py senior_devops_standard
python resume_builder.py fintech_focused -o "Pavel_Schekin_Fintech_Custom.pdf"
```
# csv
