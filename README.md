# Voice Agent Ryan (FastAPI + VAPI + Google Calendar)

Simple webhook service that accepts event data and can relay it to Google Calendar. Designed for local development with ngrok and deploys to Render.

## Features

- FastAPI endpoint: `POST /create-event`
- GET + POST handler to support webhook validation and events
- Pydantic request model (`name`, `date`, `time`, `title`)
- Optional Google Calendar integration via service account credentials
- Local ngrok test URL for VAPI callback testing

## Quickstart (local)

1. Clone project

```bash
git clone <repo-url>
cd Voice-agent-Ryan
```

2. Install Python dependencies

```bash
pip install fastapi uvicorn google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib
```

3. Set Google service account credentials (optional)

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

4. Start FastAPI server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. Start ngrok (for VAPI or remote webhook testing)

```bash
ngrok http 8000
```

6. Confirm endpoints

- `GET /create-event` -> readiness check
- `POST /create-event` -> event ingestion

Sample POST request:

```bash
curl -X POST "https://<ngrok-id>.ngrok.io/create-event" \
  -H "Content-Type: application/json" \
  -d '{"name":"Manav","date":"2026-03-20","time":"15:00","title":"Test meeting"}'
```

## VAPI (or any webhook provider)

- Callback URL: `https://<your-ngrok-url>/create-event`
- Method: `POST` (some services may verify with `GET` first)
- JSON model:
  - `name` (string)
  - `date` (YYYY-MM-DD)
  - `time` (HH:MM)
  - `title` (optional)

> If your provider sends uppercase keys (`Name`, `Date`), configure Pydantic aliases or normalize payload before creating the model.

## Google Calendar integration

The app supports `create_google_event` from `main.py`.

- Requires `GOOGLE_APPLICATION_CREDENTIALS` pointing to a service account JSON file with Calendar API scope.
- Creates a 1-hour event from provided `date` + `time`.

## Deploy to Render

1. Create a new Web Service on Render (Docker or Python).
2. Set build command (if needed): `pip install -r requirements.txt`.
3. Set start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

4. Add environment variables in Render:

- `GOOGLE_APPLICATION_CREDENTIALS` is not directly editable for file paths. Use Render Secret + startup script to write credentials to disk.
- `PYTHONPATH` (if using modules)

### Render service account file example

In **Environment** → **Secrets**:
- `GOOGLE_SERVICE_ACCOUNT_JSON` = content of JSON file.

In **Start Command**:

```bash
mkdir -p /tmp/keys
cat <<'EOF' > /tmp/keys/gsa.json
$GOOGLE_SERVICE_ACCOUNT_JSON
EOF
export GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/gsa.json
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Troubleshooting

- `405 Method Not Allowed`: check endpoint method. Use GET for probes and POST for webhook payloads.
- `422 Unprocessable Entity`: payload keys or format mismatch. Ensure required fields exist.
- Use ngrok inspector: `http://127.0.0.1:4040` for request history.

## License

MIT
