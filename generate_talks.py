#!/usr/bin/env python3
"""
Generate talk slideshows and landing page from PDF presentations.

This script processes talks from a source directory, generates reveal.js
slideshows for each talk, and creates a landing page listing all talks.
"""

import argparse
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional

import yaml
import markdown


class TalkProcessor:
    """Process talks and generate slideshows and landing page."""

    def __init__(self, talks_dir: Path, output_dir: Path, force: bool = False):
        self.talks_dir = talks_dir
        self.output_dir = output_dir
        self.force = force
        self.processed_talks: List[Dict] = []
        self.skipped_talks: List[str] = []
        self.errors: List[str] = []
        self.lock = Lock()  # Thread-safe access to shared lists

    def parse_metadata(self, metadata_file: Path) -> Optional[Dict]:
        """Parse YAML metadata file for a talk."""
        try:
            with open(metadata_file, 'r') as f:
                data = yaml.safe_load(f)

            if not data or 'talk' not in data:
                raise ValueError("Missing 'talk' section in metadata")

            talk = data['talk']
            required_fields = ['title', 'pdf', 'description', 'highlight', 'date']

            for field in required_fields:
                if field not in talk:
                    raise ValueError(f"Missing required field: {field}")

            return talk
        except Exception as e:
            with self.lock:
                self.errors.append(f"Error parsing {metadata_file}: {e}")
            return None

    def is_talk_processed(self, talk_handle: str) -> bool:
        """Check if a talk has already been processed."""
        talk_output_dir = self.output_dir / talk_handle
        index_file = talk_output_dir / "index.html"
        return index_file.exists() and talk_output_dir.is_dir()

    def process_talk(self, talk_dir: Path) -> bool:
        """Process a single talk directory."""
        talk_handle = talk_dir.name
        metadata_file = talk_dir / "metadata.yml"

        if not metadata_file.exists():
            with self.lock:
                self.errors.append(f"No metadata.yml found in {talk_dir}")
            return False

        # Parse metadata
        metadata = self.parse_metadata(metadata_file)
        if not metadata:
            return False

        # Check if already processed
        if not self.force and self.is_talk_processed(talk_handle):
            with self.lock:
                self.skipped_talks.append(talk_handle)
                # Still add to processed_talks for landing page generation
                metadata['handle'] = talk_handle
                self.processed_talks.append(metadata)
            return True

        # Find PDF file
        pdf_file = talk_dir / metadata['pdf']
        if not pdf_file.exists():
            with self.lock:
                self.errors.append(f"PDF file not found: {pdf_file}")
            return False

        # Create output directory
        talk_output_dir = self.output_dir / talk_handle
        talk_output_dir.mkdir(parents=True, exist_ok=True)

        # Call script.sh to generate slideshow
        print(f"Processing {talk_handle}...")
        try:
            cmd = [
                './script.sh',
                '-p', str(pdf_file),
                '-o', str(talk_output_dir),
                '-t', metadata['title']
            ]
            if self.force:
                cmd.append('-f')

            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout)

        except subprocess.CalledProcessError as e:
            with self.lock:
                self.errors.append(f"Error processing {talk_handle}: {e.stderr}")
            return False

        # Copy PDF to output directory
        output_pdf = talk_output_dir / metadata['pdf']
        shutil.copy2(pdf_file, output_pdf)

        # Add to processed talks
        metadata['handle'] = talk_handle
        with self.lock:
            self.processed_talks.append(metadata)

        return True

    def markdown_to_html(self, text: str) -> str:
        """Convert markdown text to HTML, removing wrapping <p> tags."""
        # Convert markdown to HTML
        html = markdown.markdown(text)
        # Remove wrapping <p></p> tags if present (since we're inline)
        if html.startswith('<p>') and html.endswith('</p>'):
            html = html[3:-4]
        return html

    def generate_landing_page(self):
        """Generate the landing page with all talks."""
        template_file = Path('templates/landing.html')

        if not template_file.exists():
            with self.lock:
                self.errors.append(f"Template file not found: {template_file}")
            return False

        # Read template
        with open(template_file, 'r') as f:
            template = f.read()

        # Sort talks by date (newest first)
        sorted_talks = sorted(
            self.processed_talks,
            key=lambda t: t['date'],
            reverse=True
        )

        # Group talks by year
        from itertools import groupby
        talks_by_year = {}
        for talk in sorted_talks:
            year = talk['date'].year
            if year not in talks_by_year:
                talks_by_year[year] = []
            talks_by_year[year].append(talk)

        # Generate all talk entries with year headings
        all_entries = []
        for year in sorted(talks_by_year.keys(), reverse=True):
            talks = talks_by_year[year]

            # Add year heading as a special list item
            year_heading = f"""            <li class="year-heading">{year}</li>"""
            all_entries.append(year_heading)

            # Generate talk entries for this year
            for talk in talks:
                handle = talk['handle']
                title = talk['title']
                pdf = talk['pdf']
                description = talk['description']
                highlight = talk['highlight']
                video = talk.get('video')  # Optional video field

                # Convert markdown description to HTML
                description_html = self.markdown_to_html(description)

                # Determine PNG padding based on number of slides
                # pdftoppm uses 2 digits for <100 slides, 3 digits for 100+
                talk_dir = self.output_dir / handle
                png_files = list(talk_dir.glob('slide-*.png'))
                num_slides = len(png_files)
                padding = 3 if num_slides >= 100 else 2
                highlight_img = f"slide-{highlight:0{padding}d}.png"

                # Build links string with optional video
                links = f"<a href=\"{handle}/{pdf}\">PDF</a>"
                if video:
                    links += f", <a href=\"{video}\">Video</a>"

                entry = f"""            <li class="talk-entry">
                <a href="{handle}/index.html">{title}</a>  ({links})
                <p class="talk-desc">
                    {description_html}
                </p>
                <figure>
                    <a href="{handle}/index.html" class="img-link"><img src="{handle}/{highlight_img}"></img></a>
                </figure>
            </li>"""
                all_entries.append(entry)

        # Join all entries into single list
        talks_html = '\n'.join(all_entries)
        talks_html = f"""        <ol type="1">
{talks_html}
        </ol>"""

        # Replace the talks-by-year section content
        import re

        # Pattern to match the talks-by-year section
        pattern = r'(<section id="talks-by-year" class="level1">)(.*?)(</section>)'

        replacement = f'\\1\n{talks_html}\n    \\3'
        updated_html = re.sub(pattern, replacement, template, flags=re.DOTALL)

        # Update the last update timestamp
        now = datetime.now().strftime('%a %b %d %Y')
        updated_html = re.sub(
            r'Last updated:.*?</div>',
            f'Last updated: {now}\n</div>',
            updated_html,
            flags=re.DOTALL
        )

        # Write landing page
        output_file = self.output_dir / 'index.html'
        with open(output_file, 'w') as f:
            f.write(updated_html)

        return True

    def copy_assets(self):
        """Copy CSS and other assets to output directory."""
        style_file = Path('templates/style.css')
        if style_file.exists():
            shutil.copy2(style_file, self.output_dir / 'style.css')

        hero_image = Path('templates/zurich_goes_networking.jpg')
        if hero_image.exists():
            shutil.copy2(hero_image, self.output_dir / 'zurich_goes_networking.jpg')

    def process_all(self):
        """Process all talks and generate landing page."""
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Find all talk directories
        talk_dirs = [d for d in self.talks_dir.iterdir()
                     if d.is_dir() and not d.name.startswith('.')]

        if not talk_dirs:
            print(f"No talk directories found in {self.talks_dir}")
            return

        # Process talks in parallel with up to 8 workers
        with ThreadPoolExecutor(max_workers=8) as executor:
            # Submit all tasks
            futures = {executor.submit(self.process_talk, talk_dir): talk_dir
                      for talk_dir in sorted(talk_dirs)}

            # Wait for completion and handle any exceptions
            for future in as_completed(futures):
                talk_dir = futures[future]
                try:
                    future.result()
                except Exception as e:
                    with self.lock:
                        self.errors.append(f"Unexpected error processing {talk_dir}: {e}")

        # Generate landing page
        if self.processed_talks:
            self.generate_landing_page()
            self.copy_assets()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print processing summary."""
        print("\n" + "="*60)
        print("PROCESSING SUMMARY")
        print("="*60)

        newly_processed = [t['handle'] for t in self.processed_talks
                          if t['handle'] not in self.skipped_talks]

        if newly_processed:
            print(f"\n✓ Newly processed talks ({len(newly_processed)}):")
            for handle in newly_processed:
                print(f"  - {handle}")

        if self.skipped_talks:
            print(f"\n⊘ Skipped talks (already processed) ({len(self.skipped_talks)}):")
            for handle in self.skipped_talks:
                print(f"  - {handle}")

        if not newly_processed and not self.skipped_talks:
            print("\nNo talks found to process.")

        if self.errors:
            print(f"\n✗ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")

        print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description='Generate talk slideshows and landing page'
    )
    parser.add_argument(
        'talks_dir',
        type=Path,
        help='Directory containing talk subdirectories'
    )
    parser.add_argument(
        'output_dir',
        type=Path,
        help='Output directory for generated HTML files'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force regeneration of all talks'
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.talks_dir.exists():
        print(f"Error: Talks directory does not exist: {args.talks_dir}")
        sys.exit(1)

    # Create processor and run
    processor = TalkProcessor(args.talks_dir, args.output_dir, args.force)
    processor.process_all()


if __name__ == '__main__':
    main()
