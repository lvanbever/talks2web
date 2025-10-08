# talks2web

Convert PDF presentations into interactive web slideshows using Reveal.js, with automated landing page generation.

## Overview

This project converts PDF presentations into web-based slideshows using Reveal.js. It supports both single PDF conversion and batch processing of multiple presentations, automatically generating a beautiful landing page that showcases all your talks with metadata, descriptions, and preview images.

## Features

- **PDF to Reveal.js Conversion**: Extracts PDF pages as optimized PNG images and creates interactive slideshows
- **Batch Processing**: Process entire directory trees of presentations at once
- **Landing Page Generation**: Automatically creates an organized landing page with:
  - Talk descriptions with markdown support
  - Preview images
  - Links to online slideshows, PDFs, and video recordings
  - Chronological organization by year
  - Social media meta tags for sharing
- **Mobile-Friendly**: Responsive design that works on desktop and mobile (landscape mode recommended)
- **Image Optimization**: Automatic PNG compression for fast web loading
- **Customizable Templates**: Easy-to-modify HTML templates and CSS styling

## Dependencies

### System Requirements

The following tools must be installed on your system:

- **pdftoppm** (from poppler): Extracts PDF pages as images
- **pngquant**: Compresses PNG images for web
- **gsed** (macOS) or **sed** (Linux): Text processing
- **Python 3.x**: For the landing page generator
- **tree** (optional): For generating directory indexes

### Python Requirements

- `pyyaml`: YAML metadata parsing
- `markdown`: Markdown to HTML conversion

## Installation (macOS)

### 1. Install Homebrew (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install System Dependencies

```bash
brew install poppler pngquant gnu-sed tree
```

### 3. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv dev

# Activate virtual environment
source dev/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
# Check that tools are available
pdftoppm -v
pngquant --version
gsed --version
python3 --version
```

## Usage

### Converting a Single PDF

```bash
./script.sh -p path/to/presentation.pdf
```

This creates an `index.html` slideshow in the same directory as the PDF.

**Options:**
- `-p <path>`: Path to PDF file (required)
- `-o <dir>`: Output directory (optional, defaults to PDF's directory)
- `-t <title>`: Page title for the slideshow (optional)
- `-f`: Force reprocessing (overwrite existing output)

**Example:**
```bash
./script.sh -p talks/my-talk/slides.pdf -t "My Amazing Talk" -f
```

### Batch Processing Multiple Talks

```bash
# Activate virtual environment first
source dev/bin/activate

# Process all talks and generate landing page
./generate_talks.py talks/ html/
```

**Options:**
- `talks_dir`: Directory containing talk subdirectories (required)
- `output_dir`: Output directory for generated HTML (required)
- `--force`: Force regeneration of all talks

**Example:**
```bash
./generate_talks.py talks/ html/ --force
```

### Directory Structure

```
talks2web/
├── talks/                    # Source directory for presentations
│   ├── talk1/
│   │   ├── metadata.yml     # Talk metadata
│   │   └── slides.pdf       # PDF presentation
│   └── talk2/
│       ├── metadata.yml
│       └── presentation.pdf
├── templates/               # HTML/CSS templates
│   ├── slideshow.html      # Reveal.js slideshow template
│   ├── landing.html        # Landing page template
│   ├── style.css           # Landing page styles
│   └── zurich_goes_networking.jpg  # Hero image
├── html/                   # Generated output (not in git)
│   ├── index.html         # Landing page
│   ├── style.css
│   ├── zurich_goes_networking.jpg
│   ├── talk1/
│   │   ├── index.html     # Slideshow
│   │   ├── slides.pdf
│   │   └── slide-*.png    # Extracted images
│   └── talk2/
│       └── ...
├── script.sh              # Single PDF converter
├── script_batch.sh        # Batch processor (legacy)
└── generate_talks.py      # Modern batch processor with landing page
```

## Metadata Format

Each talk directory must contain a `metadata.yml` file:

```yaml
talk:
  title: "Your Talk Title"
  pdf: "slides.pdf"
  description: "A brief description with [markdown](https://example.com) support."
  highlight: 1                    # Slide number to use as preview image
  date: 2025-01-15               # Talk date (YYYY-MM-DD)
  video: "https://youtu.be/..."  # Optional: video recording URL
```

**Required fields:**
- `title`: Talk title
- `pdf`: Filename of the PDF (relative to talk directory)
- `description`: Talk description (supports markdown)
- `highlight`: Slide number to feature as preview (1-indexed)
- `date`: Date of the talk

**Optional fields:**
- `video`: URL to video recording

## Reveal.js Navigation

The generated slideshows support:

- **Arrow keys**: Navigate between slides
- **Space**: Next slide
- **F**: Fullscreen mode
- **O** or **Esc**: Overview mode
- **?**: Show all keyboard shortcuts
- **Swipe**: Touch navigation on mobile devices

## Customization

### Templates

- **`templates/slideshow.html`**: Modify the Reveal.js slideshow appearance
- **`templates/landing.html`**: Customize the landing page structure
- **`templates/style.css`**: Adjust landing page styling

### Compression Speed

Edit `script.sh` line 64 to adjust PNG compression:
- `-s 1`: Slowest, best compression
- `-s 4`: Balanced (current default)
- `-s 10`: Fastest, lower compression

### Social Media Sharing

The landing page includes Open Graph and Twitter Card meta tags. Edit `templates/landing.html` to customize:
- Site URL
- Description
- Preview image

## Platform Compatibility

- **macOS**: Uses `gsed` (GNU sed via Homebrew)
- **Linux**: Uses standard `sed`

The scripts automatically detect the platform and use the appropriate tools.

## License

See [LICENSE](LICENSE) file for details.

## Credits

Originally based on [pdf2slideshow](https://github.com/coolharsh55/pdf2slideshow) by Harshvardhan J. Pandit, with extensive modifications for batch processing, landing page generation, and improved mobile support.
