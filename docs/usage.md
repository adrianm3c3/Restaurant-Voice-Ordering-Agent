# Usage Guide

This guide maps each user story to exact manual steps that a TA or tester can follow against the running system.

The recommended grading interface is the local API endpoint:

POST /api/chat

This endpoint uses the same restaurant agent logic as the Twilio phone-call path, but it does not require Twilio, ngrok, or a phone call.

## Start the System

From the project root:

docker compose up --build

In another terminal, confirm the server is healthy:

Invoke-RestMethod http://127.0.0.1:5000/health

Expected response:

{
  "status": "ok"
}

---

## US-01 — Place a Pizza Order

### Goal

Verify that a customer can add a pizza to an empty order.

### Steps

1. Start the system with `docker compose up --build`.
2. Send this request:

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/chat" `
  -ContentType "application/json" `
  -Body '{"session_id":"us01","text":"I want a large pepperoni pizza"}'

### Expected Result

The response should contain:

Added 1 large pepperoni pizza with hand tossed.

The returned order should contain one pizza with:

- type: pizza
- base: pepperoni
- size: large
- crust: hand tossed
- quantity: 1

### Reference Screenshot

docs/assets/stories/us_01_expected.png

---

## US-02 — Ask for Order Total

### Goal

Verify that the system preserves session state and calculates the current order total.

### Steps

1. Start a fresh session named `us02`.
2. Add a pizza:

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/chat" `
  -ContentType "application/json" `
  -Body '{"session_id":"us02","text":"I want a large pepperoni pizza"}'

3. Ask for the total:

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/chat" `
  -ContentType "application/json" `
  -Body '{"session_id":"us02","text":"what is my total"}'

### Expected Result

The response should contain:

Your total is $14.04.

The returned order should still contain the large pepperoni pizza from the first step.

### Reference Screenshot

docs/assets/stories/us_02_expected.png

---

## US-03 — Modify Pizza Toppings

### Goal

Verify that the customer can modify the most recent pizza by adding a topping.

### Steps

1. Start a fresh session named `us03`.
2. Add a medium cheese pizza:

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/chat" `
  -ContentType "application/json" `
  -Body '{"session_id":"us03","text":"I want a medium cheese pizza"}'

3. Add mushrooms to the pizza:

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/chat" `
  -ContentType "application/json" `
  -Body '{"session_id":"us03","text":"add mushrooms to my pizza"}'

### Expected Result

The response should contain:

Added mushrooms to your pizza.

The returned order should show the pizza with `mushrooms` in the toppings list.

### Reference Screenshot

docs/assets/stories/us_03_expected.png

---

## US-04 — Ask a Menu Ingredient Question

### Goal

Verify that the customer can ask a menu question and receive a restaurant-menu-bounded answer.

### Steps

1. Start a fresh session named `us04`.
2. Ask what comes on a pepperoni pizza:

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/chat" `
  -ContentType "application/json" `
  -Body '{"session_id":"us04","text":"what comes on a pepperoni pizza"}'

### Expected Result

The response should:

- Answer using restaurant menu information.
- Mention pizza or pepperoni.
- Avoid unrelated general knowledge.
- Not invent non-menu details.

Acceptable response examples include a description of pepperoni pizza ingredients or a restaurant-menu fallback if the live LLM endpoint is unavailable.

### Reference Screenshot

docs/assets/stories/us_04_expected.png

---

## US-05 — Complete Checkout

### Goal

Verify that a customer can complete the checkout flow after adding an item.

### Steps

1. Start a fresh session named `us05`.
2. Add a pizza:

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/chat" `
  -ContentType "application/json" `
  -Body '{"session_id":"us05","text":"I want a large pepperoni pizza"}'

3. Start checkout:

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/chat" `
  -ContentType "application/json" `
  -Body '{"session_id":"us05","text":"checkout"}'

4. Provide the customer name:

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/chat" `
  -ContentType "application/json" `
  -Body '{"session_id":"us05","text":"Adrian"}'

5. Provide pickup time:

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/chat" `
  -ContentType "application/json" `
  -Body '{"session_id":"us05","text":"6 PM"}'

6. Provide payment method:

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/chat" `
  -ContentType "application/json" `
  -Body '{"session_id":"us05","text":"card"}'

7. Decline split bill:

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/chat" `
  -ContentType "application/json" `
  -Body '{"session_id":"us05","text":"no"}'

### Expected Result

The final response should contain:

Thank you for your order.

The checkout flow should collect:

- Customer name
- Pickup time
- Payment method
- Split-bill preference

### Reference Screenshot

docs/assets/stories/us_05_expected.png

---

## US-06 — Reject Irrelevant Question

### Goal

Verify that the system does not behave like an unrestricted general chatbot.

This is an error-path story.

### Steps

1. Start a fresh session named `us06`.
2. Ask an unrelated sports question:

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/chat" `
  -ContentType "application/json" `
  -Body '{"session_id":"us06","text":"who won the football game last night"}'

### Expected Result

The response should not answer the football question.

Expected response:

I do not see that information in the restaurant menu.

Other acceptable restaurant-bounded fallback responses are allowed if they clearly refuse to answer unrelated general knowledge and redirect to restaurant/menu scope.

### Reference Screenshot

docs/assets/stories/us_06_expected.png

---

## US-07 — Clarify Chicken Wing Size

### Goal

Verify that the system asks a clarification question when the customer orders chicken wings without specifying a size.

This is a clarification/error-path story.

### Steps

1. Start a fresh session named `us07`.
2. Ask for chicken wings without a size:

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/chat" `
  -ContentType "application/json" `
  -Body '{"session_id":"us07","text":"I want chicken wings"}'

3. Respond with a size:

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/chat" `
  -ContentType "application/json" `
  -Body '{"session_id":"us07","text":"12 piece"}'

### Expected Result

After the first request, the system should ask:

Would you like 6 piece or 12 piece chicken wings?

After the second request, the system should add 12 piece chicken wings to the order.

Expected final response should contain:

Added

and the returned order should include:

- name: chicken wings
- size: 12 piece

### Reference Screenshot

docs/assets/stories/us_07_expected.png

---

## Twilio Voice Walkthrough

The API walkthrough above is the grading-friendly path. The Twilio voice mode can be tested manually if a Twilio number and ngrok tunnel are configured.

### Steps

1. Start the Flask server locally or through Docker.
2. Start ngrok:

ngrok http 5000

3. Copy the HTTPS ngrok URL.
4. In Twilio phone number voice settings, set:

Webhook URL: https://banked-fervor-scouts.ngrok-free.dev/voice
Method: HTTP POST

5. Call the Twilio phone number.
6. Say:

I want a large pepperoni pizza

7. After the bot responds, say:

what is my total

### Expected Result

The phone bot should add the pizza and then return the same total as the API flow.

---


## Notes for Manual Walkthrough

- Use a unique `session_id` for each story.
- Reusing the same `session_id` preserves order state.
- Changing the `session_id` starts an independent order.
- The `/api/chat` endpoint is preferred for grading because it is deterministic and does not require a phone call.
- Twilio mode uses Twilio speech-to-text and Twilio text-to-speech.
- Local Whisper and pyttsx3 scripts are optional and are not required for this walkthrough.
- Optional phone demo: after starting the Docker server on port `5000` and starting the ngrok tunnel, the Twilio demo number `+1 (210) 981-4764` can be called to test the live voice-ordering flow.
- The Twilio webhook must point to `https://banked-fervor-scouts.ngrok-free.dev/voice` with method `HTTP POST`.
- If the Docker server or ngrok tunnel is not running, the phone number will not reach the ordering agent.

### Optional Phone Demo Requirements

The official grading path is `/api/chat`. Phone mode is optional.

To use the Twilio demo number, run:

```bash
docker compose up --build -d
ngrok http --domain=banked-fervor-scouts.ngrok-free.dev 5000
