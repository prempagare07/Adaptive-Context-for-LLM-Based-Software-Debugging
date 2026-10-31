# Milestone 2 implementation and delivery plan

Documented by ChatGPT on October 31, 2026, at Karthik Venkata Sai Reddy Kunduru's request. Work dates use America/Phoenix. Proposed responsibilities require team coordination; a plan entry is not a completed contribution.

## Delivery target and source of requirements

Project: Adaptive Context for LLM-Based Software Debugging.
Stakeholder: Sai Rithwik Kukunuri.
Shared implementation: this repository.
Karthik's working branch: kunduru.

Milestone 2 is due November 8, 2026, at 11:59 PM Phoenix. The current assignment requires one group report of 5–10 pages, covering stakeholder follow-up, the implemented system, preliminary evaluation, an actual demo, an actual failure, remaining work, and repository/member contributions.

Requirement sources:
- [Milestone 2 assignment](https://canvas.asu.edu/courses/270345/assignments/7984232).
- Official Milestone 2 report template and Lab 10 materials provided to the team.
- [Original stakeholder baseline](https://github.com/YB-Yottabyte/adaptive-context/tree/c545608474b62e5635d240c49a790703e687848e).

The report must compare the system with at least two baselines on at least two datasets. Preliminary pilot sizes are acceptable when disclosed. Beating every baseline is not required.

## Implementation and authorship at the starting revision

The shared package starts from 6ffa0c0cf3d8c143668f063462d429adbe4b02b3, authored by Yadnesh Deshpande (yashpy). The member branches initially matched that revision.

Karthik's older phase2-adaptive-rag work at 1c82738 is a separate history extending the stakeholder baseline. Preserve that work and its authorship. Integrate individual mechanisms deliberately rather than replacing this shared package with an incompatible checkout.

The current implementation contains:
- Python AST function/method chunks and approximate symbol/call indexes.
- BM25 retrieval, optional Chroma retrieval, symbol lookup, and optional callee prefetch.
- Four compression levels, dependency ordering, and priority-based context packing.
- A plain Python request/diagnose loop and JSON output.
- An optional pytest preflight helper using a temporary repository copy.
- Static K=3, wider static K=10, adaptive, and adaptive-with-prefetch experiment modes.
- A synthetic generator, an offline simulator, and restricted generated-fix checks.

This revision has no LangGraph integration, general real-repository patch verification, completed real-case evaluator, or demonstrated live-model results. The loop directly interprets symbol/query actions; it does not expose the Tools class through full model function calling.

The existing architecture is sufficient for a clear milestone prototype. Add a framework or persistent-memory subsystem only when an observed requirement justifies it.

## Completed first contribution on kunduru

The first contribution fixes an observed correctness defect: an object containing only action=diagnose previously became a valid diagnosis.

Implemented:
- Required diagnosis fields and their types are checked before parsing/conversion succeeds.
- File, function, and cause must be nonblank strings; fix must be a string and may be empty; confidence must be high or low.
- Requests must contain at least one nonempty list of strings for symbols or queries. Either list can be omitted.
- Direct conversion of malformed objects returns an invalid Diagnosis rather than coercing missing values into successful output.
- Adaptive retry instructions now describe schema errors accurately.
- Regression tests cover static rejection, adaptive recovery, invalid request types, and exhaustion after repeated invalid replies.

Validation: 44 tests passed on Python 3.12.10. See CONTRIBUTION_LOG.md for the exact checks.

A schema-valid diagnosis can still be wrong or unsupported. This change does not implement grounding evaluation or fix token-budget accounting.

## Priority backlog and acceptance checks

### P0 — Define and enforce the budget

Current issue: the packer can return an oversized final chunk. Requested symbols receive high priority but may be compressed. Code-only estimates omit full prompt overhead.

Changes:
- Define code-context and total-input budgets separately.
- Reserve system/report/header overhead before choosing code evidence.
- Track requested evidence explicitly rather than relying only on a large score.
- Choose a documented response when full requested evidence cannot fit.
- Report budget exhaustion instead of silently sending an over-budget request.

Acceptance: budget=1, one oversized symbol, multiple requested symbols, long reports, compression-disabled mode, and ordinary successful requests have explicit, tested outcomes. Report estimated counts separately from provider usage.

### P0 — Complete termination and trace records

Record diagnosis, no progress, invalid-response exhaustion, API error, round limit, and budget exhaustion as distinct stop reasons. Validate positive CLI bounds. Keep the stakeholder's two-to-three-round scope configurable; explain any six-round experiment.

Save each request/reply, requested symbols/queries, selected chunk IDs and scores, compression levels, dropped evidence, tokens, retries, and measured wall time. Preserve failed attempts.

Acceptance: a saved run can explain what evidence changed and why it stopped without reconstructing events from aggregate numbers.

### P0 — Add real debugging cases and matched comparisons

Use a common case manifest with:
- Case ID and dataset/source identity.
- Pinned buggy repository revision.
- Bug report and allowed input artifacts.
- Reproduction/test command, environment notes, and reproduction result.
- Gold file/function and expected root cause in evaluator-only metadata.
- Optional approved fix-verification command.

Keep gold answers and maintainer patches outside model inputs. Do not count an unreproduced issue as a verified debugging success.

Acceptance: the same case loader feeds every compared system; every scored case has a revision and provenance.

### P1 — Preserve complete module evidence and improve call links

Replace the first-60-uncovered-lines module limit with multiple bounded chunks. Add duplicate-name, import-alias, and method-receiver cases for approximate callee lookup. Describe unresolved ambiguity honestly.

Acceptance: later top-level evidence remains retrievable; a graph-prefetch experiment records ambiguity and any extra evidence it adds.

### P1 — Score outcomes precisely

Separate retrieval/file/function localization, diagnosis root-cause correctness, claim grounding, optional fix correctness, tokens, calls, and measured end-to-end time. Use a written root-cause rubric and manually audit pilot scores.

The existing synthetic grounding metric checks function correctness plus presence of its chunk at an accepted compression level. It does not verify every explanatory claim.

Acceptance: the scorer distinguishes right file/wrong cause, unsupported cause, malformed output, a correct diagnosis, and unavailable verification. Keep wins, losses, and failures.

## Evaluation design

### Dataset A: controlled generated cases

Keep the generator seed, repository size, distractor count, bug depth, miss rate, retrieval settings, budget, and round cap in saved metadata.

All generated contract/return-line bugs belong to one dataset family. Increasing repository size or case count does not by itself create a second dataset.

### Dataset B: real Python issues

Prepare a small declared pilot from reproducible public Python issues or stakeholder-provided cases. Start with a few cases that fit the available environment and expand after successful reproduction. An existing Requests issue reference is a candidate until its pinned buggy revision and failure are reproduced.

Keep the payment/auth fixtures as development demonstrations. Report their origin and avoid using them as the only evidence of real-world generalization.

### Baselines and controlled comparisons

1. Preserve the original stakeholder static Chroma baseline at its pinned revision.
2. Use the shared static K=3 path for a comparison with matching AST chunks/retrieval/model settings.
3. Retain static-wide K=10 as an additional fixed-context comparison and prefetch/compression/ordering as ablations.

Confirm that the chosen two baselines satisfy the intended comparison with the stakeholder/TA. Document differences in chunking, retrieval, prompt, token allowance, and model; a change in all of these cannot be attributed solely to adaptation.

Use the same real model, case inputs, output-token cap, and scoring rubric across paired runs. Measure a one-case preflight before scaling up. Record provider failures rather than substituting simulator results.

### Result artifacts

Store raw JSONL plus aggregate JSON, including configuration, source revision, case IDs, run IDs, outputs, evidence, stop reason, token usage, and actual wall time.

Simulator results describe context-management behavior under the simulator's assumptions. Its latency is formula-based. Real-model outcomes and measured timing require separate labels and saved live-run evidence.

## Daily work and push checkpoints

Each checkpoint is a coherent tested contribution on the actual day it is completed. Dates allocate work; they do not reserve urgent fixes or promise grading outcomes. The user authorized the first push on October 31. No future push automation is configured.

### October 31 — Establish the work plan and validate model actions

Status: implemented and locally checked for this first contribution.

Deliver:
- Diagnosis/request validation and recovery regression tests.
- This milestone plan, contribution record, and AI assistance attribution.
- Correct setup/test instructions and explicit current limitations.

Check: 44 passing tests, diff review, and offline benchmark smoke. Publish this contribution to kunduru after these checks.

### November 1 — Budget correctness and termination contract

Deliver the defined budget, requested-evidence handling, minimum-context failure outcome, CLI bounds, and explicit stop reasons.

Likely files: budget.py, adaptive.py, models.py, cli.py, focused tests.

Check: tiny/oversized/normal-budget cases, deterministic exits, and existing suite. Checkpoint message after completion: fix: enforce context budgets and explicit stop reasons.

### November 2 — Trace and result schema

Deliver a run/config schema and raw per-round evidence export. Capture model errors/retries and measured end-to-end timing.

Likely files: adaptive.py, baseline.py, models.py, llm.py, new evaluation/result helpers.

Check: a saved success and failed attempt have complete, consistent records. Checkpoint: feat: persist debugging actions and measured run evidence.

### November 3 — Pinned case loading and reproduction

Deliver the common case manifest/loader, controlled fixtures, and a declared real-issue pilot with separate gold metadata.

Likely files: evaluation case loader, case manifests, fixture checks.

Check: reproduce each included failure at its pinned revision; document unavailable cases. Checkpoint: feat: load reproducible debugging cases with evaluation metadata.

### November 4 — Comparable real-model pilot

Deliver adapters for the declared baselines and adaptive modes, matched configurations, and complete raw result storage across the two dataset families.

Likely files: evaluator/runner, baseline adapter, run configuration.

Check: a declared pilot runs end to end; model access failure is explicit. Checkpoint: feat: compare static and adaptive debugging on pinned cases.

Course dependency: Code Reading 3 is also due November 4 at 11:59 PM Phoenix. Keep time for its final source check and required AI trace.

### November 5 — Scoring, actual demo, and stakeholder feedback

Deliver separate localization/root-cause/grounding scores, a readable round trace, an actual success, and an actual partial/failure case.

Check: audit selected scores manually and retain contradictory outcomes. Checkpoint: feat: score debugging outcomes and export adaptive demo traces.

Hold the stakeholder follow-up using the running system and real pilot. Record actual date, participants, feedback, team response, next action, agreed deliverables, and numerical success criteria. A meeting script does not establish that a meeting occurred.

### November 6 — Repeatability and context ablations

Deliver repeat-run support and controlled comparisons for prefetch, compression, and ordering. Improve the most consequential retrieval/module-evidence defect revealed by the pilot.

Check: raw and aggregate outcomes agree, losses remain included, and timing is measured. Checkpoint: feat: evaluate repeatability and context-management ablations.

### November 7 — Reproducible setup and report package

Deliver a clean setup smoke check, accurate CLI instructions, implemented architecture diagram, demo/failure evidence, and the seven-section report draft.

Check: a teammate can reproduce the documented example and connect every reported metric to saved runs. Checkpoint: test: verify milestone setup and evidence exports.

### November 8 — Verify and freeze submission

Deliver only necessary final fixes, the submission revision/configuration, and final evidence/report checks.

Check: 5–10 pages; two datasets/two baselines; actual demo/failure; real stakeholder follow-up; repo/branch/commit/setup; each actual contribution; required AI disclosure and full interaction trace.

Submit one group report by 11:59 PM Phoenix. Use the stable verified revision; optional features can remain on the backlog.

## Proposed ownership and coordination

Karthik's proposed area: protocol/budget correctness, real-case evaluation, trace/result provenance, and integration evidence.

The team should allocate case preparation, graph resolution, compression/ordering ablations, demo/report preparation, and stakeholder coordination based on actual work and availability. This document does not assign another member a task they have accepted.

Preserve Yadnesh's initial implementation credit and Karthik's earlier local history. Each member should link their own actual commits/PRs and explain non-code contributions. Resolve overlapping file ownership before parallel implementation.

## After Milestone 2

The final-project deadline was not established in the inspected assignment list. Maintain a rolling backlog:
- Expand real cases and bug families.
- Improve qualified call resolution and full module evidence.
- Add general real-repository patch verification if the stakeholder approves that scope.
- Improve retry accounting, cancellation, resumption, and acceptance testing.
- Ship the agreed reusable debugging/context-management capability and final demonstration.

Keep planned capabilities separate from tested delivered behavior.
