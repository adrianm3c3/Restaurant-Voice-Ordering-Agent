from src.rag_fallback import keyword_fallback_faq_chunks


def test_keyword_fallback_vegetarian():
    chunks = keyword_fallback_faq_chunks("do you have anything vegetarian")
    assert len(chunks) == 1
    assert chunks[0]["id"] == "faq_vegetarian"
    assert "veggie pizza" in chunks[0]["text"]
