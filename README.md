[![Workflow Status](https://github.com/matrosov85/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/matrosov85/foodgram-project-react/actions/workflows/yamdb_workflow.yml)

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)
[![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)](https://www.django-rest-framework.org/)
[![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)


# Продуктовый помощник
На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд...

## Проект развернут по адресу:
* http://matrosov85.ddns.net/api/v1/
* http://matrosov85.ddns.net/admin/
* http://matrosov85.ddns.net/redoc/


## Установка и запуск проекта

* Клонировать репозиторий и перейти в директорию backend:
```bash
git clone https://github.com/matrosov85/foodgram-project-react.git && cd backend
```

* Создать и активировать виртуальное окружение:
```bash
python -m venv venv && . venv/scripts/activate
```

* Обновить менеджер пакетов и установить зависимости:
```bash
python -m pip install --upgrade pip && pip install -r requirements.txt
```

* Cоздать файл `.env` со следующим содержимым:
```bash
SECRET_KEY=<secret_key>
DB_ENGINE=django.db.backends.postgresql 
DB_NAME=postgres 
POSTGRES_USER=postgres 
POSTGRES_PASSWORD=<password> 
DB_HOST=db 
DB_PORT=5432 
```

* Выполнить команду запуска контейнеров из директории `infra`:
```bash
cd infra && docker-compose up -d --build
```

* Создать и выполнить миграции:
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

* Создать суперпользователя:
```bash
docker-compose exec web python manage.py createsuperuser
```

* Собрать статику:
```bash
docker-compose exec web python manage.py collectstatic --no-input
```

* Создать дамп базы данных:
```bash
docker-compose exec web python manage.py dumpdata > fixtures.json
```

* Для остановки контейнеров выполнить команду:
```bash
docker-compose down
```