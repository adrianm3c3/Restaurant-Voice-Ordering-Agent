# User Stories — Restaurant Voice Ordering Agent

## US-01 — Place a Pizza Order

**Given** the restaurant ordering server is running and the order is empty  
**When** the customer says `I want a large pepperoni pizza`  
**Then** the system adds one large pepperoni pizza with the default crust and confirms the item.

### Manual Walkthrough

1. Start the server.
2. Send `I want a large pepperoni pizza`.
3. Confirm the response contains `Added 1 large pepperoni pizza with hand tossed.`
4. Confirm the order contains one pizza with base `pepperoni`, size `large`, and crust `hand tossed`.

### Reference Screenshot

`docs/assets/stories/us_01_expected.png`

---

## US-02 — Ask for Order Total

**Given** the customer has added a large pepperoni pizza  
**When** the customer says `what is my total`  
**Then** the system returns the current total including tax.

### Manual Walkthrough

1. Start a fresh session.
2. Send `I want a large pepperoni pizza`.
3. Send `what is my total`.
4. Confirm the response contains `Your total is`.

### Reference Screenshot

`docs/assets/stories/us_02_expected.png`

---

## US-03 — Modify Pizza Toppings

**Given** the customer has added a pizza  
**When** the customer says `add mushrooms to my pizza`  
**Then** the system adds mushrooms to the most recent pizza.

### Manual Walkthrough

1. Start a fresh session.
2. Send `I want a medium cheese pizza`.
3. Send `add mushrooms to my pizza`.
4. Confirm the response contains `Added mushrooms to your pizza.`

### Reference Screenshot

`docs/assets/stories/us_03_expected.png`

---

## US-04 — Ask a Menu Ingredient Question

**Given** the restaurant menu knowledge base is available  
**When** the customer asks `what comes on a pepperoni pizza`  
**Then** the system answers using only retrieved restaurant menu information.

### Manual Walkthrough

1. Start a fresh session.
2. Send `what comes on a pepperoni pizza`.
3. Confirm the response describes the pepperoni pizza from the menu.
4. Confirm the response does not invent unrelated menu items.

### Reference Screenshot

`docs/assets/stories/us_04_expected.png`

---

## US-05 — Complete Checkout

**Given** the customer has an item in the order  
**When** the customer says `checkout` and provides name, pickup time, payment method, and split preference  
**Then** the system confirms the final order and ends the checkout flow.

### Manual Walkthrough

1. Start a fresh session.
2. Send `I want a large pepperoni pizza`.
3. Send `checkout`.
4. Send `Adrian`.
5. Send `6 PM`.
6. Send `card`.
7. Send `no`.
8. Confirm the response contains `Thank you for your order.`

### Reference Screenshot

`docs/assets/stories/us_05_expected.png`

---

## US-06 — Reject Irrelevant Question

**Given** the system is a restaurant ordering assistant  
**When** the customer asks `who won the football game last night`  
**Then** the system does not answer as a general chatbot and responds that the information is not in the restaurant menu.

### Manual Walkthrough

1. Start a fresh session.
2. Send `who won the football game last night`.
3. Confirm the response contains `I do not see that information in the restaurant menu.`

### Reference Screenshot

`docs/assets/stories/us_06_expected.png`

---

## US-07 — Clarify Chicken Wing Size

**Given** the menu has chicken wings with multiple size options  
**When** the customer says `I want chicken wings`  
**Then** the system asks whether the customer wants 6 piece or 12 piece chicken wings.

### Manual Walkthrough

1. Start a fresh session.
2. Send `I want chicken wings`.
3. Confirm the response contains `Would you like 6 piece or 12 piece chicken wings?`
4. Send `12 piece`.
5. Confirm the system adds 12 piece chicken wings.

### Reference Screenshot

`docs/assets/stories/us_07_expected.png`