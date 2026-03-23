---
name: pdf-export-eink
description: "Export document content as a PDF optimized for E Ink reading devices. Supports the Supernotes Nomad (7.8-inch, 1404x1872, 300 PPI) with diagrams (inline SVG), mathematical equations (MathML), code blocks with syntax highlighting, tables, and lists. In Claude Desktop (no bash): generates one self-contained HTML that the user opens in their browser and prints to PDF - no intermediate files are shown. In Claude Code (bash available): generates chapter files, a MathJax preprocessor, and a packaging script that assembles and converts everything to PDF via WeasyPrint or headless Chromium. Use when the user wants to read a document, article, or technical reference on an E Ink tablet."
---

# E Ink PDF Export

**There are two rendering paths. Choose the correct one at Step 1 before writing anything.**

- **Path A — Claude Desktop / no bash**: Generate a single self-contained HTML artifact. The user opens it in Chrome or Edge and prints to PDF. No intermediate files.
- **Path B — Claude Code / bash available**: Generate chapter HTML files, a MathJax preprocessor, and a Python packaging script. Run the script to produce the PDF directly.

## Device Profiles

| Device | Screen | Resolution | DPI | Page size | Margins | Font size |
|---|---|---|---|---|---|---|
| Supernotes Nomad (`nomad`) | 7.8 in | 1404 × 1872 px | 300 PPI | 4.68 × 6.24 in | 0.40 in × 0.45 in | 11 pt |

Additional devices can be added to this table in future versions.

## Step 1: Gather Document Information and Choose Path

Ask the user for all of the following before writing any files. Collect everything in a single message:

- **Title**: The document title (required)
- **Author**: Author name (required)
- **Date**: Publication or creation date, default today's date
- **Language**: BCP-47 language code, default `en`
- **Device**: Target device slug from the table above, default `nomad`
- **Chapters**: How many chapters, and either the full text of each or a description to generate. Chapters may contain:
  - Plain paragraphs
  - Code blocks (ask for the programming language for syntax highlighting)
  - Diagrams described in natural language or Mermaid syntax
  - Mathematical equations in LaTeX notation
  - Tables (column headers and row data)
  - Ordered and unordered lists

Derive a **document slug** from the title: lowercase, spaces replaced with hyphens, non-alphanumeric characters removed. Example: "Field Guide to Algorithms" → `field-guide-to-algorithms`.

**Then determine which path to follow:**

- **Bash available** (the `Bash` tool works, you are in Claude Code): follow **Path B** (Steps 2–8).
- **No bash** (Claude Desktop, claude.ai, or any context without shell access): follow **Path A** (Step 2A only). Do not write any other files.

---

## PATH A — Claude Desktop / No Bash

### Step 2A: Generate the Single-File HTML

Write **one file only**: `{slug}.html`. Embed the CSS and all chapter content directly. Use MathJax CDN so equations render in the browser before printing. Do not write any CSS files, chapter files, or scripts.

The file structure:

```html
<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8"/>
  <title>{Title}</title>
  <style>
    /* ── Page geometry: Supernotes Nomad ── */
    @page { size: 4.68in 6.24in; margin: 0.40in 0.45in; }

    *, *::before, *::after { box-sizing: border-box; }

    body {
      font-family: "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
      font-size: 11pt; line-height: 1.5; color: #000; background: #fff;
      margin: 0; padding: 0;
      -webkit-print-color-adjust: exact; print-color-adjust: exact;
    }

    h1 { font-size: 18pt; margin: 0 0 0.6em; line-height: 1.2; }
    h2 { font-size: 14pt; margin: 1.2em 0 0.4em; line-height: 1.3; }
    h3 { font-size: 12pt; margin: 1em 0 0.3em; line-height: 1.3; }
    h1, h2, h3 { page-break-after: avoid; }

    article { page-break-after: always; }
    article:last-child { page-break-after: avoid; }

    p { margin: 0 0 0.6em; orphans: 3; widows: 3; }

    pre {
      background: #f4f4f4; border: 1pt solid #bbb; border-radius: 3pt;
      padding: 0.55em 0.7em;
      font-family: "Courier New", Courier, monospace;
      font-size: 8.5pt; line-height: 1.4;
      white-space: pre-wrap; word-break: break-all; page-break-inside: avoid;
    }
    code {
      font-family: "Courier New", Courier, monospace; font-size: 9pt;
      background: #f4f4f4; padding: 0.05em 0.25em; border-radius: 2pt;
    }
    pre code { background: none; padding: 0; font-size: 1em; }

    .kw { font-weight: bold; }
    .st { font-style: italic; }
    .cm { color: #555; font-style: italic; }
    .nm { font-weight: bold; }
    .fn { text-decoration: underline; }
    .tp { font-variant: small-caps; }

    figure.diagram { text-align: center; margin: 1.2em 0; page-break-inside: avoid; }
    figure.diagram figcaption { font-size: 9pt; color: #333; margin-top: 0.4em; font-style: italic; }
    figure.diagram svg { max-width: 100%; height: auto; }

    table {
      border-collapse: collapse; width: 100%; margin: 1em 0;
      font-size: 10pt; page-break-inside: avoid;
    }
    th, td { border: 1pt solid #888; padding: 0.35em 0.5em; text-align: left; }
    th { background: #e0e0e0; font-weight: bold; }
    tr:nth-child(even) td { background: #f6f6f6; }

    ul, ol { margin: 0.4em 0 0.4em 1.4em; padding: 0; }
    li { margin-bottom: 0.2em; }

    blockquote {
      border-left: 3pt solid #888; margin: 0.8em 0;
      padding-left: 1em; color: #333; font-style: italic;
    }

    .title-page { text-align: center; padding-top: 1.8in; }
    .title-page h1 { font-size: 22pt; margin-bottom: 0.5em; }
    .title-page .author { font-size: 13pt; font-style: italic; margin: 0.3em 0; }
    .title-page .date { font-size: 10pt; color: #555; margin-top: 1em; }

    /* ── Print-to-PDF notice (hidden when printing) ── */
    @media screen {
      #print-notice {
        position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
        background: #1a1a1a; color: #fff; padding: 10px 20px;
        font: bold 13px/1.4 sans-serif; text-align: center;
      }
    }
    @media print { #print-notice { display: none; } }
  </style>
  <!--
    MathJax renders MathML equations as SVG in the browser.
    Wait for the notice below to disappear before printing.
  -->
  <script>
    MathJax = {
      startup: {
        typeset: true,
        ready() {
          MathJax.startup.defaultReady();
          MathJax.startup.promise.then(() => {
            const n = document.getElementById('print-notice');
            if (n) n.textContent =
              'Equations loaded. Print: Ctrl+P → Save as PDF'
              + ' · Paper: Custom 4.68 × 6.24 in · Margins: None';
          });
        }
      }
    };
  </script>
  <script id="MathJax-script" async
    src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/mml-svg.js"></script>
</head>
<body>
  <div id="print-notice">Loading equations — please wait before printing…</div>

  <!-- Title page -->
  <article class="title-page">
    <h1>{Title}</h1>
    <p class="author">{Author}</p>
    <p class="date">{Date}</p>
  </article>

  <!-- Chapter 1 -->
  <article>
    <h1>{Chapter 1 Title}</h1>
    <!-- chapter content here -->
  </article>

  <!-- add more <article> elements for each chapter -->
</body>
</html>
```

**Content rules** — same as Path B (see sections 4a–4f below for reference). Assemble all chapters directly inside this one file.

**After writing the file**, tell the user:

> I've created `{slug}.html`. To convert it to PDF:
> 1. Open the file in **Chrome** or **Edge**
> 2. Wait for the black bar at the top to say "Equations loaded"
> 3. Press **Ctrl+P** (or ⌘P on Mac) → **Save as PDF**
> 4. In More settings: Paper size → **Custom** → **4.68 × 6.24 inches**, Margins → **None**
> 5. Save as `{slug}.pdf`

That is the complete output for Path A. Do not write any other files.

---

## PATH B — Claude Code / Bash Available

## Step 2: Create the Directory Structure

Write the following files in order using the Write tool. Replace `{slug}` with the actual document slug throughout.

### 2a. `{slug}/styles/main.css`

This file is shared by every chapter and contains the `@page` rule that sets the physical page dimensions for the target device.

```css
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
```

## Step 3: Write the Title Page

Write `{slug}/title.html`:

```html
<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8"/>
  <title>{Title}</title>
  <link rel="stylesheet" type="text/css" href="styles/main.css"/>
</head>
<body>
  <article class="title-page">
    <h1>{Title}</h1>
    <p class="author">{Author}</p>
    <p class="date">{Date}</p>
  </article>
</body>
</html>
```

## Step 4: Build Chapter HTML Files

For each chapter write `{slug}/chapters/ch{NNN}.html` where `{NNN}` is zero-padded to three digits (ch001.html, ch002.html, …).

Use this skeleton for every chapter:

```html
<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8"/>
  <title>{Chapter Title}</title>
  <link rel="stylesheet" type="text/css" href="../styles/main.css"/>
</head>
<body>
  <article>
    <h1>{Chapter Title}</h1>
    <!-- content here -->
  </article>
</body>
</html>
```

Write chapters **one file at a time**. Do not attempt to write multiple chapters in a single Write call.

### 4a. Plain Text

Wrap each paragraph in `<p>` tags. Prefer separate `<p>` elements over `<br/>` for paragraph breaks.

### 4b. Code Blocks

Use `<pre><code class="language-{lang}">`. Apply manual syntax highlighting spans using the CSS classes defined in main.css. Because E Ink displays are greyscale, use **typographic contrast** rather than colour:

| Class | Role | Effect |
|---|---|---|
| `.kw` | Keyword | Bold |
| `.st` | String literal | Italic |
| `.cm` | Comment | Italic + mid-grey |
| `.nm` | Number literal | Bold |
| `.fn` | Function / method name | Underline |
| `.tp` | Type name | Small-caps |
| `.op` | Operator | Plain |

Highlight keywords, strings, and comments at minimum. Escape `<`, `>`, and `&` in code content as `&lt;`, `&gt;`, `&amp;`.

```html
<pre><code class="language-python"><span class="kw">def</span> <span class="fn">greet</span>(name: <span class="tp">str</span>) -&gt; <span class="tp">str</span>:
    <span class="kw">return</span> <span class="st">"Hello, "</span> + name
</code></pre>
```

### 4c. Diagrams (Inline SVG)

Generate a **static SVG** — no JavaScript, no external resources. Wrap it in `<figure class="diagram">`.

**E Ink SVG rules**:

1. Use only `#000` (black) and shades of grey (`#888`, `#aaa`, `#ccc`, `#eee`) for strokes and fills. Colour cues are invisible on E Ink — use fill patterns and stroke styles to distinguish regions instead.
2. Minimum stroke width: `1.5` to guarantee visibility at 300 PPI.
3. Give `<svg>` the attributes `xmlns="http://www.w3.org/2000/svg"`, `width="100%"`, and `viewBox="0 0 {W} {H}"`. The CSS will constrain the rendered width to the text area.
4. Use SVG primitives only: `<rect>`, `<circle>`, `<ellipse>`, `<line>`, `<polyline>`, `<polygon>`, `<path>`, `<text>`, `<g>`, `<defs>`, `<marker>`, `<pattern>`.
5. All `<text>` elements must use `fill="#000"` (not a colour value).

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

**Hatch patterns** — use inside `<defs>` to distinguish diagram regions without colour:

```xml
<defs>
  <!-- Light diagonal hatch — for secondary/alternate regions -->
  <pattern id="hatch-light" patternUnits="userSpaceOnUse" width="6" height="6">
    <line x1="0" y1="6" x2="6" y2="0" stroke="#bbb" stroke-width="1"/>
  </pattern>
  <!-- Dense cross-hatch — for highlighted/warning regions -->
  <pattern id="hatch-dense" patternUnits="userSpaceOnUse" width="5" height="5">
    <line x1="0" y1="5" x2="5" y2="0" stroke="#888" stroke-width="1"/>
    <line x1="0" y1="0" x2="5" y2="5" stroke="#888" stroke-width="1"/>
  </pattern>
</defs>
```

Apply a pattern as a fill: `fill="url(#hatch-light)"`.

**Diagram types** — use these layout conventions:

- **Flowchart**: process boxes `<rect rx="4" fill="#f0f0f0">`, decision diamonds `<polygon fill="url(#hatch-light)">`, start/end ellipses `<ellipse fill="#d0d0d0">`, arrows `<line marker-end="url(#arrow)">`.
- **Sequence diagram**: participant boxes with graduated grey fills (e.g. `#e8e8e8`, `#d0d0d0`, `#b8b8b8`), vertical lifelines as `<line stroke-dasharray="4,3" stroke="#777">`, request arrows as solid black lines, response arrows as `stroke-dasharray="5,3"` dashed lines.
- **Class diagram**: class box as `<rect fill="#f0f0f0">` with separator `<line>`, inheritance as hollow-triangle marker, aggregation as open-diamond marker.
- **ER diagram**: entities as `<rect fill="#e8e8e8">`, attributes as `<ellipse fill="#f4f4f4">`, relationships as `<polygon fill="url(#hatch-light)">`, connected by `<line>`.
- **Component / tier diagram**: tier outlines as dashed `<rect>` with light grey fills at different levels (e.g. `#f0f0f0`, `#e0e0e0`, `#d0d0d0`), component boxes as `<rect fill="#fff">` with black stroke so they stand out against any tier background.

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

### 4d. Mathematical Equations (MathML)

Write equations as MathML in the chapter HTML files. The packaging script (Step 6) pre-renders every `<math>` element to SVG using MathJax before WeasyPrint sees the file — WeasyPrint renders SVG correctly but treats MathML as plain text. Use `xmlns="http://www.w3.org/1998/Math/MathML"`.

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

### 4e. Tables

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

### 4f. Lists

- Unordered: `<ul><li>item</li></ul>`
- Ordered: `<ol><li>item</li></ol>`
- Nested: place a child `<ul>` or `<ol>` directly inside a `<li>`

## Step 5: Write the MathJax Preprocessor

Write `mathml-to-svg.js` in the same directory as the packaging script. This file is shared across all documents — write it once per project, not once per document. It converts every `<math>` element in the assembled HTML to an SVG using MathJax, producing a file that WeasyPrint can render correctly.

**Prerequisite** (run once): `npm install mathjax-full`

```javascript
#!/usr/bin/env node
'use strict';
/**
 * mathml-to-svg.js
 *
 * Pre-render every <math> element in an HTML file to SVG using MathJax.
 * WeasyPrint renders SVG correctly but treats MathML as plain text.
 *
 * Usage:
 *   npm install mathjax-full   # once
 *   node mathml-to-svg.js <input.html> <output.html>
 */

const { mathjax }             = require('mathjax-full/js/mathjax.js');
const { MathML }              = require('mathjax-full/js/input/mathml.js');
const { SVG }                 = require('mathjax-full/js/output/svg.js');
const { liteAdaptor }         = require('mathjax-full/js/adaptors/liteAdaptor.js');
const { RegisterHTMLHandler } = require('mathjax-full/js/handlers/html.js');
const fs = require('fs');

const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);

const doc = mathjax.document('', {
  InputJax: new MathML(),
  OutputJax: new SVG({ fontCache: 'none' }),
});

/**
 * Convert a MathML string to an HTML snippet containing an SVG.
 * Block math → <div class="math-block">
 * Inline math → <span class="math-inline" style="vertical-align:…">
 */
function mathmlToSvg(mathml, display) {
  const node = doc.convert(mathml, { display });
  const raw  = adaptor.outerHTML(node);

  if (display) {
    return raw
      .replace(/^<mjx-container[^>]*>/, '<div class="math-block">')
      .replace(/<\/mjx-container>$/, '</div>');
  }

  // Preserve the vertical-align inline style MathJax sets on the container
  const vaMatch = raw.match(/style="([^"]*)"/);
  const va = vaMatch ? ` style="${vaMatch[1]}"` : '';
  return raw
    .replace(/^<mjx-container[^>]*>/, `<span class="math-inline"${va}>`)
    .replace(/<\/mjx-container>$/, '</span>');
}

const [,, inputFile, outputFile] = process.argv;
if (!inputFile || !outputFile) {
  console.error('Usage: node mathml-to-svg.js <input.html> <output.html>');
  process.exit(1);
}

let html = fs.readFileSync(inputFile, 'utf8');

// Replace every <math …>…</math> block in one pass.
let count = 0;
html = html.replace(/<math[\s\S]*?<\/math>/gi, (match) => {
  const display = /display\s*=\s*["']block["']/i.test(match);
  count++;
  return mathmlToSvg(match, display);
});

// Inject CSS for the generated elements before the closing </style>.
const css = `
    /* ── MathJax SVG output ── */
    .math-inline { display: inline-block; line-height: 0; }
    .math-inline svg { overflow: visible; }
    .math-block  { display: block; text-align: center; margin: 1em 0; line-height: 1; }
    .math-block svg { display: block; margin: 0 auto; overflow: visible; }`;

html = html.replace('</style>', css + '\n  </style>');

fs.writeFileSync(outputFile, html, 'utf8');
console.log(`Converted ${count} equation(s):  ${inputFile} → ${outputFile}`);
```

## Step 6: Write the Packaging Script

Write `{slug}-package.py`. Replace `{slug}` with the actual slug value. List every chapter file in reading order inside `SOURCES`.

```python
#!/usr/bin/env python3
"""
Assemble {slug} chapter files into a single HTML document, pre-render
MathML equations to SVG, then convert to PDF.

Usage:
    pip install weasyprint      # first time only
    npm install mathjax-full    # first time only
    python3 {slug}-package.py

Or for headless Chromium instead of WeasyPrint:
    python3 {slug}-package.py --chrome

Run from the directory containing the '{slug}/' folder.
Requires Python 3.6+ and Node.js.
"""
import os
import re
import subprocess
import sys

SLUG  = "{slug}"
TITLE = "{Title}"
LANG  = "{lang}"

# List every source file in reading order (relative to the {slug}/ directory)
SOURCES = [
    "title.html",
    "chapters/ch001.html",
    # add more chapters here, e.g.:
    # "chapters/ch002.html",
    # "chapters/ch003.html",
]


def extract_body(path: str) -> str:
    """Return the content between <body> and </body>."""
    with open(path, encoding="utf-8") as f:
        html = f.read()
    m = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else html.strip()


def main() -> None:
    use_chrome = "--chrome" in sys.argv
    here = os.path.dirname(os.path.abspath(__file__))

    # ── Step 1: Assemble combined HTML ───────────────────────────────────────
    css_path = os.path.join(SLUG, "styles", "main.css")
    with open(css_path, encoding="utf-8") as f:
        css = f.read()

    body_parts: list[str] = []
    for source in SOURCES:
        body_parts.append(extract_body(os.path.join(SLUG, source)))

    body_content = "".join(part + "\n\n" for part in body_parts)
    combined_html = f"""<!DOCTYPE html>
<html lang="{LANG}">
<head>
  <meta charset="UTF-8"/>
  <title>{TITLE}</title>
  <style>
{css}
  </style>
</head>
<body>
{body_content}
</body>
</html>"""

    combined_path = os.path.join(SLUG, "combined.html")
    with open(combined_path, "w", encoding="utf-8") as f:
        f.write(combined_html)
    print(f"Assembled → {combined_path}")

    # ── Step 2: Pre-render MathML → SVG with MathJax ─────────────────────────
    # WeasyPrint treats MathML as plain text; SVG renders correctly.
    mathsvg_path = os.path.join(SLUG, "combined-mathsvg.html")
    mathjs = os.path.join(here, "mathml-to-svg.js")
    try:
        result = subprocess.run(
            ["node", mathjs, combined_path, mathsvg_path],
            check=True, capture_output=True, text=True,
        )
        print(f"Math SVG  → {mathsvg_path}  ({result.stdout.strip()})")
        render_path = mathsvg_path
    except FileNotFoundError:
        print("Warning: node not found — MathML will not render correctly.", file=sys.stderr)
        render_path = combined_path
    except subprocess.CalledProcessError as e:
        print(f"Warning: mathml-to-svg.js failed: {e.stderr.strip()}", file=sys.stderr)
        render_path = combined_path

    # ── Step 3: Convert to PDF ────────────────────────────────────────────────
    out_pdf = f"{SLUG}.pdf"

    if use_chrome:
        for binary in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
            try:
                subprocess.run(
                    [binary, "--headless", "--disable-gpu",
                     f"--print-to-pdf={out_pdf}",
                     "--no-pdf-header-footer",
                     "--run-all-compositor-stages-before-draw",
                     "--virtual-time-budget=5000",
                     render_path],
                    check=True,
                )
                print(f"Created  → {out_pdf}  (via {binary})")
                return
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
        print("No Chromium binary found on PATH.", file=sys.stderr)
        sys.exit(1)
    else:
        try:
            from weasyprint import HTML  # type: ignore
            HTML(render_path).write_pdf(out_pdf)
            print(f"Created  → {out_pdf}  (via WeasyPrint)")
        except ImportError:
            print("WeasyPrint is not installed.", file=sys.stderr)
            print("  pip install weasyprint", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
```

## Step 7: Run the Packaging Script

### If Bash is available (Desktop)

```bash
npm install mathjax-full   # once — needed for math rendering
pip install weasyprint     # once — needed for PDF conversion
python3 {slug}-package.py
```

Verify:

```bash
ls -lh {slug}.pdf
```

## Step 8: Final Summary

Report back to the user with:

1. **Output**: `{slug}.pdf` created (Path B) or print-to-PDF instructions (Path A).
2. **Special content table**:

   | Type | Count / Details |
   |---|---|
   | Diagrams (SVG) | N diagrams: list figure numbers and types |
   | Math equations | N inline, N block |
   | Code blocks | list languages used |
   | Tables | N tables |

3. **Caveats**: flag any SVG that uses approximate geometry and should be reviewed, and any MathML conversion that was uncertain.

4. **Transfer tip**: Copy the PDF to the device via USB, the Supernotes desktop app, or any cloud sync service. On the Nomad, open it with the built-in PDF reader or KOReader for best text-reflow support.

---

## E Ink PDF Validity Checklist

Before declaring the task complete, verify each item mentally.

### Path A (single-file HTML)

- [ ] Only one file written: `{slug}.html`
- [ ] `@page { size: 4.68in 6.24in; margin: 0.40in 0.45in; }` is embedded in `<style>`
- [ ] `font-size` on `body` is `11pt`
- [ ] `-webkit-print-color-adjust: exact` and `print-color-adjust: exact` are set
- [ ] MathJax CDN `<script>` is present; the `ready()` callback updates `#print-notice`
- [ ] All content (title page + all chapters) is assembled inside the single file
- [ ] All MathML elements have `xmlns="http://www.w3.org/1998/Math/MathML"`
- [ ] All inline SVG has `xmlns="http://www.w3.org/2000/svg"` and `width="100%"` with `viewBox`
- [ ] SVG strokes `≥ 1.5`; greyscale fills only; all text `fill="#000"`
- [ ] Code blocks use typographic contrast (bold/italic/underline), not colour alone
- [ ] Special HTML characters in code are escaped: `&lt;` `&gt;` `&amp;`
- [ ] User instructions provided (open in Chrome/Edge, wait, Ctrl+P, custom paper size)

### Path B (multi-file + packaging script)

- [ ] `styles/main.css` has `@page { size: 4.68in 6.24in; margin: 0.40in 0.45in; }`
- [ ] `font-size` on `body` is `11pt`
- [ ] `-webkit-print-color-adjust: exact` and `print-color-adjust: exact` are both set on `body`
- [ ] Every `<article>` except the last has `page-break-after: always` (via CSS rule)
- [ ] No external resources in chapter files (no remote `<link>`, `src`, or `url()`)
- [ ] Stylesheet path: `href="styles/main.css"` (title), `href="../styles/main.css"` (chapters)
- [ ] All inline SVG elements have `xmlns="http://www.w3.org/2000/svg"`
- [ ] All `<svg>` elements use `width="100%"` with a `viewBox`
- [ ] SVG strokes `≥ 1.5`; greyscale fills only; all text `fill="#000"`
- [ ] All MathML elements have `xmlns="http://www.w3.org/1998/Math/MathML"`
- [ ] Code blocks use typographic contrast (bold/italic/underline), not colour alone
- [ ] Special HTML characters in code are escaped: `&lt;` `&gt;` `&amp;`
- [ ] `page-break-inside: avoid` is set on `pre`, `figure.diagram`, and `table`
- [ ] `mathml-to-svg.js` written alongside the packaging script
- [ ] `SOURCES` list in the packaging script matches the files written, in order
