# Resume Builder System - Pavel Schekin

## Структура системы

Система позволяет создавать адаптированные версии резюме из модульных JSON блоков, избегая "оверскилла" для разных позиций.

### Файлы блоков:

1. **personal_info.json** - Базовая информация и варианты должностей
2. **professional_summaries.json** - Различные варианты summary для разных ролей
3. **experience_blocks.json** - Опыт работы с тегами для фильтрации
4. **technical_skills.json** - Навыки по категориям и уровням владения
5. **resume_templates.json** - Готовые шаблоны для разных позиций

### Как это работает:

1. **Теги опыта** - Каждая позиция помечена тегами (fintech, kubernetes, startup и т.д.)
2. **Фильтрация** - Шаблоны автоматически скрывают нерелевантный опыт
3. **Уровни навыков** - expert/proficient/familiar для адаптации под уровень позиции
4. **Умная компоновка** - Автоматическая приоритизация релевантного опыта

## Использование

### Создание резюме по шаблону:
```bash
python resume_builder.py senior_devops_standard
python resume_builder.py fintech_focused
python resume_builder.py sre_position
python resume_builder.py startup_friendly
```

### Создание кастомного резюме:
```bash
python resume_builder.py senior_devops_standard -o "Pavel_Schekin_DevOps_CompanyName.pdf"
```

## Готовые шаблоны:

### 1. **senior_devops_standard**
- Для: Стандартные Senior DevOps позиции
- Опыт: Последние 7 лет (включая AI Startup 2025+)
- Навыки: Полный стек DevOps технологий
- Скрывает: Legacy разработку

### 2. **fintech_focused**
- Для: Позиции в финтехе/банках
- Опыт: Акцент на банковский опыт и безопасность
- Навыки: Security, compliance, high-load
- Скрывает: Нерелевантный опыт

### 3. **sre_position**
- Для: Site Reliability Engineer роли
- Опыт: Monitoring, high-scale системы
- Навыки: Акцент на надежность и мониторинг
- Скрывает: Чистую разработку

### 4. **startup_friendly**
- Для: Стартапы и небольшие компании
- Опыт: Последние 5 лет, акцент на versatility
- Навыки: Широкий стек, cost optimization
- Показывает: Способность работать с нуля

### 5. **lead_position**
- Для: Lead/Principal позиции
- Опыт: Полный опыт включая менеджмент
- Навыки: Все технологии + leadership
- Показывает: Весь путь карьеры

### 6. **ai_startup_modern** 🆕
- Для: AI/ML стартапы и современные tech компании
- Опыт: Последние 4 года (AI Startup первый)
- Навыки: Golang, VictoriaMetrics, hybrid cloud, AI workloads
- Показывает: Современные технологии и актуальный опыт

## Кастомизация

### Добавление нового опыта:
```json
{
  "id": "exp_new_2025",
  "title": "DevOps Engineer",
  "company": "New Company",
  "period": "2025 – Present",
  "tags": ["cloud", "kubernetes", "specific_tech"],
  "responsibilities": [
    "Responsibility 1",
    "Responsibility 2"
  ],
  "achievements": [
    "Achievement 1"
  ],
  "hidden_for": ["junior"]
}
```

### Создание нового шаблона:
```json
"custom_template": {
  "name": "Custom Role",
  "profile": "senior_devops",
  "experience_filter": {
    "priority_tags": ["specific_tech"],
    "exclude_tags": ["legacy"],
    "limit_years": 5
  },
  "skills_preset": "senior_devops"
}
```

## Советы по использованию:

1. **Для Junior позиций** - Используйте limit_years: 3-4
2. **Для Senior позиций** - Показывайте 5-7 лет опыта
3. **Для Lead позиций** - Показывайте весь релевантный опыт
4. **Для специфичных ролей** - Создавайте кастомные шаблоны с нужными тегами

## Примеры адаптации:

- **$3000-4000 позиция** → senior_devops_standard (без Lead опыта)
- **$5000-6000 позиция** → lead_position (полный опыт)
- **Gambling/Gaming** → startup_friendly (акцент на масштабирование)
- **Banking/FinTech** → fintech_focused (безопасность и compliance)

---

Система позволяет быстро создавать целевые резюме без "пугающего" 20-летнего опыта для позиций среднего уровня, при этом сохраняя возможность показать полную экспертизу для senior/lead ролей.