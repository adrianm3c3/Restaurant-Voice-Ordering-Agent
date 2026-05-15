import json
import re

from src.config import CONFIG
from src.intent_parser import parse_intent
from src.order_manager import OrderManager
from src.pricing import compute_total_with_tax
from src.rag_qa import answer_rag_question
from src.restaurant_text import (
    ADDED_ITEM_TEMPLATE,
    ADD_TOPPING_RESPONSE_TEMPLATE,
    CHICKEN_WINGS_SIZE_PROMPT,
    CHICKEN_WINGS_SIZE_REPROMPT,
    CHECKOUT_CANCEL_WORDS,
    CHECKOUT_CANCELLED_MESSAGE,
    CHECKOUT_COMPLETION_MARKERS,
    CHECKOUT_CONFIRMATION_NO_SPLIT_TEMPLATE,
    CHECKOUT_CONFIRMATION_WITH_SPLIT_TEMPLATE,
    CHECKOUT_EMPTY_MESSAGE,
    CHECKOUT_NAME_REPROMPT,
    CHECKOUT_PAYMENT_PROMPT,
    CHECKOUT_PAYMENT_REPROMPT,
    CHECKOUT_PICKUP_PROMPT,
    CHECKOUT_PICKUP_REPROMPT,
    CHECKOUT_SPLIT_COUNT_PROMPT,
    CHECKOUT_SPLIT_COUNT_REPROMPT,
    CHECKOUT_SPLIT_PROMPT,
    CHECKOUT_SPLIT_REPROMPT,
    CHECKOUT_THANK_YOU_MESSAGE,
    CHECKOUT_TOTAL_AND_NAME_PROMPT,
    DESCRIBE_PIZZA_EXTRAS_SUFFIX,
    DESCRIBE_PIZZA_NO_PIZZA_MESSAGE,
    DESCRIBE_PIZZA_REMOVALS_SUFFIX,
    DESCRIBE_PIZZA_TEMPLATE,
    DETAILED_MENU_MARKERS,
    EMPTY_ORDER_MESSAGE,
    EXIT_WORDS,
    GREETING_TEMPLATE,
    LAST_REMOVED_TEMPLATE,
    LLM_UNAVAILABLE_MESSAGE,
    MENU_CATEGORY_FALLBACK_MESSAGE,
    MENU_CATEGORY_TEMPLATES,
    NAME_PREFIX_PHRASES,
    NO_LAST_REMOVED_MESSAGE,
    NO_MATCHING_ITEM_TEMPLATE,
    NO_MATCHING_PIZZA_TEMPLATE,
    NO_RESPONSE_WORDS,
    NO_REMOVE_MESSAGE,
    ORDER_COUNT_TEMPLATE,
    ORDER_SUMMARY_PREFIX,
    PAYMENT_CARD_WORDS,
    PAYMENT_CASH_WORDS,
    PENDING_ACTION_CANCEL_MESSAGE,
    PENDING_ACTION_FAILED_MESSAGE,
    PICKUP_TIME_PREFIX_PHRASES,
    PIZZA_MODIFY_NOT_FOUND_MESSAGE,
    RAG_NO_CONTEXT_MESSAGE,
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
    YES_RESPONSE_WORDS,
)

from src.intent_parser import WORD_NUMBERS

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
        total=format_currency(result["total"]),
    )


def format_topping_for_customer(topping):
    if topping == "mozzarella":
        return "cheese"
    if topping == "black olives":
        return "olives"
    return topping


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
            parts.append(
                "plus "
                + ", ".join(format_topping_for_customer(t) for t in toppings)
            )

        if removals:
            parts.append(
                "no "
                + ", ".join(format_topping_for_customer(r) for r in removals)
            )

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


def join_natural_list(items):
    items = [str(x) for x in items if x]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def find_last_pizza(order):
    for item in reversed(order):
        if item.get("type") == "pizza":
            return item
    return None


def build_describe_pizza_response(order, menu):
    pizza = find_last_pizza(order)
    if not pizza:
        return DESCRIBE_PIZZA_NO_PIZZA_MESSAGE

    size = pizza.get("size", CONFIG["menu_defaults"]["default_pizza_size"])
    base = pizza.get("base", CONFIG["menu_defaults"]["default_pizza_base"])
    crust = pizza.get("crust", CONFIG["menu_defaults"]["default_crust"])
    extras = pizza.get("toppings", []) or []
    removals = pizza.get("removals", []) or []

    base_ingredients = menu["pizzas"].get(base, {}).get("ingredients", [])
    base_ingredients = [
        ing for ing in base_ingredients if ing not in removals
    ]

    response = DESCRIBE_PIZZA_TEMPLATE.format(
        size=size,
        base=base,
        ingredients=join_natural_list(base_ingredients) or "the standard ingredients",
        crust=crust,
    )

    if extras:
        response += DESCRIBE_PIZZA_EXTRAS_SUFFIX.format(
            toppings=join_natural_list(
                format_topping_for_customer(topping)
                for topping in extras
            ),
        )

    if removals:
        response += DESCRIBE_PIZZA_REMOVALS_SUFFIX.format(
            removals=join_natural_list(
                format_topping_for_customer(removal)
                for removal in removals
            ),
        )

    return response


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


def parse_wing_size_response(user_text):
    text = user_text.lower().strip()

    if "12" in text or "twelve" in text:
        return "12 piece"

    if "6" in text or "six" in text:
        return "6 piece"

    return None


def is_cancel_request(user_text):
    text = user_text.lower().strip().rstrip(".!?")
    return text in CHECKOUT_CANCEL_WORDS


def is_yes_response(user_text):
    text = user_text.lower().strip().rstrip(".!?")
    if text in YES_RESPONSE_WORDS:
        return True
    return any(text.startswith(w + " ") for w in YES_RESPONSE_WORDS)


def is_no_response(user_text):
    text = user_text.lower().strip().rstrip(".!?")
    if text in NO_RESPONSE_WORDS:
        return True
    return any(text.startswith(w + " ") for w in NO_RESPONSE_WORDS)


def parse_customer_name(user_text):
    """Strip common lead-in phrases ('my name is ...', 'this is ...') and
    return a tidy capitalized name. Returns None if nothing usable remains."""
    text = user_text.strip().rstrip(".!?")

    if not text:
        return None

    lowered = text.lower()
    for prefix in NAME_PREFIX_PHRASES:
        if lowered.startswith(prefix):
            text = text[len(prefix):].strip()
            break

    text = text.strip(" ,.")

    if not text:
        return None

    return " ".join(part.capitalize() for part in text.split())


def parse_pickup_time(user_text):
    """Return a tidy pickup time string, or None if empty."""
    text = user_text.strip().rstrip(".!?")

    if not text:
        return None

    lowered = text.lower()
    for prefix in PICKUP_TIME_PREFIX_PHRASES:
        if lowered.startswith(prefix):
            text = text[len(prefix):].strip()
            break

    return text or None


def parse_payment_method(user_text):
    text = user_text.lower().strip().rstrip(".!?")

    if not text:
        return None

    for word in PAYMENT_CARD_WORDS:
        if re.search(rf"\b{re.escape(word)}\b", text):
            return "card"

    for word in PAYMENT_CASH_WORDS:
        if re.search(rf"\b{re.escape(word)}\b", text):
            return "cash"

    return None


def parse_split_count(user_text):
    text = user_text.lower().strip().rstrip(".!?")

    digit_match = re.search(r"\b(\d+)\b", text)
    if digit_match:
        value = int(digit_match.group(1))
        return value if value >= 2 else None

    for word, value in WORD_NUMBERS.items():
        if value < 2:
            continue
        if re.search(rf"\b{re.escape(word)}\b", text):
            return value

    return None


def start_checkout_flow(order_manager, menu, state):
    order = order_manager.get_order()

    if not order:
        return CHECKOUT_EMPTY_MESSAGE

    summary = build_order_summary(order)
    result = compute_total_with_tax(order, menu)

    state["checkout_info"] = {
        "tax": result["tax"],
        "total": result["total"],
    }
    state["checkout_step"] = "name"

    return CHECKOUT_TOTAL_AND_NAME_PROMPT.format(
        summary=summary,
        totals=build_total_response(result),
    )


def reset_checkout_state(state):
    state["checkout_step"] = None
    state["checkout_info"] = None


def build_checkout_confirmation(info):
    total = format_currency(info["total"])
    split_count = info.get("split_count")

    if split_count and split_count > 1:
        per_person = round(info["total"] / split_count, 2)
        return CHECKOUT_CONFIRMATION_WITH_SPLIT_TEMPLATE.format(
            name=info["name"],
            total=total,
            split_count=split_count,
            per_person=format_currency(per_person),
            payment=info["payment"],
            pickup_time=info["pickup_time"],
        )

    return CHECKOUT_CONFIRMATION_NO_SPLIT_TEMPLATE.format(
        name=info["name"],
        total=total,
        payment=info["payment"],
        pickup_time=info["pickup_time"],
    )


def handle_checkout_step(user_text, state):
    """Drives the multi-step checkout: name -> pickup -> payment -> split."""
    if is_cancel_request(user_text):
        reset_checkout_state(state)
        return CHECKOUT_CANCELLED_MESSAGE

    step = state.get("checkout_step")
    info = state.get("checkout_info") or {}

    if step == "name":
        name = parse_customer_name(user_text)
        if not name:
            return CHECKOUT_NAME_REPROMPT
        info["name"] = name
        state["checkout_info"] = info
        state["checkout_step"] = "pickup_time"
        return CHECKOUT_PICKUP_PROMPT.format(name=name)

    if step == "pickup_time":
        pickup_time = parse_pickup_time(user_text)
        if not pickup_time:
            return CHECKOUT_PICKUP_REPROMPT
        info["pickup_time"] = pickup_time
        state["checkout_info"] = info
        state["checkout_step"] = "payment"
        return CHECKOUT_PAYMENT_PROMPT.format(pickup_time=pickup_time)

    if step == "payment":
        payment = parse_payment_method(user_text)
        if not payment:
            return CHECKOUT_PAYMENT_REPROMPT
        info["payment"] = payment
        state["checkout_info"] = info
        state["checkout_step"] = "split_ask"
        return CHECKOUT_SPLIT_PROMPT.format(payment=payment)

    if step == "split_ask":
        if is_yes_response(user_text):
            state["checkout_step"] = "split_count"
            return CHECKOUT_SPLIT_COUNT_PROMPT
        if is_no_response(user_text):
            info["split_count"] = 1
            state["checkout_info"] = info
            confirmation = build_checkout_confirmation(info)
            reset_checkout_state(state)
            return confirmation
        return CHECKOUT_SPLIT_REPROMPT

    if step == "split_count":
        count = parse_split_count(user_text)
        if not count:
            return CHECKOUT_SPLIT_COUNT_REPROMPT
        info["split_count"] = count
        state["checkout_info"] = info
        confirmation = build_checkout_confirmation(info)
        reset_checkout_state(state)
        return confirmation

    # Defensive: unknown step. Clear and bail.
    reset_checkout_state(state)
    return VOICE_INPUT_NOT_CAUGHT_MESSAGE


def handle_user_input(user_text, order_manager, menu, state):

    if state.get("checkout_step"):
        return handle_checkout_step(user_text, state)

    pending_wing_item = state.get("pending_wing_item")
    if pending_wing_item:
        wing_size = parse_wing_size_response(user_text)

        if not wing_size:
            return CHICKEN_WINGS_SIZE_REPROMPT

        pending_wing_item["size"] = wing_size
        pending_wing_item.pop("needs_size_confirmation", None)
        state["pending_wing_item"] = None
        order_manager.add_item(pending_wing_item)
        return ADDED_ITEM_TEMPLATE.format(item=summarize_item(pending_wing_item))

    parsed = parse_intent(user_text, menu)

    if CONFIG["runtime"]["debug"]:
        print("DEBUG PARSED:", parsed)

    intent = parsed.get("intent")

    if intent == "add_item":
        item = parsed["item"]

        if (
            item.get("type") == "side"
            and item.get("name") == "chicken wings"
            and item.get("needs_size_confirmation")
        ):
            state["pending_wing_item"] = item
            return CHICKEN_WINGS_SIZE_PROMPT

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

        toppings_text = ", ".join(
            format_topping_for_customer(topping)
            for topping in toppings
        )

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

    if intent == "describe_last_pizza":
        order = order_manager.get_order()
        return build_describe_pizza_response(order, menu)

    if intent == "ask_last_removed":
        last_removed = state.get("last_removed")

        if last_removed:
            return LAST_REMOVED_TEMPLATE.format(
                item=summarize_item(last_removed),
            )

        return NO_LAST_REMOVED_MESSAGE

    if intent == "checkout":
        return start_checkout_flow(order_manager, menu, state)

    if intent == "retrieval_qa":
        query = parsed.get("query", user_text)
        return answer_rag_question(query, menu)

    if intent == "menu_query":
        category = parsed.get("category")

        if is_detailed_menu_question(user_text):
            return answer_rag_question(user_text, menu)

        return handle_menu_query(category, menu)

    if intent == "llm_unavailable":
        return RAG_NO_CONTEXT_MESSAGE

    return answer_rag_question(user_text, menu)


def speak_or_print(response, use_voice):
    print("Assistant:", response)

    if use_voice and speak:
        speak(response)


def run_agent(use_voice=True):
    order_manager = OrderManager()
    state = {
        "last_removed": None,
        "last_modified": None,
        "pending_wing_item": None,
        "checkout_step": None,
        "checkout_info": None,
    }

    restaurant_name = CONFIG["restaurant"]["name"]
    greeting = GREETING_TEMPLATE.format(restaurant_name=restaurant_name)

    speak_or_print(greeting, use_voice)

    while True:
        try:
            user_text = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_text or not user_text.strip():
            speak_or_print(VOICE_INPUT_NOT_CAUGHT_MESSAGE, use_voice)
            continue

        if user_text.lower().strip() in EXIT_WORDS:
            break

        try:
            response = handle_user_input(user_text, order_manager, MENU, state)
        except Exception as exc:
            if CONFIG["runtime"]["debug"]:
                print("DEBUG handle_user_input error:", exc)
            response = LLM_UNAVAILABLE_MESSAGE

        speak_or_print(response, use_voice)

        if is_checkout_complete_response(response):
            break


if __name__ == "__main__":
    run_agent(use_voice=CONFIG["voice"]["tts_enabled"])