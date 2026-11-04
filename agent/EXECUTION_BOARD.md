# xAI — Execution Board

**Workspace:** `/Users/enaguthiabhishek/xai` (upstream: `xai-org/xai-sdk-python`)  
**Problem Canvas:** [`COMPANY_PROBLEM_CANVAS.md`](./COMPANY_PROBLEM_CANVAS.md)  
**Gold standard:** `~/Documents/PRODUCT_ARTIFACT_PROMPTS.md` §21 + checklist

---

## Two independent tracks (parallel)

| Track | What | Status | Next action |
|-------|------|--------|-------------|
| **A — PR** | Multimodal Collections helpers ([#78](https://github.com/xai-org/xai-sdk-python/issues/78)) | **Open** — [PR #169](https://github.com/xai-org/xai-sdk-python/pull/169) on fork `Abhishek21g:feature/collections-multimodal` | Respond to review; do **not** block product on merge |
| **B — Product** | **Grok Collections Reliability Kit** (plan/run/doctor/report) | **MVP shipped** — `grok-collections-reliability-kit/`, 17 tests, site publishing | Push public repo; outreach |

---

## Track A — PR (upstream code quality)

| Item | Detail |
|------|--------|
| **Issue** | [#78](https://github.com/xai-org/xai-sdk-python/issues/78) — SDK helpers for multimodal Collections workflows |
| **PR** | [#169](https://github.com/xai-org/xai-sdk-python/pull/169) |
| **Branch** | `feature/collections-multimodal` |
| **Scope** | `xai_sdk.multimodal_collections` — field schema, upload wrappers, search path resolution, vision message bridge; sync + async; 13 tests |
| **Avoid** | [#166](https://github.com/xai-org/xai-sdk-python/pull/166) concurrent uploads (open); [#147](https://github.com/xai-org/xai-sdk-python/pull/147) docs |
| **Verification** | `uv run pytest` (776+), `ruff check`, `pyright` on new module |
| **Proves** | Can contribute correct, tested code to xAI's SDK |

**PR does NOT include:** scenario harness, fleet doctor CLI, public product repo, or site (those are Track B).

---

## Track B — Product (company-native solution)

| Item | Detail |
|------|--------|
| **Name** | Grok Collections Reliability Kit |
| **Thesis** | Canvas §5 — CI-grade Collections pipeline validation (#77 pain) |
| **Target repo** | `github.com/Abhishek21g/grok-collections-reliability-kit` (new public repo — **not** upstream) |
| **Target site** | `enaguthi.com/grok-reliability-kit/site/` |
| **CLI (required)** | `plan` · `run` · `doctor` · `report` (+ `--mock`, `--json`) |
| **Scenarios (min 3)** | 1) offline contract (no API key) 2) single-doc upload→search→chat 3) multi-doc / concurrent upload stress |
| **Doctor rules (min)** | missing management key, indexing failed/backlog/stuck, search smoke, multimodal path resolution, optional stream-hygiene stub for #142 |
| **Artifacts** | `out/receipts/<run-id>/manifest.json`, `summary.json`, `findings.json`, `report.md` |
| **Tests** | 15+ unit tests on doctor + scenario compiler (mock transport) |
| **References** | [tinker-workbench](https://github.com/Abhishek21g/tinker-workbench), [sia-eval-harness](https://github.com/Abhishek21g/sia-eval-harness), [ramp-agent-kit](https://enaguthi.com/ramp-agent-kit/site/) |

### Gold checklist — status (v0.1)

| Requirement | Status | Notes |
|-------------|--------|-------|
| `plan \| run \| doctor \| report` CLI | ✅ | `grok-collections` |
| Scenario YAML | ✅ | 3 bundled scenarios |
| `out/receipts/<run-id>/` layout | ✅ | manifest, summary, steps, findings, report |
| Mock mode (no API key) | ✅ | `--mock` / `mode: mock` |
| 15+ tests | ✅ | 17 pytest |
| Site polish | ✅ | `enaguthi.com/grok-reliability-kit/site/` |
| §6 independence from PR | ✅ | Anchored on #77; PR optional |
| Live mode full multimodal | ⚠️ | v0.1 live: probe/upload/search; multimodal deferred |

### Product phases (after canvas sign-off)

| Phase | Deliverable | Exit criteria |
|-------|-------------|---------------|
| **P1** | `COMPANY_PROBLEM_CANVAS.md` + this board | §6 written; user approves thesis |
| **P2** | New repo scaffold + `plan`/`run` mock scenario | `pytest` green, one receipt in `out/receipts/` |
| **P3** | `doctor` + `report` + 15+ tests | Doctor catches bundled failing fixture |
| **P4** | Live mode + optional use of PR #169 helpers | Works with `XAI_API_KEY` + `XAI_MANAGEMENT_KEY` |
| **P5** | Site `grok-reliability-kit/site/` + publish script | 60s demo path from canvas §7 |
| **P6** | Outreach | Two links: PR #169 + kit demo; cite #77 not #78 as product anchor |

---

## What to deprecate / rename

| Current | Verdict |
|---------|---------|
| `tools/xai_sdk_receipts` | Salvage **doctor/probe/indexing** logic into new kit repo; rename CLI |
| `enaguthi.com/xai-sdk-receipts/` | Replace with `grok-reliability-kit` or redirect after P5 |
| `agent/XAI_API_PROPOSAL.md` | Stays **PR track** only |

---

## Outreach template (when both tracks ready)

> **PR:** Opened [#169](https://github.com/xai-org/xai-sdk-python/pull/169) — typed multimodal Collections helpers for [#78](https://github.com/xai-org/xai-sdk-python/issues/78).  
> **Product:** Built [Grok Collections Reliability Kit](https://enaguthi.com/grok-reliability-kit/site/) because [#77](https://github.com/xai-org/xai-sdk-python/issues/77) describes production RAG pipelines hitting SDK scaling/indexing gaps xAI doesn't ship tooling for — scenario `plan/run/doctor/report` with mock CI mode.

---

## Do not do (product track)

- Ship website-only product without CLI/tests/mock
- Make the site a visualization of PR #169
- Block product on PR merge
- Claim affiliation with xAI
