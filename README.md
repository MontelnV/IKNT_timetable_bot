
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
