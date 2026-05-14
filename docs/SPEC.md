# Specification — Restaurant Voice Ordering Agent

## 1. Purpose

The Restaurant Voice Ordering Agent is a phone and API based ordering assistant for a pizza restaurant. It lets a customer ask menu questions, place orders, modify pizzas, remove items, ask for totals, and complete checkout.

The system supports two interaction modes:

1. Twilio voice mode: customers call a Twilio phone number and speak naturally.
2. Local/API demo mode: testers send text requests to the Flask API.

The system is bounded to restaurant ordering tasks. It should not answer unrelated general knowledge questions.

## 2. Component Inventory

| Component | Module Path | Responsibility |
|---|---|---|
| Twilio/Flask server | `twilio_phone_server.py` | Receives phone/API requests, manages per-session state, returns TwiML or JSON |
| Agent core | `src/agent.py` | Main conversation controller; routes intents, updates state, returns user-facing responses |
| Intent parser | `src/intent_parser.py` | Converts customer text into structured intents using direct rules and LLM fallback |
| Order manager | `src/order_manager.py` | Stores, merges, modifies, and removes order items |
| Pricing | `src/pricing.py` | Computes subtotal, tax, and final total |
| RAG question answering | `src/rag_qa.py` | Answers menu knowledge questions using retrieved menu chunks |
| Knowledge builder | `src/knowledge_builder.py` | Builds menu and FAQ chunks from menu data |
| Chroma retriever | `src/retriever_chroma.py` | Retrieves semantically relevant menu chunks |
| LLM client | `src/llm_client.py` | Sends OpenAI-compatible chat completion requests |
| Prompts | `src/prompts.py` | Stores intent parser and RAG prompts |
| Response text/constants | `src/restaurant_text.py` | Stores fixed response templates, phrase markers, menu hints, and FAQ text |
| Configuration | `src/config.py` | Loads environment variables and runtime settings |

## 3. Data Flow

### 3.1 Twilio Voice Flow

1. Caller calls the Twilio number.
2. Twilio sends a request to `POST /voice`.
3. Flask creates or retrieves a session by `CallSid`.
4. Twilio speech recognition provides the caller's transcript as `SpeechResult`.
5. Flask passes `SpeechResult` to `handle_user_input()`.
6. The agent parses the intent, updates the order state, and returns a response string.
7. Flask wraps the response in TwiML using `<Say>` and `<Gather>`.
8. Twilio speaks the response and listens for the next caller utterance.

### 3.2 API Demo Flow

1. Tester sends `POST /api/chat` or `POST /debug` with JSON text input.
2. Flask creates or retrieves a session by `session_id` or `call_sid`.
3. Flask passes the text to `handle_user_input()`.
4. The agent returns a response and updated order state.
5. Flask returns JSON containing reply, order, and state.

### 3.3 Agent Flow

1. `handle_user_input()` checks active checkout state.
2. If no checkout step is active, it calls `parse_intent()`.
3. The parser first uses deterministic phrase/rule parsing.
4. If deterministic parsing cannot classify the request, the parser uses the LLM intent parser.
5. The agent executes the intent:
   - add item
   - remove item
   - modify pizza
   - change crust
   - calculate total
   - summarize order
   - answer menu question
   - start or continue checkout
6. The agent returns a short response suitable for phone conversation.

## 4. Public Interfaces

### 4.1 `GET /health`

Returns server health.

Response:

```json
{
  "status": "ok"
}