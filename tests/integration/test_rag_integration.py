import pytest

from src.agent import MENU
from src.rag_qa import answer_rag_question
from src.restaurant_text import RAG_EMPTY_RESPONSE_MESSAGE, RAG_NO_CONTEXT_MESSAGE


@pytest.mark.integration
def test_real_rag_answers_pepperoni_question():
    """
    Given the Chroma vector store and menu data are available
    When the customer asks what comes on a pepperoni pizza
    Then RAG returns a non-empty restaurant-menu answer
    """
    reply = answer_rag_question(
        "what comes on a pepperoni pizza",
        MENU,
    )

    assert isinstance(reply, str)
    assert len(reply.strip()) > 0
    assert reply not in {
        RAG_EMPTY_RESPONSE_MESSAGE,
        RAG_NO_CONTEXT_MESSAGE,
    }
    assert "pepperoni" in reply.lower() or "pizza" in reply.lower()


@pytest.mark.integration
def test_real_rag_rejects_irrelevant_question():
    """
    Given the system is bounded to restaurant menu knowledge
    When the customer asks an unrelated sports question
    Then RAG does not answer as a general chatbot
    """
    reply = answer_rag_question(
        "who won the football game last night",
        MENU,
    )

    assert isinstance(reply, str)
    assert len(reply.strip()) > 0
    assert (
        "restaurant menu" in reply.lower()
        or "do not see" in reply.lower()
        or "couldn’t answer" in reply.lower()
        or "couldn't answer" in reply.lower()
    )