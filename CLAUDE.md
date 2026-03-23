# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a collection of **Claude Skills** — reusable SKILL.md definitions that teach Claude how to generate formatted documents. Each skill is a standalone markdown file with YAML frontmatter and step-by-step instructions.

The target runtime is **Claude Desktop or Claude Mobile** (not Claude Code). Skills are written and tested for environments where the user interacts via chat and Claude writes files directly using the Write tool, without a terminal or build pipeline.

## Skills

### `epub-export/SKILL.md`
Generates valid EPUB2 ebook files from structured content. The skill produces a directory tree (XHTML 1.1 chapters, CSS, NCX navigation file, OPF package, external SVG images) then packages it as a ZIP archive with special mimetype handling. Targets EPUB2 for compatibility with devices like the Supernote Nomad that do not support EPUB3.

### `pdf-export-eink/SKILL.md`
Generates PDFs optimized for E Ink devices (specifically the Supernotes Nomad: 7.8", 1404×1872 px, 300 DPI). Has two execution paths:
- **Path A**: Single self-contained HTML file (Claude Desktop, no bash) — user prints to PDF
- **Path B**: Multi-file HTML directory + Python packaging script (Claude Code with bash access)

## SKILL.md Format

Every skill file follows this structure:
```
---
name: <skill-name>
description: <capability description shown to Claude when deciding whether to invoke>
---

# Title

[Numbered step-by-step instructions with inline code templates]
```

## Content Type Conventions

Both skills share the same supported document elements and rendering strategies:

| Element | EPUB2 | PDF/E Ink |
|---|---|---|
| Math equations | MathML with `xmlns` (best-effort; not in EPUB2 spec but renders on WebKit) | MathJax CDN → SVG |
| Diagrams | External `.svg` files in `OEBPS/images/`, referenced via `<img>` | Inline SVG |
| Code blocks | XHTML 1.1 `<pre><code>` | Typographic cues (bold/italic/underline/small-caps, no color) |
| Tables | HTML `<table>` with `<thead>` | HTML `<table>` |

## EPUB2 Technical Requirements

- `mimetype` must be the first file in the ZIP, stored uncompressed (`zip -X -0`)
- Navigation uses the NCX file (`toc.ncx`) — the `<spine toc="ncx">` attribute links them; `dtb:uid` must exactly match `<dc:identifier>`
- A **visible TOC chapter** (`chapters/toc.xhtml`) is written as the first spine item — this is the primary user-facing TOC because the Supernote reader may not surface the NCX to the user
- **Tables are rendered as SVG images** (`OEBPS/images/tbl{NNN}.svg`) using SVG `<rect>` grids — never HTML `<table>` elements, which render unreliably on e-ink EPUB readers
- Diagrams are external SVG files in `OEBPS/images/fig{NNN}.svg`, referenced with `<img>`
- No `epub:type`, `xmlns:epub`, or `properties` attributes — these are EPUB3-only
- Chapter files use XHTML 1.1 DOCTYPE and `<div class="chapter">` (not `<section epub:type="chapter">`)

## Examples

The `examples/` directory contains reference outputs:
- `mathematics-and-data-flow.epub` + source directory — 3-chapter EPUB with math, SVG diagrams, and tables
- `mathematics-and-data-flow-nomad.pdf` + source directory — E Ink PDF of the same content

The `examples/` directory has a `package.json` with MathJax dependencies used during PDF preprocessing.
