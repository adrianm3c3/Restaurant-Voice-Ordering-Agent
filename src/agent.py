import json

from src.config import CONFIG
from src.intent_parser import parse_intent
from src.order_manager import OrderManager
from src.pricing import compute_total_with_tax
from src.rag_qa import answer_rag_question
from src.restaurant_text import (
    ADDED_ITEM_TEMPLATE,
    ADD_TOPPING_RESPONSE_TEMPLATE,
    CHECKOUT_COMPLETION_MARKERS,
    CHECKOUT_EMPTY_MESSAGE,
    CHECKOUT_THANK_YOU_MESSAGE,
    DETAILED_MENU_MARKERS,
    EMPTY_ORDER_MESSAGE,
    EXIT_WORDS,
    GREETING_TEMPLATE,
    LAST_REMOVED_TEMPLATE,
    MENU_CATEGORY_FALLBACK_MESSAGE,
    MENU_CATEGORY_TEMPLATES,
    NO_LAST_REMOVED_MESSAGE,
    NO_MATCHING_ITEM_TEMPLATE,
    NO_MATCHING_PIZZA_TEMPLATE,
    NO_REMOVE_MESSAGE,
    ORDER_COUNT_TEMPLATE,
    ORDER_SUMMARY_PREFIX,
    PENDING_ACTION_CANCEL_MESSAGE,
    PENDING_ACTION_FAILED_MESSAGE,
    PIZZA_MODIFY_NOT_FOUND_MESSAGE,
    REMOVED_ITEM_TEMPLATE,
    REMOVE_LAST_PIZZA_TEMPLATE,
    REMOVE_NAMED_ITEM_TEMPLATE,
    REMOVE_NAMED_PIZZA_TEMPLATE,
    REMOVE_TOPPING_RESPONSE_TEMPLATE,
    SINGULAR_SPECIAL_CASES,
    PLURAL_SPECIAL_CASES,
    TOTAL_TEMPLATE,
    UNKNOWN_CRUST_MESSAGE,
    UPDATED_CRUST_TEMPLATE,
    UPDATED_PIZZA_MESSAGE,
    VOICE_INPUT_NOT_CAUGHT_MESSAGE,
)

try:
    from voice.text_to_speech import speak
except Exception:
    speak = None


MENU_PATH = CONFIG["paths"]["menu"]


def load_menu(path=MENU_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


MENU = load_menu()


def format_currency(x):
    return f"${x:.2f}"


def build_total_response(result):
    return TOTAL_TEMPLATE.format(
        subtotal=format_currency(result["subtotal"]),
        tax=format_currency(result["tax"]),
        total=format_currency(result["total"]),
    )


def pluralize_word(word, qty):
    if qty == 1:
        return SINGULAR_SPECIAL_CASES.get(word, word)

    return PLURAL_SPECIAL_CASES.get(word, word + "s")


def summarize_item(item):
    item_type = item.get("type")
    quantity = item.get("quantity", 1)

    if item_type == "pizza":
        size = item.get(
            "size",
            CONFIG["menu_defaults"]["default_pizza_size"],
        )

        base = item.get(
            "base",
            CONFIG["menu_defaults"]["default_pizza_base"],
        )

        crust = item.get(
            "crust",
            CONFIG["menu_defaults"]["default_crust"],
        )

        toppings = item.get("toppings", [])
        removals = item.get("removals", [])

        pizza_word = "pizza" if quantity == 1 else "pizzas"

        parts = [
            f"{quantity} {size} {base} {pizza_word} with {crust}"
        ]

        if toppings:
            parts.append("plus " + ", ".join(toppings))

        if removals:
            parts.append("no " + ", ".join(removals))

        return " ".join(parts)

    if item_type == "side":
        name = item.get("name", "side")

        if name == "chicken wings":
            wing_size = item.get(
                "size",
                CONFIG["menu_defaults"]["default_wing_size"],
            )

            order_word = "order" if quantity == 1 else "orders"

            return (
                f"{quantity} {order_word} "
                f"of {wing_size} chicken wings"
            )

        return f"{quantity} {pluralize_word(name, quantity)}"

    if item_type == "drink":
        name = item.get("name", "drink")
        return f"{quantity} {pluralize_word(name, quantity)}"

    if item_type == "dessert":
        name = item.get("name", "dessert")
        return f"{quantity} {pluralize_word(name, quantity)}"

    return "item"


def build_order_summary(order):
    if not order:
        return EMPTY_ORDER_MESSAGE

    return (
        ORDER_SUMMARY_PREFIX
        + "; ".join(summarize_item(item) for item in order)
        + "."
    )


def count_total_items(order):
    return sum(item.get("quantity", 1) for item in order)


def count_total_pizzas(order):
    return sum(
        item.get("quantity", 1)
        for item in order
        if item.get("type") == "pizza"
    )


def handle_menu_query(category, menu):
    if category == "pizzas":
        return MENU_CATEGORY_TEMPLATES["pizzas"].format(
            items=", ".join(menu["pizzas"].keys()),
        )

    if category == "toppings":
        return MENU_CATEGORY_TEMPLATES["toppings"].format(
            items=", ".join(menu["toppings_price"].keys()),
        )

    if category == "sides":
        return MENU_CATEGORY_TEMPLATES["sides"].format(
            items=", ".join(menu["sides"].keys()),
        )

    if category == "drinks":
        return MENU_CATEGORY_TEMPLATES["drinks"].format(
            items=", ".join(menu["drinks"].keys()),
        )

    if category == "desserts":
        return MENU_CATEGORY_TEMPLATES["desserts"].format(
            items=", ".join(menu["desserts"].keys()),
        )

    if category == "crusts":
        return MENU_CATEGORY_TEMPLATES["crusts"].format(
            items=", ".join(menu["crust_price"].keys()),
        )

    if category == "sizes":
        return MENU_CATEGORY_TEMPLATES["sizes"].format(
            items=", ".join(CONFIG["menu_defaults"]["pizza_sizes"]),
        )

    return MENU_CATEGORY_FALLBACK_MESSAGE


def build_removed_response(parsed, menu):
    quantity = parsed.get("removed_quantity", parsed.get("quantity"))
    name = parsed["name"]

    if name == "__last_pizza__":
        if quantity is None or quantity == 1:
            return REMOVE_LAST_PIZZA_TEMPLATE.format(quantity=1)

        return REMOVE_LAST_PIZZA_TEMPLATE.format(quantity=quantity)

    if name in menu["pizzas"]:
        pizza_word = "pizza" if quantity is None or quantity == 1 else "pizzas"

        return REMOVE_NAMED_PIZZA_TEMPLATE.format(
            quantity=1 if quantity is None else quantity,
            size=f"{parsed['size']} " if parsed.get("size") else "",
            name=name,
            pizza_word=pizza_word,
        )

    if quantity is None or quantity == 1:
        return REMOVE_NAMED_ITEM_TEMPLATE.format(
            quantity=1,
            item=pluralize_word(name, 1),
        )

    return REMOVE_NAMED_ITEM_TEMPLATE.format(
        quantity=quantity,
        item=pluralize_word(name, quantity),
    )


def is_detailed_menu_question(user_text):
    lower_text = user_text.lower()
    return any(marker in lower_text for marker in DETAILED_MENU_MARKERS)


def is_checkout_complete_response(response):
    lower_response = response.lower()
    return any(marker in lower_response for marker in CHECKOUT_COMPLETION_MARKERS)


def handle_user_input(user_text, order_manager, menu, state):

    parsed = parse_intent(user_text, menu)

    if CONFIG["runtime"]["debug"]:
        print("DEBUG PARSED:", parsed)

    intent = parsed.get("intent")

    if intent == "add_item":
        item = parsed["item"]
        order_manager.add_item(item)
        return ADDED_ITEM_TEMPLATE.format(item=summarize_item(item))

    if intent == "modify_last_pizza":
        toppings = parsed.get("toppings")

        if toppings is None:
            topping = parsed.get("topping")
            toppings = [topping] if topping else []

        modified = order_manager.modify_last_pizza(
            parsed.get("action"),
            toppings,
        )

        if not modified:
            return PIZZA_MODIFY_NOT_FOUND_MESSAGE

        state["last_modified"] = modified

        toppings_text = ", ".join(toppings)

        if parsed.get("action") in {"remove_topping", "remove_toppings"}:
            return REMOVE_TOPPING_RESPONSE_TEMPLATE.format(
                toppings=toppings_text,
            )

        if parsed.get("action") in {"add_topping", "add_toppings"}:
            return ADD_TOPPING_RESPONSE_TEMPLATE.format(
                toppings=toppings_text,
            )

        return UPDATED_PIZZA_MESSAGE

    if intent == "change_pizza_crust":
        crust = parsed.get("crust")

        if crust not in menu["crust_price"]:
            return "I could not find that crust option."

        modified = order_manager.change_last_pizza_crust(crust)

        if not modified:
            return "I could not find a pizza in your order to update."

        extra_cost = menu["crust_price"].get(crust, 0)

        if extra_cost > 0:
            return (
                f"Updated your pizza to {crust}. "
                f"That adds {format_currency(extra_cost)}."
            )

        return f"Updated your pizza to {crust}."

    if intent == "remove_named_item":
        if parsed["name"] == "__last_pizza__":
            quantity = parsed.get("quantity")

            if quantity is None:
                quantity = 1

            removed = order_manager.remove_last_pizza(
                quantity,
                parsed.get("size"),
            )

            if removed:
                state["last_removed"] = removed
                parsed["removed_quantity"] = removed.get("quantity", quantity)
                return build_removed_response(parsed, menu)

            return NO_MATCHING_PIZZA_TEMPLATE.format(description="matching")

        removed = order_manager.remove_item_by_name(
            parsed["name"],
            parsed.get("quantity"),
            parsed.get("size"),
        )

        if removed:
            state["last_removed"] = removed
            parsed["removed_quantity"] = removed.get(
                "quantity",
                parsed.get("quantity"),
            )
            return build_removed_response(parsed, menu)

        if parsed["name"] in menu["pizzas"]:
            if parsed.get("size"):
                return NO_MATCHING_PIZZA_TEMPLATE.format(
                    description=f"{parsed['size']} {parsed['name']}",
                )

            return NO_MATCHING_PIZZA_TEMPLATE.format(
                description=parsed["name"],
            )

        return NO_MATCHING_ITEM_TEMPLATE.format(name=parsed["name"])

    if intent == "remove_item":
        removed = order_manager.remove_last_item()

        if removed:
            state["last_removed"] = removed
            return REMOVED_ITEM_TEMPLATE.format(item=summarize_item(removed))

        return NO_REMOVE_MESSAGE

    if intent == "get_total":
        result = compute_total_with_tax(order_manager.get_order(), menu)
        return build_total_response(result)

    if intent == "get_order_count":
        pizza_count = count_total_pizzas(order_manager.get_order())
        item_count = count_total_items(order_manager.get_order())

        return ORDER_COUNT_TEMPLATE.format(
            pizza_count=pizza_count,
            item_count=item_count,
        )

    if intent == "get_order_summary":
        order = order_manager.get_order()
        return build_order_summary(order)

    if intent == "ask_last_removed":
        last_removed = state.get("last_removed")

        if last_removed:
            return LAST_REMOVED_TEMPLATE.format(
                item=summarize_item(last_removed),
            )

        return NO_LAST_REMOVED_MESSAGE

    if intent == "checkout":
        order = order_manager.get_order()

        if not order:
            return CHECKOUT_EMPTY_MESSAGE

        summary = build_order_summary(order)
        result = compute_total_with_tax(order, menu)

        return (
            f"{summary} "
            f"{build_total_response(result)} "
            f"{CHECKOUT_THANK_YOU_MESSAGE}"
        )

    if intent == "retrieval_qa":
        query = parsed.get("query", user_text)
        return answer_rag_question(query, menu)

    if intent == "menu_query":
        category = parsed.get("category")

        if is_detailed_menu_question(user_text):
            return answer_rag_question(user_text, menu)

        return handle_menu_query(category, menu)

    return answer_rag_question(user_text, menu)


def speak_or_print(response, use_voice):
    if use_voice and speak:
        speak(response)
    else:
        print("Assistant:", response)


def run_agent(use_voice=True):
    order_manager = OrderManager()
    state = {
        "last_removed": None,
        "last_modified": None,
    }

    restaurant_name = CONFIG["restaurant"]["name"]
    greeting = GREETING_TEMPLATE.format(restaurant_name=restaurant_name)

    speak_or_print(greeting, use_voice)

    while True:
        user_text = input("You: ")

        if not user_text or not user_text.strip():
            speak_or_print(VOICE_INPUT_NOT_CAUGHT_MESSAGE, use_voice)
            continue

        if user_text.lower().strip() in EXIT_WORDS:
            break

        response = handle_user_input(user_text, order_manager, MENU, state)

        speak_or_print(response, use_voice)

        if is_checkout_complete_response(response):
            break


if __name__ == "__main__":
    run_agent(use_voice=False)