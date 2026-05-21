## ДОМАШНЕЕ ЗАДАНИЕ 35.2 (Продолжение ДЗ 30.1, 30.2, 31, 32.1, 32.2, 33)

#### Задание 1
Настроить удаленный сервер для работы с веб-приложением, 
которое разрабатывали в рамках домашних работ на курсе DRF.

#### Задание 2 
Создан и настроен файл GitHub Actions workflow, который:

- Запускает тесты проекта автоматически при каждом push в репозиторий.
- Автоматически деплоит проект на удаленный сервер после успешного прохождения тестов.

#### Дополнительное задание
Развернут проект на удаленном сервере с использованием Docker:  
Для этого:   
- Написан Dockerfile для проекта.
- Настроен GitHub Actions для автоматической сборки Docker-образа и его деплоя на удаленный сервер.

  
# CURS_5 — Трекер привычек с Telegram-уведомлениями

Сервис для отслеживания полезных и приятных привычек с интеграцией Telegram-бота для напоминаний. Построен на Django REST Framework с фоновыми задачами через Celery.

---

## Функциональность

- Регистрация и авторизация пользователей
- CRUD для привычек (полезных и приятных)
- Публичные привычки — можно делиться с другими пользователями
- Валидация: время выполнения ≤ 120 секунд, периодичность от 1 до 7 дней, связанная привычка только приятная
- Пагинация — 5 привычек на страницу
- Telegram-уведомления о запланированных привычках
- Документация API: Swagger и ReDoc

---

## Стек технологий

| Компонент | Технология |
|-----------|------------|
| Backend | Django 5.1, Django REST Framework |
| База данных | PostgreSQL 16 |
| Брокер сообщений | Redis 7 |
| Фоновые задачи | Celery (worker + beat) |
| Уведомления | Telegram Bot API |
| Веб-сервер | Nginx (проксирование + статика) |
| Контейнеризация | Docker, Docker Compose |
| CI/CD | GitHub Actions |

---

## Локальный запуск

### Предварительные требования

- Docker и Docker Compose (v2)
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))

### 1. Клонирование репозитория

```bash
git clone https://github.com/vladimirbutyrskii/CURS_5.git
cd CURS_5
2. Настройка переменных окружения
Создайте файл .env в корне проекта:

bash
cp .env.example .env
Отредактируйте .env, заполнив обязательные поля:

ini
SECRET_KEY=ваш-секретный-ключ-django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*

DB_HOST=db
DB_PORT=5432
DB_NAME=curs_5
DB_USER=postgres
DB_PASSWORD=ваш-пароль
POSTGRES_PASSWORD=ваш-пароль
POSTGRES_DB=curs_5

REDIS_HOST=redis
REDIS_PORT=6379

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

TELEGRAM_BOT_TOKEN=токен-вашего-бота
CORS_ALLOWED_ORIGINS=http://localhost:3000
NGINX_PORT=80
3. Запуск одной командой
bash
docker compose up -d
Сервис будет доступен:

API: http://localhost/api/

Swagger: http://localhost/swagger/

ReDoc: http://localhost/redoc/

4. Создание суперпользователя
bash
docker compose exec web python manage.py csu
5. Остановка
bash
docker compose down
Структура сервисов в Docker
Сервис	Порт	Описание
nginx	80	Проксирование запросов, раздача статики
web	8000 (внутр.)	Django + Gunicorn
db	5432 (внутр.)	PostgreSQL
redis	6379 (внутр.)	Брокер сообщений
celery_worker	—	Обработка фоновых задач
celery_beat	—	Периодические задачи (рассылка уведомлений)
Настройка CI/CD и деплоя на сервер
1. Подготовка удаленного сервера
Требования: Ubuntu 20.04+ с доступом по SSH.

bash
# Установка Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# Выйти и зайти заново

# Установка Docker Compose Plugin
sudo apt update
sudo apt install docker-compose-plugin -y

# Клонирование проекта
sudo mkdir -p /opt/curs5
sudo chown $USER:$USER /opt/curs5
git clone https://github.com/vladimirbutyrskii/CURS_5.git /opt/curs5
2. Настройка Self-Hosted Runner (GitHub Actions)
На сервере:

bash
mkdir ~/actions-runner && cd ~/actions-runner
curl -o actions-runner-linux-x64.tar.gz -L https://github.com/actions/runner/releases/download/v2.317.0/actions-runner-linux-x64-2.317.0.tar.gz
tar xzf actions-runner-linux-x64.tar.gz
В репозитории GitHub: Settings → Actions → Runners → New self-hosted runner.
Выбрать Linux, x64, скопировать команду ./config.sh и выполнить на сервере.

bash
sudo ./svc.sh install
sudo ./svc.sh start
3. Настройка GitHub Secrets
В репозитории: Settings → Secrets and variables → Actions → New repository secret

Добавьте секреты:

Secret	Описание
SECRET_KEY	Секретный ключ Django
ALLOWED_HOSTS	IP сервера, localhost, web, * (через запятую)
DB_NAME	Имя базы данных
DB_USER	Пользователь БД
DB_PASSWORD	Пароль БД
POSTGRES_PASSWORD	Пароль суперпользователя PostgreSQL
POSTGRES_DB	Имя создаваемой БД
TELEGRAM_BOT_TOKEN	Токен Telegram бота
CORS_ALLOWED_ORIGINS	Разрешенные CORS-источники
4. Как работает деплой
Вы делаете git push в ветку feature/curs_8

GitHub Actions запускает pipeline:

test — линтинг (flake8) + тесты (pytest)

build — проверка сборки Docker-образов

deploy — self-hosted runner на сервере:

git pull

Создает .env из GitHub Secrets

docker compose down && docker compose up -d --build

Применяет миграции

Собирает статику

Полезные команды
bash
# Логи сервисов
docker compose logs -f web
docker compose logs -f celery_worker

# Статус контейнеров
docker compose ps

# Перезапуск конкретного сервиса
docker compose restart celery_worker

# Выполнение команд в контейнере
docker compose exec web python manage.py shell_plus
docker compose exec web python manage.py createsuperuser

# Полный перезапуск
docker compose down && docker compose up -d
