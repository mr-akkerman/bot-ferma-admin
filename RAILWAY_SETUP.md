# Настройка для Railway

## 🚀 Деплой на Railway

### 1. Подготовка PostgreSQL сервисов

В Railway создай **два PostgreSQL сервиса**:

**Сервис 1: Admin Database (для админов)**
- Название: `admin-db` 
- Автоматически создается переменная `DATABASE_URL`

**Сервис 2: Profiles Database (для статистики)**  
- Название: `profiles-db`
- Нужно настроить доступ только на чтение к твоей продакшен базе

### 2. Настройка переменных окружения

В настройках приложения Railway добавь:

#### Обязательные переменные:
```env
SECRET_KEY=your_super_secret_production_key_here
FLASK_ENV=production
```

#### Для базы данных профилей (вариант 1 - полная строка):
```env
PROFILES_DATABASE_URL=postgresql://readonly_user:password@your_host:5432/farm_profiles
```

#### Для базы данных профилей (вариант 2 - отдельные переменные):
```env
PROFILES_DB_HOST=your_profiles_host
PROFILES_DB_PORT=5432
PROFILES_DB_NAME=farm_profiles
PROFILES_DB_USER=readonly_user
PROFILES_DB_PASSWORD=readonly_password
```

### 3. Автоматические переменные Railway

Railway автоматически создаст:
- `DATABASE_URL` - будет использована для админской базы данных
- `PORT` - порт для приложения

### 4. Структура приложения

```
🔹 Admin Database (DATABASE_URL)
  └── таблица users (админы с полными правами)

🔹 Profiles Database (PROFILES_DATABASE_URL) 
  └── таблица profiles (только чтение, продакшен данные)
```

### 5. Проверка конфигурации

После деплоя в логах Railway ты увидишь:

```
🔧 Using configuration: ProductionConfig
🔒 Admin DB: postgresql://user:***@host:5432/admin_db  
📊 Profiles DB: postgresql://readonly:***@host:5432/profiles_db
✅ Admin database tables created/verified
✅ Создан дефолтный админ: admin/admin
```

### 6. Первый запуск

1. **Деплой**: `git push` в связанный репозиторий
2. **Логи**: Проверь логи развертывания в Railway
3. **Доступ**: Открой URL приложения
4. **Логин**: `admin` / `admin`
5. **Безопасность**: Сразу смени пароль админа!

### 7. Возможные проблемы

**❌ Ошибка инициализации БД админов:**
- Проверь `DATABASE_URL` в настройках Railway
- Убедись что PostgreSQL сервис запущен

**❌ Ошибка подключения к профилям:**
- Проверь `PROFILES_DATABASE_URL` или `PROFILES_DB_*`
- Убедись что продакшен база доступна
- Проверь права доступа readonly пользователя

**❌ Ошибка SECRET_KEY:**
- Добавь `SECRET_KEY` в переменные окружения Railway
- Используй криптографически стойкий ключ (не менее 32 символов)

### 8. Локальная разработка

Создай файл `.env` (скопируй из `env.example`):

```env
SECRET_KEY=dev_secret_key_change_in_production
FLASK_ENV=development

# Admin Database (локальный PostgreSQL)
ADMIN_DB_HOST=localhost
ADMIN_DB_PORT=5432
ADMIN_DB_NAME=admin_panel
ADMIN_DB_USER=postgres
ADMIN_DB_PASSWORD=password

# Profiles Database (подключение к продакшен)
PROFILES_DATABASE_URL=postgresql://readonly:pass@prod_host:5432/farm_profiles
```

Запуск: `python run.py`

## ✅ Готово!

Теперь у тебя есть полностью готовое приложение для Railway с двумя PostgreSQL базами данных!
