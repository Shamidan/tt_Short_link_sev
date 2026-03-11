### 1. Запуск через Docker Compose

#### 1.1. Клонировать репозиторий
```bash
git clone https://github.com/Shamidan/tt_Short_link_sev.git
```
#### 1.2. Собрать и запустить контейнеры
```bash
docker-compose up --build -d
```

### 2. Работа методов

#### 2.1. /shorten

Создает короткую ссылку

На вход ссылка:
```json
{
  "original_url": "https://example.com/very/long/url"
}
```

Возвращает short_id и original_url:
```json
{
  "short_id": "abc123",
  "original_url": "https://example.com/very/long/url"
}
```

#### 2.2. /{short_id}
Редиректит на короткую ссылку

На вход:
short_id: string

На выход:
http://127.0.0.1:8000/abc123 -> Редирект на https://example.com/very/long/url

#### 2.3. /stats/{short_id} 

Возвращает статистику по short_id

На вход:
short_id: string

На выход:
```json
{
  "short_id": "abc123",
  "clicks": 1,
  "original_url": "https://example.com/very/long/url"
}
```


### 3. Запуск тестов

#### 3.1. Установка зависимостей
```bash
pip install req.txt
```

#### 3.2. Запуск тестов
```bash
 pytest tests/test_links.py -v
```

#### 4. Что тестируется
#### 4.1.Unit-тест: `test_unit_get_stats_raises_not_found`
Проверяет, что сервис выбрасывает исключение `LinkNotFoundError` при запросе статистики для несуществующей ссылки
- Мокает репозиторий и сессию БД
- Проверяет вызов метода `get_clicks_count`
- Ожидает исключение с ID несуществующей ссылки
#### 4.2. Unit-тест: `test_unit_create_link_handles_collisions`
Проверяет обработку коллизий при генерации короткого ID
- Мокает генератор ID, возвращающий повторяющиеся значения
- Мокает репозиторий, сообщающий о существующих ID
- Проверяет, что сервис продолжает генерировать ID пока не найдет уникальный
- Убеждается, что в итоге создается ссылка с уникальным ID
#### 4.3. Интеграционный тест: `test_api_create_and_redirect`
Проверяет полный цикл работы сервиса:
1. **POST /shorten** - создание короткой ссылки
   - Статус: 201 Created
   - Возвращает `short_id` и оригинальный URL
2. **GET /{short_id}** - редирект по короткой ссылке
   - Статус: 307 Temporary Redirect
   - Заголовок `location` содержит оригинальный URL
3. **GET /stats/{short_id}** - статистика переходов
   - Статус: 200 OK
   - Счетчик `clicks` увеличен до 1
#### 4.4. Интеграционный тест: `test_api_not_found_handling`
Проверяет обработку ошибок для несуществующих ссылок:
- **GET /{short_id}** с несуществующим ID → 404 Not Found
- **GET /stats/{short_id}** с несуществующим ID → 404 Not Found
- Проверяет сообщение об ошибке в ответе