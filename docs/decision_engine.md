# The Decision Engine

This document explains how Decision OS goes from "a list of options" to
"a ranked recommendation with an explanation," and how it improves with
use. The relevant code lives in `backend/app/services/`.

## 1. Preferences

A **preference** (`models/preference.py`) is a `(category, weight)` pair
scoped to a user, e.g.:

```
category="cost",    weight=0.8
category="quality",  weight=0.4
category="speed",    weight=0.2
```

Weights are stored as raw floats (0.0–1.0) and normalized at scoring time
by `utils/normalization.normalize_weights`, which scales them so they sum
to 1.0. This means you don't have to keep weights balanced yourself when
adding or editing preferences — the engine normalizes on every read.

## 2. Options and attributes

Each candidate **option** (`models/option.py`) attached to a decision
carries an `attributes` field: a JSON-encoded dict mapping category names
to a normalized score in the same 0.0–1.0 range, e.g.:

```json
{"cost": 0.8, "quality": 0.4, "speed": 0.6}
```

How those per-category scores get produced is intentionally left open —
today they're supplied by the client when the option is created; a
future iteration could compute them from structured data (e.g. actual
price/spec comparisons) or have the LLM estimate them from a free-text
description.

## 3. Scoring

`services/scoring_service.py` is the core of the engine:

```
score(option) = Σ  option.attributes[category] × normalized_weight[category]
                category
```

Categories present in an option's attributes but absent from the user's
preferences are ignored (contribute 0). Categories present in
preferences but absent from an option are also treated as 0 for that
option, rather than raising an error — the engine is deliberately
forgiving of partial data.

Options are sorted descending by score, each gets a `rank`, and the
scored options are persisted back onto their `Option` rows.

See `backend/tests/test_scoring.py` for worked examples of this
calculation.

## 4. Explanation

`services/explanation_service.py` takes the ranked options and builds a
prompt (`ai/prompts.build_explanation_prompt`) asking the configured LLM
to explain, in plain language, why the top option won and what the
trade-off is versus the runner-up. The prompt explicitly includes only
the computed scores and names — the model is instructed not to invent
details that aren't in the ranked list.

If the LLM call fails for any reason (provider outage, missing API key,
network error), `explanation_service` falls back to a deterministic,
template-based explanation so the `/decisions/{id}/evaluate` endpoint
never hard-fails purely because of an upstream AI provider issue.

## 5. Learning from feedback

After a decision is made, the user can submit **feedback**
(`models/feedback.py`) — a 1–5 satisfaction rating plus optional notes.
`services/learning_service.apply_feedback` reacts to that rating:

| Rating | Effect on preference weights                          |
|--------|---------------------------------------------------------|
| 4–5    | All of the user's category weights nudged up by `LEARNING_RATE` (default `0.05`) |
| 3      | No change (neutral)                                     |
| 1–2    | All of the user's category weights nudged down by `LEARNING_RATE` |

Weights are clamped to the `[0.0, 1.0]` range after adjustment. This is
intentionally a simple, transparent update rule rather than a black-box
model — it's easy to reason about why a recommendation changed, which
matters for a tool whose whole point is helping people trust their own
decisions.

### Where this is simplistic today, and how it could evolve

The current learning rule adjusts *all* of a user's preferences equally
in the direction of the feedback, rather than attributing credit to the
specific categories that drove the chosen option's score. A natural next
step (see `services/learning_service.py`) would be to weight the
adjustment per-category, proportional to how much each category
contributed to the winning option's score — so a bad outcome that was
mostly driven by "speed" would dampen "speed" more than "cost."

## 6. Putting it together

```
POST /decisions                 → create Decision + Options
POST /decisions/{id}/evaluate   → score_options() → generate_explanation()
                                   → persist chosen_option_id + explanation
POST /feedback                   → apply_feedback() → adjust preference weights
```

Every subsequent decision for that user benefits from the updated
weights, so the engine's recommendations should track what the user
actually valued in practice, not just what they said they valued when
they first set up their profile.
