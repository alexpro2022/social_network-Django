# Социальная сеть
[![Yatube CI/CD](https://github.com/alexpro2022/social_network-Django/actions/workflows/main.yml/badge.svg)](https://github.com/alexpro2022/social_network-Django/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/alexpro2022/social_network-Django/branch/master/graph/badge.svg?token=1ETL9DOJEB)](https://codecov.io/gh/alexpro2022/social_network-Django)

Социальная сеть для публикации личных дневников. 



## Оглавление:
- [Технологии](#технологии)
- [Описание работы](#описание-работы)
- [Установка и запуск](#установка-и-запуск)
- [Удаление](#удаление)
- [Автор](#автор)



## Технологии:
<details><summary>Развернуть</summary>

**Языки программирования, библиотеки и модули:**

[![Python](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue?logo=python)](https://www.python.org/)
[![Requests](https://img.shields.io/badge/-Requests:_HTTP_for_Humans™-464646?logo=Python)](https://pypi.org/project/requests/)
[![Pillow](https://img.shields.io/badge/-Pillow-464646?logo=Python)](https://pypi.org/project/Pillow/)

[![HTML](https://img.shields.io/badge/-HTML-464646?logo=HTML)](https://html.spec.whatwg.org/multipage/)


**Фреймворк, расширения и библиотеки:**

[![Django](https://img.shields.io/badge/-Django-464646?logo=Django)](https://www.djangoproject.com/)
[![sorl-thumbnail](https://img.shields.io/badge/-sorl--thumbnail-464646?logo=sorl-thumbnail)](https://sorl-thumbnail.readthedocs.io/en/latest/)


**База данных:**

[![SQLite3](https://img.shields.io/badge/-SQLite3-464646?logo=SQLite)](https://www.sqlite.com/version3.html)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?logo=PostgreSQL)](https://www.postgresql.org/)



**Тестирование:**

[![Pytest](https://img.shields.io/badge/-Pytest-464646?logo=Pytest)](https://docs.pytest.org/en/latest/)
[![Pytest-cov](https://img.shields.io/badge/-Pytest--cov-464646?logo=Pytest)](https://pytest-cov.readthedocs.io/en/latest/)
[![Coverage](https://img.shields.io/badge/-Coverage-464646?logo=Python)](https://coverage.readthedocs.io/en/latest/)


**CI/CD:**

[![GitHub_Actions](https://img.shields.io/badge/-GitHub_Actions-464646?logo=GitHub)](https://docs.github.com/en/actions)
[![docker_hub](https://img.shields.io/badge/-Docker_Hub-464646?logo=docker)](https://hub.docker.com/)
[![docker_compose](https://img.shields.io/badge/-Docker%20Compose-464646?logo=docker)](https://docs.docker.com/compose/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?logo=NGINX)](https://nginx.org/ru/)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?logo=Yandex)](https://cloud.yandex.ru/)
[![Telegram](https://img.shields.io/badge/-Telegram-464646?logo=Telegram)](https://core.telegram.org/api)

[⬆️Оглавление](#оглавление)
</details>



## Описание работы:
- Социальная сеть для публикации личных дневников. Это сайт, на котором можно создать свою страницу.
  - После регистрации пользователь получает свой профайл, то есть получает свою страницу
- Если на нее зайти, то можно посмотреть все записи автора.
  - После публикации каждая запись доступна на странице автора.
- Пользователи могут заходить на чужие страницы, подписываться на авторов и комментировать их записи.
- Автор может выбрать для своей страницы имя и уникальный адрес.
  - Эта часть реализована в момент регистрации. Мы не добавляли возможность изменять свой username: если бы сайт уже был в сети, то при смене имени пользователя старые ссылки на уже опубликованные записи перестали бы работать.
- Есть возможность модерировать записи и блокировать пользователей, если начнут присылать спам.
  - Эту часть мы получили вместе с интерфейсом администратора. Будем банить спамеров через админку.
- Записи можно отправить в сообщество и посмотреть там записи разных авторов.

[⬆️Оглавление](#оглавление)



## Установка и запуск:
Удобно использовать принцип copy-paste - копировать команды из GitHub Readme и вставлять в командную строку Git Bash или IDE (например VSCode).
### Предварительные условия для Docker Compose:
<details><summary>Развернуть</summary>

Предполагается, что пользователь:
 - создал аккаунт [DockerHub](https://hub.docker.com/), если запуск будет производиться на удаленном сервере.
 - установил [Docker](https://docs.docker.com/engine/install/) и [Docker Compose](https://docs.docker.com/compose/install/) на локальной машине или на удаленном сервере, где проект будет запускаться в контейнерах. Проверить наличие можно выполнив команды:
    ```bash
    docker --version && docker-compose --version
    ```
</details>
<hr>
<details>
<summary>Локальный запуск</summary> 

**!!! Для пользователей Windows обязательно выполнить команду:** иначе файл start.sh при клонировании будет бракован:
```bash
git config --global core.autocrlf false
```

1. Клонируйте репозиторий с GitHub: 
```bash
git clone https://github.com/alexpro2022/social_network-Django.git && \
cd social_network-Django
```

<details><summary>сервер Django/SQLite3</summary>

2. Введите данные для переменных окружения (значения даны для примера, но их можно оставить):
```bash
cp env_example .env && nano .env
```

3. Создайте и активируйте виртуальное окружение:
   * Если у вас Linux/macOS
   ```bash
    python -m venv venv && source venv/bin/activate
   ```
   * Если у вас Windows
   ```bash
    python -m venv venv && source venv/Scripts/activate
   ```

4. Установите в виртуальное окружение все необходимые зависимости из файла **requirements.txt**:
```bash
python -m pip install --upgrade pip && pip install -r yatube/requirements.txt
```

5. Выполните миграции, создайте суперюзера (потребуется ввод персональных данных) и запустите приложение:
```bash
cd yatube && \
python manage.py makemigrations && \
python manage.py migrate && \
python manage.py prepare_load_data && \
python manage.py loaddata dump.json && \
python manage.py createsuperuser && \
python manage.py runserver && cd ..
```
Сервер запустится локально по адресу http://127.0.0.1:8000/

6. Остановить сервер Django можно комбинацией клавиш Ctl-C.
<hr></details>

<details><summary>Docker Compose/PostgreSQL</summary>

2. Введите данные для переменных окружения (значения даны для примера, но их можно оставить):
```bash
cp env_docker .env && nano .env
```

3. Из корневой директории проекта выполните команду:
```bash
docker compose -f infra/local/docker-compose.yml up -d --build
```
Проект будет развернут в трех docker-контейнерах (db, web, nginx) по адресу http://localhost.

4. Остановить docker и удалить контейнеры можно командой из корневой директории проекта:
```bash
docker compose -f infra/local/docker-compose.yml down
```
Если также необходимо удалить тома базы данных, статики и медиа:
```bash
docker compose -f infra/local/docker-compose.yml down -v
```
</details><hr></details>

<details><summary>Запуск на удаленном сервере</summary>

1. Сделайте [форк](https://docs.github.com/en/get-started/quickstart/fork-a-repo) в свой репозиторий.

2. Создайте `Actions.Secrets` согласно списку ниже + переменные окружения из **env_example** файла:
```py
PROJECT_NAME
SECRET_KEY 

CODECOV_TOKEN 

DOCKERHUB_USERNAME 
DOCKERHUB_PASSWORD 

# Данные удаленного сервера и ssh-подключения:
HOST 
USERNAME 
SSH_KEY    
PASSPHRASE 

# Учетные данные Телеграм-бота для получения сообщения о успешном завершении workflow:
TELEGRAM_USER_ID 
TELEGRAM_BOT_TOKEN 

# База данных:
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_HOST=db
DB_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=12345
```

3. Запустите вручную `workflow`, чтобы автоматически развернуть проект в трех docker-контейнерах `db, web, nginx` на удаленном сервере.
</details>
<hr>

Вход в админ-зону осуществляется по адресу: http://`hostname`/admin/ , где `hostname`:
  * 127.0.0.1:8000
  * localhost
  * IP-адрес удаленного сервера  

**! Только для Docker Compose:**

При первом запуске будут автоматически произведены следующие действия:    
  * выполнены миграции БД
  * БД заполнена начальными данными
  * создан суперюзер (пользователь с правами админа) с учетными данными из переменных окружения `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD`.
  * собрана статика

[⬆️Оглавление](#оглавление)


## Удаление:
Для удаления проекта выполните следующие действия:
```bash
cd .. && rm -fr social_network-Django && deactivate
```
  
[⬆️Оглавление](#оглавление)
  


## Автор:
[Aleksei Proskuriakov](https://github.com/alexpro2022)

[⬆️В начало](#социальная-сеть)
