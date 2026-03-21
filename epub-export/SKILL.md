---
name: epub-export
description: Export document content as a valid EPUB3 file with support for diagrams (inline SVG), mathematical equations (MathML), code blocks with syntax highlighting, tables, and lists. Use when the user wants to create an EPUB ebook or technical document from content, notes, or conversation. Creates all required EPUB3 files and packages them into a .epub archive on Desktop, or provides a Python packaging script on Web/Mobile.
---

# EPUB3 Document Export

This skill creates a complete, valid EPUB3 document from content provided by the user. Follow every step in order. Do not skip steps.

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

/* Diagrams */
figure.diagram {
  text-align: center;
  margin: 2em 0;
}

figure.diagram figcaption {
  font-size: 0.85em;
  color: #555;
  margin-top: 0.5em;
  font-style: italic;
}

figure.diagram svg {
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

/* Tables */
table {
  border-collapse: collapse;
  width: 100%;
  margin: 1.5em 0;
  font-size: 0.95em;
}

th, td {
  border: 1px solid #ccc;
  padding: 0.5em 0.75em;
  text-align: left;
}

th {
  background: #f0f0f0;
  font-weight: bold;
}

tr:nth-child(even) td {
  background: #fafafa;
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

Every chapter must be valid XHTML5. Use this skeleton:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:epub="http://www.idpf.org/2007/ops"
      xml:lang="{lang}">
  <head>
    <meta charset="UTF-8"/>
    <title>{Chapter Title}</title>
    <link rel="stylesheet" type="text/css" href="../styles/main.css"/>
  </head>
  <body>
    <section epub:type="chapter">
      <h1>{Chapter Title}</h1>
      <!-- content here -->
    </section>
  </body>
</html>
```

Track which chapters contain SVG and which contain MathML — you will need this for Step 5.

### 3a. Plain Text

Wrap each paragraph in `<p>` tags. Prefer separate `<p>` elements over `<br/>` for paragraph breaks.

### 3b. Code Blocks

Use `<pre><code class="language-{lang}">`. Apply manual syntax highlighting spans using the CSS classes defined in main.css: `kw` (keywords), `st` (strings), `cm` (comments), `nm` (numbers), `fn` (function names), `tp` (types), `op` (operators). Highlight keywords and strings at minimum.

```xml
<pre><code class="language-python"><span class="kw">def</span> <span class="fn">greet</span>(name):
    <span class="kw">return</span> <span class="st">"Hello, "</span> + name
</code></pre>
```

### 3c. Diagrams (Inline SVG)

EPUB3 XHTML supports inline SVG natively. For every diagram:

1. Read the user's description or Mermaid syntax.
2. Generate a **static SVG representation** — no JavaScript, no external resources.
3. Use only SVG primitives: `<rect>`, `<circle>`, `<ellipse>`, `<line>`, `<polyline>`, `<polygon>`, `<path>`, `<text>`, `<g>`, `<defs>`, `<marker>`.
4. Give the `<svg>` explicit `width`, `height`, `viewBox` attributes and `xmlns="http://www.w3.org/2000/svg"`.
5. Wrap in `<figure class="diagram"><figcaption>`.

**Arrowhead marker** — add this inside `<defs>` whenever you need arrows:

```xml
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="7"
          refX="10" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#333"/>
  </marker>
</defs>
```

Use `marker-end="url(#arrow)"` on `<line>` and `<path>` elements that need arrowheads.

**Flowchart**: boxes → `<rect rx="4">` + centered `<text>`, decisions → `<polygon>` diamond shape, arrows → `<line marker-end="url(#arrow)">`.

**Sequence diagram**: participant boxes along the top row, vertical lifelines as `<line stroke-dasharray="4,2">`, messages as horizontal `<line marker-end="url(#arrow)">` with `<text>` labels above.

**Class diagram**: class box as `<rect>` with a separator `<line>` between name and members; relationships as `<line>` with hollow triangle (inheritance) or open diamond (aggregation) end markers.

**ER diagram**: entities as `<rect>`, attributes as `<ellipse>`, relationships as a diamond `<polygon>`, connecting `<line>` elements.

Example wrapper:

```xml
<figure class="diagram">
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
  <figcaption>Figure {N}: {description}</figcaption>
</figure>
```

Mark this chapter as requiring `properties="svg"` in the manifest.

### 3d. Mathematical Equations (MathML)

EPUB3 XHTML supports MathML 3 natively. Use `xmlns="http://www.w3.org/1998/Math/MathML"`.

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

Mark this chapter as requiring `properties="mathml"` in the manifest.

### 3e. Tables

```xml
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

## Step 4: Write the Navigation Document

Write `{slug}/OEBPS/nav.xhtml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:epub="http://www.idpf.org/2007/ops"
      xml:lang="{lang}">
  <head>
    <meta charset="UTF-8"/>
    <title>Table of Contents</title>
    <link rel="stylesheet" type="text/css" href="styles/main.css"/>
  </head>
  <body>
    <nav epub:type="toc" id="toc">
      <h1>Table of Contents</h1>
      <ol>
        <li><a href="chapters/ch001.xhtml">{Chapter 1 Title}</a></li>
        <li><a href="chapters/ch002.xhtml">{Chapter 2 Title}</a></li>
        <!-- one <li> per chapter -->
      </ol>
    </nav>
  </body>
</html>
```

## Step 5: Write the Package Document

Write `{slug}/OEBPS/content.opf`. Use today's date and time for the `dcterms:modified` value in UTC ISO 8601 format (e.g., `2024-01-15T12:00:00Z`).

For each chapter item in the manifest:
- Add `properties="svg"` if the chapter contains an `<svg>` element
- Add `properties="mathml"` if the chapter contains a `<math>` element
- Add `properties="svg mathml"` if it contains both

```xml
<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf"
         version="3.0"
         unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">{identifier}</dc:identifier>
    <dc:title>{Title}</dc:title>
    <dc:creator>{Author}</dc:creator>
    <dc:language>{lang}</dc:language>
    <meta property="dcterms:modified">{YYYY-MM-DDTHH:MM:SSZ}</meta>
  </metadata>

  <manifest>
    <!-- Navigation document — properties="nav" is required -->
    <item id="nav"
          href="nav.xhtml"
          media-type="application/xhtml+xml"
          properties="nav"/>

    <!-- Stylesheet -->
    <item id="css"
          href="styles/main.css"
          media-type="text/css"/>

    <!-- Chapters — add properties="svg", "mathml", or "svg mathml" as needed -->
    <item id="ch001"
          href="chapters/ch001.xhtml"
          media-type="application/xhtml+xml"/>
    <!-- repeat for ch002, ch003, … -->
  </manifest>

  <spine>
    <!-- Reading order — do not include nav -->
    <itemref idref="ch001"/>
    <!-- repeat for ch002, ch003, … -->
  </spine>
</package>
```

## Step 6: Package into .epub

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

## Step 7: Final Summary

Report back to the user with:

1. **File tree** of everything written, in a code block with tree-style formatting.
2. **Output**: `{slug}.epub` created, or the Python packaging script provided.
3. **Special content table**:

   | Type | Count / Details |
   |---|---|
   | Diagrams (SVG) | N diagrams: list names and types |
   | Math equations | N inline, N block |
   | Code blocks | list languages used |

4. **Caveats**: flag any diagram where the SVG is approximate and should be reviewed, or any MathML conversion that was uncertain.
5. **Recommended readers**: Calibre (desktop, free), Apple Books (iOS/macOS), Kobo, or any EPUB3-compliant reader.

---

## EPUB3 Validity Checklist

Before declaring the task complete, verify each item mentally:

- [ ] `mimetype` file exists at root, contains exactly `application/epub+zip`, no trailing newline
- [ ] `META-INF/container.xml` `full-path` points to `OEBPS/content.opf`
- [ ] `content.opf` has `version="3.0"` and includes `<meta property="dcterms:modified">`
- [ ] `nav.xhtml` has `epub:type="toc"` and an `<a>` link for every chapter
- [ ] All chapter files have `xmlns="http://www.w3.org/1999/xhtml"` on the `<html>` element
- [ ] All inline SVG elements have `xmlns="http://www.w3.org/2000/svg"`
- [ ] All MathML elements have `xmlns="http://www.w3.org/1998/Math/MathML"`
- [ ] Chapters with SVG have `properties="svg"` on their `<item>` in content.opf
- [ ] Chapters with MathML have `properties="mathml"` on their `<item>` in content.opf
- [ ] All paths in content.opf are relative to `OEBPS/`
- [ ] All chapter `href` values in nav.xhtml are relative to `OEBPS/` (i.e., `chapters/ch001.xhtml`)
