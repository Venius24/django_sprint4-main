# Блогикум — учебный проект Django, спринт 4

Блог с публикациями, категориями, профилями пользователей и комментариями. Публичная лента показывает опубликованные записи с наступившей датой публикации. Автор может видеть свои скрытые и отложенные записи в профиле и на странице записи.

## Локальный запуск

Проверено с Python 3.12. Команды выполняются из корня репозитория:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe blogicum\manage.py migrate
.venv\Scripts\python.exe blogicum\manage.py runserver
```

Сайт откроется по адресу http://127.0.0.1:8000/. Регистрация доступна по `/auth/registration/`. SQLite, загруженные изображения и отправленные через файловый почтовый backend письма сохраняются локально в каталоге `blogicum`; они исключены из Git.

Настройки читают переменные окружения (пример значений — `.env.example`; файл не загружается автоматически): `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` (`1` или `0`) и `DJANGO_ALLOWED_HOSTS` (список через запятую). Для локальной разработки по умолчанию используются `DEBUG=1`, адреса `localhost,127.0.0.1` и заведомо небезопасный ключ-заглушка. Перед запуском с `DJANGO_DEBUG=0` обязательно задайте собственный ключ, например в PowerShell:

```powershell
$env:DJANGO_SECRET_KEY = 'replace-with-a-private-random-key'
$env:DJANGO_DEBUG = '0'
$env:DJANGO_ALLOWED_HOSTS = 'example.com'
```

## Проверки

```powershell
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe blogicum\manage.py test blog.tests
.venv\Scripts\python.exe blogicum\manage.py check
```

Это учебная конфигурация для локального запуска. Перед размещением в открытом доступе требуются отдельные настройки статики и почты; ключ из ранее опубликованной истории Git следует считать раскрытым и заменить там, где он использовался.
