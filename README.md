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
На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Проект развернут по адресу:
* http://foodgram.freedynamicdns.net/
* http://foodgram.freedynamicdns.net/admin/
* http://foodgram.freedynamicdns.net/api/docs/


## Установка и запуск проекта

* Клонировать репозиторий:
```bash
git clone https://github.com/matrosov85/foodgram-project-react.git
```

* Создать и активировать виртуальное окружение:
```bash
python -m venv venv && . venv/scripts/activate
```

* Обновить менеджер пакетов и установить зависимости:
```bash
python -m pip install --upgrade pip && pip install -r requirements.txt
```

* В папке `infra` Cоздать файл `.env` со следующим содержимым:
```bash
SECRET_KEY=<secret_key>
CSRF_TRUSTED_ORIGINS=http://<host>
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

* Для остановки контейнеров выполнить команду:
```bash
docker-compose stop
```

## Примеры запросов к API

### Получение списка всех рецептов

[GET-запрос]:

```bash
.../api/recipes/
```

Доступно без токена.

Параметры запроса:
- **page** (integer) Номер страницы
- **limit**	(integer) Количество объектов на странице
- **is_favorited** (integer Enum: 0 1) Показывать только рецепты, находящиеся в списке избранного
- **is_in_shopping_cart** (integer Enum: 0 1) Показывать только рецепты, находящиеся в списке покупок
- **author** (integer) Показывать рецепты только автора с указанным id
- **tags** (Array of strings) Показывать рецепты только с указанными тегами (по slug)

Ответ API - (**200**):

```bash
{
    "count": 123,
    "next": "http://foodgram.example.org/api/recipes/?page=4",
    "previous": "http://foodgram.example.org/api/recipes/?page=2",
    "results": [
        {
            "id": 0,
            "tags": [
                {
                    "id": 0,
                    "name": "Завтрак",
                    "color": "#E26C2D",
                    "slug": "breakfast"
                }
            ],
            "author": {
                "email": "user@example.com",
                "id": 0,
                "username": "string",
                "first_name": "Вася",
                "last_name": "Пупкин",
                "is_subscribed": false
            },
            "ingredients": [
                {
                    "id": 0,
                    "name": "Картофель отварной",
                    "measurement_unit": "г",
                    "amount": 1
                }
            ],
            "is_favorited": true,
            "is_in_shopping_cart": true,
            "name": "string",
            "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
            "text": "string",
            "cooking_time": 1
        }
    ]
}
```

### Регистрация пользователя

[POST-запрос]:

```bash
.../api/users/
```

Body:

```bash
{
    "email": "vpupkin@yandex.ru",
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "password": "Qwerty123"
}
```

Ответ API - (**201**):

```bash
{
    "email": "vpupkin@yandex.ru",
    "id": 0,
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Пупкин"
}
```

Другие возможные ответы:
- **400** Отсутствует обязательное поле или оно некорректно


### Удалить рецепт из списка покупок

Доступно только авторизованным пользователям. Авторизация по токену.
Все запросы от имени пользователя должны выполняться с заголовком "Authorization: Token TOKENVALUE"

[DELETE-запрос]:

```bash
.../api/recipes/{id}/shopping_cart/
```

Параметры запроса:
- **id** (string) Уникальный идентификатор этого рецепта

Ответ API - (**204**):

Другие возможные ответы:
- **400** Ошибка удаления из списка покупок (например, когда рецепта там не было)
- **401** Пользователь не авторизован