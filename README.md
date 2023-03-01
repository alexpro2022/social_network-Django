# Проект: социальная сеть Yatube
[![status](https://github.com/alexpro2022/hw05_final/actions/workflows/python-app.yml/badge.svg)](https://github.com/alexpro2022/hw05_final/actions)
[![codecov](https://codecov.io/gh/alexpro2022/hw05_final/branch/master/graph/badge.svg?token=1ETL9DOJEB)](https://codecov.io/gh/alexpro2022/hw05_final)

Социальная сеть для публикации личных дневников. Это сайт, на котором можно создать свою страницу. 
Если на нее зайти, то можно посмотреть все записи автора.
Пользователи могут заходить на чужие страницы, подписываться на авторов и комментировать их записи. 
Автор может выбрать для своей страницы имя и уникальный адрес.
Есть возможность модерировать записи и блокировать пользователей, если начнут присылать спам.
Записи можно отправить в сообщество и посмотреть там записи разных авторов.


## Оглавление:
- [Технологии](#технологии)
- [Описание работы](#описание-работы)
- [Установка](#установка)
- [Запуск](#запуск)
- [Автор](#автор)


## Технологии:
[![Python](https://warehouse-camo.ingress.cmh1.psfhosted.org/7c5873f1e0f4375465dfebd35bf18f678c74d717/68747470733a2f2f696d672e736869656c64732e696f2f707970692f707976657273696f6e732f7072657474797461626c652e7376673f6c6f676f3d707974686f6e266c6f676f436f6c6f723d464645383733)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/-Pytest-464646?logo=Pytest)](https://docs.pytest.org/en/latest/)
[![Pytest-cov](https://img.shields.io/badge/-Pytest-*cov-464646?logo=Pytest)](https://pytest-cov.readthedocs.io/en/latest/)
[![Coverage](https://img.shields.io/badge/-Coverage-464646?logo=Python)](https://coverage.readthedocs.io/en/latest/)
[![Faker](https://img.shields.io/badge/-Faker-464646?logo=Python)](https://pypi.org/project/Faker/)
[![Pillow](https://img.shields.io/badge/-Pillow-464646?logo=Python)](https://pypi.org/project/Pillow/)
[![Requests](https://img.shields.io/badge/-Requests:_HTTP_for_Humans™-464646?logo=Python)](https://pypi.org/project/requests/)

[![Django](https://img.shields.io/badge/-Django-464646?logo=Django)](https://www.djangoproject.com/)
[![sorl-thumbnail](https://img.shields.io/badge/-sorl--thumbnail-464646?logo=Django)](https://pypi.org/project/sorl-thumbnail/)
[![mixer](https://img.shields.io/badge/-mixer-464646?logo=Django)](https://pypi.org/project/mixer/)

[![GitHub](https://img.shields.io/badge/-GitHub-464646?logo=GitHub)](https://docs.github.com/en)
[![GitHub_Actions](https://img.shields.io/badge/-GitHub_Actions-464646?logo=GitHub)](https://docs.github.com/en/actions)

[![Telegram](https://img.shields.io/badge/-Telegram-464646?logo=Telegram)](https://core.telegram.org/api)

[⬆️Оглавление](#оглавление)


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


## Установка:
1. Клонировать репозиторий с GitHub:
```
git clone git@github.com:alexpro2022/hw05_final.git
```

2. Перейти в созданную директорию проекта:
```
cd hw05_final
```

3. Создать и активировать виртуальное окружение:
```
python -m venv venv
```
* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/Scripts/activate
    ```

4. Установить все необходимые зависимости из файла **requirements.txt**:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
pip list
```

[⬆️Оглавление](#оглавление)


## Запуск:
Выполните команду:

```
python yatube/manage.py runserver
```
Сервер запустится локально по адресу http://127.0.0.1:8000/

[⬆️Оглавление](#оглавление)


## Автор:
[Aleksei Proskuriakov](https://github.com/alexpro2022)

[⬆️В начало](#Проект-социальная-сеть-Yatube)