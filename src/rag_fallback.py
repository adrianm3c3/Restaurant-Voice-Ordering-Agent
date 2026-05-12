"""Keyword FAQ selection when vector retrieval returns no chunks."""

from src.restaurant_text import FAQ_CHUNKS


def keyword_fallback_faq_chunks(question):
    """
    When Chroma returns nothing (empty DB, threshold too strict, first-run embed),
    still answer common policy questions from baked-in FAQ text.
    """
    q = question.lower().replace("'", "'")
    out = []
    seen = set()

    def push(chunk_id):
        if chunk_id in seen:
            return
        for chunk in FAQ_CHUNKS:
            if chunk.get("id") == chunk_id:
                seen.add(chunk_id)
                out.append(chunk)
                return

    if any(
        w in q
        for w in (
            "vegetarian",
            "vegetarians",
            "meatless",
            "plant-based",
            "plant based",
        )
    ):
        push("faq_vegetarian")

    if "vegan" in q or "vegans" in q:
        push("faq_vegan")

    if "gluten" in q or "celiac" in q or "wheat allergy" in q:
        push("faq_gluten")

    if any(
        w in q
        for w in (
            "spicy",
            "spiciness",
            "jalapeño",
            "jalapeno",
            "hot pepper",
        )
    ):
        push("faq_spicy")

    if any(
        w in q
        for w in (
            "calorie",
            "calories",
            "nutrition",
            "nutritional",
            "protein",
            "macros",
            "macro",
            "sodium",
            "carb",
        )
    ):
        push("faq_nutrition")

    if "meat lovers" not in q and (
        "pork" in q
        or ("halal" in q or "kosher" in q)
        or ("which" in q and "meat" in q)
        or ("what" in q and "meat" in q and "pizza" in q)
    ):
        push("faq_meat_and_pork")

    if any(
        w in q
        for w in (
            "tomato sauce",
            "white sauce",
            "garlic sauce",
            "bbq sauce",
            "buffalo sauce",
            "pizza sauce",
            "red sauce",
        )
    ):
        push("faq_tomato_sauce")

    if any(
        w in q
        for w in (
            "recommend",
            "popular",
            "best seller",
            "favorite",
            "favourite",
            "special",
        )
    ):
        push("faq_recommendations")

    return out[:6]
