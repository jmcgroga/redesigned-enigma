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

const { mathjax }          = require('mathjax-full/js/mathjax.js');
const { MathML }           = require('mathjax-full/js/input/mathml.js');
const { SVG }              = require('mathjax-full/js/output/svg.js');
const { liteAdaptor }      = require('mathjax-full/js/adaptors/liteAdaptor.js');
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
  const raw  = adaptor.outerHTML(node);  // <mjx-container …><svg …/></mjx-container>

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

// ── Main ─────────────────────────────────────────────────────────────────────

const [,, inputFile, outputFile] = process.argv;
if (!inputFile || !outputFile) {
  console.error('Usage: node mathml-to-svg.js <input.html> <output.html>');
  process.exit(1);
}

let html = fs.readFileSync(inputFile, 'utf8');

// Replace every <math …>…</math> block in one pass.
// Detect display="block" to choose inline vs. displayed rendering.
let count = 0;
html = html.replace(/<math[\s\S]*?<\/math>/gi, (match) => {
  const display = /display\s*=\s*["']block["']/i.test(match);
  count++;
  return mathmlToSvg(match, display);
});

// Inject CSS for the generated spans/divs before the closing </style>.
const css = `
    /* ── MathJax SVG output ── */
    .math-inline { display: inline-block; line-height: 0; }
    .math-inline svg { overflow: visible; }
    .math-block  { display: block; text-align: center; margin: 1em 0; line-height: 1; }
    .math-block svg { display: block; margin: 0 auto; overflow: visible; }`;

html = html.replace('</style>', css + '\n  </style>');

fs.writeFileSync(outputFile, html, 'utf8');
console.log(`Converted ${count} equation(s):  ${inputFile} → ${outputFile}`);
