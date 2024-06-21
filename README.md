
## Настройка

Добавьте файл .env в корневой каталог с переменной TOKEN="BOT_TOKEN"

Сборка проекта:
  ```sh
  docker build . --tag bot
  ```
Запуск проекта:
  ```sh
  docker run -d --name bot bot
  ```

## Запуск без контейнера Docker

Создание venv:
  ```sh
  python -m venv venv
  ```
Активация venv:
  ```sh
  .\venv\Scripts\Activate.ps1
  ```
Установка библиотек:
  ```sh
  pip install -r requirements.txt
  ```
Запуск:
  ```sh
  python run.py
  ```
* После перезапуска приложения необходимо вручную удалить образ БД .db
* Для автоматического сброса раскомментируйте в файле run.py функцию drop_tables()
* Для тестового добавления секретаря (помимо вас) раскомментируйте 28: строки в файле app/handlers.py
