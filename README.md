# fastapi-sample

Single-file FastAPI MVP. Two endpoint groups:

| Route        | Style              | Demonstrates                                      |
|--------------|--------------------|---------------------------------------------------|
| `/cars`      | Full REST CRUD     | All verbs — `GET`, `POST`, `PUT`, `PATCH`, `DELETE` — on a `Car` (color + model). |
| `/tools`     | MCP-style dispatch | `GET /tools` to discover tools with JSON Schema, `POST /tools/run` to call one by name. |

No env vars, no external services, no nested packages — everything lives in `main.py`.

## Run

```bash
uv sync
uv run uvicorn main:app --reload
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
