import pytest

from src.agent import MENU, build_order_summary, handle_user_input
from src.order_manager import OrderManager


@pytest.mark.user_story("US-01")
def test_customer_can_ask_menu_question_add_pizza_and_checkout():
    """
    Given the pizza ordering agent is running
    When a customer asks about a pizza, adds it, checks the order, checks total, and checks out
    Then the assistant answers from the menu, updates the order, calculates total, and confirms checkout
    """
    order_manager = OrderManager()
    state = {
        "last_removed": None,
        "last_modified": None,
        "pending_action": None,
    }

    response = handle_user_input(
        "what comes on the supreme",
        order_manager,
        MENU,
        state,
    )
    assert "supreme" in response.lower()
    assert "pepperoni" in response.lower()

    response = handle_user_input(
        "add a large pepperoni pizza",
        order_manager,
        MENU,
        state,
    )
    assert "added" in response.lower()
    assert len(order_manager.get_order()) == 1

    response = handle_user_input(
        "what is my order",
        order_manager,
        MENU,
        state,
    )
    assert "pepperoni pizza" in response.lower()

    response = handle_user_input(
        "and my total",
        order_manager,
        MENU,
        state,
    )
    assert "subtotal" in response.lower()
    assert "tax" in response.lower()
    assert "total" in response.lower()

    response = handle_user_input(
        "i want to checkout now",
        order_manager,
        MENU,
        state,
    )
    assert "thank you for your order" in response.lower()


@pytest.mark.user_story("US-02")
def test_order_summary_empty_before_items_added():
    """
    Given the customer has not added any items
    When the customer asks for their order
    Then the assistant says the order is empty
    """
    assert build_order_summary([]) == "Your order is currently empty."