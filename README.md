# fastapi-sample

Minimal FastAPI app: car CRUD, random users, a Marketo SSFS flow action, and a few dev test routes.

## Layout

```
.
├── main.py                 # app entry, wires routers
├── auth_methods/
│   └── auth.py             # optional Basic auth for SSFS
├── endpoints/
│   ├── cars.py             # /cars CRUD
│   └── users.py            # GET /users
├── schemas/
│   ├── cars.py
│   └── users.py
├── utils/
│   └── users.py            # random name/email helpers
├── ssfs/
│   ├── routes.py           # Marketo flow action (Adobe path names)
│   └── openapi.json        # SSFS spec for Marketo install
├── dev/
│   └── routes.py           # local auth/ping playground
├── tests/
│   └── test_ssfs.py        # auth + async + callback delivery tests
├── .env.example
└── requirements.txt
```

## Routes

| Route | Auth | Purpose |
| --- | --- | --- |
| `GET/POST/PUT/PATCH/DELETE /cars` | none | In-memory car CRUD |
| `GET /users?count=10` | none | List users with random names/emails |
| `GET /health` | none | Liveness probe |
| `GET /` | none | Links to docs and Marketo install URL |
| `GET /install` | none | Marketo SSFS OpenAPI spec |
| `GET /getServiceDefinition` | Basic* | SSFS service definition |
| `GET /status` | Basic* | SSFS health for Marketo nightly poll |
| `POST /submitAsyncAction` | Basic* | SSFS async flow step + callback |
| `POST /marketo-test` | none | Dev: `hello <user>` if Basic sent |
| `GET/POST /marketo-key` | none | Dev: ping/pong |

\*Basic auth is enforced only when both `MARKETO_USER` and `MARKETO_PASSWORD` are set.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional
uvicorn main:app --reload --port 8088
```

- Swagger UI: http://localhost:8088/docs
- App OpenAPI (all routes): http://localhost:8088/openapi.json
- Marketo install spec: http://localhost:8088/install

## Environment variables

Copy `.env.example` to `.env`. All are optional for local dev.

| Variable | Purpose |
| --- | --- |
| `MARKETO_USER` | Basic auth username for SSFS routes |
| `MARKETO_PASSWORD` | Basic auth password for SSFS routes |
| `API_BASE_URL` | Overrides `servers.url` in `/install` OpenAPI |

On Replit, set `MARKETO_USER` and `MARKETO_PASSWORD` before connecting Marketo.

## Try it

```bash
# Random users
curl "http://localhost:8088/users?count=3"

# Car CRUD
curl -X POST http://localhost:8088/cars \
  -H 'content-type: application/json' \
  -d '{"color":"red","model":"Tesla Model 3"}'
curl http://localhost:8088/cars

# Dev playground
curl -X POST http://localhost:8088/marketo-test
curl http://localhost:8088/marketo-key

# SSFS (with .env creds)
curl -u marketo:secret http://localhost:8088/getServiceDefinition
curl -u marketo:secret http://localhost:8088/status
```

## Marketo SSFS

Adobe Self-Service Flow Actions require fixed path names (`/submitAsyncAction`, etc.) and a validated OpenAPI file. That contract lives in `ssfs/` — the rest of the app is normal Python.

1. Deploy the app (e.g. Replit).
2. Set `MARKETO_USER` and `MARKETO_PASSWORD` in secrets.
3. In Marketo: **Admin → Service Providers → Add New Service**.
4. Install URL: `https://<your-host>/install`
5. Enter the same Basic credentials when prompted.

The flow step assigns each lead a random `generated_email` and `generated_name` via the SSFS callback.

**Async contract**: `POST /submitAsyncAction` returns `201` immediately and POSTs the
result to Marketo's `callbackUrl` in a background task (with `x-api-key` and
`x-callback-token` headers). Synchronous invocation is not supported per the
SSFS spec — failed callbacks are logged but do not change the 201 ack.

## Tests

```bash
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/test_ssfs.py -v
```

14 tests cover: `/install` shape + server-URL rewrite, Basic auth gate
(401 when wrong, 200 when valid, bypassed when env vars unset), required-field
validation on `/submitAsyncAction`, async 201 ack, callback delivery with
correct headers + body (asserted via `respx`), and 201 contract holding when
the callback target returns 500 or is unreachable.

Validate the spec locally (optional):

```bash
git clone https://github.com/adobe/Marketo-SSFS-Service-Provider-Interface.git
cd Marketo-SSFS-Service-Provider-Interface
npm install
node -e "require('./scripts/validate').validateFile('$(pwd)/../fastapi-sample/ssfs/openapi.json', './schema.yaml')"
```

Reference: [Adobe Marketo SSFS Service Provider Interface](https://github.com/adobe/Marketo-SSFS-Service-Provider-Interface)
