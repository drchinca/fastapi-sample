# fastapi-sample

A minimal, idiomatic FastAPI app with two endpoint groups:

| Route        | Style              | Demonstrates                                       |
|--------------|--------------------|----------------------------------------------------|
| `/items`     | Full REST CRUD     | All HTTP verbs (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) over a Pydantic resource backed by an in-memory repository. |
| `/tools`    | MCP-style dispatch | One `POST /tools/run` that routes to a named tool with a typed payload, plus `GET /tools` to list available tools. |

No environment variables, no external services — runnable as-is.

## Run

```bash
uv sync
uv run uvicorn app.main:app --reload
```

Then open the auto-generated docs: <http://localhost:8000/docs>.

## Layout

```
app/
├── main.py              # FastAPI app, router wiring
├── core/
│   └── dependencies.py  # Shared FastAPI dependencies
├── schemas/             # Pydantic request/response models
│   ├── items.py
│   └── tools.py
├── services/
│   └── items_repo.py    # In-memory repository (swap for a DB later)
├── tools/               # MCP-style tool registry
│   ├── registry.py
│   ├── echo.py
│   └── add.py
└── routers/
    ├── items.py         # CRUD router
    └── tools.py         # Tool dispatch router
```

## Examples

```bash
# CRUD
curl -X POST localhost:8000/items -H 'content-type: application/json' \
     -d '{"name":"Widget","price":9.99}'
curl localhost:8000/items
curl -X PATCH localhost:8000/items/1 -H 'content-type: application/json' -d '{"price":12.5}'
curl -X DELETE localhost:8000/items/1

# MCP-style tool call
curl -X POST localhost:8000/tools/run -H 'content-type: application/json' \
     -d '{"tool":"add","arguments":{"a":2,"b":3}}'
```
