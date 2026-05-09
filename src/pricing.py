import logging

from src.config import CONFIG


logger = logging.getLogger(__name__)


DEFAULT_CRUST = CONFIG["menu_defaults"]["default_crust"]
DEFAULT_WING_SIZE = CONFIG["menu_defaults"]["default_wing_size"]


def calculate_pizza_price(pizza, menu):
    try:
        base = pizza["base"]
        size = pizza["size"]

        crust = pizza.get(
            "crust",
            DEFAULT_CRUST,
        )

        toppings = pizza.get("toppings", [])
        quantity = pizza.get("quantity", 1)

        base_price = menu["pizzas"][base]["base_price"][size]

        crust_price = menu["crust_price"].get(
            crust,
            0,
        )

        toppings_cost = sum(
            menu["toppings_price"].get(topping, 0)
            for topping in toppings
        )

        total = (
            base_price
            + crust_price
            + toppings_cost
        ) * quantity

        return round(total, 2)

    except KeyError as e:
        logger.error("Invalid pizza field: %s", e)
        return 0

    except Exception as e:
        logger.exception("Pizza pricing failed: %s", e)
        return 0


def calculate_side_price(item, menu):
    try:
        name = item["name"]
        quantity = item.get("quantity", 1)

        if name == "chicken wings":
            size = item.get(
                "size",
                DEFAULT_WING_SIZE,
            )

            price = menu["sides"][name][size]

        else:
            price = menu["sides"][name]

        return round(price * quantity, 2)

    except KeyError as e:
        logger.error("Invalid side item: %s", e)
        return 0

    except Exception as e:
        logger.exception("Side pricing failed: %s", e)
        return 0


def calculate_drink_price(item, menu):
    try:
        name = item["name"]
        quantity = item.get("quantity", 1)

        price = menu["drinks"][name]

        return round(price * quantity, 2)

    except KeyError as e:
        logger.error("Invalid drink item: %s", e)
        return 0

    except Exception as e:
        logger.exception("Drink pricing failed: %s", e)
        return 0


def calculate_dessert_price(item, menu):
    try:
        name = item["name"]
        quantity = item.get("quantity", 1)

        price = menu["desserts"][name]

        return round(price * quantity, 2)

    except KeyError as e:
        logger.error("Invalid dessert item: %s", e)
        return 0

    except Exception as e:
        logger.exception("Dessert pricing failed: %s", e)
        return 0


def apply_tax(subtotal, tax_rate=None):
    if tax_rate is None:
        tax_rate = CONFIG["pricing"]["tax_rate"]

    tax = subtotal * tax_rate
    total_with_tax = subtotal + tax

    return (
        round(tax, 2),
        round(total_with_tax, 2),
    )


def compute_subtotal(order, menu):
    subtotal = 0

    for item in order:
        item_type = item.get("type")

        if item_type == "pizza":
            subtotal += calculate_pizza_price(item, menu)

        elif item_type == "side":
            subtotal += calculate_side_price(item, menu)

        elif item_type == "drink":
            subtotal += calculate_drink_price(item, menu)

        elif item_type == "dessert":
            subtotal += calculate_dessert_price(item, menu)

        else:
            logger.warning(
                "Unknown item type: %s",
                item_type,
            )

    return round(subtotal, 2)


def compute_total_with_tax(order, menu, tax_rate=None):
    subtotal = compute_subtotal(order, menu)

    tax, total = apply_tax(
        subtotal,
        tax_rate,
    )

    return {
        "subtotal": round(subtotal, 2),
        "tax": tax,
        "total": total,
    }