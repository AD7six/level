# Roadmap

Intended functionality

## v0.1 — Foundation

- Modular CLI architecture
- Config system + validation
- `config set/show/doctor`
- Strict mypy + lint + coverage
- CI pipeline
- Structured test layout

---

## v0.2 — Data Layer Formalization

- `level init`
- Canonical directory structure
- Data directory resolution rules
- Doctor checks for structure + permissions
- Tests for filesystem bootstrap

---

## v0.3 — Applications (First Full Vertical Slice)

- `apply new/list/show/status/archive`
- Filesystem-backed application model
- Enforced state transitions
- Schema validation
- Doctor corruption detection
- Complete workflow usable end-to-end

---

## v0.4 — Planning & Reviews (Second Vertical Slice)

- `plan show/edit`
- `review weekly/quarterly`
- Structured metadata model (meta.toml) for plans and reviews
- Canonical directory structure (mirroring applications pattern)
- Domain-specific doctor checks
- Basic metrics extraction from reviews

Goal: establish canonical + metadata + repair pattern across a second domain.

---

## v0.5 — Practice Engine

- `practice new/list/open/review`
- Metadata-driven practice model
- Weak-area tagging
- Frequency tracking
- Canonical path derivation
- Doctor + repair support
- Stats integration hooks

Goal: ensure all domains follow canonical filesystem + metadata contract.

---

## v0.6 — Resume System

- `resume new/list/build`
- Template layering
- Deterministic rendering
- Version tracking per application
- Resume ↔ application linkage
- Canonical resume version storage
- Doctor validation of template structure

Goal: deterministic artifact generation tied to applications.

---

## v0.7 — Metrics & Aggregation Layer

- `stats applications/practice/progression`
- Cross-domain aggregation
- Conversion tracking
- Longitudinal metrics
- Domain-agnostic metrics engine
- Query/filter layer for applications and practice

Goal: cohesive system-level visibility across domains.

---

## v0.8 — Hardening & Data Contract Freeze

- Freeze filesystem schema across domains
- Add explicit schema versioning
- Migration support framework
- Expand doctor diagnostics to all domains
- Error consistency pass
- Raise coverage thresholds for core logic

Goal: formalize the data contract before stabilization.

---

## v0.9 — Stabilization

- CLI UX audit
- Naming finalization
- Documentation pass
- Real-world usage validation
- No new features

---

## v1.0.0 — Stability Contract

- Stable CLI interface
- Stable directory structure
- Schema version defined
- Backwards compatibility guaranteed
- Fully test-covered core domains
- Deterministic canonical storage across all domains

---

## Architectural Principles (Pre-1.0)

- Each domain must use:
  - Canonical path derivation
  - Metadata model (`meta.toml`)
  - Collision-safe resolution
  - Doctor + repair support
- Filesystem is source of truth
- No speculative abstraction
- Strict typing in `src`
- Tests required for new behavior
- No backwards compatibility guarantees pre-1.0
