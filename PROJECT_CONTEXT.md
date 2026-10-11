# PROJECT_CONTEXT — ChinaGoods

## О проекте
Объединение трёх проектов: VK-бот + mini-CRM + парсер 1688/Avito.
Цель: полный цикл — от поиска товара до доставки.

## Три проекта
1. **VK-бот** — консультирует клиентов в группе ВК (241598165), локально, gigachat 0.2.3, vk_api.
2. **mini-CRM** — учёт заказов, Streamlit + SQLite + GigaChat HTTP v1, 64 теста.
   GitHub: AlexeyAKr/mini-crm-delivery
   Live: mini-crm-delivery-hnpcznbpw7siqqta2jpwkp.streamlit.app
3. **Project 3 (avito-1688-analyzer)** — только структура, кода нет.
   GitHub: AlexeyAKr/avito-1688-analyzer

## Архитектура объединения
- Монорепо `china-goods/` (создано в C:\Users\user\Documents\china_goods)
- Общая PostgreSQL на Supabase
- SQLAlchemy + Alembic
- JSONB для атрибутов товаров
- Отдельная таблица категорий

## Ключевые решения
- PostgreSQL, а не SQLite (три машины, облако)
- Прямые HTTP к GigaChat v1 (библиотека 0.2.3 не работает)
- Монорепо с папкой `shared/`

## Что дальше
- Фаза 1: MVP Project 3 (ручной ввод товаров + маржа)
- Фаза 2: mini-CRM на PostgreSQL
- Фаза 3: связка CRM + Project 3
- Фаза 4: VK-бот → запись заявок в CRM
- Фаза 5: парсер 1688