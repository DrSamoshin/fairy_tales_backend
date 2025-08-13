# Coffee point DB (PostgreSQL)

## Архитектура

- **СУБД**: PostgreSQL
- **Хостинг**: Google Cloud SQL
- **Подключение**:
  - Через **Cloud SQL Proxy** (в Cloud Run)
  - Или по **внешнему IP** (локально, CI)

---
ENV

prod db - подключение через Cloud SQL Proxy (github secret)
* DB_USER Имя пользователя базы данных
* DB_PASS Пароль
* USE_CLOUD_SQL_PROXY true / false — использовать ли Cloud SQL Proxy
* INSTANCE_CONNECTION_NAME project:region:instance (для Cloud SQL Proxy)

local run подключение через IP
* DB_NAME Название базы данных
* DB_HOST Адрес хоста (например, localhost или внешний IP)
* DB_PORT Порт (обычно 5432)
---
