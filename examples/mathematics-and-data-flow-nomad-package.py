#!/usr/bin/env python3
"""
Assemble mathematics-and-data-flow-nomad chapter files into a single HTML
document and convert to PDF for the Supernotes Nomad (7.8-inch, 300 PPI).

Usage:
    pip install weasyprint      # first time only
    python3 mathematics-and-data-flow-nomad-package.py

Or for headless Chromium instead of WeasyPrint:
    python3 mathematics-and-data-flow-nomad-package.py --chrome

Run from the 'examples/' directory (the directory containing this script).
Requires Python 3.6+.
"""
import os
import re
import sys

SLUG  = "mathematics-and-data-flow-nomad"
TITLE = "Mathematics and Data Flow: A Technical Overview"
LANG  = "en"

# Source files in reading order (relative to the {slug}/ directory)
SOURCES = [
    "title.html",
    "chapters/ch001.html",
    "chapters/ch002.html",
    "chapters/ch003.html",
]


def extract_body(path: str) -> str:
    """Return the content between <body> and </body>."""
    with open(path, encoding="utf-8") as f:
        html = f.read()
    m = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else html.strip()


def main() -> None:
    use_chrome = "--chrome" in sys.argv

    # Read shared stylesheet
    css_path = os.path.join(SLUG, "styles", "main.css")
    with open(css_path, encoding="utf-8") as f:
        css = f.read()

    # Collect body content from every source file
    body_parts: list[str] = []
    for source in SOURCES:
        path = os.path.join(SLUG, source)
        body_parts.append(extract_body(path))

    # Assemble combined HTML
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

    out_pdf = f"{SLUG}.pdf"

    if use_chrome:
        import subprocess
        for binary in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
            try:
                subprocess.run(
                    [binary, "--headless", "--disable-gpu",
                     f"--print-to-pdf={out_pdf}",
                     "--no-pdf-header-footer",
                     "--run-all-compositor-stages-before-draw",
                     "--virtual-time-budget=5000",
                     combined_path],
                    check=True,
                )
                print(f"Created  → {out_pdf}  (via {binary})")
                return
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
        print("No Chromium binary found on PATH.", file=sys.stderr)
        print("Try: chromium --headless --print-to-pdf=... combined.html", file=sys.stderr)
        sys.exit(1)
    else:
        try:
            from weasyprint import HTML  # type: ignore
            HTML(combined_path).write_pdf(out_pdf)
            print(f"Created  → {out_pdf}  (via WeasyPrint)")
        except ImportError:
            print("WeasyPrint is not installed.", file=sys.stderr)
            print("  pip install weasyprint", file=sys.stderr)
            print(f"  python3 {SLUG}-package.py", file=sys.stderr)
            print("Or use Chrome:", file=sys.stderr)
            print(f"  python3 {SLUG}-package.py --chrome", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
