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
        "checkout_step": None,
        "checkout_info": None,
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
    assert "total" in response.lower()
    assert "tax" not in response.lower()
    assert "subtotal" not in response.lower()

    response = handle_user_input(
        "i want to checkout now",
        order_manager,
        MENU,
        state,
    )
    assert "name for the order" in response.lower()
    assert state["checkout_step"] == "name"

    response = handle_user_input("my name is John", order_manager, MENU, state)
    assert "john" in response.lower()
    assert state["checkout_step"] == "pickup_time"

    response = handle_user_input("7pm", order_manager, MENU, state)
    assert "cash or card" in response.lower()
    assert state["checkout_step"] == "payment"

    response = handle_user_input("card", order_manager, MENU, state)
    assert "split the bill" in response.lower()
    assert state["checkout_step"] == "split_ask"

    response = handle_user_input("yes", order_manager, MENU, state)
    assert "how many" in response.lower()
    assert state["checkout_step"] == "split_count"

    response = handle_user_input("2", order_manager, MENU, state)
    assert "thank you for your order" in response.lower()
    assert "per person" in response.lower()
    assert state["checkout_step"] is None


@pytest.mark.user_story("US-03")
def test_checkout_without_splitting_bill():
    """
    Given the customer has an item in their order
    When they checkout, provide name/pickup/payment, and decline splitting
    Then the assistant confirms without per-person breakdown
    """
    order_manager = OrderManager()
    state = {
        "last_removed": None,
        "last_modified": None,
        "pending_action": None,
        "checkout_step": None,
        "checkout_info": None,
    }

    handle_user_input("add a medium cheese pizza", order_manager, MENU, state)

    response = handle_user_input("checkout", order_manager, MENU, state)
    assert "name for the order" in response.lower()

    handle_user_input("Alice", order_manager, MENU, state)
    handle_user_input("6:30pm", order_manager, MENU, state)
    handle_user_input("cash", order_manager, MENU, state)
    response = handle_user_input("no", order_manager, MENU, state)

    assert "alice" in response.lower()
    assert "6:30pm" in response.lower()
    assert "cash" in response.lower()
    assert "per person" not in response.lower()
    assert "thank you for your order" in response.lower()
    assert state["checkout_step"] is None


@pytest.mark.user_story("US-04")
def test_checkout_can_be_cancelled():
    """
    Given the customer started checkout
    When they say 'cancel' during the flow
    Then the checkout flow is aborted and they can keep ordering
    """
    order_manager = OrderManager()
    state = {
        "last_removed": None,
        "last_modified": None,
        "pending_action": None,
        "checkout_step": None,
        "checkout_info": None,
    }

    handle_user_input("add a medium cheese pizza", order_manager, MENU, state)
    handle_user_input("checkout", order_manager, MENU, state)

    response = handle_user_input("cancel", order_manager, MENU, state)
    assert "cancelled" in response.lower()
    assert state["checkout_step"] is None


@pytest.mark.user_story("US-02")
def test_order_summary_empty_before_items_added():
    """
    Given the customer has not added any items
    When the customer asks for their order
    Then the assistant says the order is empty
    """
    assert build_order_summary([]) == "Your order is currently empty."