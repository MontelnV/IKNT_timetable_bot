
## Настройка

Добавьте файл .env в корневой каталог с переменной TOKEN="BOT_TOKEN"

Сборка проекта:
  ```sh
  docker build . --tag events-backend
  ```
Запуск проекта:
  ```sh
  docker run -d --name bot bot
  ```
