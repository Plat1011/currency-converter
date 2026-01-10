# Currency Converter

Full-stack учебный проект: конвертер валют с backend на FastAPI и frontend на Vite.
Backend берёт список валют и курсы из внешнего сервиса (Frankfurter API), фронт позволяет выбрать валюты, ввести сумму и получить результат конвертации.

## Features
- Получение доступных валют: `GET /currencies`
- Конвертация: `POST /convert`
- Отображение результата на UI
- Базовая клиентская валидация суммы (кнопка Convert отключается при `amount <= 0`)
- CI: backend (ruff + pytest), frontend (npm ci + build, тесты если есть)

## Tech Stack
**Backend:** FastAPI, httpx, Pydantic  
**Frontend:** Vite, Vanilla JS, HTML/CSS  
**CI:** GitHub Actions

---

## API

### `GET /currencies`
Возвращает словарь код -> название валюты.

Пример ответа:
```json
{
  "currencies": {
    "USD": "United States Dollar",
    "EUR": "Euro"
  }
}```
### `POST /convert`
Пример запроса:
```json
{
  "amount": 1,
  "from_currency": "USD",
  "to_currency": "EUR"
}```
Пример ответа:
```json
{
  "amount": 1,
  "from_currency": "USD",
  "to_currency": "EUR",
  "rate": 0.85896,
  "result": 0.85896
}```

