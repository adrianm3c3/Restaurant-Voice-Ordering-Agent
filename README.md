# Restaurant Voice Ordering Agent

A phone and API based restaurant ordering assistant for a pizza restaurant. The system lets a customer ask menu questions, place pizza orders, modify items, ask for totals, and complete checkout. It supports Twilio voice calls, a Flask webhook server, and a local API endpoint for automated testing and grading.

## Project Summary

This project demonstrates an NLP/agentic AI restaurant ordering system. The application accepts natural language customer input, parses the customer’s intent, tracks order state, answers menu questions using retrieval augmented generation, calculates totals, and guides the customer through checkout.

The project supports three interaction paths:

1. Twilio voice mode: caller speaks to a Twilio phone number. Phone number is +1 210 981 4764 with limited minutes (around 10 minutes)
2. API mode: tester sends text to `/api/chat`.
3. Debug/local mode: developer sends JSON requests to test the agent without Twilio.

For grading and reproducibility, the recommended path is the Docker + `/api/chat` API mode.

## Tech Stack

- Python 3.10
- Flask
- Twilio Programmable Voice
- ChromaDB
- Sentence Transformers
- OpenAI-compatible LLM client
- Pytest
- Pytest-cov
- Docker / Docker Compose

## Features

- Twilio voice webhook at `/voice`
- Local grading/test API at `/api/chat`
- Health endpoint at `/health`
- Restaurant menu question answering with RAG
- Pizza, side, drink, and dessert ordering
- Pizza topping modification
- Pizza crust changes
- Item removal
- Order summary
- Total calculation with tax
- Multi-step checkout flow
- Session-based order state
- Out-of-scope question handling

## Quick Start

### 1. Clone the repository

git clone https://github.com/adrianm3c3/Restaurant-Voice-Ordering-Agent.git

cd ResturauntProject

### 2. Create environment file

Linux/macOS:

cp .env.example .env

Windows PowerShell:

Copy-Item .env.example .env -Force

### 3. Start the system with Docker

docker compose up --build

The application should start at:

http://127.0.0.1:5000

### 4. Check health

Linux/macOS:

curl http://127.0.0.1:5000/health

Windows PowerShell:

Invoke-RestMethod http://127.0.0.1:5000/health

Expected response:

{
  "status": "ok"
}

### 5. Test the ordering API

Windows PowerShell:

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/chat" `
  -ContentType "application/json" `
  -Body '{"session_id":"demo","text":"I want a large pepperoni pizza"}'

Expected reply:

Added 1 large pepperoni pizza with hand tossed.

Then test that the session remembers the order:

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/chat" `
  -ContentType "application/json" `
  -Body '{"session_id":"demo","text":"what is my total"}'

Expected reply:

Your total is $14.04.

## Twilio Voice Mode

The Twilio webhook endpoint is:

POST /voice

For local development, expose the Flask server with ngrok:

ngrok http 5000

Then configure the Twilio phone number voice webhook:

https://banked-fervor-scouts.ngrok-free.dev/voice

Method:

HTTP POST

In this mode:

Caller speech  
→ Twilio speech recognition  
→ Flask /voice  
→ Restaurant agent  
→ TwiML response  
→ Twilio text-to-speech  
→ Caller hears response

The local Whisper and pyttsx3 scripts are optional utilities and are not required for the Docker grading path.

## API Endpoints

### GET /health

Checks whether the server is running.

Example response:

{
  "status": "ok"
}

### POST /api/chat

Primary grading and local testing endpoint.

Request:

{
  "session_id": "demo",
  "text": "I want a large pepperoni pizza"
}

Response:

{
  "session_id": "demo",
  "user_text": "I want a large pepperoni pizza",
  "reply": "Added 1 large pepperoni pizza with hand tossed.",
  "order": [],
  "state": {}
}

### POST /voice

Twilio webhook endpoint.

Expected Twilio form fields:

| Field | Description |
|---|---|
| `CallSid` | Twilio call/session ID |
| `SpeechResult` | Caller speech transcribed by Twilio |

Response format:

TwiML XML

## Source Layout

src/  
  agent.py                 Main conversation and action routing logic  
  intent_parser.py         Rule-based and LLM-backed intent parsing  
  order_manager.py         Order state management  
  pricing.py               Subtotal, tax, and total calculation  
  rag_qa.py                Retrieval-augmented menu question answering  
  knowledge_builder.py     Builds menu and FAQ knowledge chunks  
  retriever_chroma.py      Chroma vector retrieval  
  llm_client.py            OpenAI-compatible LLM client  
  prompts.py               Intent parser and RAG prompts  
  restaurant_text.py       Response text, phrase triggers, FAQ text  
  config.py                Environment/config loading  

tests/  
  user_stories/            User story acceptance tests  
  integration/             API and RAG integration tests  
  edge/                    Edge case tests  
  load/                    Load tests  

docs/  
  SPEC.md                  System specification  
  STORIES.md               User stories and walkthroughs  
  REPRODUCE.md             Reproduction instructions  
  DATA.md                  Data provenance  
  MODELS.md                Model provenance  
  MODEL_CARD.md            Responsible AI model card  
  LOGGING.md               Logging strategy  
  usage.md                 Story-by-story usage guide  
  benchmarks.md            Load/stress benchmark notes  

grading/  
  manifest.yaml            Reproducibility manifest  
  traceability.yaml        Story-to-code-to-test traceability  

## Running Tests

Install dependencies locally:

pip install -r requirements.txt

Build the vector store:

python -m src.build_vector_store

Run all tests:

pytest tests --junitxml=reports/user_stories.xml --cov=src --cov-report=xml:reports/coverage.xml --cov-report=html:reports/coverage_html -v

Expected current result:

22 passed

## Reproduction

The expected reproduction path is:

cp .env.example .env  
docker compose up --build

Then run:

pytest tests --junitxml=reports/user_stories.xml --cov=src --cov-report=xml:reports/coverage.xml --cov-report=html:reports/coverage_html -v

See:

docs/REPRODUCE.md

## Current Results

| Check | Expected Result |
|---|---|
| Docker build | Successful |
| Docker health check | HTTP 200 |
| `/api/chat` pizza order | Adds pizza |
| `/api/chat` total query | Returns `$14.04` for large pepperoni pizza |
| User story tests | 100% pass |
| API integration tests | 100% pass |
| RAG integration tests | 100% pass |
| Current full test run | 22 passed |

## Documentation

| Document | Purpose |
|---|---|
| `docs/SPEC.md` | Full system specification |
| `docs/STORIES.md` | User stories and manual walkthroughs |
| `docs/usage.md` | Exact commands for each user story |
| `docs/REPRODUCE.md` | Fresh-clone reproduction instructions |
| `docs/DATA.md` | Data provenance and limitations |
| `docs/MODELS.md` | Model and embedding documentation |
| `docs/MODEL_CARD.md` | Intended use, limitations, risks, and out-of-scope use |
| `docs/LOGGING.md` | Logging and request tracing plan |
| `docs/benchmarks.md` | Smoke-test and benchmark evidence |
| `grading/traceability.yaml` | Story-to-source-to-test mapping |
| `grading/manifest.yaml` | Reproducibility manifest |
| `CONTRIBUTIONS.md` | Team roles and contribution breakdown |

## Known Limitations

- The menu is synthetic and is not connected to a real restaurant.
- The system does not process real payments.
- The system does not submit real kitchen tickets.
- Twilio trial accounts may restrict who can call the phone number.
- RAG quality depends on menu data and the configured embedding model.
- The LLM endpoint must be available for live RAG generation.
- Local microphone/Whisper mode is optional and not part of the main Docker grading path.

## Contribution Summary

See:

CONTRIBUTIONS.md
