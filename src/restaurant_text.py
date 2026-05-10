# =========================
# Response wording
# =========================

SINGULAR_SPECIAL_CASES = {
    "breadsticks": "order of breadsticks",
    "garlic knots": "order of garlic knots",
    "mozzarella sticks": "order of mozzarella sticks",
    "fries": "order of fries",
    "chicken wings": "order of chicken wings",
}

PLURAL_SPECIAL_CASES = {
    "coke": "cokes",
    "diet coke": "diet cokes",
    "sprite": "sprites",
    "lemonade": "lemonades",
    "iced tea": "iced teas",
    "orange soda": "orange sodas",
    "bottled water": "bottled waters",
    "brownie": "brownies",
    "chocolate chip cookie": "chocolate chip cookies",
    "cheesecake": "cheesecakes",
    "tiramisu": "tiramisus",
    "breadsticks": "orders of breadsticks",
    "garlic knots": "orders of garlic knots",
    "mozzarella sticks": "orders of mozzarella sticks",
    "side salad": "side salads",
    "fries": "orders of fries",
    "chicken wings": "orders of chicken wings",
}

EXIT_WORDS = {
    "quit",
    "exit",
}

TOTAL_TEMPLATE = (
    "Your subtotal is {subtotal}, "
    "tax is {tax}, "
    "and your total is {total}."
)

GREETING_TEMPLATE = (
    "Hello, welcome to {restaurant_name}. "
    "What would you like to order?"
)

ADDED_ITEM_TEMPLATE = "Added {item}."
REMOVED_ITEM_TEMPLATE = "Removed {item}."

EMPTY_ORDER_MESSAGE = "Your order is currently empty."
ORDER_SUMMARY_PREFIX = "Your order contains: "
NO_REMOVE_MESSAGE = "There is nothing to remove."

CHECKOUT_EMPTY_MESSAGE = (
    "Your order is empty. Please add something before checkout."
)

CHECKOUT_THANK_YOU_MESSAGE = "Thank you for your order."

RAG_NO_CONTEXT_MESSAGE = (
    "I do not see that information in the restaurant menu."
)

RAG_EMPTY_RESPONSE_MESSAGE = (
    "I’m sorry, I couldn’t answer that from the menu."
)

CRUST_EXTRA_COST_TEMPLATE = (
    "{crust} costs an additional {extra_cost}. "
    "Would you like me to update your pizza?"
)

CRUST_NO_EXTRA_COST_TEMPLATE = (
    "{crust} has no additional cost. "
    "Would you like me to update your pizza?"
)

PENDING_ACTION_CANCEL_MESSAGE = "Okay, I will leave it unchanged."
PENDING_ACTION_FAILED_MESSAGE = "I could not complete that pending action."

PIZZA_MODIFY_NOT_FOUND_MESSAGE = (
    "I could not find a pizza in your order to modify."
)

UNKNOWN_CRUST_MESSAGE = "I could not find that crust option."
UPDATED_PIZZA_MESSAGE = "I updated your pizza."
NO_LAST_REMOVED_MESSAGE = "No item has been removed yet."
VOICE_INPUT_NOT_CAUGHT_MESSAGE = "I did not catch that. Please say that again."

REMOVE_TOPPING_RESPONSE_TEMPLATE = "Removed {toppings} from your pizza."
ADD_TOPPING_RESPONSE_TEMPLATE = "Added {toppings} to your pizza."
UPDATED_CRUST_TEMPLATE = "Updated your pizza to {crust}."
LAST_REMOVED_TEMPLATE = "The last item removed was {item}."

ORDER_COUNT_TEMPLATE = (
    "You currently have {pizza_count} pizza(s) "
    "and {item_count} total item(s) in your order."
)

NO_MATCHING_PIZZA_TEMPLATE = (
    "I could not find a {description} pizza in your order."
)

NO_MATCHING_ITEM_TEMPLATE = "I could not find {name} in your order."

REMOVE_LAST_PIZZA_TEMPLATE = "Removed {quantity} pizza(s) from your order."

REMOVE_NAMED_PIZZA_TEMPLATE = (
    "Removed {quantity} {size}{name} {pizza_word} from your order."
)

REMOVE_NAMED_ITEM_TEMPLATE = "Removed {quantity} {item} from your order."

MENU_CATEGORY_TEMPLATES = {
    "pizzas": "Our pizzas are {items}.",
    "toppings": "Our toppings are {items}.",
    "sides": "Our sides are {items}.",
    "drinks": "Our drinks are {items}.",
    "desserts": "Our desserts are {items}.",
    "crusts": "Our crust options are {items}.",
    "sizes": "Our pizza sizes are {items}.",
}

MENU_CATEGORY_FALLBACK_MESSAGE = (
    "I can help with pizzas, toppings, crusts, sizes, sides, drinks, and desserts."
)

CHECKOUT_COMPLETION_MARKERS = [
    "thank you for your order",
]


# =========================
# Menu/RAG routing markers
# =========================

DETAILED_MENU_MARKERS = [
    "ingredient",
    "ingredients",
    "what comes in",
    "what comes on",
    "what is in",
    "what's in",
    "price of",
    "how much is",
    "spicy",
    "vegetarian",
    "vegan",
    "gluten free",
    "gluten-free",
    "contains",
    "difference between",
    "allergy",
    "allergies",
    "dairy",
    "meat",
    "special",
    "specials",
    "recommend",
    "what do you recommend",
    "recommend something",
    "recommendation",
]

RETRIEVAL_MARKERS = [
    "what comes on",
    "what comes in",
    "what is on",
    "what is in",
    "what's on",
    "what's in",
    "ingredients",
    "ingredient",
    "does it have",
    "does the",
    "do you have anything",
    "vegetarian",
    "vegan",
    "gluten free",
    "gluten-free",
    "allergy",
    "allergies",
    "dairy",
    "meat",
    "spicy",
    "contains",
    "difference between",
    "compare",
    "which pizza",
    "which pizzas",
    "recommend",
    "what do you recommend",
    "recommend something",
    "recommendation",
    "popular",
    "special",
    "specials",
]

MENU_PRICE_MARKERS = [
    "how much is",
    "how much are",
    "how much does",
    "price of",
    "cost of",
]


# =========================
# Intent parser phrase triggers
# =========================

MENU_QUERY_PHRASES = {
    "pizzas": [
        "what pizzas do you have",
        "what pizzas are there",
        "types of pizza",
        "types of pizzas",
        "pizza options",
        "what kind of pizza",
        "what kinds of pizza",
    ],
    "toppings": [
        "what toppings do you have",
        "what toppings are there",
        "toppings do you have",
        "what can i add",
    ],
    "sides": [
        "what sides do you have",
        "what sides are there",
        "sides do you have",
        "what sides can i get",
        "what sides can i have",
    ],
    "drinks": [
        "what drinks do you have",
        "what drinks are there",
        "drinks do you have",
    ],
    "desserts": [
        "what desserts do you have",
        "what desserts are there",
        "desserts do you have",
        "any desserts",
    ],
    "crusts": [
        "what crusts do you have",
        "what crust options do you have",
        "types of crust",
        "types of crusts",
        "what crust do you have",
    ],
    "sizes": [
        "what sizes do you have",
        "what sizes are there",
        "pizza sizes",
        "sizes do you have",
    ],
}

ADD_ITEM_PHRASES = [
    "add",
    "get",
    "have",
    "want",
    "like",
    "hook me up",
    "lemme get",
    "throw in",
]

REMOVE_ITEM_PHRASES = [
    "remove",
    "delete",
    "take off",
    "cancel",
]

CHECKOUT_PHRASES = [
    "checkout",
    "check out",
    "done",
    "that's all",
    "thats all",
    "finish order",
]

TOTAL_PHRASES = [
    "total",
    "cost so far",
    "order total",
    "my total",
]

ORDER_COUNT_PHRASES = [
    "how many pizzas do i have",
    "how many pizzas are in my order",
    "how many are in my order",
    "how many items do i have",
    "how many items are in my order",
    "how many pizzas",
    "how many in my order",
]

ORDER_SUMMARY_PHRASES = [
    "what is my current order",
    "what's my current order",
    "what is my order",
    "what's my order",
    "show my order",
    "read back my order",
    "what do i have",
    "what have i ordered",
]

ASK_LAST_REMOVED_PHRASES = [
    "which pizza was removed",
    "what was removed",
    "what did you remove",
    "which item was removed",
]

PIZZA_REFERENCE_PHRASES = [
    "my pizza",
    "the pizza",
    "that pizza",
    "last pizza",
    "to it",
    "on it",
]

ADD_TOPPING_PHRASES = [
    "add",
    "put",
    "include",
    "with",
]

REMOVE_TOPPING_PHRASES = [
    "remove",
    "take off",
    "without",
    "no ",
]

CRUST_CHANGE_PHRASES = [
    "change",
    "switch",
    "make",
]


# =========================
# Menu item name variants / synonyms
# =========================

NAME_VARIANTS = {
    "meat lovers": [
        "meat lover",
        "meat lovers",
        "meatlovers",
        "meat lovers pizza",
    ],
    "bbq chicken": [
        "bbq chicken",
        "barbecue chicken",
        "barbeque chicken",
        "bbq chicken pizza",
    ],
    "buffalo chicken": [
        "buffalo chicken",
        "buffalo chicken pizza",
        "buffalo",
    ],
    "white pizza": [
        "white pizza",
        "white pie",
        "white",
    ],
    "mushrooms": [
        "mushroom",
        "mushrooms",
    ],
    "onions": [
        "onion",
        "onions",
    ],
    "bell peppers": [
        "bell pepper",
        "bell peppers",
        "peppers",
        "pepper",
    ],
    "black olives": [
        "black olive",
        "black olives",
        "olive",
        "olives",
    ],
    "jalapeños": [
        "jalapeño",
        "jalapeños",
        "jalapeno",
        "jalapenos",
    ],
    "tomatoes": [
        "tomato",
        "tomatoes",
    ],
    "grilled chicken": [
        "grilled chicken",
        "chicken",
    ],
    "extra cheese": [
        "extra cheese",
        "more cheese",
        "cheese",
    ],
    "garlic drizzle": [
        "garlic drizzle",
        "garlic sauce",
    ],
    "ranch drizzle": [
        "ranch drizzle",
        "ranch",
    ],
    "bbq drizzle": [
        "bbq drizzle",
        "bbq sauce",
        "barbecue sauce",
        "barbecue drizzle",
    ],
    "buffalo drizzle": [
        "buffalo drizzle",
        "buffalo sauce",
    ],
    "thin crust": [
        "thin crust",
        "thin",
    ],
    "hand tossed": [
        "hand tossed",
        "hand-tossed",
        "regular crust",
        "normal crust",
        "regular",
    ],
    "pan crust": [
        "pan crust",
        "pan",
    ],
    "stuffed crust": [
        "stuffed crust",
        "stuffed",
    ],
    "gluten-free crust": [
        "gluten free",
        "gluten-free",
        "gluten free crust",
        "gluten-free crust",
    ],
    "breadsticks": [
        "breadstick",
        "breadsticks",
    ],
    "cheesy bread": [
        "cheese bread",
        "cheesy bread",
    ],
    "garlic knots": [
        "garlic knot",
        "garlic knots",
    ],
    "mozzarella sticks": [
        "mozzarella stick",
        "mozzarella sticks",
    ],
    "chicken wings": [
        "chicken wing",
        "chicken wings",
        "wing",
        "wings",
    ],
    "side salad": [
        "salad",
        "side salad",
    ],
    "coke": [
        "coke",
        "cokes",
    ],
    "diet coke": [
        "diet coke",
        "diet cokes",
    ],
    "sprite": [
        "sprite",
        "sprites",
    ],
    "dr pepper": [
        "dr pepper",
        "dr. pepper",
        "doctor pepper",
    ],
    "lemonade": [
        "lemonade",
        "lemonades",
    ],
    "iced tea": [
        "iced tea",
        "iced teas",
    ],
    "orange soda": [
        "orange soda",
        "orange sodas",
    ],
    "bottled water": [
        "bottled water",
        "bottled waters",
        "water",
        "waters",
    ],
    "chocolate chip cookie": [
        "cookie",
        "cookies",
        "chocolate chip cookie",
        "chocolate chip cookies",
    ],
    "cinnamon sticks": [
        "cinnamon stick",
        "cinnamon sticks",
    ],
}


# =========================
# RAG knowledge chunk wording
# =========================

PIZZA_CHUNK_TEMPLATE = (
    "{name} pizza includes {ingredients}. "
    "Prices are {price_text}."
)

SPICY_HINT_TEXT = (
    "This item has ingredients commonly associated with spicy flavor."
)

VEGETARIAN_PIZZA_TEXT = "This is a vegetarian pizza."
CONTAINS_CHICKEN_TEXT = "Contains chicken."
CONTAINS_PORK_TEXT = "Contains pork."
CONTAINS_MEAT_TEXT = "Contains meat."
POPULAR_ITEM_TEXT = "This is one of the restaurant's popular items."
GLUTEN_FREE_CRUST_TEXT = "Gluten-free crust is available."
SAUCE_INFORMATION_TEMPLATE = "Sauce information: {sauces}."

SPICY_INGREDIENT_MARKERS = [
    "jalapeños",
    "buffalo sauce",
]

VEGETARIAN_PIZZAS = {
    "cheese",
    "veggie",
    "margherita",
    "white pizza",
}

PORK_MARKERS = [
    "ham",
    "bacon",
    "sausage",
    "pepperoni",
]

MEAT_MARKERS = [
    "pepperoni",
    "sausage",
    "bacon",
    "ham",
    "chicken",
    "beef",
]

SPICY_TOPPINGS = {
    "jalapeños",
    "buffalo drizzle",
}

VEGETARIAN_TOPPINGS = {
    "mushrooms",
    "onions",
    "bell peppers",
    "black olives",
    "spinach",
    "tomatoes",
    "pineapple",
}

ALLERGEN_MARKERS = {
    "dairy": [
        "mozzarella",
        "ricotta",
        "feta",
        "parmesan",
        "extra cheese",
    ],
    "gluten": [
        "pizza dough",
        "crust",
        "breadsticks",
        "cheesy bread",
        "garlic knots",
        "mozzarella sticks",
        "fries",
        "cinnamon sticks",
    ],
    "garlic": [
        "garlic sauce",
        "garlic drizzle",
        "garlic knots",
    ],
    "tomato": [
        "pizza sauce",
        "tomato sauce",
        "tomatoes",
    ],
}

SAUCE_MARKERS = [
    "pizza sauce",
    "tomato sauce",
    "bbq sauce",
    "buffalo sauce",
    "garlic sauce",
]

PIZZA_STYLE_HINTS = {
    "bbq chicken": "This pizza is sweet and smoky.",
    "buffalo chicken": "This pizza is spicy and tangy.",
    "hawaiian": "This pizza is sweet and savory.",
    "white pizza": "This pizza uses garlic sauce instead of tomato sauce.",
    "margherita": (
        "This pizza is a vegetarian pizza with tomato sauce, "
        "mozzarella, and basil. It contains dairy and is not vegan."
    ),
    "meat lovers": "This pizza is meat-heavy and contains pork.",
    "supreme": "This pizza has both meat and vegetables.",
}

POPULAR_ITEMS = {
    "pepperoni",
    "buffalo chicken",
    "mozzarella sticks",
    "chocolate chip cookie",
}

FAQ_CHUNKS = [
    {
        "id": "faq_gluten",
        "type": "faq",
        "category": "allergy",
        "name": "gluten_free",
        "text": (
            "Gluten-free crust is available. "
            "Cross-contamination information is not guaranteed."
        ),
    },
    {
        "id": "faq_vegetarian",
        "type": "faq",
        "category": "dietary",
        "name": "vegetarian",
        "text": (
            "Vegetarian options include cheese pizza, veggie pizza, "
            "margherita pizza, white pizza, and vegetable toppings such as "
            "mushrooms, onions, bell peppers, black olives, spinach, "
            "tomatoes, and pineapple. Vegetarian items may still contain dairy."
        ),
    },
    {
        "id": "faq_vegan",
        "type": "faq",
        "category": "dietary",
        "name": "vegan",
        "text": (
            "The menu does not list any fully vegan pizzas. "
            "Cheese-containing pizzas are not vegan."
        ),
    },
    {
        "id": "faq_spicy",
        "type": "faq",
        "category": "spicy_food",
        "name": "spicy",
        "text": (
            "Spicy and hot options include jalapeños, "
            "buffalo drizzle, and buffalo chicken pizza."
        ),
    },
    {
        "id": "faq_nutrition",
        "type": "faq",
        "category": "nutrition",
        "name": "nutrition_information",
        "text": (
            "The menu does not list nutrition facts such as calories, "
            "protein, carbohydrates, fat, sodium, or macro information."
        ),
    },
    {
        "id": "faq_meat_and_pork",
        "type": "faq",
        "category": "dietary",
        "name": "meat_and_pork",
        "text": (
            "Pizzas containing pork include pepperoni, meat lovers, "
            "hawaiian, and supreme. Pizzas containing chicken include "
            "bbq chicken and buffalo chicken. Meat lovers is the most "
            "meat-heavy pizza."
        ),
    },

    {
        "id": "faq_tomato_sauce",
        "type": "faq",
        "category": "sauces",
        "name": "tomato_sauce",
        "text": (
            "Pizzas with tomato-based sauce include cheese pizza, pepperoni pizza, "
            "supreme pizza, veggie pizza, hawaiian pizza, meat lovers pizza, "
            "and margherita pizza. Cheese, pepperoni, supreme, veggie, "
            "hawaiian, and meat lovers use pizza sauce. "
            "Margherita uses tomato sauce. "
            "White pizza uses garlic sauce instead of tomato sauce. "
            "BBQ chicken pizza uses bbq sauce. "
            "Buffalo chicken pizza uses buffalo sauce."
        ),
    },

    {
        "id": "faq_recommendations",
        "type": "faq",
        "category": "recommendations",
        "name": "popular_recommendations",
        "text": (
            "Popular recommended items include pepperoni pizza, "
            "buffalo chicken pizza, mozzarella sticks, and "
            "chocolate chip cookie."
        ),
    },
]


MODIFICATION_POLICY_CHUNKS = [
    {
        "id": "faq_modifications",
        "type": "faq",
        "category": "modifications",
        "name": "modifications",
        "text": (
            "Customers can add or remove toppings from pizzas. "
            "Adding toppings may increase the price. "
            "Removing toppings does not reduce the price."
        ),
    },
    {
        "id": "faq_crust_modifications",
        "type": "faq",
        "category": "modifications",
        "name": "crust_modifications",
        "text": (
            "Customers can change the crust on a pizza. "
            "Pan crust, stuffed crust, and gluten-free crust may cost extra."
        ),
    },
]