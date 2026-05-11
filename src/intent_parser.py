import json
import re

from src.config import CONFIG
from src.llm_client import chat_completion, extract_json_from_text
from src.prompts import INTENT_PARSER_SYSTEM_PROMPT, INTENT_PARSER_USER_PROMPT_TEMPLATE
from src.restaurant_text import (
    ADD_ITEM_PHRASES,
    ADD_TOPPING_PHRASES,
    ASK_LAST_REMOVED_PHRASES,
    CHECKOUT_PHRASES,
    CRUST_CHANGE_PHRASES,
    DESCRIBE_PIZZA_PHRASES,
    MENU_PRICE_MARKERS,
    MENU_QUERY_PHRASES,
    NAME_VARIANTS,
    ORDER_COUNT_PHRASES,
    ORDER_SUMMARY_PHRASES,
    ORDER_TOTAL_QUESTION_PHRASES,
    PIZZA_REFERENCE_PHRASES,
    REMOVE_ITEM_PHRASES,
    REMOVE_TOPPING_PHRASES,
    RETRIEVAL_MARKERS,
    TOTAL_PHRASES,
)


WORD_NUMBERS = {
    "a": 1,
    "an": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def normalize_text(text):
    return text.lower().strip()


def build_menu_context(menu):
    return {
        "pizzas": list(menu["pizzas"].keys()),
        "pizza_sizes": CONFIG["menu_defaults"]["pizza_sizes"],
        "crusts": list(menu["crust_price"].keys()),
        "toppings": list(menu["toppings_price"].keys()),
        "sides": list(menu["sides"].keys()),
        "drinks": list(menu["drinks"].keys()),
        "desserts": list(menu["desserts"].keys()),
    }


def singularize(name):
    if name.endswith("ies"):
        return name[:-3] + "y"
    if name.endswith("s") and not name.endswith("ss"):
        return name[:-1]
    return name


def pluralize(name):
    if name.endswith("y") and not name.endswith(("ay", "ey", "iy", "oy", "uy")):
        return name[:-1] + "ies"
    if name.endswith("s"):
        return name
    return name + "s"


def expand_name_variants(name):
    variants = {name}
    variants.add(singularize(name))
    variants.add(pluralize(name))
    variants.update(NAME_VARIANTS.get(name, []))
    return variants


def extract_quantity(text, default=1, max_word_number=10):
    text = normalize_text(text)

    qty_match = re.search(r"\b(\d+)\b", text)
    if qty_match:
        return int(qty_match.group(1))

    for word, value in WORD_NUMBERS.items():
        if value > max_word_number:
            continue

        if re.search(rf"\b{re.escape(word)}\b", text):
            return value

    return default


def parse_direct_menu_query(text):
    for category, phrases in MENU_QUERY_PHRASES.items():
        if any(phrase in text for phrase in phrases):
            return {"intent": "menu_query", "category": category}

    return None


def parse_direct_retrieval_qa(text):
    if any(marker in text for marker in RETRIEVAL_MARKERS):
        return {
            "intent": "retrieval_qa",
            "query": text,
        }

    return None


def parse_direct_total_or_checkout(text):
    if any(phrase in text for phrase in ORDER_TOTAL_QUESTION_PHRASES):
        return {"intent": "get_total"}

    if any(marker in text for marker in MENU_PRICE_MARKERS):
        return {
            "intent": "retrieval_qa",
            "query": text,
        }

    if any(phrase in text for phrase in TOTAL_PHRASES):
        return {"intent": "get_total"}

    if any(phrase in text for phrase in CHECKOUT_PHRASES):
        return {"intent": "checkout"}

    return None


def parse_direct_order_count(text):
    if any(phrase in text for phrase in ORDER_COUNT_PHRASES):
        return {"intent": "get_order_count"}

    return None


def parse_direct_order_summary(text):
    if any(phrase in text for phrase in ORDER_SUMMARY_PHRASES):
        return {"intent": "get_order_summary"}

    return None


def parse_direct_describe_pizza(text):
    if any(phrase in text for phrase in DESCRIBE_PIZZA_PHRASES):
        return {"intent": "describe_last_pizza"}

    return None


def parse_direct_add(text, menu):
    if not any(phrase in text for phrase in ADD_ITEM_PHRASES):
        return None

    quantity = extract_quantity(text, default=1, max_word_number=10)

    for name in sorted(menu["drinks"].keys(), key=len, reverse=True):
        for variant in expand_name_variants(name):
            if re.search(rf"\b{re.escape(variant)}\b", text):
                return {
                    "intent": "add_item",
                    "item": {
                        "type": "drink",
                        "name": name,
                        "quantity": quantity,
                    },
                }

    for name in sorted(menu["sides"].keys(), key=len, reverse=True):
        for variant in expand_name_variants(name):
            if re.search(rf"\b{re.escape(variant)}\b", text):
                item = {
                    "type": "side",
                    "name": name,
                    "quantity": quantity,
                }

                if name == "chicken wings":
                    if (
                        re.search(r"\b12\s*piece\b", text)
                        or re.search(r"\b12\s*wings\b", text)
                    ):
                        item["size"] = "12 piece"
                        item["quantity"] = 1

                    elif (
                        re.search(r"\b6\s*piece\b", text)
                        or re.search(r"\b6\s*wings\b", text)
                    ):
                        item["size"] = "6 piece"
                        item["quantity"] = 1

                    else:
                        item["needs_size_confirmation"] = True

                return {"intent": "add_item", "item": item}

    for name in sorted(menu["desserts"].keys(), key=len, reverse=True):
        for variant in expand_name_variants(name):
            if re.search(rf"\b{re.escape(variant)}\b", text):
                return {
                    "intent": "add_item",
                    "item": {
                        "type": "dessert",
                        "name": name,
                        "quantity": quantity,
                    },
                }

    return None


def parse_direct_pizza_modification(text, menu):
    if (
        (re.search(r"\bpizza\b", text) or re.search(r"\bpizzas\b", text))
        and not any(phrase in text for phrase in PIZZA_REFERENCE_PHRASES)
    ):
        return None
    
    has_pizza_reference = any(
        phrase in text
        for phrase in PIZZA_REFERENCE_PHRASES
    )

    has_add_action = any(
        phrase in text
        for phrase in ADD_TOPPING_PHRASES
    )

    has_remove_action = any(
        phrase in text
        for phrase in REMOVE_TOPPING_PHRASES
    )

    if not has_pizza_reference and not has_add_action and not has_remove_action:
        return None

    matched_toppings = []

    if (
        has_remove_action
        and re.search(r"\bcheese\b", text)
        and not re.search(r"\b(extra|more)\s+cheese\b", text)
    ):
        matched_toppings.append("mozzarella")

    for topping in menu["toppings_price"].keys():
        if topping == "extra cheese" and "mozzarella" in matched_toppings:
            continue

        for variant in expand_name_variants(topping):
            if re.search(rf"\b{re.escape(variant)}\b", text):
                matched_toppings.append(topping)
                break

    matched_toppings = list(dict.fromkeys(matched_toppings))

    if not matched_toppings:
        return None

    if has_remove_action:
        return {
            "intent": "modify_last_pizza",
            "action": "remove_toppings",
            "toppings": matched_toppings,
        }

    if has_add_action:
        return {
            "intent": "modify_last_pizza",
            "action": "add_toppings",
            "toppings": matched_toppings,
        }

    return None


def parse_direct_remove(text, menu):
    if any(phrase in text for phrase in ASK_LAST_REMOVED_PHRASES):
        return {"intent": "ask_last_removed"}

    if not any(phrase in text for phrase in REMOVE_ITEM_PHRASES):
        return None

    quantity = extract_quantity(
        text,
        default=None,
        max_word_number=3,
    )

    size = None
    for s in CONFIG["menu_defaults"]["pizza_sizes"]:
        if re.search(rf"\b{s}\b", text):
            size = s
            break

    for pizza_name in sorted(menu["pizzas"].keys(), key=len, reverse=True):
        for variant in expand_name_variants(pizza_name):
            if re.search(rf"\b{re.escape(variant)}\b", text):
                return {
                    "intent": "remove_named_item",
                    "name": pizza_name,
                    "quantity": quantity,
                    "size": size,
                }

    if re.search(r"\bpizza\b", text) or re.search(r"\bpizzas\b", text):
        return {
            "intent": "remove_named_item",
            "name": "__last_pizza__",
            "quantity": quantity,
            "size": size,
        }

    other_names = (
        list(menu["sides"].keys())
        + list(menu["drinks"].keys())
        + list(menu["desserts"].keys())
    )

    for name in sorted(other_names, key=len, reverse=True):
        for variant in expand_name_variants(name):
            if re.search(rf"\b{re.escape(variant)}\b", text):
                return {
                    "intent": "remove_named_item",
                    "name": name,
                    "quantity": quantity,
                }

    return {"intent": "unknown"}


def parse_direct_crust_change(text, menu):
    if not any(phrase in text for phrase in CRUST_CHANGE_PHRASES):
        return None

    for crust in menu["crust_price"].keys():
        for variant in expand_name_variants(crust):
            if re.search(rf"\b{re.escape(variant)}\b", text):
                return {
                    "intent": "change_pizza_crust",
                    "crust": crust,
                }

    return None


def parse_intent(user_text, menu):
    text = normalize_text(user_text)

    direct = parse_direct_menu_query(text)
    if direct:
        return direct

    direct = parse_direct_crust_change(text, menu)
    if direct:
        return direct

    direct = parse_direct_add(text, menu)
    if direct:
        return direct

    direct = parse_direct_pizza_modification(text, menu)
    if direct:
        return direct

    direct = parse_direct_describe_pizza(text)
    if direct:
        return direct

    direct = parse_direct_retrieval_qa(text)
    if direct:
        return direct

    direct = parse_direct_total_or_checkout(text)
    if direct:
        return direct

    direct = parse_direct_order_count(text)
    if direct:
        return direct

    direct = parse_direct_order_summary(text)
    if direct:
        return direct

    direct = parse_direct_remove(text, menu)
    if direct:
        return direct

    menu_context = build_menu_context(menu)

    user_prompt = INTENT_PARSER_USER_PROMPT_TEMPLATE.format(
        menu_context=json.dumps(menu_context, indent=2),
        user_text=text,
    )

    raw = chat_completion(
        INTENT_PARSER_SYSTEM_PROMPT,
        user_prompt,
        temperature=CONFIG["parser"]["temperature"],
        max_tokens=CONFIG["parser"]["max_tokens"],
    )

    parsed = extract_json_from_text(raw)

    if not parsed:
        return {"intent": "unknown"}

    return validate_parsed_intent(parsed, menu)


def validate_parsed_intent(parsed, menu):
    intent = parsed.get("intent")

    allowed_intents = {
        "add_item",
        "remove_named_item",
        "remove_item",
        "get_total",
        "checkout",
        "menu_query",
        "retrieval_qa",
        "get_order_count",
        "get_order_summary",
        "describe_last_pizza",
        "ask_last_removed",
        "modify_last_pizza",
        "change_pizza_crust",
        "unknown",
    }

    if intent not in allowed_intents:
        return {"intent": "unknown"}

    if intent == "menu_query":
        category = parsed.get("category")
        if category in MENU_QUERY_PHRASES:
            return {"intent": "menu_query", "category": category}
        return {"intent": "unknown"}

    if intent == "retrieval_qa":
        query = parsed.get("query")
        if not isinstance(query, str) or not query.strip():
            return {"intent": "unknown"}
        return {"intent": "retrieval_qa", "query": query.strip()}

    if intent == "change_pizza_crust":
        crust = parsed.get("crust")
        if crust in menu["crust_price"]:
            return {"intent": "change_pizza_crust", "crust": crust}
        return {"intent": "unknown"}

    if intent == "remove_named_item":
        name = parsed.get("name")
        quantity = parsed.get("quantity", None)
        size = parsed.get("size", None)

        valid_names = (
            set(menu["pizzas"].keys())
            | set(menu["sides"].keys())
            | set(menu["drinks"].keys())
            | set(menu["desserts"].keys())
            | {"__last_pizza__"}
        )

        if name in valid_names:
            if quantity is not None and (not isinstance(quantity, int) or quantity < 1):
                quantity = None

            return {
                "intent": "remove_named_item",
                "name": name,
                "quantity": quantity,
                "size": size,
            }

        return {"intent": "unknown"}

    if intent == "modify_last_pizza":
        action = parsed.get("action")
        topping = parsed.get("topping")
        toppings = parsed.get("toppings")

        if action not in {
            "remove_topping",
            "remove_toppings",
            "add_topping",
            "add_toppings",
        }:
            return {"intent": "unknown"}

        removable_base_ingredients = {
            ingredient
            for pizza in menu["pizzas"].values()
            for ingredient in pizza.get("ingredients", [])
        }
        valid_toppings = (
            set(menu["toppings_price"].keys())
            | removable_base_ingredients
        )

        if toppings is None:
            toppings = [topping] if topping else []

        if not isinstance(toppings, list):
            return {"intent": "unknown"}

        toppings = [t for t in toppings if t in valid_toppings]

        if not toppings:
            return {"intent": "unknown"}

        return {
            "intent": "modify_last_pizza",
            "action": action,
            "toppings": toppings,
        }

    if intent in {
        "remove_item",
        "get_total",
        "checkout",
        "get_order_count",
        "get_order_summary",
        "describe_last_pizza",
        "ask_last_removed",
        "unknown",
    }:
        return {"intent": intent}

    if intent == "add_item":
        item = parsed.get("item", {})
        item_type = item.get("type")

        if item_type == "pizza":
            return validate_pizza_item(item, menu)
        if item_type == "side":
            return validate_side_item(item, menu)
        if item_type == "drink":
            return validate_drink_item(item, menu)
        if item_type == "dessert":
            return validate_dessert_item(item, menu)

    return {"intent": "unknown"}


def validate_pizza_item(item, menu):
    size = item.get("size", CONFIG["menu_defaults"]["default_pizza_size"])
    base = item.get("base", CONFIG["menu_defaults"]["default_pizza_base"])
    crust = item.get("crust", CONFIG["menu_defaults"]["default_crust"])
    toppings = item.get("toppings", [])
    removals = item.get("removals", [])
    quantity = item.get("quantity", 1)

    if size not in CONFIG["menu_defaults"]["pizza_sizes"]:
        size = CONFIG["menu_defaults"]["default_pizza_size"]

    if base not in menu["pizzas"]:
        base = CONFIG["menu_defaults"]["default_pizza_base"]

    if crust not in menu["crust_price"]:
        crust = CONFIG["menu_defaults"]["default_crust"]

    if not isinstance(toppings, list):
        toppings = []

    if not isinstance(removals, list):
        removals = []

    valid_toppings = set(menu["toppings_price"].keys())
    toppings = [t for t in toppings if t in valid_toppings]
    removals = [t for t in removals if t in valid_toppings]

    base_ingredients = [
        x.lower()
        for x in menu["pizzas"][base].get("ingredients", [])
    ]

    toppings = [
        t for t in toppings
        if t not in base_ingredients and t not in removals
    ]

    if not isinstance(quantity, int) or quantity < 1:
        quantity = 1

    return {
        "intent": "add_item",
        "item": {
            "type": "pizza",
            "size": size,
            "base": base,
            "crust": crust,
            "toppings": list(dict.fromkeys(toppings)),
            "removals": list(dict.fromkeys(removals)),
            "quantity": quantity,
        },
    }


def validate_side_item(item, menu):
    name = item.get("name")
    quantity = item.get("quantity", 1)

    if name not in menu["sides"]:
        return {"intent": "unknown"}

    if not isinstance(quantity, int) or quantity < 1:
        quantity = 1

    clean_item = {
        "type": "side",
        "name": name,
        "quantity": quantity,
    }

    if name == "chicken wings":
        size = item.get("size", CONFIG["menu_defaults"]["default_wing_size"])
        if size not in menu["sides"]["chicken wings"]:
            size = CONFIG["menu_defaults"]["default_wing_size"]
        clean_item["size"] = size

    return {"intent": "add_item", "item": clean_item}


def validate_drink_item(item, menu):
    name = item.get("name")
    quantity = item.get("quantity", 1)

    if name not in menu["drinks"]:
        return {"intent": "unknown"}

    if not isinstance(quantity, int) or quantity < 1:
        quantity = 1

    return {
        "intent": "add_item",
        "item": {
            "type": "drink",
            "name": name,
            "quantity": quantity,
        },
    }


def validate_dessert_item(item, menu):
    name = item.get("name")
    quantity = item.get("quantity", 1)

    if name not in menu["desserts"]:
        return {"intent": "unknown"}

    if not isinstance(quantity, int) or quantity < 1:
        quantity = 1

    return {
        "intent": "add_item",
        "item": {
            "type": "dessert",
            "name": name,
            "quantity": quantity,
        },
    }