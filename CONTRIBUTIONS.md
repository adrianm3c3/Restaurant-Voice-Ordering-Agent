# Contributions

## Team Members

| Member | Role | Modules / Artifacts Owned | Contribution |
|---|---|---|---:|
| Adrian Cisneros | Integration / Deployment Developer | Twilio setup, Flask server, `/api/chat`, Docker, API testing, documentation integration | 34% |
| Horus E. Ortega | RAG Backend Developer | RAG backend, Chroma retrieval, knowledge builder, menu QA integration | 33% |
| Tien Vo | Ordering / NLP Developer | Complex order handling, TTS support, intent parser improvements, main agent flow | 33% |

## Contribution Summary

### Adrian Cisneros

Adrian Cisneros contributed to system integration, deployment, and grading readiness, including:

- Twilio phone number and voice webhook setup.
- Flask server integration.
- `/voice` Twilio webhook endpoint.
- `/api/chat` grading and testing endpoint.
- Dockerfile and Docker Compose deployment.
- Docker smoke testing.
- API session testing.
- README and grading documentation integration.
- Test report and deployment report generation.

Primary related files and areas:

twilio_phone_server.py  
Dockerfile  
docker-compose.yml  
.dockerignore  
requirements-docker.txt  
README.md  
docs/  
grading/  
reports/

### Horus E. Ortega

Horus E. Ortega contributed to the RAG backend and retrieval infrastructure, including:

- Retrieval-augmented generation backend.
- Chroma vector store setup and validation.
- Menu knowledge chunk generation.
- Menu question-answering integration.
- RAG integration testing.
- Model/data documentation support.

Primary related files and areas:

src/rag_qa.py  
src/retriever_chroma.py  
src/knowledge_builder.py  
src/llm_client.py  
src/config.py  
tests/integration/test_rag_integration.py  
docs/DATA.md  
docs/MODELS.md  
docs/REPRODUCE.md

### Tien Vo

Tien Vo contributed to complex restaurant ordering behavior and NLP interaction improvements, including:

- Complex order flow handling.
- Intent parser improvements.
- Main agent conversation flow.
- Checkout flow validation.
- Order modification support.
- TTS/local voice support work.
- User story and order-flow testing.

Primary related files and areas:

src/agent.py  
src/intent_parser.py  
src/order_manager.py  
src/pricing.py  
src/restaurant_text.py  
speech_ui.py  
speech_controller.py  
speech_recording.py  
speech_totext.py  
tests/user_stories/  
tests/integration/test_api_chat.py

## Module Ownership

| Area | Primary Contributor(s) | Files / Folders |
|---|---|---|
| Twilio / Flask integration | Adrian Cisneros | `twilio_phone_server.py` |
| Docker deployment | Adrian Cisneros | `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `requirements-docker.txt` |
| API testing and smoke testing | Adrian Cisneros | `/api/chat`, `reports/docker_smoke_test.txt`, `tests/integration/test_api_chat.py` |
| RAG backend | Horus E. Ortega | `src/rag_qa.py`, `src/retriever_chroma.py`, `src/knowledge_builder.py` |
| Menu QA / vector retrieval | Horus E. Ortega | `data/menu/`, `src/restaurant_text.py`, `tests/integration/test_rag_integration.py` |
| Order logic | Tien Vo | `src/agent.py`, `src/order_manager.py`, `src/pricing.py` |
| Intent parsing | Tien Vo | `src/intent_parser.py`, `src/prompts.py` |
| TTS / local voice support | Tien Vo | `speech_ui.py`, `speech_controller.py`, `speech_recording.py`, `speech_totext.py` |
| Documentation | Adrian Cisneros, Horus E. Ortega, Tien Vo | `README.md`, `docs/`, `grading/` |

## Git Contribution Report

The git contribution report is generated with:

git shortlog -sne --all --no-merges > reports/git_contributions.txt

## Declared Contribution Split

Adrian Cisneros: 34%  
Horus E. Ortega: 33%  
Tien Vo: 33%

## Notes

The declared contribution split reflects functional ownership. Adrian Cisneros focused on integration, Twilio, Flask, Docker, testing evidence, and grading readiness. Horus E. Ortega focused on the RAG backend and retrieval system. Tien Vo focused on complex ordering behavior, TTS support, and intent parser improvements to the main agent.