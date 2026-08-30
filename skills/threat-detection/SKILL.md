---
name: threat-detection
description: >
  Design defensive threat detection and security monitoring: suspicious behaviors to detect, useful logs and telemetry, detection rules and alerts, false-positive handling, and safe ways to test detections. Use when the user runs /threat-detection, or asks for detection rules, security monitoring, audit logging design, alert tuning, or SOC-style detections for an app.
argument-hint: <context, path, or brief>
metadata:
  short-description: "Defensive detection, logs, alerts"
---

# /threat-detection — Detection & Security Monitoring

Design **defensive** detections: what to log, what to alert on, and how to test safely.

## Hard rules

1. **Defensive monitoring only** — no offensive tooling guidance.
2. **Start from behaviors that matter** for this app (abuse cases), not a generic SIEM rule dump.
3. **Every alert needs** signal, severity, expected false positives, and response hint.
4. **Prefer high-signal telemetry** over logging everything.
5. **Describe safe test methods** (synthetic events, staging) — not production attack instructions.

## When invoked

1. Understand the app's sensitive actions (login, payment, admin, data export, multiplayer anti-cheat surfaces, etc.).
2. Inventory existing logs/metrics if any.
3. Propose detection catalog + logging gaps + alert routing.
4. Include FP controls and test plan.

## Output format

```markdown
# Threat detection plan: <app>

## Assets & abuse cases
…

## Telemetry requirements
| Event | Fields | Why |
|-------|--------|-----|
| … | … | … |

## Detections
| ID | Behavior | Rule sketch | Severity | FP notes | Response hint |
|----|----------|-------------|----------|----------|---------------|
| … | … | … | … | … | … |

## Alert routing & noise control
…

## Safe test plan
…
```

