# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pdf2slideshow is a bash-based tool that converts PDF documents into Reveal.js HTML slideshows. Each PDF page becomes an image slide in the presentation.

## Core Architecture

The project consists of two main bash scripts that orchestrate a three-step conversion pipeline:

1. **script.sh** - Converts a single PDF to HTML slideshow
2. **script_batch.sh** - Processes multiple PDFs in nested folder structures

### Conversion Pipeline

The conversion happens in three sequential steps:

1. **PDF Extraction** (`pdftoppm`): Extracts each PDF page as a PNG image with naming pattern `slide-N.png`
2. **Compression** (`pngquant`): Aggressively compresses PNGs using `-s 1` flag for web optimization
3. **HTML Assembly** (`sed`/`gsed`): Inserts image references into HTML template at line 16

### Template System

- Base template: `templates/template.html`
- Template is copied to output folder as `index.html`
- Reveal.js resources loaded from `https://media.harshp.com/dev/revealjs/`
- Image slides inserted at line 16 in reverse order (via `sort -r`) within `<div class="slides">`
- Each slide format: `<section><img src='slide-N.png'></section>`

## Commands

### Single PDF Conversion
```bash
./script.sh -p <PDF_PATH>           # Convert single PDF
./script.sh -p <PDF_PATH> -f        # Force reprocessing (overwrites existing)
```

### Batch Processing
```bash
./script_batch.sh -p <FOLDER_PATH>           # Process all PDFs in folder tree
./script_batch.sh -p <FOLDER_PATH> -f        # Force reprocessing
./script_batch.sh -p <FOLDER_PATH> -i        # Also generate root index.html using tree
```

### Testing
```bash
shellcheck script.sh script_batch.sh         # Lint bash scripts
```

## Platform Compatibility

The scripts handle macOS/Linux differences in sed behavior:
- **Linux**: Uses standard `sed -i`
- **macOS**: Uses `gsed -i` (GNU sed via Homebrew/MacPorts)

Detection is automatic via `$OSTYPE` check in script.sh:65-66.

## Key Implementation Details

- **Skip logic**: script.sh exits early if `index.html` exists (unless `-f` flag is used)
- **Template source**: Must be executed from repo root as script.sh uses `./template.html` path (line 56)
- **Slide ordering**: PNG files are sorted in reverse (`sort -r`) to maintain proper page order
- **Index generation**: script_batch.sh can generate folder tree HTML via `tree -r -I '*.png' -H './'`

## Dependencies

Required:
- `pdftoppm` (from poppler/poppler-utils)
- `pngquant`
- `sed` (Linux) or `gsed` (macOS)

Optional:
- `tree` (for generating index pages with `-i` flag)
