<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/brand/typeanvil-lockup-dark@2x.png">
    <img src="docs/assets/brand/typeanvil-lockup-light@2x.png" alt="TypeAnvil" width="480" />
  </picture>
</p>

TypeAnvil is an open-source HTML and Markdown → PDF typesetting engine written
in Rust. It turns documents with paged-media CSS into production PDFs for
reports, invoices, letters, papers, and books.

It is built for developers, and the AI agents they run, who need print-quality
pagination without a commercial rendering engine or a headless browser farm.

TypeAnvil is a document compiler, not a browser. It runs no JavaScript and
does not cover all of CSS. If your documents depend on scripts or on
browser-only layout, use a browser-based renderer instead.

Contributing as an AI agent? Read [AGENTS.md](AGENTS.md) first.

## Why TypeAnvil

- **Deterministic output.** The same input, flags, engine version, and
  installed fonts produce a byte-identical PDF. Diff-test your documents in CI.
  Fonts count as input: a different font set can change the output.
- **Built for agents.** An MCP server, a JSON capability manifest, JSON
  diagnostics, and layout assertions let an agent render, check, and fix a
  document in a loop without a human. See [Use with AI agents](#use-with-ai-agents).
- **Typography by default.** Measured text shaping, line breaking, hyphenation,
  and widow/orphan handling are part of the engine's typography pipeline.
- **Paged-media CSS.** `@page` rules with margin boxes, named pages, page
  counters, running headers and running elements, footnotes, leader fills,
  multi-column layout, floats, and repeating table headers and footers.
- **Accessibility.** PDFs carry a tagged structure tree by default
  (`--no-tagged` turns it off). `--ua` also validates against PDF/UA-1.

PrinceXML and Chromium are comparison tools. CSS specifications define
TypeAnvil's expected behavior.

## Install

### npm or Bun (quickest)

Run it without installing:

```bash
npx typeanvil --version
bunx typeanvil --version
```

Or install it globally, which puts `typeanvil` on your `PATH`:

```bash
npm install -g typeanvil     # or: bun add -g typeanvil
typeanvil --version
```

The `typeanvil` package installs only the native binary for your platform
(macOS arm64/x64, Linux x64 glibc/musl, Linux arm64 glibc). It needs Node.js 18
or later, or Bun. There is no Windows package.

### Release binary

[GitHub Releases](https://github.com/winterloom/typeanvil/releases) has one
archive per platform plus a `SHA256SUMS` file. Targets:
`aarch64-apple-darwin`, `x86_64-apple-darwin`, `x86_64-unknown-linux-gnu`,
`x86_64-unknown-linux-musl`, and `aarch64-unknown-linux-gnu`.

Example for macOS on Apple Silicon (change `TARGET` for your platform):

```bash
VERSION=2026.11.0
TARGET=aarch64-apple-darwin
gh release download "v$VERSION" -R winterloom/typeanvil \
  -p SHA256SUMS -p "typeanvil-$VERSION-$TARGET.tar.gz"
shasum -a 256 -c SHA256SUMS --ignore-missing
tar -xzf "typeanvil-$VERSION-$TARGET.tar.gz"
sudo install "typeanvil-$VERSION-$TARGET/typeanvil" /usr/local/bin/typeanvil
typeanvil --version
```

Without the GitHub CLI, download the same two files from the release page.
The rest of this README assumes `typeanvil` is on your `PATH`.

### Build from source

You need a current stable Rust toolchain:

```bash
git clone https://github.com/winterloom/typeanvil
cd typeanvil
cargo build --release --manifest-path engine/Cargo.toml
```

The binary is `engine/target/release/typeanvil`. Copy it onto your `PATH`, or
call it by that path.

**Versions.** Releases use CalVer tags (`vYYYY.M.N`), and a release binary
prints that version (`typeanvil 2026.11.0`). A source build prints the version
in `engine/Cargo.toml` instead. Include the commit hash in bug reports from
source builds.

### Container image

Each release also publishes a Linux image with fonts included:

```bash
docker run --rm -v "$PWD:/work" ghcr.io/winterloom/typeanvil:2026.11.0 \
  render /work/input.html --page-width 8.5in --page-height 11in -o /work/output.pdf
```

See [Containers and packages](docs/guides/container.md).

### Fonts

The binary does not embed a fallback font. It reads Arial on macOS, or
Liberation Sans from `/usr/share/fonts/typeanvil/` on Linux. On a bare Linux
host, copy `docker/fonts/typeanvil/` there or use the container image. Details:
[Getting started § How input files are resolved](docs/guides/getting-started.md#how-input-files-are-resolved).

## Quick start

Save this as `input.html`:

```html
<!DOCTYPE html>
<html>
<head>
<title>Quarterly Report</title>
<style>
@page {
  size: Letter;
  margin: 1in;
  @top-left { content: string(chapter); font-size: 9pt; color: #666; }
  @bottom-center { content: "Page " counter(page) " of " counter(pages); }
}
h1 { string-set: chapter content(); }
table { width: 100%; }
th { background-color: #eee; }
thead { display: table-header-group; }
</style>
</head>
<body>
<h1>Quarterly Report</h1>
<p>Long content flows across pages with running headers and table pagination.</p>
<table>
  <thead><tr><th>Item</th><th>Value</th></tr></thead>
  <tbody><tr><td>Revenue</td><td>1,000</td></tr></tbody>
</table>
</body>
</html>
```

Render it:

```bash
typeanvil render input.html --page-width 8.5in --page-height 11in -o output.pdf
```

`--page-width`, `--page-height` and `-o` are required. An `@page { size }`
rule overrides them on the pages it matches. A successful run prints nothing
and exits `0`.

### Markdown

A file ending in `.md`, `.markdown` or `.mdown` is read as Markdown and styled
with a built-in stylesheet. YAML frontmatter sets the PDF title and author.

````markdown
---
title: Release Notes
author: A. Author
---

# Release Notes

| Item    | Status |
|---------|--------|
| Parser  | done   |
| Layout  | done   |

A note with a footnote.[^1]

[^1]: Footnotes print at the bottom of the page.
````

```bash
typeanvil render notes.md --page-width 8.5in --page-height 11in \
  --margin-top 1in --margin-right 1in --margin-bottom 1in --margin-left 1in \
  -o notes.pdf
```

Add CSS with `--css style.css`, or drop the built-in stylesheet with
`--no-default-css`. See [Markdown to PDF](docs/guides/markdown.md).

### Data templates

Render a template with JSON data. The data is checked against the template's
JSON Schema first. The repository includes an invoice and a report template:

```bash
typeanvil template-schema templates/invoice/invoice.tmpl.html
typeanvil render templates/invoice/invoice.tmpl.html \
  --data templates/invoice/invoice.example.json \
  --page-width 8.5in --page-height 11in -o invoice.pdf
```

See [templates/README.md](templates/README.md).

## Commands

| Command | What it does |
|---|---|
| `typeanvil render` | Render an HTML or Markdown file (or a template with `--data`) to PDF. |
| `typeanvil capabilities --json` | Print what this engine build supports, as JSON. |
| `typeanvil template-schema <template>` | Print the JSON Schema a template's data must match. |
| `typeanvil mcp` | Run the MCP server over stdio. |
| `typeanvil call <tool>` | Run one MCP tool once: JSON request on stdin, JSON result on stdout. |

Useful `render` flags:

| Flag | Purpose |
|---|---|
| `--diagnostics json\|text` | Report CSS the engine ignored and layout problems (overflow, empty pages, font fallback). |
| `--assert rules.json`, `--fail-on-assert` | Check layout goals (page count, keep-together, no overflow); exit `3` on failure. |
| `--embed-source`, `--embed-data <file>` | Attach the source or data file inside the PDF. |
| `--fetch none\|local\|allow-list`, `--max-pages`, `--timeout` | Safety limits for untrusted input; a stopped render exits `4`. |
| `--title`, `--author`, `--no-tagged`, `--ua` | Metadata and accessibility. |

Every flag, default, and exit code is in the [CLI reference](docs/guides/cli.md).

## Use with AI agents

TypeAnvil is designed as a feedback loop for agents: write the document,
render it, read back what went wrong, fix it, repeat.

**MCP server.** Nothing to install first: `npx` fetches TypeAnvil when the
client starts the server. Claude Code:

```bash
claude mcp add typeanvil -- npx -y typeanvil mcp --root "$HOME/reports"
```

Claude Desktop, Cursor and other JSON-configured clients:

```json
{ "mcpServers": { "typeanvil": { "command": "npx", "args": ["-y", "typeanvil", "mcp", "--root", "/path/to/reports"] } } }
```

With a global install or a release binary, use `typeanvil` as the command and
drop `-y typeanvil` from the arguments.

`--root` limits file access to that folder (repeatable). Leave it out to allow
every path the user can read. The server offers six tools: `render`,
`validate`, `inspect_page`, `capabilities`, `explain`, and `templates`.

**The loop:**

1. `capabilities`: learn which CSS this build supports.
2. Write the HTML or Markdown.
3. `validate` (or `render --diagnostics json --assert rules.json`): get the
   layout report and assertion results.
4. Fix what the report names, then repeat step 3.
5. `render`: produce the final PDF.

**Without MCP**, `typeanvil call` runs the same tools from a script:

```bash
echo '{"document":{"path":"input.html"},"assertions":[{"kind":"page_count","max":3}]}' \
  | typeanvil call validate
```

**Agent resources:**

- [Agent authoring guide](docs/guides/agent-authoring.md): how to write HTML
  that renders well, generated from the capability manifest.
- [skills/typeanvil-authoring](skills/typeanvil-authoring/SKILL.md): a
  ready-made agent skill.
- [schemas/mcp/v1](schemas/mcp/v1/): JSON Schemas for every tool's input and
  output.
- [MCP guide](docs/guides/mcp.md) and the
  [MCP tool contract](docs/specifications/mcp-tool-contract.spec.md).

## Features and known gaps

**Supported:** HTML and Markdown input; `@page` rules, margin boxes, named
pages, page and pages counters, running strings and running elements;
footnotes; cross-references and PDF bookmarks; fragmentation with widows,
orphans, and `break-*`; tables with repeating headers; multi-column layout;
floats; flexbox and basic grid; absolute and fixed positioning; vertical
writing modes; images (PNG, JPEG, GIF, SVG); `@font-face` and OpenType
features; hyphenation; MathML; tagged PDF and PDF/UA-1.

**Known gaps:**

- No JavaScript, browser APIs, or interactive layout.
- Partial CSS coverage. Notable gaps include attribute selectors, `rowspan`,
  `table-layout: fixed`, `clear`, column rules, grid `repeat()` and explicit
  placement, and flex `order`.
- Only `background-color` paints on elements and table cells. Background
  images and gradients do not.
- `vw`/`vh` resolve against a fixed 1024×768 viewport, not the page box.
- No network access: `http://` and `https://` stylesheets, fonts, and images
  are skipped. For untrusted input, also limit local file reads with
  `--fetch local` and set `--max-pages` and `--timeout`.

The [CSS support guide](docs/guides/css-support.md) lists every feature with
its limits. `typeanvil capabilities --json` reports the same facts for the
binary you are running.

**Performance.** On the bundled corpus, TypeAnvil renders typical reports and
invoices faster than PrinceXML, WeasyPrint, and headless Chrome; very large
documents and wide tables can be slower. Method and full results:
[benchmarks/RESULTS.md](benchmarks/RESULTS.md).

## Showcase

Rendered output for every release lives in the
[typeanvil-showcase](https://github.com/winterloom/typeanvil-showcase) repo and
on its [Pages site](https://winterloom.github.io/typeanvil-showcase/). The
[latest version](https://github.com/winterloom/typeanvil-showcase/tree/main/latest)
link stays stable.

## Documentation

- [Getting started](docs/guides/getting-started.md)
- [CLI reference](docs/guides/cli.md)
- [Paged media CSS](docs/guides/paged-media-css.md)
- [CSS support](docs/guides/css-support.md)
- [MCP server](docs/guides/mcp.md)
- [Containers and packages](docs/guides/container.md)
- [Architecture overview](docs/architecture/overview.md)
- [Feature specifications](docs/specifications/)

## Repository layout

| Path | Contents |
|---|---|
| `engine/` | The Rust engine and the `typeanvil` CLI |
| `harness/` | WPT conformance harness and release gate |
| `docs/` | Guides, specifications, architecture, and runbooks |
| `docsite/` | Docusaurus site built from `docs/` |
| `templates/` | Data templates (invoice, report) |
| `skills/` | Bundled agent skill |
| `schemas/mcp/` | MCP tool JSON Schemas |
| `npm/` | npm packages (`typeanvil` and the per-platform binaries) |
| `corpus/` | Real-world documents for regression and showcase |
| `benchmarks/` | Engine benchmark scripts and results |

## Contributing

- **Spec first.** Every feature starts with a spec in `docs/specifications/`,
  updated in the same change as the code.
- **Build and test in the dev container:**
  `./scripts/dev-container.sh cargo test --manifest-path /work/engine/Cargo.toml -j 2`.
  See [the dev container runbook](docs/operations/dev-container.md).
- **Run the gate** before you open a PR: `python3 scripts/gate.py`.
- **Land through a PR.** Release branches reject direct pushes;
  `scripts/land.py` opens the PR and enables auto-merge.
- **Sign the CLA.** Read [CLA.md](CLA.md).

Full guidelines:
[development guidelines](docs/conventions/development-guidelines.md). Agents:
[AGENTS.md](AGENTS.md).

## License

TypeAnvil is free software under the
[AGPL-3.0-only](https://www.gnu.org/licenses/agpl-3.0.html) license. The engine
has no license check, watermark, activation flow, phone-home behavior, or
feature gate.
