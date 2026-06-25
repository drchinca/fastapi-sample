# fastapi-sample

A minimal, idiomatic FastAPI app. Routes, schemas, and the app entry point are split into separate modules.

| Route   | Style              | Demonstrates                                                          |
|---------|--------------------|-----------------------------------------------------------------------|
| `/cars` | Full REST CRUD     | All verbs — `GET`, `POST`, `PUT`, `PATCH`, `DELETE` — on `Car { id, color, model }`. |
| `/tools`| MCP-style dispatch | `GET /tools` lists tools with JSON Schema; `POST /tools/run` dispatches by name. |

No env vars, no external services.

## Layout

```
.
├── main.py               # FastAPI app, includes routers
├── routers/
│   ├── cars.py           # /cars endpoints
│   └── tools.py          # /tools endpoints + tool handlers
├── schemas/
│   ├── cars.py           # Pydantic models for /cars
│   └── tools.py          # Pydantic models for /tools
└── requirements.txt
```

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Auto-generated docs: <http://localhost:8000/docs>.

## Try it

```bash
# CRUD on cars
curl -X POST localhost:8000/cars -H 'content-type: application/json' \
     -d '{"color":"red","model":"Tesla Model 3"}'
curl localhost:8000/cars
curl -X PATCH localhost:8000/cars/1 -H 'content-type: application/json' -d '{"color":"blue"}'
curl -X DELETE localhost:8000/cars/1

# MCP-style tool call
curl localhost:8000/tools
curl -X POST localhost:8000/tools/run -H 'content-type: application/json' \
     -d '{"tool":"add","arguments":{"a":2,"b":3}}'
```
