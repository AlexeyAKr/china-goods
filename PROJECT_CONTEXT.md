# PROJECT_CONTEXT — ChinaGoods (Монорепо)

## 1. О проекте
Монорепо для магазина ChinaGoods. Цель — объединить парсинг товаров (Китай), учет заказов (CRM), консультирование клиентов (ВК-бот) и анализ новостей в единую экосистему.
**GitHub:** https://github.com/AlexeyAKr/china-goods (Private)
**Стек:** Python 3.12, Streamlit, SQLAlchemy 2.1.4, psycopg 3.3.6, Supabase (PostgreSQL), Apify, ProxyAPI (GPT-4o-mini).

## 2. Текущая структура монорепо
china_goods/
├── shared/ # Ядро: config.py, db.py, models.py (Category, Supplier, Product)
├── parser_1688/ # Streamlit UI: список товаров, карточка, парсинг с 1688
├── mini_crm/ # Копия mini-CRM (пока на SQLite, требует переезда)
├── vk_bot/ # Копия VK-бота (gigachat 0.2.3, требует интеграции)
├── avito_module/ # Заготовка
└── PROJECT_CONTEXT.md

text

## 3. Что уже работает (Статус на 26.10.2026)
### ✅ Парсинг и Каталог (Project 3)
- **База данных:** Supabase PostgreSQL (проект `china-goods`). RLS включен для всех таблиц.
- **Парсинг 1688:** Страница «Спарсить с 1688» в Streamlit. Использует Apify (`songd/1688-search-scraper`). 
- **ИИ-обработка:** После парсинга `gpt-4o-mini` (через ProxyAPI) переводит названия, убирает HTML-теги и автоматически распределяет товары по категориям (8 категорий: electronics, home-kitchen, toys, и т.д.).
- **Картинки:** Парсер сохраняет ссылки на изображения (`image_url` в JSONB-атрибутах). Они отображаются в списке и в карточке товара.
- **UI:** Streamlit (список с фильтрами, карточка редактирования, экспорт CSV).

### ⏳ Что еще НЕ сделано (Зона роста)
- **mini_crm:** Скопирован в монорепо, но работает изолированно на SQLite. Не переведен на общую базу Supabase.
- **vk_bot:** Работает локально, не пишет заявки в общую базу.
- **avito_module:** Только папка.

## 4. Ключевые технические решения (Грабли)
- **Supabase:** Обязательно использовать драйвер `psycopg` (v3), `poolclass=NullPool` и `prepare_threshold: None`.
- **VPN:** Обязателен для Supabase, Apify и загрузки картинок с `alicdn.com`.
- **Apify:** Токен в `.env` (`APIFY_TOKEN`). Из-за нового тарифа ($4.90 за 1000 товаров) нужно следить за балансом.
- **ИИ:** Используем ProxyAPI (модель `openai/gpt-4o-mini`). Ключ в `.env` (`PROXYAPI_KEY`).

## 5. План развития (Следующие шаги)
1. **Фаза 2: Переезд mini-CRM на PostgreSQL.** Настроить модели `Order`, `Client` в `shared/models.py` (связать `Order` с `Product` по `product_id`). Перевести `mini_crm` на общую базу.
2. **Фаза 3: Связка CRM + Парсер.** В CRM при создании заказа выбирать товар из спарсенного каталога (автоподстановка цены и маржи).
3. **Фаза 4: VK-бот -> CRM.** Научить бота писать заявки напрямую в таблицу `orders` в Supabase.
4. **Фаза 5: Мониторинг рисков.** Перенести логику `news-analyzer` в `china-goods` для отслеживания новостей о поставщиках, курсе и логистике.
5. **Деплой:** Streamlit Cloud для UI + VPS для бота.