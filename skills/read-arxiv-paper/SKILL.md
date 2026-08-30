---
name: read-arxiv-paper
description: >
  Read an arXiv paper from its TeX source (not PDF), cache it locally, and write
  a project-relative markdown summary with optional relevance to the current
  workspace. Use when the user runs /read-arxiv-paper, pastes an arXiv abs/pdf/html
  URL, or asks to read/summarize an arXiv paper from source.
argument-hint: "<arxiv-url-or-id> [tag]"
metadata:
  short-description: "Read arXiv TeX source and summarize"
---

# /read-arxiv-paper — Read arXiv from TeX source

Fetch **TeX source** (not the PDF), unpack, read the LaTeX tree, and write a
summary under the current project's `./knowledge/`.

## When to use

- User gives an arXiv URL or id (`2601.07372`, `abs/…`, `pdf/…`, `html/…`)
- “Read this arXiv paper”, “summarize this paper from source”

## When NOT to use

- Non-arXiv PDFs/docs (use ordinary PDF/read tools)
- “Cite a paper” without reading it
- Bulk scraping many papers (do one at a time unless asked)

## Workflow

### 1) Normalize to source URL

Prefer the helper (deterministic):

```bash
python3 ~/.grok/skills/read-arxiv-paper/scripts/fetch_src.py --id-or-url "<input>" --print-only
```

Rules if doing it by hand:

- Extract id like `2601.07372` or `2601.07372v1` (strip version for cache key if you prefer; keep version in metadata).
- Source URL: `https://arxiv.org/src/{id}` (also accept `www.arxiv.org`).

**Always use `/src/`, never the PDF**, for reading.

### 2) Download + unpack (cached)

```bash
python3 ~/.grok/skills/read-arxiv-paper/scripts/fetch_src.py --id-or-url "<input>"
```

Default cache:

- tarball: `~/.cache/arxiv/{arxiv_id}.tar.gz`
- unpack: `~/.cache/arxiv/{arxiv_id}/`

Skip re-download if the tarball already exists (helper does this).

Legacy nanochat cache `~/.cache/nanochat/knowledge/` may still hold older
downloads — check there only if the default cache misses and the user is in a
nanochat context.

### 3) Locate the entrypoint

In the unpacked dir, find the main TeX file (`main.tex`, `paper.tex`, or the
`.tex` that `\input`/`\include`s the rest). Prefer the file named in
`00README` / `Makefile` when present.

### 4) Read the paper

Read the entrypoint, then follow `\input` / `\include` (and clearly relevant
sibling `.tex` files). Skim appendices as needed; do not invent missing sections.

### 5) Write the summary

Write **into the current workspace** (easy to open), not only under `~/.cache`:

```text
./knowledge/summary_{tag}.md
```

- Create `./knowledge/` if missing.
- Choose a short `tag` from the topic (e.g. `conditional_memory`). If the user
  passed a tag in `$ARGUMENTS`, use that.
- **Do not overwrite** an existing `summary_{tag}.md` — pick a new tag or
  `summary_{tag}_2.md`.

Summary contents:

1. Title, authors (if present), arXiv id, source URL, cache path
2. Problem / contribution (short)
3. Method (enough to act on)
4. Results / claims (as stated in the paper)
5. Limitations / open questions
6. **Relevance to the current project** — only when the workspace gives a clear
   hook (e.g. nanochat training, MiroFish simulation, Heretic abliteration).
   If none, say so and list general takeaways instead of forcing a fake link.

## Hard rules

1. TeX source first; PDF only if `/src/` fails and the user still wants a read.
2. Never print secrets from the environment.
3. Do not treat the summary as a substitute for citing the paper accurately.
4. One paper per invocation unless the user explicitly batches.

## Response

Tell the user: arXiv id, cache path, summary path, and 3–6 bullet highlights.
