## Conversational Model

Model:
meta-llama/Llama-3.1-8B-Instruct

Purpose:
Conversational response generation and RAG answering.

Source:
Meta Llama

License:
Llama 3.1 Community License Agreement

Configuration:
Configured through UTSA_MODEL environment variable.

---

## Intent Parser Model

Model:
meta-llama/Llama-3.1-8B-Instruct

Purpose:
Fallback intent parsing and structured JSON generation.

Source:
Meta Llama

License:
Llama 3.1 Community License Agreement

Configuration:
Configured through PARSER_MODEL environment variable.

---

## Embedding Model

Model:
sentence-transformers/all-MiniLM-L6-v2

Purpose:
Semantic embedding generation for ChromaDB retrieval.

Source:
Sentence Transformers / Hugging Face

License:
Apache 2.0

Configuration:
Configured through EMBED_MODEL environment variable.
