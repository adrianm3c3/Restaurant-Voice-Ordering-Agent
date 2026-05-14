# Models Documentation

## Overview

The Restaurant Voice Ordering Agent uses model-backed components for intent parsing fallback, retrieval-augmented menu question answering, and vector retrieval.

The project uses deterministic rule-based logic first for common restaurant actions. The LLM is used only when a request cannot be handled directly by rules or when the system needs to generate a menu-bounded answer from retrieved context.

## Model-Related Components

| Component | Purpose | Main Files |
|---|---|---|
| Intent parser fallback | Converts unclear customer text into structured restaurant intents | `src/intent_parser.py`, `src/prompts.py`, `src/llm_client.py` |
| RAG answer generation | Answers menu questions from retrieved restaurant context | `src/rag_qa.py`, `src/prompts.py`, `src/llm_client.py` |
| Embedding model | Converts menu/FAQ chunks into vectors for retrieval | `src/retriever_chroma.py`, `src/knowledge_builder.py` |
| Vector store | Stores and searches embedded menu/FAQ chunks | ChromaDB, `data/vector_store/chroma_db` |

## Chat Completion Model

| Field | Value |
|---|---|
| Provider | OpenAI-compatible endpoint |
| Default model ID | `meta-llama/Llama-3.1-8B-Instruct` |
| Configuration module | `src/config.py` |
| LLM client module | `src/llm_client.py` |
| Prompt module | `src/prompts.py` |
| Primary uses | Intent parser fallback and RAG answer generation |

## Chat Model Environment Variables

| Variable | Purpose |
|---|---|
| `UTSA_BASE_URL` | OpenAI-compatible API base URL |
| `UTSA_API_KEY` | API key or endpoint placeholder |
| `UTSA_MODEL` | Main model used for response generation |
| `PARSER_MODEL` | Model used for intent parser fallback |
| `GEN_TEMPERATURE` | General generation temperature |
| `GEN_MAX_TOKENS` | General response token limit |
| `RAG_TEMP` | RAG response temperature |
| `RAG_MAX_TOKENS` | RAG response token limit |
| `PARSER_TEMPERATURE` | Parser generation temperature |
| `PARSER_MAX_TOKENS` | Parser token limit |

## Embedding Model

| Field | Value |
|---|---|
| Library | `sentence-transformers` |
| Default model ID | `all-MiniLM-L6-v2` |
| Vector database | ChromaDB |
| Collection name | `pizza_menu` |
| Configuration module | `src/config.py` |
| Retriever module | `src/retriever_chroma.py` |
| Primary use | Retrieve relevant menu/FAQ chunks for restaurant questions |

## Embedding Environment Variables

| Variable | Purpose |
|---|---|
| `EMBED_MODEL` | Embedding model name |
| `EMBEDDING_DEVICE` | Embedding device, default `cpu` |
| `CHROMA_STORE` | Chroma persistence directory |
| `CHROMA_COLLECTION_NAME` | Chroma collection name |
| `SIMILARITY_THRESHOLD` | Retrieval similarity threshold |
| `RETRIEVAL_TOP_K` | Number of retrieved chunks |
| `NORMALIZE_EMBEDDINGS` | Whether embeddings are normalized |

## Prompt Inventory

Prompts are located in:

`src/prompts.py`

| Prompt | Purpose |
|---|---|
| `INTENT_PARSER_SYSTEM_PROMPT` | Restricts parser output to valid JSON and known restaurant intents |
| `INTENT_PARSER_USER_PROMPT_TEMPLATE` | Injects menu context and customer request for intent parsing |
| `RAG_SYSTEM_PROMPT` | Restricts menu QA to retrieved restaurant information |
| `RAG_USER_PROMPT_TEMPLATE` | Provides retrieved context and customer question to the RAG model |

## RAG Flow

The RAG flow works as follows:

1. Build menu and FAQ chunks from the restaurant data.
2. Embed those chunks using the sentence-transformer model.
3. Store/retrieve chunks using ChromaDB.
4. Pass retrieved context and the customer question to the OpenAI-compatible chat model.
5. Return a menu-bounded answer.
6. If no answer can be generated, return a restaurant-bounded fallback instead of hallucinating.

## Deterministic Logic First

The project does not rely entirely on the LLM. Common ordering behaviors are handled directly by Python logic, including:

- Adding pizzas.
- Adding sides such as chicken wings.
- Asking for totals.
- Modifying pizza toppings.
- Checkout state transitions.
- Tracking order state by session.
- Rejecting or redirecting irrelevant questions.

This makes the system more stable for grading and reduces dependence on the external LLM endpoint.

## Model Selection Rationale

The menu domain is small and structured, so deterministic parsing is preferred for common actions. LLM fallback is used only when a request is not handled by direct rules. Retrieval uses a lightweight sentence-transformer model because the knowledge base is small and menu-focused.

The default embedding model, `all-MiniLM-L6-v2`, is appropriate for lightweight semantic retrieval over short restaurant menu and FAQ chunks.

## Reproducibility Notes

The Docker grading path installs dependencies from:

`requirements-docker.txt`

The local development path installs dependencies from:

`requirements.txt`

To rebuild the vector store:

python -m src.build_vector_store

Expected output:

Chroma vector store built.

To run RAG integration tests:

pytest tests/integration/test_rag_integration.py -v

## Known Constraints

- Live RAG generation depends on the configured LLM endpoint.
- If `.env` is empty or credentials are invalid, live LLM calls may fail with an authentication error.
- If the LLM endpoint is unavailable, RAG may return a restaurant-bounded fallback instead of a detailed answer.
- Embedding model downloads may require internet access on first run.
- Chroma vector stores created under incompatible package versions may need to be deleted and rebuilt.
- Model output may vary if the endpoint model, prompt, temperature, or credentials change.
- The system is bounded to restaurant ordering and menu questions.
- The Docker grading path does not require local microphone STT or local pyttsx3 TTS.

## Tested Model-Related Behavior

The project has tested:

- Chroma/vector retrieval behavior.
- RAG fallback behavior for irrelevant questions.
- API order flow without requiring live Twilio.
- User-story flows through pytest.
- Docker startup and `/api/chat` behavior.

Live LLM generation should be tested only when a valid `.env` is configured.

