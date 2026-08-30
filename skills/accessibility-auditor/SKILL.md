---
name: accessibility-auditor
description: >
  Accessibility audit for web applications and user interfaces: keyboard navigation, focus management, semantic structure, forms, labels, screen-reader compatibility, color contrast, motion, text readability, interactive controls, and appropriate ARIA usage. Identify real problems, explain impact, prioritize findings, and provide concrete fixes without unnecessary ARIA or complexity. Use when the user runs /accessibility-auditor, or asks for an a11y audit, WCAG review, keyboard/focus fixes, ARIA review, or contrast/semantics issues.
argument-hint: <context, path, or brief>
metadata:
  short-description: "UI a11y audit with concrete fixes"
---

# /accessibility-auditor — Accessibility Audit

Audit UI for **real** accessibility barriers and give **minimal, correct** fixes.

## Hard rules

1. Prefer **native semantics** over ARIA. No ARIA when HTML already expresses the role.
2. Cite **where** (component/file/selector) and **impact** (who is blocked).
3. Prioritize by severity × frequency × workaround difficulty.
4. Don't pad with theoretical issues unsupported by the UI under review.
5. Fixes should be concrete (code-level guidance), not slogan checklists only.

## Focus areas

Keyboard order & operability · focus visible/trapping/restoration · headings/landmarks · forms & labels · name/role/value · live regions (sparingly) · contrast · motion/reduced-motion · target size/readability · custom controls

## When invoked

1. Inspect relevant UI code and, when possible, exercise critical flows mentally or via running app.
2. Produce prioritized findings with fixes.
3. Note what was **not** tested (e.g. no screen-reader run performed).

## Output format

```markdown
# Accessibility audit: <surface>

## Summary
- Top blockers
- Overall posture

## Findings
### [SEV] Title
- **Where:** …
- **Problem:** …
- **Impact:** …
- **Fix:** … (prefer semantic HTML; ARIA only if needed)
- **WCAG-ish mapping:** (optional, e.g. 2.1.1 Keyboard)

## Unnecessary ARIA / complexity to remove
…

## Not tested / residual risk
…
```

## Severity guide

- **Critical:** inaccessible core task (can't operate/submit/navigate)
- **High:** major flow degraded for AT/SR/vision users
- **Medium:** partial barriers with workarounds
- **Low:** polish / best-practice

