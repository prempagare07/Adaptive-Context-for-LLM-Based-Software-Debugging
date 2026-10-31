# Contribution and verification record

Documented by ChatGPT on October 31, 2026.

## Starting implementation

Commit 6ffa0c0cf3d8c143668f063462d429adbe4b02b3 belongs to Yadnesh Deshpande (yashpy). It introduced the shared Python package, tests, example, generator, and evaluator. This contribution preserves that history.

Karthik's previous phase2-adaptive-rag commits are a separate extension of the original stakeholder repository; they have not been represented as ancestors of this shared package.

## October 31 — Karthik's first kunduru contribution, with ChatGPT assistance

Problem: a response containing only action=diagnose was converted into Diagnosis(valid=True). Malformed request types could also reach retrieval code without schema validation.

Changed:
- src/adaptive_context/protocol.py: validate required diagnosis fields and request list types; direct malformed conversion remains invalid.
- src/adaptive_context/adaptive.py: give a schema-specific retry instruction.
- tests/test_protocol.py: regression cases for malformed/missing fields, valid empty fix, qualified function names, static rejection, adaptive recovery, invalid requests, and round exhaustion.
- README.md: current test/setup guidance and accurate verification/temporary-copy descriptions.
- docs/MILESTONE2_PLAN.md: dependency order, acceptance checks, evaluation design, proposed ownership, deadlines, and meaningful daily checkpoints.
- docs/AI_ASSISTANCE.md: scope and attribution of AI-assisted work.

Verification:
- Python 3.12.10, isolated project environment.
- python -m pytest -q: 44 passed in 2.53s.
- git diff --check: passed.
- Offline generated-case smoke: 30 cases, seed 0, one worker, simulated miss rate 0.1. Function localization remained 7/30 for static_k3, 8/30 for static_wide, 28/30 for adaptive, and 25/30 for adaptive_graph. Each static mode now counts two incomplete simulated diagnoses as failures; both adaptive modes recorded zero schema failures. These are simulator outcomes, not live-model measurements.

Results establish response-shape validation and regression behavior. They do not establish real-model accuracy, strict total-input budgeting, complete grounding, or stakeholder acceptance.

The commit containing this entry is the first authored contribution on kunduru after the shared initial revision. Its permanent URL is available from this file's Git history. Publication status is recorded after the remote branch has been checked; no future contribution is claimed here.

## Record format for subsequent completed work

For each real contribution record:
- Actual date and author.
- Observed problem and resulting behavior.
- Files changed and linked commit/PR.
- Checks, case/run IDs, and outcomes.
- Model and dataset provenance where relevant.
- Remaining limitations.
- AI assistance attribution.

Future work belongs in MILESTONE2_PLAN.md until completed and verified.
