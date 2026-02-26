# Architecture guardrail tests

These tests enforce structural boundaries between layers.

## Scope

Guardrails apply only to domain-backed command entrypoints
(e.g. application, practice, review, plan). Infrastructure
commands such as config, init, and internal helpers are excluded.

## Rules

- Commands must remain thin orchestration only.
- Domain logic must live in `level.domains.<domain>`.
- Filesystem and parsing must not occur in command modules.
- Aggregation and business logic must be implemented in the
  corresponding domain and called from the command.

Simple presentation formatting (e.g. joining lines for output)
is allowed.

## Purpose

These tests exist to:

- Prevent architectural drift
- Enforce layering mechanically
- Provide guardrails for AI-generated changes

They are intentionally strict and represent an architectural contract,
not a style preference.
