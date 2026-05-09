import json

from src.config import CONFIG
from src.restaurant_text import (
    ALLERGEN_MARKERS,
    CONTAINS_CHICKEN_TEXT,
    CONTAINS_MEAT_TEXT,
    CONTAINS_PORK_TEXT,
    FAQ_CHUNKS,
    GLUTEN_FREE_CRUST_TEXT,
    MEAT_MARKERS,
    MODIFICATION_POLICY_CHUNKS,
    PIZZA_CHUNK_TEMPLATE,
    PIZZA_STYLE_HINTS,
    POPULAR_ITEM_TEXT,
    POPULAR_ITEMS,
    PORK_MARKERS,
    SAUCE_INFORMATION_TEMPLATE,
    SAUCE_MARKERS,
    SPICY_HINT_TEXT,
    SPICY_INGREDIENT_MARKERS,
    SPICY_TOPPINGS,
    VEGETARIAN_PIZZA_TEXT,
    VEGETARIAN_PIZZAS,
    VEGETARIAN_TOPPINGS,
)


MENU_PATH = CONFIG["paths"]["menu"]


def load_menu(path=MENU_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_semantic_hints(name, ingredients):
    hints = []
    lower_ingredients = ingredients.lower()

    if any(x in lower_ingredients for x in SPICY_INGREDIENT_MARKERS):
        hints.append(SPICY_HINT_TEXT)

    if name in VEGETARIAN_PIZZAS:
        hints.append(VEGETARIAN_PIZZA_TEXT)

    if "chicken" in lower_ingredients:
        hints.append(CONTAINS_CHICKEN_TEXT)

    if any(x in lower_ingredients for x in PORK_MARKERS):
        hints.append(CONTAINS_PORK_TEXT)

    if any(x in lower_ingredients for x in MEAT_MARKERS):
        hints.append(CONTAINS_MEAT_TEXT)

    for allergen, markers in ALLERGEN_MARKERS.items():
        if any(marker in lower_ingredients for marker in markers):
            hints.append(f"Contains {allergen}.")

    sauces = [
        sauce
        for sauce in SAUCE_MARKERS
        if sauce in lower_ingredients
    ]

    if sauces:
        hints.append(
            SAUCE_INFORMATION_TEMPLATE.format(
                sauces=", ".join(sauces),
            )
        )

    if name in PIZZA_STYLE_HINTS:
        hints.append(PIZZA_STYLE_HINTS[name])

    if name in POPULAR_ITEMS:
        hints.append(POPULAR_ITEM_TEXT)

    return " ".join(hints)


def build_knowledge_chunks(menu):
    chunks = []

    for name, data in menu["pizzas"].items():
        ingredients = ", ".join(data.get("ingredients", []))

        prices = data.get("base_price", {})
        price_text = ", ".join(
            f"{size}: ${price:.2f}"
            for size, price in prices.items()
        )

        text = PIZZA_CHUNK_TEMPLATE.format(
            name=name,
            ingredients=ingredients,
            price_text=price_text,
        )

        semantic_hints = build_semantic_hints(name, ingredients)

        if semantic_hints:
            text += " " + semantic_hints

        chunks.append({
            "id": f"pizza_{name.replace(' ', '_')}",
            "type": "menu_item",
            "category": "pizzas",
            "name": name,
            "text": text,
        })

    crust_text = ", ".join(
        f"{crust}: additional cost ${price:.2f}"
        for crust, price in menu["crust_price"].items()
    )

    if "gluten-free crust" in menu["crust_price"]:
        crust_text += f". {GLUTEN_FREE_CRUST_TEXT}"

    chunks.append({
        "id": "crust_options",
        "type": "menu_section",
        "category": "crusts",
        "name": "crusts",
        "text": f"Crust options are {crust_text}.",
    })

    topping_descriptions = []

    for topping, price in menu["toppings_price"].items():
        desc = f"{topping}: ${price:.2f}"

        if topping in SPICY_TOPPINGS:
            desc += " spicy"

        if topping in VEGETARIAN_TOPPINGS:
            desc += " vegetarian"

        topping_descriptions.append(desc)

    topping_text = ", ".join(topping_descriptions)

    chunks.append({
        "id": "topping_options",
        "type": "menu_section",
        "category": "toppings",
        "name": "toppings",
        "text": f"Available toppings are {topping_text}.",
    })

    side_lines = []

    for name, price in menu["sides"].items():
        if isinstance(price, dict):
            size_text = ", ".join(
                f"{k}: ${v:.2f}"
                for k, v in price.items()
            )
            side_lines.append(f"{name}: {size_text}")
        else:
            side_lines.append(f"{name}: ${price:.2f}")

    chunks.append({
        "id": "side_options",
        "type": "menu_section",
        "category": "sides",
        "name": "sides",
        "text": "Available sides are " + "; ".join(side_lines) + ".",
    })

    drink_text = ", ".join(
        f"{name}: ${price:.2f}"
        for name, price in menu["drinks"].items()
    )

    chunks.append({
        "id": "drink_options",
        "type": "menu_section",
        "category": "drinks",
        "name": "drinks",
        "text": f"Available drinks are {drink_text}.",
    })

    dessert_text = ", ".join(
        f"{name}: ${price:.2f}"
        for name, price in menu["desserts"].items()
    )

    chunks.append({
        "id": "dessert_options",
        "type": "menu_section",
        "category": "desserts",
        "name": "desserts",
        "text": f"Available desserts are {dessert_text}.",
    })

    chunks.extend(FAQ_CHUNKS)
    chunks.extend(MODIFICATION_POLICY_CHUNKS)

    return chunks