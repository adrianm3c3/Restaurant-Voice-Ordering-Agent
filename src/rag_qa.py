from src.config import CONFIG
from src.knowledge_builder import build_knowledge_chunks
from src.llm_client import chat_completion
from src.prompts import (
    RAG_SYSTEM_PROMPT,
    RAG_USER_PROMPT_TEMPLATE,
)
from src.restaurant_text import (
    RAG_EMPTY_RESPONSE_MESSAGE,
    RAG_NO_CONTEXT_MESSAGE,
)
from src.retriever_chroma import retrieve_with_chroma


def format_retrieved_context(chunks):
    return "\n\n".join(
        f"[{chunk['id']}]\n{chunk['text']}"
        for chunk in chunks
    )


def answer_rag_question(question, menu, top_k=None):
    if top_k is None:
        top_k = CONFIG["retrieval"]["top_k"]

    chunks = build_knowledge_chunks(menu)

    retrieved_chunks = retrieve_with_chroma(
        question,
        chunks,
        top_k=top_k,
    )

    if not retrieved_chunks:
        return RAG_NO_CONTEXT_MESSAGE

    context = format_retrieved_context(
        retrieved_chunks
    )

    system_prompt = RAG_SYSTEM_PROMPT

    user_prompt = RAG_USER_PROMPT_TEMPLATE.format(
        context=context,
        question=question,
    )

    response = chat_completion(
        system_prompt,
        user_prompt,
        temperature=CONFIG["rag_generation"]["temperature"],
        max_tokens=CONFIG["rag_generation"]["max_tokens"],
    )

    if not response:
        return RAG_EMPTY_RESPONSE_MESSAGE

    return response