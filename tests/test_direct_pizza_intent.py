"""Regression: meat lovers + RETRIEVAL_MARKERS 'meat' must not route orders to RAG."""

import json
from pathlib import Path

import pytest

from src.intent_parser import (
    parse_direct_add_pizza,
    parse_direct_pizza_modification,
    parse_direct_retrieval_qa,
    parse_intent,
)


@pytest.fixture
def menu():
    path = Path(__file__).resolve().parent.parent / "data" / "menu" / "menu.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def test_meat_lovers_order_not_routed_to_retrieval_qa(menu):
    text = "i'll take a large meat lovers pizza on stuffed crust"
    assert parse_direct_retrieval_qa(text) is None
    parsed = parse_direct_add_pizza(text, menu)
    assert parsed["intent"] == "add_item"
    item = parsed["item"]
    assert item["type"] == "pizza"
    assert item["base"] == "meat lovers"
    assert item["size"] == "large"
    assert item["crust"] == "stuffed crust"


def test_do_you_have_meat_lovers_not_treated_as_order(menu):
    text = "do you have meat lovers pizza"
    assert parse_direct_add_pizza(text, menu) is None


def test_add_extra_cheese_to_my_pizza_is_modify_not_new_cheese_pizza(menu):
    text = "add extra cheese to my pizza"
    parsed = parse_direct_pizza_modification(text, menu)
    assert parsed is not None
    assert parsed["intent"] == "modify_last_pizza"
    assert parsed["action"] == "add_toppings"
    assert "extra cheese" in parsed["toppings"]


def test_twelve_piece_wings_without_i_want_phrase(menu):
    text = "a 12 piece chicken wings please"
    parsed = parse_intent(text, menu)
    assert parsed["intent"] == "add_item"
    assert parsed["item"]["name"] == "chicken wings"
    assert parsed["item"]["size"] == "12 piece"
    assert parsed["item"]["quantity"] == 1


def test_what_is_in_chicken_wings_is_not_an_order(menu):
    text = "what is in the chicken wings"
    parsed = parse_intent(text, menu)
    assert parsed["intent"] == "retrieval_qa"


def test_veggie_no_olives_parsed_as_black_olives_removal(menu):
    text = "i want a medium veggie pizza on thin crust, no olives"
    parsed = parse_direct_add_pizza(text, menu)
    assert parsed["intent"] == "add_item"
    assert parsed["item"]["base"] == "veggie"
    assert "black olives" in parsed["item"]["removals"]
