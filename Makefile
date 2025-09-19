.PHONY: test test-structure test-app test-models test-init-db test-templates help install

# Основная команда для запуска всех тестов через pytest
test:
	@echo "Запуск всех тестов через pytest..."
	.venv/bin/python -m pytest -v

# Отдельные команды для конкретных тестов
test-structure:
	@echo "Запуск теста структуры проекта..."
	.venv/bin/python -m pytest test_structure.py -v

test-app:
	@echo "Запуск теста Flask приложения..."
	.venv/bin/python -m pytest test_app.py -v

test-models:
	@echo "Запуск тестов моделей..."
	.venv/bin/python -m pytest test_models.py -v

test-init-db:
	@echo "Запуск тестов инициализации БД..."
	.venv/bin/python -m pytest test_init_db.py -v

test-templates:
	@echo "Запуск тестов шаблонов..."
	.venv/bin/python -m pytest test_templates.py -v

# Установка зависимостей
install:
	.venv/bin/pip install -r requirements.txt

# Помощь по доступным командам
help:
	@echo "Доступные команды:"
	@echo "  make test           - Запустить все тесты через pytest"
	@echo "  make test-structure - Запустить только тест структуры"
	@echo "  make test-app       - Запустить только тест приложения"
	@echo "  make test-models    - Запустить только тесты моделей"
	@echo "  make test-init-db   - Запустить только тесты инициализации БД"
	@echo "  make test-templates - Запустить только тесты шаблонов"
	@echo "  make install        - Установить зависимости"
	@echo "  make help           - Показать эту справку"
