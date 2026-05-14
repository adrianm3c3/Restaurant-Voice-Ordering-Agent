# Model Card — Restaurant Voice Ordering Agent

## Intended Use

The Restaurant Voice Ordering Agent is intended for a class project demonstration of a restaurant ordering assistant. It is designed for a synthetic pizza restaurant scenario and supports both phone-based and API-based interaction.

The system is intended to help a customer:

- Ask menu questions.
- Place pizza orders.
- Order sides, drinks, and desserts.
- Modify pizza toppings.
- Ask for an order summary.
- Ask for the current total.
- Complete a checkout-style flow.
- Interact through a Twilio phone call.
- Interact through the local `/api/chat` endpoint for testing and grading.

The system is intended for demonstration, testing, and educational use only.

## System Components

The project combines several components:

- Flask server for `/voice`, `/api/chat`, `/debug`, and `/health`.
- Twilio Programmable Voice for phone-call speech input and voice output.
- Restaurant agent logic for conversation flow and order handling.
- Intent parsing for identifying order actions.
- Order manager for maintaining session-specific order state.
- Pricing logic for subtotal, tax, and total calculation.
- RAG/menu question answering using Chroma retrieval and an OpenAI-compatible LLM endpoint.
- Optional local speech-related scripts for microphone/STT/TTS experiments.

## Model and AI Usage

The project uses model-backed behavior in two main places:

1. Intent parsing fallback when deterministic rules are not enough.
2. Retrieval-augmented menu question answering.

The RAG path retrieves restaurant menu/FAQ context from ChromaDB and uses an OpenAI-compatible chat completion endpoint to generate menu-bounded answers.

The project also uses a sentence-transformer embedding model for vector retrieval.

## Intended Users

The intended users are:

- Course graders or teaching assistants.
- Developers testing the restaurant ordering flow.
- Demo callers using the Twilio phone number.
- Project team members validating agent behavior.

## Not Intended For Production

This system is not intended for production restaurant use. It does not connect to a real POS system, kitchen printer, payment processor, inventory system, or customer database.

## Limitations

- The restaurant menu is synthetic.
- The system does not submit real kitchen tickets.
- The system does not process real payments.
- The checkout flow is a simulated confirmation flow.
- The system does not authenticate users.
- The system does not store long-term customer profiles.
- Nutrition facts are not available unless explicitly present in the menu data.
- Allergen and dietary information is limited to manually encoded hints.
- Cross-contamination cannot be guaranteed.
- Twilio transcription errors may cause incorrect interpretations.
- RAG quality depends on retrieval quality and the configured LLM endpoint.
- If `.env` is missing or the LLM endpoint is unavailable, RAG may return a restaurant-bounded fallback instead of a detailed answer.
- LLM fallback behavior may vary if the endpoint model, prompt, or credentials change.
- The Flask server is currently used as a development/demo server, not a production WSGI deployment.

## Risks

- A user may treat synthetic menu information as real restaurant policy.
- Speech recognition may mishear an order during phone calls.
- The system may add or modify the wrong item if the transcript is ambiguous.
- The system may fail to answer menu questions if the LLM endpoint is unavailable or unauthorized.
- The system may produce unsupported claims if prompt restrictions are weakened.
- Public phone or ngrok demos may receive abusive, irrelevant, or unexpected input.
- Logs may include raw user input such as names, pickup times, and order preferences.
- If connected to real ordering infrastructure without review, mistakes could affect real customers.

## Out of Scope

The system is not intended to:

- Process real payments.
- Place real restaurant orders.
- Replace human staff in production.
- Provide medical, nutrition, or allergen guarantees.
- Answer general knowledge questions.
- Answer sports, weather, legal, medical, financial, or emergency questions.
- Authenticate callers.
- Store customer profiles.
- Support production multilingual ordering.
- Handle emergency calls.
- Make safety-critical decisions.
- Guarantee exact behavior when the external LLM endpoint is unavailable.

## Responsible AI Controls

The project includes the following safeguards:

- Deterministic parsing for common restaurant order actions.
- Menu-bounded RAG prompt.
- Out-of-scope fallback for irrelevant questions.
- User story tests for irrelevant question handling.
- Integration tests for API behavior.
- RAG/retrieval tests for menu question behavior.
- Explicit limitations in documentation.
- Synthetic data only.
- No real payment processing.
- No real restaurant order submission.

## Tested Behaviors

The following behaviors have been tested manually and/or through automated tests:

- Adding a large pepperoni pizza.
- Asking for the order total.
- Maintaining session state through `/api/chat`.
- Handling irrelevant questions with a restaurant-bounded fallback.
- Running the app with Docker Compose.
- Checking `/health`.
- Testing API order flow in Docker.
- Testing RAG/retrieval behavior.
- Testing user-story flows through pytest.

## Known Failure Modes

Known failure modes include:

- Missing or empty `.env` can cause live LLM calls to fail.
- Invalid LLM credentials can cause 401 Unauthorized errors.
- Chroma vector stores created with incompatible package versions may need to be deleted and rebuilt.
- Twilio trial accounts may restrict who can call the number.
- ngrok URLs change unless a static/reserved domain is used.
- Local STT/TTS scripts are optional and are not required for the main Docker grading path.

## Recommended Use in Grading

For grading, use the `/api/chat` endpoint rather than Twilio. This avoids requiring a phone call, ngrok, or Twilio account access.

Recommended grading path:

1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.
3. Check `GET /health`.
4. Run the `/api/chat` walkthroughs in `docs/usage.md`.
5. Run the pytest suite.
6. Review reports and screenshots.

## Privacy Considerations

The project does not require real personal data. Testers should avoid entering:

- Real payment information.
- Full addresses.
- Sensitive personal information.
- Private API keys in prompts or logs.

The `.env` file should not be committed.