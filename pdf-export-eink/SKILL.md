---
name: pdf-export-eink
description: Export document content as a PDF optimized for E Ink reading devices. Supports the Supernotes Nomad (7.8-inch, 1404×1872, 300 PPI) with diagrams (inline SVG), mathematical equations (MathML), code blocks with syntax highlighting, tables, and lists. Creates a single print-ready HTML file that converts to a pixel-perfect PDF via headless Chromium or WeasyPrint. Use when the user wants to read a document, article, or technical reference on an E Ink tablet.
---

# E Ink PDF Export

This skill creates a print-ready HTML document sized and typeset for a specific E Ink device, then converts it to PDF. Follow every step in order. Do not skip steps.

## Device Profiles

| Device | Screen | Resolution | DPI | Page size | Margins | Font size |
|---|---|---|---|---|---|---|
| Supernotes Nomad (`nomad`) | 7.8 in | 1404 × 1872 px | 300 PPI | 4.68 × 6.24 in | 0.40 in × 0.45 in | 11 pt |

Additional devices can be added to this table in future versions.

## Step 1: Gather Document Information

Ask the user for all of the following before writing any files. Collect everything in a single message:

- **Title**: The document title (required)
- **Author**: Author name (required)
- **Date**: Publication or creation date, default today's date
- **Language**: BCP-47 language code, default `en`
- **Device**: Target device slug from the table above, default `nomad`
- **Sections**: How many sections, and either the full text of each or a description to generate. Sections may contain:
  - Plain paragraphs
  - Code blocks (ask for the programming language for syntax highlighting)
  - Diagrams described in natural language or Mermaid syntax
  - Mathematical equations in LaTeX notation
  - Tables (column headers and row data)
  - Ordered and unordered lists

Derive a **document slug** from the title: lowercase, spaces replaced with hyphens, non-alphanumeric characters removed. Example: "Field Guide to Algorithms" → `field-guide-to-algorithms`. The output is a single file named `{slug}.html`.

## Step 2: Write the HTML File

Write `{slug}.html` as a **single self-contained file** — all CSS is embedded in `<style>` tags; no external resources. Use the skeleton below, substituting the device's `@page` values from the Device Profiles table.

### 2a. Full file skeleton

```html
<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8"/>
  <title>{Title}</title>
  <style>
    /* ── Page geometry: Supernotes Nomad (7.8 in, 300 PPI, 1404 × 1872 px) ── */
    @page {
      size: 4.68in 6.24in;
      margin: 0.40in 0.45in;
    }

    /* ── Reset ── */
    *, *::before, *::after { box-sizing: border-box; }

    /* ── Base typography ── */
    body {
      font-family: "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
      font-size: 11pt;
      line-height: 1.5;
      color: #000;
      background: #fff;
      margin: 0;
      padding: 0;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }

    /* ── Headings ── */
    h1 { font-size: 18pt; margin: 0 0 0.6em; line-height: 1.2; }
    h2 { font-size: 14pt; margin: 1.2em 0 0.4em; line-height: 1.3; }
    h3 { font-size: 12pt; margin: 1em 0 0.3em; line-height: 1.3; }
    h1, h2, h3 { page-break-after: avoid; }

    /* ── Sections / page breaks ── */
    article { page-break-after: always; }
    article:last-child { page-break-after: avoid; }

    /* ── Paragraphs ── */
    p {
      margin: 0 0 0.6em;
      orphans: 3;
      widows: 3;
    }

    /* ── Code blocks ── */
    pre {
      background: #f4f4f4;
      border: 1pt solid #bbb;
      border-radius: 3pt;
      padding: 0.55em 0.7em;
      font-family: "Courier New", Courier, monospace;
      font-size: 8.5pt;
      line-height: 1.4;
      white-space: pre-wrap;
      word-break: break-all;
      page-break-inside: avoid;
    }

    code {
      font-family: "Courier New", Courier, monospace;
      font-size: 9pt;
      background: #f4f4f4;
      padding: 0.05em 0.25em;
      border-radius: 2pt;
    }

    pre code { background: none; padding: 0; font-size: 1em; }

    /* ── Syntax highlighting — typographic contrast, not colour ──
       E Ink screens render in greyscale; colour-only cues are invisible.
       Use bold, italic, underline, and small-caps instead.             */
    .kw { font-weight: bold; }                    /* keyword     */
    .st { font-style: italic; }                   /* string      */
    .cm { color: #555; font-style: italic; }      /* comment     */
    .nm { font-weight: bold; }                    /* number      */
    .fn { text-decoration: underline; }           /* function    */
    .tp { font-variant: small-caps; }             /* type        */
    .op { }                                       /* operator    */

    /* ── Diagrams ── */
    figure.diagram {
      text-align: center;
      margin: 1.2em 0;
      page-break-inside: avoid;
    }

    figure.diagram figcaption {
      font-size: 9pt;
      color: #333;
      margin-top: 0.4em;
      font-style: italic;
    }

    figure.diagram svg {
      max-width: 100%;
      height: auto;
    }

    /* ── Math ── */
    math[display="block"] {
      display: block;
      text-align: center;
      margin: 1em 0;
    }

    /* ── Tables ── */
    table {
      border-collapse: collapse;
      width: 100%;
      margin: 1em 0;
      font-size: 10pt;
      page-break-inside: avoid;
    }

    th, td {
      border: 1pt solid #888;
      padding: 0.35em 0.5em;
      text-align: left;
    }

    th {
      background: #e0e0e0;
      font-weight: bold;
    }

    tr:nth-child(even) td { background: #f6f6f6; }

    /* ── Lists ── */
    ul, ol { margin: 0.4em 0 0.4em 1.4em; padding: 0; }
    li { margin-bottom: 0.2em; }

    /* ── Blockquotes ── */
    blockquote {
      border-left: 3pt solid #888;
      margin: 0.8em 0;
      padding-left: 1em;
      color: #333;
      font-style: italic;
    }

    /* ── Title page ── */
    .title-page {
      text-align: center;
      padding-top: 1.8in;
    }

    .title-page h1 { font-size: 22pt; margin-bottom: 0.5em; }
    .title-page .author { font-size: 13pt; font-style: italic; margin: 0.3em 0; }
    .title-page .date { font-size: 10pt; color: #555; margin-top: 1em; }
  </style>
</head>
<body>

  <!-- Title page -->
  <article class="title-page">
    <h1>{Title}</h1>
    <p class="author">{Author}</p>
    <p class="date">{Date}</p>
  </article>

  <!-- Insert <article> blocks here for each section (Step 3) -->

</body>
</html>
```

## Step 3: Build Section Content

For each section insert an `<article>` block after the title-page article. Begin each with a heading. Sections are separated by page breaks automatically.

```html
<article>
  <h1>{Section Title}</h1>
  <!-- section content -->
</article>
```

### 3a. Plain Text

Wrap each paragraph in `<p>` tags. Prefer separate `<p>` elements over `<br/>` for paragraph breaks.

### 3b. Code Blocks

Use `<pre><code class="language-{lang}">`. Apply manual syntax highlighting spans using the CSS classes defined in the stylesheet. Because E Ink displays are greyscale, use **typographic contrast** rather than colour:

| Class | Role | Effect |
|---|---|---|
| `.kw` | Keyword | Bold |
| `.st` | String literal | Italic |
| `.cm` | Comment | Italic + mid-grey |
| `.nm` | Number literal | Bold |
| `.fn` | Function / method name | Underline |
| `.tp` | Type name | Small-caps |
| `.op` | Operator | Plain |

Highlight keywords, strings, and comments at minimum.

```html
<pre><code class="language-python"><span class="kw">def</span> <span class="fn">greet</span>(name: <span class="tp">str</span>) -&gt; <span class="tp">str</span>:
    <span class="kw">return</span> <span class="st">"Hello, "</span> + name
</code></pre>
```

### 3c. Diagrams (Inline SVG)

Generate a **static SVG** — no JavaScript, no external resources. Wrap it in `<figure class="diagram">`.

**E Ink SVG rules**:

1. Use only `#000` (black) and shades of grey (`#888`, `#aaa`, `#ccc`, `#eee`) for strokes and fills. Colour cues are invisible on E Ink — use fill patterns and stroke styles to distinguish regions instead.
2. Minimum stroke width: `1.5` to guarantee visibility at 300 PPI.
3. Give `<svg>` the attributes `xmlns="http://www.w3.org/2000/svg"`, `width="100%"`, and `viewBox="0 0 {W} {H}"`. The CSS will constrain the rendered width to the text area.
4. Use SVG primitives only: `<rect>`, `<circle>`, `<ellipse>`, `<line>`, `<polyline>`, `<polygon>`, `<path>`, `<text>`, `<g>`, `<defs>`, `<marker>`, `<pattern>`.

**Arrowhead marker** — add inside `<defs>` when arrows are needed:

```xml
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7"
          refX="10" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#000"/>
  </marker>
</defs>
```

Use `marker-end="url(#arrow)"` on `<line>` and `<path>` elements.

**Hatch patterns** — use these inside `<defs>` to visually distinguish diagram regions without colour:

```xml
<defs>
  <!-- Light diagonal hatch — for secondary regions -->
  <pattern id="hatch-light" patternUnits="userSpaceOnUse" width="6" height="6">
    <line x1="0" y1="6" x2="6" y2="0" stroke="#bbb" stroke-width="1"/>
  </pattern>
  <!-- Dense cross-hatch — for highlighted regions -->
  <pattern id="hatch-dense" patternUnits="userSpaceOnUse" width="5" height="5">
    <line x1="0" y1="5" x2="5" y2="0" stroke="#888" stroke-width="1"/>
    <line x1="0" y1="0" x2="5" y2="5" stroke="#888" stroke-width="1"/>
  </pattern>
  <!-- Dot grid — for background areas -->
  <pattern id="dots" patternUnits="userSpaceOnUse" width="6" height="6">
    <circle cx="3" cy="3" r="1" fill="#aaa"/>
  </pattern>
</defs>
```

Apply a pattern as a fill: `fill="url(#hatch-light)"`.

**Diagram types** — use the same layout conventions as the EPUB skill:

- **Flowchart**: process boxes `<rect rx="4">`, decision diamonds `<polygon>`, start/end ellipses `<ellipse>`, arrows `<line marker-end="url(#arrow)">`.
- **Sequence diagram**: participant boxes at the top, vertical lifelines as `<line stroke-dasharray="4,2">`, messages as horizontal `<line marker-end="url(#arrow)">` with `<text>` labels.
- **Class diagram**: class box as `<rect>` with separator `<line>`, inheritance as hollow-triangle marker, aggregation as open-diamond marker.
- **ER diagram**: entities as `<rect>`, attributes as `<ellipse>`, relationships as `<polygon>` diamond, connected by `<line>`.

Example wrapper:

```html
<figure class="diagram">
  <svg xmlns="http://www.w3.org/2000/svg"
       width="100%" viewBox="0 0 480 300">
    <defs>
      <marker id="arrow" markerWidth="10" markerHeight="7"
              refX="10" refY="3.5" orient="auto">
        <polygon points="0 0, 10 3.5, 0 7" fill="#000"/>
      </marker>
    </defs>
    <!-- diagram elements -->
  </svg>
  <figcaption>Figure {N}: {description}</figcaption>
</figure>
```

### 3d. Mathematical Equations (MathML)

Chromium 109+ and WeasyPrint 60+ both support MathML Core natively. Use `xmlns="http://www.w3.org/1998/Math/MathML"`.

- **Inline** (within a sentence): `<math xmlns="http://www.w3.org/1998/Math/MathML">…</math>`
- **Block** (displayed on its own line): `<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">…</math>`

**LaTeX → MathML conversion reference**:

| LaTeX | MathML |
|---|---|
| `\frac{a}{b}` | `<mfrac><mi>a</mi><mi>b</mi></mfrac>` |
| `x^2` | `<msup><mi>x</mi><mn>2</mn></msup>` |
| `x_i` | `<msub><mi>x</mi><mi>i</mi></msub>` |
| `\sqrt{x}` | `<msqrt><mi>x</mi></msqrt>` |
| `\sum_{i=0}^{n}` | `<munderover><mo>&#x2211;</mo><mrow><mi>i</mi><mo>=</mo><mn>0</mn></mrow><mi>n</mi></munderover>` |
| `\int_{a}^{b}` | `<munderover><mo>&#x222B;</mo><mi>a</mi><mi>b</mi></munderover>` |
| `\alpha` `\beta` `\gamma` | `<mi>&#x3B1;</mi>` `<mi>&#x3B2;</mi>` `<mi>&#x3B3;</mi>` |
| `\pi` `\sigma` `\mu` | `<mi>&#x3C0;</mi>` `<mi>&#x3C3;</mi>` `<mi>&#x3BC;</mi>` |
| `\times` | `<mo>&#x00D7;</mo>` |
| `\cdot` | `<mo>&#x22C5;</mo>` |
| `\leq` `\geq` | `<mo>&#x2264;</mo>` `<mo>&#x2265;</mo>` |
| `\neq` | `<mo>&#x2260;</mo>` |
| `\infty` | `<mo>&#x221E;</mo>` |
| `\pm` | `<mo>&#x00B1;</mo>` |
| `{…}` grouping | `<mrow>…</mrow>` |
| plain variable | `<mi>x</mi>` |
| number | `<mn>42</mn>` |
| operator | `<mo>+</mo>` |

Example — block equation for `E = mc^2`:

```xml
<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
  <mi>E</mi>
  <mo>=</mo>
  <mi>m</mi>
  <msup>
    <mi>c</mi>
    <mn>2</mn>
  </msup>
</math>
```

### 3e. Tables

```html
<table>
  <thead>
    <tr>
      <th>Column A</th>
      <th>Column B</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Value 1</td>
      <td>Value 2</td>
    </tr>
  </tbody>
</table>
```

### 3f. Lists

- Unordered: `<ul><li>item</li></ul>`
- Ordered: `<ol><li>item</li></ol>`
- Nested: place a child `<ul>` or `<ol>` directly inside a `<li>`

## Step 4: Convert to PDF

The HTML file is self-contained and ready for conversion. Two conversion paths are supported.

### Option A — Headless Chromium (recommended)

Headless Chromium produces the highest-fidelity output, including native MathML rendering. It honours the `@page` size and margin rules exactly.

```bash
# Chromium / Chrome — adjust binary name to match your system:
#   chromium, chromium-browser, google-chrome, google-chrome-stable
chromium --headless --disable-gpu \
  --print-to-pdf="{slug}.pdf" \
  --no-pdf-header-footer \
  --run-all-compositor-stages-before-draw \
  --virtual-time-budget=5000 \
  "{slug}.html"
```

Verify the output:

```bash
# Check the file was created and has a reasonable size
ls -lh "{slug}.pdf"
```

### Option B — WeasyPrint (Python, no browser required)

WeasyPrint is a pure-Python PDF renderer with good CSS Paged Media support and basic MathML support. Install it once, then run it on any system.

```bash
pip install weasyprint
weasyprint "{slug}.html" "{slug}.pdf"
```

### If neither Bash nor a terminal is available

Write `{slug}-convert.py` with this content (replace `{slug}` with the actual value):

```python
#!/usr/bin/env python3
"""
Convert {slug}.html to {slug}.pdf using WeasyPrint.
Run from the directory containing {slug}.html:
    pip install weasyprint
    python3 {slug}-convert.py
"""
import subprocess
import sys

html_file = "{slug}.html"
pdf_file  = "{slug}.pdf"

try:
    from weasyprint import HTML
    HTML(html_file).write_pdf(pdf_file)
    print(f"Created {pdf_file}")
except ImportError:
    print("WeasyPrint is not installed. Run: pip install weasyprint", file=sys.stderr)
    sys.exit(1)
```

Then tell the user: "Run `python3 {slug}-convert.py` after installing WeasyPrint (`pip install weasyprint`) to produce `{slug}.pdf`."

## Step 5: Final Summary

Report back to the user with:

1. **Output file**: `{slug}.html` written (and `{slug}.pdf` if conversion ran, or the Python script location).

2. **Device settings used**:

   | Setting | Value |
   |---|---|
   | Device | Supernotes Nomad |
   | Page size | 4.68 × 6.24 in |
   | Resolution | 1404 × 1872 px @ 300 PPI |
   | Font size | 11 pt (Palatino) |
   | Text area width | ~3.78 in (~66 chars/line) |

3. **Special content table**:

   | Type | Count / Details |
   |---|---|
   | Diagrams (SVG) | N diagrams: list figure numbers and types |
   | Math equations | N inline, N block |
   | Code blocks | list languages used |
   | Tables | N tables |

4. **Caveats**: flag any SVG diagram that uses approximate geometry and should be reviewed, and any MathML conversion that was uncertain.

5. **Transfer tip**: Copy the PDF to the device via USB, the Supernotes desktop app, or any cloud sync service supported by the device. On the Nomad, open it with the built-in PDF reader or a third-party reader such as KOReader for best text-reflow support.

---

## E Ink PDF Validity Checklist

Before declaring the task complete, verify each item mentally:

- [ ] `@page` `size` matches the target device dimensions exactly (4.68in × 6.24in for Nomad)
- [ ] `font-size` on `body` is `11pt` (not px, not em) so it scales correctly with the page unit
- [ ] `-webkit-print-color-adjust: exact` and `print-color-adjust: exact` are both set on `body`
- [ ] Every `<article>` except the last has `page-break-after: always`
- [ ] Title page is the first `<article>` with class `title-page`
- [ ] No external resources referenced (no `<link>`, no `src=""`, no `url()` pointing outside the file)
- [ ] All inline SVG elements have `xmlns="http://www.w3.org/2000/svg"`
- [ ] All `<svg>` elements use `width="100%"` with a `viewBox` (not fixed pixel widths)
- [ ] SVG strokes are `≥ 1.5` wide; fills use only black, grey, or hatch patterns
- [ ] All MathML elements have `xmlns="http://www.w3.org/1998/Math/MathML"`
- [ ] Code blocks use typographic contrast (bold/italic/underline), not colour alone
- [ ] Special HTML characters in code blocks are escaped: `&lt;` `&gt;` `&amp;`
- [ ] `page-break-inside: avoid` is set on `pre`, `figure.diagram`, and `table`
