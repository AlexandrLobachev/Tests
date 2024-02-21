# Проект "Tests"

В том проекте применял на практике тестирование при помощи unittest и pytest.

## Автор:

[Александр Лобачев](https://github.com/AlexandrLobachev/)
<br>

## Технологии используемые в проекте:
- [Python 3.11](https://docs.python.org/release/3.11.5/)
- [Django 3.2](https://docs.djangoproject.com/en/3.2/)
- [Pytest 7.1.3](https://docs.pytest.org/en/7.1.x/)
- [Unittest](https://docs.python.org/3/library/unittest.html)
- [SQLite](https://www.sqlite.org/docs.html)

<br>

## Развёртывание проекта:
+ Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:AlexandrLobachev/Tests.git
```

```
cd tests/
```

+ Cоздать и активировать виртуальное окружение (Windows/Bash):
```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

<br>

## Тестирование проекта:
### Unittest
+ Перейти в директорию проекта `ya_note`:
```
cd ya_note/
```
+ Запустить тесты:
```
python manage.py test
```

### Pytest
+ Перейти в директорию проекта `ya_news`:
```
cd ya_news/
```
+ Запустить тесты:
```
pytest
```

<br>



