import pytest

from src.agent import handle_user_input, MENU
from src.order_manager import OrderManager


def make_state():
    return {
        "last_removed": None,
        "last_modified": None,
        "pending_wing_item": None,
        "checkout_step": None,
        "checkout_info": None,
    }


def make_session():
    return OrderManager(), make_state()


@pytest.mark.user_story("US-01")
def test_us_01_place_pizza_order():
    """
    Given an empty order
    When the customer orders a large pepperoni pizza
    Then the system adds one large pepperoni pizza with default crust
    """
    order_manager, state = make_session()

    reply = handle_user_input(
        "I want a large pepperoni pizza",
        order_manager,
        MENU,
        state,
    )

    order = order_manager.get_order()

    assert "Added 1 large pepperoni pizza with hand tossed" in reply
    assert len(order) == 1
    assert order[0]["type"] == "pizza"
    assert order[0]["base"] == "pepperoni"
    assert order[0]["size"] == "large"
    assert order[0]["crust"] == "hand tossed"


@pytest.mark.user_story("US-02")
def test_us_02_order_total():
    """
    Given the customer has ordered a large pepperoni pizza
    When the customer asks for the total
    Then the system returns the current total
    """
    order_manager, state = make_session()

    handle_user_input("I want a large pepperoni pizza", order_manager, MENU, state)
    reply = handle_user_input("what is my total", order_manager, MENU, state)

    assert "Your total is" in reply
    assert "$" in reply


@pytest.mark.user_story("US-03")
def test_us_03_modify_pizza_toppings():
    """
    Given the customer has ordered a pizza
    When the customer adds mushrooms to the pizza
    Then the system modifies the most recent pizza
    """
    order_manager, state = make_session()

    handle_user_input("I want a medium cheese pizza", order_manager, MENU, state)
    reply = handle_user_input("add mushrooms to my pizza", order_manager, MENU, state)

    order = order_manager.get_order()

    assert "Added mushrooms to your pizza" in reply
    assert "mushrooms" in order[0]["toppings"]


@pytest.mark.user_story("US-04")
def test_us_04_menu_ingredient_question_routes_to_rag(monkeypatch):
    """
    Given the menu knowledge base is available
    When the customer asks what comes on a pepperoni pizza
    Then the agent routes the question to menu knowledge answering
    """
    order_manager, state = make_session()

    def fake_answer_rag_question(question, menu):
        assert "pepperoni" in question
        return "Pepperoni pizza includes pizza sauce, mozzarella, and pepperoni."

    monkeypatch.setattr(
        "src.agent.answer_rag_question",
        fake_answer_rag_question,
    )

    reply = handle_user_input(
        "what comes on a pepperoni pizza",
        order_manager,
        MENU,
        state,
    )

    assert "Pepperoni pizza includes" in reply
    assert "pepperoni" in reply.lower()


@pytest.mark.user_story("US-05")
def test_us_05_checkout_flow():
    """
    Given the customer has an item in the order
    When the customer completes checkout steps
    Then the system confirms the order and thanks the customer
    """
    order_manager, state = make_session()

    handle_user_input("I want a large pepperoni pizza", order_manager, MENU, state)

    reply1 = handle_user_input("checkout", order_manager, MENU, state)
    reply2 = handle_user_input("Adrian", order_manager, MENU, state)
    reply3 = handle_user_input("6 PM", order_manager, MENU, state)
    reply4 = handle_user_input("card", order_manager, MENU, state)
    reply5 = handle_user_input("no", order_manager, MENU, state)

    assert "Can I get a name" in reply1
    assert "What time" in reply2
    assert "cash or card" in reply3
    assert "split the bill" in reply4
    assert "Thank you for your order" in reply5


@pytest.mark.user_story("US-06")
def test_us_06_irrelevant_question_routes_to_restaurant_fallback(monkeypatch):
    """
    Given the system is a restaurant ordering assistant
    When the customer asks an unrelated sports question
    Then the system does not answer as a general chatbot
    """
    order_manager, state = make_session()

    def fake_answer_rag_question(question, menu):
        assert "football" in question
        return "I do not see that information in the restaurant menu."

    monkeypatch.setattr(
        "src.agent.answer_rag_question",
        fake_answer_rag_question,
    )

    reply = handle_user_input(
        "who won the football game last night",
        order_manager,
        MENU,
        state,
    )

    assert "restaurant menu" in reply.lower()


@pytest.mark.user_story("US-07")
def test_us_07_chicken_wing_size_clarification():
    """
    Given chicken wings have multiple sizes
    When the customer asks for chicken wings without specifying size
    Then the system asks for a 6 piece or 12 piece clarification
    """
    order_manager, state = make_session()

    reply1 = handle_user_input("I want chicken wings", order_manager, MENU, state)
    reply2 = handle_user_input("12 piece", order_manager, MENU, state)

    order = order_manager.get_order()

    assert "6 piece or 12 piece" in reply1
    assert "Added" in reply2
    assert order[0]["name"] == "chicken wings"
    assert order[0]["size"] == "12 piece"