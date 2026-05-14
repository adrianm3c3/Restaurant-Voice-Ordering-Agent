# Logging

## Current Logging Behavior

The current system provides basic runtime logging through Flask request logs and a small number of application-level print statements.

Current logs include:

- Flask HTTP request logs, such as `GET /health HTTP/1.1" 200`
- Flask HTTP request logs for `/api/chat`
- Twilio `/voice` call logs showing what the caller said and what the assistant replied

The `/voice` route currently logs messages in this format:

[CALL_SID] Caller said: <transcribed caller speech>  
[CALL_SID] Assistant: <assistant reply>

Docker logs can be captured with:

docker compose logs app > reports/docker_logs.txt

## Request ID Strategy

The system has session identifiers that can be used as request trace keys:

| Endpoint | Request ID Source | Current Use |
|---|---|---|
| `/voice` | Twilio `CallSid` | Used in current print logs |
| `/api/chat` | JSON `session_id` | Used for session state, not yet fully logged |
| `/debug` | JSON `call_sid` | Used for debug session state |
| `/health` | Health check request | Logged by Flask request logs |

## Current Limitations

The current implementation does not yet provide full structured JSON logging.

The following are not fully implemented yet:

- JSON-formatted log lines
- Request ID propagation through every internal module
- `intent_parsed` log events
- `order_updated` log events
- RAG retrieval count logs
- LLM failure reason logs with redacted credentials

## Target Structured Logging Format

For production-level observability, the system should eventually log structured JSON lines with these fields:

| Field | Meaning |
|---|---|
| `timestamp` | ISO timestamp |
| `level` | Log level |
| `module` | Source module |
| `request_id` | Session ID or Twilio CallSid |
| `event` | Machine-readable event name |
| `message` | Human-readable summary |

Example target log lines:

{"timestamp":"2026-05-14T14:00:00Z","level":"INFO","module":"twilio_phone_server","request_id":"demo","event":"request_received","message":"Received /api/chat request"}  
{"timestamp":"2026-05-14T14:00:00Z","level":"INFO","module":"agent","request_id":"demo","event":"intent_parsed","message":"Parsed add_item intent"}  
{"timestamp":"2026-05-14T14:00:00Z","level":"INFO","module":"order_manager","request_id":"demo","event":"item_added","message":"Added large pepperoni pizza"}  
{"timestamp":"2026-05-14T14:00:00Z","level":"INFO","module":"twilio_phone_server","request_id":"demo","event":"response_sent","message":"Returned assistant reply"}

These are target examples, not the current complete implementation.

## Privacy Considerations

Logs may contain raw customer text. For example, checkout logs may include names, pickup times, and order preferences.

The project should not log:

- Payment card numbers
- Full addresses
- Sensitive personal data
- API keys
- `.env` contents
- Twilio auth tokens

## Recommended Future Improvements

- Replace print statements with Python `logging`.
- Add a shared JSON logger utility.
- Log `/api/chat` requests with `session_id`.
- Pass `request_id` into `agent.py`, `order_manager.py`, `rag_qa.py`, and `llm_client.py`.
- Log intent parser output.
- Log order update events.
- Log RAG retrieval count and fallback reason.
- Log LLM errors without exposing credentials.