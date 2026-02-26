# Architecture guardrail tests.

These tests enforce structural boundaries between layers:
- Commands must remain thin orchestration only.
- Domain logic must live in level.domains.<x>.
- Filesystem and parsing must not occur in command modules.

These tests exist to:
- Prevent architectural drift
- Enforce layering mechanically
- Provide guardrails for AI-generated changes

They are intentionally strict.
