---
name: epub-export
description: Export document content as a valid EPUB2 file with support for diagrams (external SVG), mathematical equations (MathML), code blocks with syntax highlighting, tables (rendered as SVG images for reliable display), and lists. Use when the user wants to create an EPUB ebook or technical document from content, notes, or conversation. Compatible with EPUB2 readers including Supernote Nomad. Creates all required EPUB2 files and packages them into a .epub archive on Desktop, or provides a Python packaging script on Web/Mobile.
---

# EPUB2 Document Export

This skill creates a complete, valid EPUB2 document from content provided by the user. Follow every step in order. Do not skip steps.

## Step 1: Gather Document Information

Ask the user for all of the following before writing any files. Collect everything in a single message:

- **Title**: The document title (required)
- **Author**: Author name (required)
- **Language**: BCP-47 language code, default `en`
- **Identifier**: A unique ID such as a UUID or ISBN (if none, generate a random UUID formatted as `urn:uuid:xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`)
- **Chapters**: How many chapters, and either the full text of each or a description to generate. Chapters may contain:
  - Plain paragraphs
  - Code blocks (ask for the programming language for syntax highlighting)
  - Diagrams described in natural language or Mermaid syntax
  - Mathematical equations in LaTeX notation
  - Tables (ask for column headers and row data)
  - Ordered and unordered lists

Derive a **document slug** from the title: lowercase, spaces replaced with hyphens, non-alphanumeric characters removed. Example: "My Great Book" → `my-great-book`. All output files go under a directory named with this slug.

Maintain two image counters as you write files:
- **fig counter**: diagrams → `OEBPS/images/fig001.svg`, `fig002.svg`, …
- **tbl counter**: table images → `OEBPS/images/tbl001.svg`, `tbl002.svg`, …

## Step 2: Create the Directory Structure

Write the following files in order using the Write tool. Replace `{slug}` with the actual document slug throughout.

### 2a. `{slug}/mimetype`

Write exactly this content — no trailing newline, no BOM:

```
application/epub+zip
```

### 2b. `{slug}/META-INF/container.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf"
              media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
```

### 2c. `{slug}/OEBPS/styles/main.css`

```css
/* Base typography */
body {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1em;
  line-height: 1.6;
  margin: 0;
  padding: 1em 2em;
  color: #1a1a1a;
}

h1 { font-size: 2em; margin-top: 0; }
h2 { font-size: 1.5em; }
h3 { font-size: 1.2em; }

/* Code blocks */
pre {
  background: #f4f4f4;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 1em;
  overflow-x: auto;
  font-family: "Courier New", Courier, monospace;
  font-size: 0.85em;
  line-height: 1.45;
}

code {
  font-family: "Courier New", Courier, monospace;
  font-size: 0.9em;
  background: #f4f4f4;
  padding: 0.1em 0.3em;
  border-radius: 2px;
}

pre code {
  background: none;
  padding: 0;
  font-size: 1em;
}

/* Syntax highlighting classes */
.kw { color: #0000ff; font-weight: bold; }   /* keyword */
.st { color: #008000; }                       /* string */
.cm { color: #808080; font-style: italic; }  /* comment */
.nm { color: #800000; }                       /* number */
.fn { color: #795e26; }                       /* function */
.tp { color: #267f99; }                       /* type */
.op { color: #666; }                          /* operator */

/* Diagrams and table images */
figure.diagram, figure.table-image {
  text-align: center;
  margin: 2em 0;
}

figure.diagram figcaption, figure.table-image figcaption {
  font-size: 0.85em;
  color: #555;
  margin-top: 0.5em;
  font-style: italic;
}

figure.diagram img, figure.table-image img {
  max-width: 100%;
  height: auto;
}

/* Math */
math[display="block"] {
  display: block;
  text-align: center;
  margin: 1.5em 0;
  overflow-x: auto;
}

/* TOC page */
nav ol, nav ul {
  padding-left: 1.5em;
  line-height: 2;
}

/* Blockquotes */
blockquote {
  border-left: 4px solid #ccc;
  margin-left: 0;
  padding-left: 1.5em;
  color: #555;
  font-style: italic;
}
```

## Step 3: Build Chapter XHTML Files

For each chapter write `{slug}/OEBPS/chapters/ch{NNN}.xhtml` where `{NNN}` is zero-padded to three digits (ch001.xhtml, ch002.xhtml, …).

Every chapter must be valid XHTML 1.1. Use this skeleton — note: no `xmlns:epub` attribute, no `epub:type`, use `<div class="chapter">` for the body container:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{lang}">
  <head>
    <meta http-equiv="Content-Type" content="application/xhtml+xml; charset=UTF-8"/>
    <title>{Chapter Title}</title>
    <link rel="stylesheet" type="text/css" href="../styles/main.css"/>
  </head>
  <body>
    <div class="chapter">
      <h1>{Chapter Title}</h1>
      <!-- content here -->
    </div>
  </body>
</html>
```

### 3a. Plain Text

Wrap each paragraph in `<p>` tags. Prefer separate `<p>` elements over `<br/>` for paragraph breaks.

### 3b. Code Blocks

Use `<pre><code class="language-{lang}">`. Apply manual syntax highlighting spans using the CSS classes defined in main.css: `kw` (keywords), `st` (strings), `cm` (comments), `nm` (numbers), `fn` (function names), `tp` (types), `op` (operators). Highlight keywords and strings at minimum.

```xml
<pre><code class="language-python"><span class="kw">def</span> <span class="fn">greet</span>(name):
    <span class="kw">return</span> <span class="st">"Hello, "</span> + name
</code></pre>
```

### 3c. Diagrams (External SVG)

In EPUB2, diagrams are external SVG files referenced by `<img>`. For every diagram:

1. Write a separate file `{slug}/OEBPS/images/fig{NNN}.svg` (zero-padded, incrementing from `fig001.svg`).
2. Reference it in the chapter with `<img>` inside a `<figure>`.
3. Add the SVG file to the manifest in Step 6.

**SVG file format** — standalone SVG, not embedded in XHTML:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="480" height="300" viewBox="0 0 480 300">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7"
            refX="10" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333"/>
    </marker>
  </defs>
  <!-- diagram elements -->
</svg>
```

Use only SVG primitives: `<rect>`, `<circle>`, `<ellipse>`, `<line>`, `<polyline>`, `<polygon>`, `<path>`, `<text>`, `<g>`, `<defs>`, `<marker>`. No JavaScript, no external resources.

Use `marker-end="url(#arrow)"` on `<line>` and `<path>` elements that need arrowheads.

**Flowchart**: boxes → `<rect rx="4">` + centered `<text>`, decisions → `<polygon>` diamond shape, arrows → `<line marker-end="url(#arrow)">`.

**Sequence diagram**: participant boxes along the top row, vertical lifelines as `<line stroke-dasharray="4,2">`, messages as horizontal `<line marker-end="url(#arrow)">` with `<text>` labels above.

**Chapter reference wrapper** — in the XHTML chapter file:

```xml
<figure class="diagram">
  <img src="../images/fig001.svg" alt="{diagram description}"/>
  <figcaption>Figure {N}: {description}</figcaption>
</figure>
```

### 3d. Mathematical Equations (MathML)

MathML is not part of the EPUB2 standard but many readers (including WebKit-based ones) render it. Include MathML inline in XHTML 1.1; it may silently fall back to plain text on readers that do not support it.

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
| `\times` | `<mo>&#x00D7;</mo>` |
| `\cdot` | `<mo>&#x22C5;</mo>` |
| `\leq` `\geq` | `<mo>&#x2264;</mo>` `<mo>&#x2265;</mo>` |
| `\infty` | `<mo>&#x221E;</mo>` |
| `{…}` grouping | `<mrow>…</mrow>` |
| plain variable | `<mi>x</mi>` |
| number | `<mn>42</mn>` |
| operator | `<mo>+</mo>` |

### 3e. Tables (Rendered as SVG Images)

**Do not use HTML `<table>` elements.** E Ink EPUB readers (including Supernote) render HTML tables unreliably — columns collapse or disappear. Instead, render every table as an external SVG image file using the same mechanism as diagrams.

For each table:

1. Write a separate file `{slug}/OEBPS/images/tbl{NNN}.svg` (zero-padded, incrementing from `tbl001.svg`).
2. Reference it in the chapter with `<img>` inside a `<figure>`.
3. Add the SVG file to the manifest in Step 6.

**SVG table layout rules:**
- Total SVG width: **480px**
- Column width: `480 ÷ number_of_columns` px (equal columns by default; adjust if column content widths differ significantly)
- Header row height: **32px** (fill `#f0f0f0`, bold text at y = row_top + 21)
- Data row height: **28px** (alternate fill: even rows `#ffffff`, odd rows `#fafafa`; text at y = row_top + 19)
- Total SVG height: `32 + (number_of_data_rows × 28)` px
- All cells: `stroke="#cccccc"` `stroke-width="0.5"`
- Font: `font-family="Georgia, serif"` header `font-size="13"`, data `font-size="12"`, fill `#1a1a1a`
- Text anchor: `text-anchor="middle"`, x = column_left + (column_width ÷ 2)
- **Long cell text**: if content exceeds ~22 characters for the column width, split into two `<tspan>` lines (first `dy="0"`, second `dy="1.3em"`) and increase row height to **44px**, adjusting text y to row_top + 14

**Template for a 3-column, 2-data-row table (480px wide, col_w=160):**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="480" height="88" viewBox="0 0 480 88">
  <!-- Header row (y=0, h=32) -->
  <rect x="0"   y="0" width="160" height="32" fill="#f0f0f0" stroke="#ccc" stroke-width="0.5"/>
  <rect x="160" y="0" width="160" height="32" fill="#f0f0f0" stroke="#ccc" stroke-width="0.5"/>
  <rect x="320" y="0" width="160" height="32" fill="#f0f0f0" stroke="#ccc" stroke-width="0.5"/>
  <text x="80"  y="21" text-anchor="middle" font-family="Georgia, serif" font-size="13" font-weight="bold" fill="#1a1a1a">Column A</text>
  <text x="240" y="21" text-anchor="middle" font-family="Georgia, serif" font-size="13" font-weight="bold" fill="#1a1a1a">Column B</text>
  <text x="400" y="21" text-anchor="middle" font-family="Georgia, serif" font-size="13" font-weight="bold" fill="#1a1a1a">Column C</text>
  <!-- Data row 1 (y=32, h=28) — white -->
  <rect x="0"   y="32" width="160" height="28" fill="#ffffff" stroke="#ccc" stroke-width="0.5"/>
  <rect x="160" y="32" width="160" height="28" fill="#ffffff" stroke="#ccc" stroke-width="0.5"/>
  <rect x="320" y="32" width="160" height="28" fill="#ffffff" stroke="#ccc" stroke-width="0.5"/>
  <text x="80"  y="51" text-anchor="middle" font-family="Georgia, serif" font-size="12" fill="#1a1a1a">Value 1A</text>
  <text x="240" y="51" text-anchor="middle" font-family="Georgia, serif" font-size="12" fill="#1a1a1a">Value 1B</text>
  <text x="400" y="51" text-anchor="middle" font-family="Georgia, serif" font-size="12" fill="#1a1a1a">Value 1C</text>
  <!-- Data row 2 (y=60, h=28) — light gray -->
  <rect x="0"   y="60" width="160" height="28" fill="#fafafa" stroke="#ccc" stroke-width="0.5"/>
  <rect x="160" y="60" width="160" height="28" fill="#fafafa" stroke="#ccc" stroke-width="0.5"/>
  <rect x="320" y="60" width="160" height="28" fill="#fafafa" stroke="#ccc" stroke-width="0.5"/>
  <text x="80"  y="79" text-anchor="middle" font-family="Georgia, serif" font-size="12" fill="#1a1a1a">Value 2A</text>
  <text x="240" y="79" text-anchor="middle" font-family="Georgia, serif" font-size="12" fill="#1a1a1a">Value 2B</text>
  <text x="400" y="79" text-anchor="middle" font-family="Georgia, serif" font-size="12" fill="#1a1a1a">Value 2C</text>
</svg>
```

**Chapter reference wrapper** — in the XHTML chapter file:

```xml
<figure class="table-image">
  <img src="../images/tbl001.svg" alt="Table: {description}"/>
  <figcaption>Table {N}: {caption}</figcaption>
</figure>
```

### 3f. Lists

- Unordered: `<ul><li>item</li></ul>`
- Ordered: `<ol><li>item</li></ol>`
- Nested: place a child `<ul>` or `<ol>` directly inside a `<li>`

## Step 4: Write the Visible TOC Chapter

Write `{slug}/OEBPS/chapters/toc.xhtml`. This is a **human-readable table of contents page** that appears as the first page of the book — it guarantees the reader sees a chapter list regardless of whether the reader app uses the NCX navigation file. Include one `<li>` per chapter.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{lang}">
  <head>
    <meta http-equiv="Content-Type" content="application/xhtml+xml; charset=UTF-8"/>
    <title>Contents</title>
    <link rel="stylesheet" type="text/css" href="../styles/main.css"/>
  </head>
  <body>
    <div class="chapter">
      <h1>Contents</h1>
      <nav>
        <ol>
          <li><a href="ch001.xhtml">{Chapter 1 Title}</a></li>
          <li><a href="ch002.xhtml">{Chapter 2 Title}</a></li>
          <!-- one <li> per chapter -->
        </ol>
      </nav>
    </div>
  </body>
</html>
```

## Step 5: Write the NCX Navigation File

Write `{slug}/OEBPS/toc.ncx`. This powers the reader's built-in TOC panel and navigation. The `dtb:uid` content value must exactly match the `<dc:identifier>` value in content.opf. Include `toc.xhtml` as `navpoint-1` so the TOC page is the first navigable destination.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
  "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="{identifier}"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNum" content="0"/>
  </head>
  <docTitle>
    <text>{Title}</text>
  </docTitle>
  <navMap>
    <navPoint id="navpoint-1" playOrder="1">
      <navLabel><text>Contents</text></navLabel>
      <content src="chapters/toc.xhtml"/>
    </navPoint>
    <navPoint id="navpoint-2" playOrder="2">
      <navLabel><text>{Chapter 1 Title}</text></navLabel>
      <content src="chapters/ch001.xhtml"/>
    </navPoint>
    <navPoint id="navpoint-3" playOrder="3">
      <navLabel><text>{Chapter 2 Title}</text></navLabel>
      <content src="chapters/ch002.xhtml"/>
    </navPoint>
    <!-- one <navPoint> per chapter, playOrder increments by 1 -->
  </navMap>
</ncx>
```

## Step 6: Write the Package Document

Write `{slug}/OEBPS/content.opf`. Use today's date for `<dc:date>` in `YYYY-MM-DD` format.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf"
         version="2.0"
         unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/"
            xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:identifier id="uid">{identifier}</dc:identifier>
    <dc:title>{Title}</dc:title>
    <dc:creator opf:role="aut">{Author}</dc:creator>
    <dc:language>{lang}</dc:language>
    <dc:date opf:event="publication">{YYYY-MM-DD}</dc:date>
  </metadata>

  <manifest>
    <!-- NCX navigation — id must be "ncx" -->
    <item id="ncx"
          href="toc.ncx"
          media-type="application/x-dtbncx+xml"/>

    <!-- Stylesheet -->
    <item id="css"
          href="styles/main.css"
          media-type="text/css"/>

    <!-- Visible TOC page -->
    <item id="toc"
          href="chapters/toc.xhtml"
          media-type="application/xhtml+xml"/>

    <!-- Chapters -->
    <item id="ch001"
          href="chapters/ch001.xhtml"
          media-type="application/xhtml+xml"/>
    <!-- repeat for ch002, ch003, … -->

    <!-- Diagram SVG files — one entry per fig written in Step 3c -->
    <item id="fig001"
          href="images/fig001.svg"
          media-type="image/svg+xml"/>
    <!-- repeat for fig002, … — omit entirely if no diagrams -->

    <!-- Table SVG files — one entry per tbl written in Step 3e -->
    <item id="tbl001"
          href="images/tbl001.svg"
          media-type="image/svg+xml"/>
    <!-- repeat for tbl002, … — omit entirely if no tables -->
  </manifest>

  <!-- toc attribute references the NCX item id -->
  <spine toc="ncx">
    <!-- TOC page first so it is the opening page -->
    <itemref idref="toc"/>
    <itemref idref="ch001"/>
    <!-- repeat for ch002, ch003, … -->
  </spine>
</package>
```

## Step 7: Package into .epub

The .epub format is a ZIP archive. The `mimetype` entry **must be first and stored without compression** (ZIP STORE method, not DEFLATE).

### If Bash is available (Desktop)

```bash
cd {slug}
zip -X -0 ../{slug}.epub mimetype
zip -rq ../{slug}.epub META-INF OEBPS
```

Flag notes: `-X` strips extra attributes, `-0` stores without compression (required for mimetype), `-r` recursive, `-q` quiet.

Verify the archive:

```bash
unzip -t ../{slug}.epub | head -20
```

### If Bash is not available (Web or Mobile)

Write `{slug}-package.py` with the following content (replace `{slug}` with the actual slug value):

```python
#!/usr/bin/env python3
"""
Package the EPUB directory into a valid .epub file.
Run from the directory containing the '{slug}' folder:
    python3 {slug}-package.py
Requires Python 3.6+ and no third-party libraries.
"""
import zipfile
import os

slug = "{slug}"
epub_dir = slug
output_file = f"{slug}.epub"

with zipfile.ZipFile(output_file, "w") as zf:
    # mimetype MUST be first and stored uncompressed
    mimetype_path = os.path.join(epub_dir, "mimetype")
    zf.write(mimetype_path, "mimetype", compress_type=zipfile.ZIP_STORED)

    # Add all other files with standard compression
    for dirpath, dirnames, filenames in os.walk(epub_dir):
        dirnames.sort()
        for filename in sorted(filenames):
            if filename == "mimetype" and dirpath == epub_dir:
                continue  # already added above
            filepath = os.path.join(dirpath, filename)
            arcname = os.path.relpath(filepath, epub_dir)
            zf.write(filepath, arcname, compress_type=zipfile.ZIP_DEFLATED)

print(f"Created {output_file}")
print(f"Verify: python3 -c \"import zipfile; zipfile.ZipFile('{output_file}').testzip() or print('OK')\"")
```

Then tell the user: "Run `python3 {slug}-package.py` from the directory containing the `{slug}/` folder to produce `{slug}.epub`."

## Step 8: Final Summary

Report back to the user with:

1. **File tree** of everything written, in a code block with tree-style formatting.
2. **Output**: `{slug}.epub` created, or the Python packaging script provided.
3. **Special content table**:

   | Type | Count / Details |
   |---|---|
   | Diagrams (SVG) | N diagrams: list file names and types |
   | Tables (SVG) | N tables: list file names and captions |
   | Math equations | N inline, N block (note: MathML renders on WebKit-based readers; may display as plain text on others) |
   | Code blocks | list languages used |

4. **Caveats**: flag any diagram or table SVG where the content is approximate or text was truncated.
5. **Recommended readers**: Calibre (desktop, free), Apple Books (iOS/macOS), Kobo, Supernote Nomad, or any EPUB2-compliant reader.

---

## EPUB2 Validity Checklist

Before declaring the task complete, verify each item mentally:

- [ ] `mimetype` file exists at root, contains exactly `application/epub+zip`, no trailing newline
- [ ] `META-INF/container.xml` `full-path` points to `OEBPS/content.opf`
- [ ] `content.opf` has `version="2.0"` and `<spine toc="ncx">`
- [ ] `toc.ncx` exists; `dtb:uid` matches `<dc:identifier>` exactly; has a `<navPoint>` for every chapter plus the TOC page
- [ ] `toc.xhtml` exists as the first `<itemref>` in the spine
- [ ] All chapter files use XHTML 1.1 DOCTYPE and have no `xmlns:epub` or `epub:type` attributes
- [ ] All chapter files have `xmlns="http://www.w3.org/1999/xhtml"` on the `<html>` element
- [ ] No HTML `<table>` elements in any chapter — all tables are SVG images in `OEBPS/images/tbl{NNN}.svg`
- [ ] All SVG files (diagrams and tables) are in `OEBPS/images/` and each has its own manifest `<item>` with `media-type="image/svg+xml"`
- [ ] All MathML elements have `xmlns="http://www.w3.org/1998/Math/MathML"`
- [ ] All paths in content.opf are relative to `OEBPS/`
- [ ] All chapter `src` values in toc.ncx are relative to `OEBPS/` (i.e., `chapters/ch001.xhtml`)
