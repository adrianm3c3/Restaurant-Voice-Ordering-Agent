# CS 6263 Spec Regeneration Prompt

You are regenerating a Python Flask restaurant ordering agent from a software specification.

Use the repository's `docs/SPEC.md` as the source of truth.

The regenerated system must support:

- A Flask web server.
- `GET /health`.
- `POST /api/chat` with JSON fields:
  - `session_id`
  - `text`
- Session-based order state.
- Pizza, side, drink, and dessert ordering.
- Pizza topping modification.
- Pizza crust changes.
- Item removal.
- Order summary.
- Total calculation with tax.
- Multi-step checkout.
- Menu question answering using retrieved restaurant/menu knowledge.
- Safe out-of-scope handling.
- Tests matching the user stories in `docs/STORIES.md`.

Return only source code and required project files. Do not include explanation text.
