# API Response Examples (Phase 6)

These examples were captured and normalized from the Requests-based API integration suite in `tests/integration/api/`.

Date captured: 2026-04-29
Environment: local dev (`.venv`, SQLite)

## 1) Token authentication success

`POST /api/auth/token/`

```json
{
  "token": "<redacted-token>"
}
```

## 2) Books list response (authenticated)

`GET /api/books/`

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "The Hobbit",
      "author": 1,
      "summary": "...",
      "isbn": "9780000000001",
      "genre": [1],
      "language": 1
    }
  ]
}
```

## 3) Book instance detail response

`GET /api/book-instances/<id>/`

```json
{
  "id": "5f0f8f8f-1111-2222-3333-444444444444",
  "book": 1,
  "imprint": "1st",
  "due_back": "2026-05-10",
  "borrower": 2,
  "status": "o",
  "is_overdue": false
}
```

## 4) Catalog stats response

`GET /api/stats/`

```json
{
  "book_count": 2,
  "book_instance_count": 3,
  "book_instance_available_count": 1,
  "author_count": 2,
  "genre_count": 2,
  "language_count": 1
}
```

## 5) Unauthenticated access rejection

`GET /api/books/` (without token)

```json
{
  "detail": "Authentication credentials were not provided."
}
```

## Notes

- Exact IDs and counts vary by fixture data.
- Required payload keys and status-code behaviors are asserted by the integration test suite.
