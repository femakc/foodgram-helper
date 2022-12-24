Учебный проект Foodgram
Описание
REST API для проекта Foodgram - «Продуктовый помощник». На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

http://адрес Продуктовый помощник
http://адрес/admin Админ-панель
СуперПользователь:
email:     admin@a.ru
password:  admin
login:     admin
CI и CD: Включает в себя 4 шага
example branch parameter

Tests: автоматический запуск тестов
Build: обновление образов на Docker Hub
Deploy: автоматический деплой на боевой сервер при пуше в главную ветку main
Inform: отправление сообщения в Telegram
Для реализации проекта используются:              ПРОВЕРИТЬ ВЕРСИИ !!!!!!!!!!
Python 3.7.9
Django 3.2.15
Django REST Framework 3.12.4
gunicorn 20.0.4
psycopg2-binary
docker
docker-compose
Ubuntu 20.04 LTS на сервере
Подготовка репозитория
В settings/secrets нужно подготовить ключи:              ПОМЕНЯТЬ ПЕРЕМЕННОЕ ОКРУЖЕНИЕ

- DOCKER_USERNAME - Username для DockerHub
- DOCKER_PASSWORD - Пароль для DockerHub
- HOST - хост или IP для deploy
- USER - Username на сервере
- SSH_KEY - Приватный ключ
- PASSPHRASE - Если ваш ssh-ключ защищён фразой-паролем
- DB_ENGINE - django.db.backends.postgresql_psycopg2
- DB_NAME - Имя базы данных
- POSTGRES_USER - Логин для подключения к базе данных 
- POSTGRES_PASSWORD - Пароль для подключения к БД
- DB_HOST - Название сервиса
- DB_PORT - порт для подключения к БД
Запуск проекта
Клонировать репозиторий и перейти в него в командной строке:

git clone https://github.com/Denis-Guselnikov/foodgram-project-react      ПОМЕНЯТЬ АДРЕСА !!!!!!!!
cd foodgram-project-react
Создать файл .env в infra/ и заполнить необходимыми данными:
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=db_name # имя базы данных
POSTGRES_USER=db_user # логин для подключения к базе данных
POSTGRES_PASSWORD=db_password # пароль для подключения к БД (установите свой)
DB_HOST=db_host # название сервиса (контейнера)
DB_PORT=5432  # порт для подключения к БД
SECRET_KEY=secret_key
Там же, нужно создать контейнеры:
docker-compose up -d --build
Выполните по очереди команды:
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py load_ingredients
docker-compose exec backend python manage.py load_tags
Создайте Суперпользователя:
docker-compose exec backend python manage.py createsuperuser
Запустить в браузере
http://localhost/
