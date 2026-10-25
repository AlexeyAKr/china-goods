# PROJECT_CONTEXT — ChinaGoods

## О проекте

Монорепо для магазина ChinaGoods. Собирает воедино:
- **парсинг 1688** (что закупать)
- **mini-CRM** (учёт заказов и доставки)
- **VK-бот** (консультации клиентов)
- **parser_1688** (наполнение каталога)

**Цель:** полный цикл — от поиска товара в Китае до доставки клиенту.

**Репозиторий:** https://github.com/AlexeyAKr/china-goods

## Архитектура монорепо
china_goods/
├── shared/ # ядро: модели, БД, конфиг
├── parser_1688/ # Streamlit UI + парсинг 1688
├── mini_crm/ # копия mini-CRM (пока на SQLite)
├── vk_bot/ # копия VK-бота (gigachat 0.2.3)
├── avito_module/ # заготовка
└── PROJECT_CONTEXT.md

text

**Общая БД:** PostgreSQL на Supabase (проект `china-goods`)

## Стек

- Python 3.12, Streamlit 1.65+
- SQLAlchemy 2.1.4 + **psycopg 3.3.6** (НЕ psycopg2!)
- Supabase PostgreSQL 17.11
- Apify (`songd/1688-search-scraper`) — парсинг 1688
- ProxyAPI (`openai/gpt-4o-mini`) — очистка названий
- GigaChat — резерв (без VPN)
- Alembic 1.20.0 (для будущих миграций)

## Ключевые решения

| Решение | Почему |
|---|---|
| PostgreSQL, а не SQLite | Три машины, облако |
| `psycopg v3` + `prepare_threshold: None` + `NullPool` | Supabase pooler не поддерживает prepared statements |
| Apify вместо своего парсера | Не нужен прокси и обход антибота |
| ProxyAPI для чистки названий | GigaChat иногда с истекшим ключом |
| JSONB для атрибутов товаров | Гибкость без миграций |
| Отдельная таблица категорий | Фильтры, отсутствие опечаток |

## Модели данных

- **Category:** id, name, slug, parent_id
- **Supplier:** id, name, url_1688, rating, min_order_qty, contacts (JSONB)
- **Product:** id, name, category_id, supplier_id, price_cny, price_rub, weight_kg, markup_percent, source_url, sku_1688, parsed_at, attributes (JSONB)

## Текущий статус (19.10.2026)

### ✅ Сделано

- **Ядро проекта:** монорепо, `shared/`, Supabase PostgreSQL
- **MVP Project 3:** Streamlit UI — список, форма, карточка, фильтры, экспорт CSV
- **Sidebar:** курс юаня и тариф доставки с пересчётом
- **Парсинг 1688:** Apify + `test_apify_1688.py` — 100 товаров за 2 минуты
- **Импорт в БД:** `import_1688_to_db.py` — 93 товара сохранены
- **ИИ-чистка названий:** `clean_product_names.py` — GPT-4o-mini перевёл 93 названия
- **Безопасность:** токены только в `.env`, не в коде

### ✅ Достижения (25.10.2026)
- **Парсинг:** Страница «Спарсить с 1688» в Streamlit. Интеграция с Apify.
- **ИИ:** Автоматическая чистка названий и распределение по категориям (ProxyAPI / GPT-4o-mini).
- **Картинки:** Изображения извлекаются при парсинге и отображаются в списке товаров и в карточке.
- **Безопасность:** Включен RLS во всех таблицах Supabase.

### ⏳ Следующие шаги (по приоритету)

1. **Кнопка «Спарсить 1688» в Streamlit** — не запускать скрипт из терминала (30 мин)
2. **Автораспределение по категориям** — GPT определяет категорию при чистке (30 мин)
3. **Скриншоты каталога** — добавить в README (5 мин)
4. **Фаза 2 (отложена):** переезд mini-CRM с SQLite на PostgreSQL
5. **Фаза 4 (отложена):** VK-бот → запись заявок в CRM
6. **News-analyzer:** отдельный проект для мониторинга новостей (риски, тренды)

## Связанные проекты

### news-analyzer (отдельный репозиторий)
- **GitHub:** https://github.com/AlexeyAKr/news-analyzer
- **Назначение:** анализ новостного фона по активам через Perplexity + GPT
- **Потенциал:** мониторинг рисков для ChinaGoods (поставщики, логистика, курс)

### mini-crm-delivery (оригинал в портфолио)
- **GitHub:** https://github.com/AlexeyAKr/mini-crm-delivery
- **Live:** https://mini-crm-delivery-hnpcznbpw7siqqta2jpwkp.streamlit.app
- **Роль:** самостоятельный кейс в портфолио (принят куратором)

## Известные ограничения

- **VPN обязателен** для работы с Supabase и ProxyAPI из РФ
- **Apify** — платный после free trial ($5)
- **ProxyAPI** — платный, ключ периодически нужно пополнять
- Курс и тариф в sidebar не сохраняются между перезапусками
- **mini-CRM** пока на SQLite (Фаза 2 отложена)
- Репозиторий **Private** на GitHub

## Полезные команды

```powershell
# Запустить каталог
streamlit run parser_1688/app.py

# Спарсить новые товары с 1688
python test_apify_1688.py

# Импортировать в БД (указать DATASET_ID из прошлого запуска)
python import_1688_to_db.py

# Почистить названия через GPT
python clean_product_names.py
Ссылки
GitHub: https://github.com/AlexeyAKr/china-goods

Supabase: проект china-goods

Apify: https://console.apify.com

ProxyAPI: https://proxyapi.ru