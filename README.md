# level

> A personal career operating system for engineers.

`level` is a CLI-first, filesystem-native tool for managing long-term career growth.

It is designed to support:

- Career planning
- Skill development and interview preparation
- Resume and artifact management
- Application tracking
- Reflection and progression review

The goal is not just to "get a job", but to intentionally level up over time.

---

## Philosophy

- **Filesystem as source of truth** – Your data lives in plain directories and files.
- **Version-control friendly** – Everything is git-trackable.
- **CLI-first** – Fast, scriptable, engineer-native workflows.
- **Separation of logic and data** – Tooling is public; personal data is private.
- **Long-term growth over short-term hunting** – Career progression is continuous.

---

## Scope (MVP)

### 1. Career Planning

- Define long-term goals (role, compensation, domain)
- Track current level and desired level
- Maintain skill gap analysis
- Periodic self-review checkpoints

### 2. Interview Preparation

- Generate and manage coding/system design exercises
- Track weak areas
- Store artifacts (notes, diagrams, retros)
- Review performance over time

### 3. Resume & Artifact Management

- Maintain structured application artifacts
- Version resumes per role
- Track tailored cover letters
- Store supporting documents

### 4. Application Tracking

- Track pipeline stages (draft, applied, interviewing, stalled, archived)
- Store company-specific context
- Log interview notes and outcomes
- Maintain historical record

---

## Architecture

`level` is composed of two repositories:

### 1️⃣ level (public)

- CLI implementation
- Domain logic
- Generic templates
- Tests

### 2️⃣ level-data (private)

- Personal career data
- Application records
- Interview artifacts
- User-modified templates

The CLI operates on a configurable data directory.

---

## Design Principles

- Minimal magic
- Explicit structure
- Portable data
- Extensible command model
- Override-friendly templating

---

## Future Directions

- Structured metadata models (TOML/JSON schemas)
- Skill graph and progression tracking
- Review cadence automation
- Metrics over time (applications, interviews, offers)
- Optional local AI-assisted exercise generation

---

## Status

Early-stage personal tool under active development.

This repository defines the engine.

The data lives elsewhere.
