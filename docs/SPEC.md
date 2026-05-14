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
```

## 5. Model and Prompt Selection

### 5.1 Conversational, Intent Parsing, and Embedding Models

The system uses OpenAI-compatible large language models to handle the conversation, intent parsing, and semantic embedding generation for ChromaDB retrieval.

Model configuration:

Agent model:
`meta-llama/Llama-3.1-8B-Instruct`

Parser model:
`meta-llama/Llama-3.1-8B-Instruct`

Embedding model:
`sentence-transformers/all-MiniLM-L6-v2`

The models are accessed through an OpenAI-compatible API endpoint
configured through environment variables.

Configuration source:
`src/config.py`

Relevant configuration:

```python
"model": {
    "agent": "meta-llama/Llama-3.1-8B-Instruct",
    "parser": "meta-llama/Llama-3.1-8B-Instruct",
    "embedding": "all-MiniLM-L6-v2",
}
```

### 5.2 Prompt Design

Prompt templates are stored in:

`src/prompts.py`

The system separates prompts into:
- intent parsing prompts
- retrieval-augmented generation (RAG) prompts

This separation allows the system to use different constraints and behaviors
for structured parsing versus conversational answering.

---

#### 5.2.1 Intent Parsing Prompts

The intent parser prompt converts natural language restaurant requests
into structured JSON intents.

Primary prompt variables:
- menu context
- customer request text

The parser prompt enforces:
- valid JSON-only output
- no markdown or explanations
- intent restriction to supported restaurant actions
- menu item grounding to known menu data

Intents Performed:
- add_item
- remove_named_item
- remove_item
- get_total
- checkout
- menu_query
- retrieval_qa
- get_order_count
- get_order_summary
- ask_last_removed
- modify_last_pizza
- change_pizza_crust
- unknown

The parser prompt defines explicit JSON schemas for:
- pizza orders
- sides
- drinks
- desserts
- retrieval queries
- pizza modifications
- crust changes

The parser prompt also constrains the model to:
- avoid hallucinated menu items
- avoid adding toppings not explicitly requested
- return "unknown" when classification confidence is low

The parser uses deterministic settings for reproducibility and decrease output variability:
- temperature = 0.0
- strict JSON output

---

#### 5.2.2 Retrieval-Augmented Generation (RAG) Prompts

The RAG prompts answer menu knowledge questions using retrieved
restaurant information.

The RAG system prompt instructs the model to:
- answer only from retrieved context
- avoid hallucinated menu items
- avoid unsupported nutrition claims
- avoid unsupported allergy guarantees
- avoid unsupported dietary labels
- return uncertainty when information is unavailable

The RAG prompt uses strict rules to reduce hallucinations.

The retrieved context may include:
- menu descriptions
- ingredients
- pricing
- FAQ entries
- restaurant policies
- modification policies

The RAG user prompt injects:
- retrieved restaurant information
- customer question

into the final prompt sent to the conversational model.

The generated response should:
- remain grounded in retrieved information
- remain short and conversational
- be suitable for phone-based interaction
- avoid unsupported assumptions

If retrieved information does not support the requested claim,
the system should state that the information is unavailable.


