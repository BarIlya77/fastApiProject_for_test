# FastAPI Project for Test

Проект на FastAPI с PostgreSQL в Docker-контейнере для демонстрации возможностей.

## 📌 Особенности проекта

- FastAPI как основной фреймворк
- PostgreSQL в качестве базы данных
- Docker и Docker Compose для контейнеризации
- Автоматическая документация API через Swagger UI

## 🚀 Быстрый старт

### Предварительные требования
- Установленный Docker и Docker Compose
- Python 3.12

### Запуск проекта

1. Клонируйте репозиторий:
```bash
git clone https://github.com/BarIlya77/fastApiProject_for_test.git
cd fastApiProject_for_test
```
2. Запустите проект через Docker Compose:
```bash
docker-compose up -d --build
```
3. После запуска приложение будет доступно по адресу:
```bash
http://localhost:8000
```
4. Документация API (Swagger UI):
```bash
http://localhost:8000/docs
```
## 🔧 Технические детали

### Структура проекта
```
fastApiProject_for_test/
├── app/                  # Основной код приложения
│   ├── main.py           # Точка входа FastAPI
│   ├── database.py       # Настройки подключения к БД
│   ├── models.py         # SQLAlchemy модели
│   ├── schemas.py        # Pydantic-схемы
│   ├── fake_data.py      # Заполнение БД тестовыми данными
│   ├── routers.py        # Эндпойнты 
│   └── init.py
├── requirements.txt      # Зависимости Python
├── Dockerfile            # Конфигурация Docker
├── docker-compose.yml    # Конфигурация сервисов
└── .gitignore
```
### Используемые технологии
- FastAPI - современный фреймворк для API
- SQLAlchemy - ORM для работы с БД
- PostgreSQL - реляционная база данных
- Docker - контейнеризация приложения
- Uvicorn - ASGI-сервер