---
name: api-tester
description: >
  Test APIs and network interfaces: contracts, authentication, authorization, validation, error handling, edge cases, rate limiting, concurrency, malformed inputs, and response consistency. Generate useful tests; separate functional failures from security findings. Use when the user runs /api-tester, or asks to test an API, write API tests, fuzz edge cases, or verify authz on endpoints.
argument-hint: <context, path, or brief>
metadata:
  short-description: "API/contract, auth, edge-case testing"
---

# /api-tester — API & Network Interface Testing

Test APIs thoroughly. Separate **functional** failures from **security** findings (hand security depth to `/security-engineer` when needed).

## Hard rules

1. Inspect the real contract (OpenAPI, routes, handlers) before writing tests.
2. Cover happy path, authn/z failures, validation, edge cases, malformed input.
3. Note concurrency/rate-limit expectations when relevant.
4. **Label results:** Functional bug vs Security concern vs Spec ambiguity.
5. Prefer executable tests in the project's harness.

## When invoked

1. Discover base URL/routes/auth scheme.
2. Build a test matrix.
3. Add/run tests; report failures with request/response evidence.
4. Don't claim "secure" — claim "these cases passed/failed."

## Output format

```markdown
# API test report: <api>

## Contract summary
…

## Matrix
| Case | Type | Result | Evidence |
|------|------|--------|----------|
| … | functional/security/edge | pass/fail | … |

## Failures
…

## Added tests
- paths …
```

