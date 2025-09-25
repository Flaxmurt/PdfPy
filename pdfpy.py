"""
A command-line utility to split a PDF file into separate chapters.

This script offers two primary modes of operation:
1.  Automatic Mode: Detects chapters using bookmarks or text style analysis.
2.  Manual Mode: Splits the PDF based on a user-provided list of page numbers.

Usage:
    Automatic: python pdfpy.py path/to/your/document.pdf
    Manual:    python pdfpy.py path/to/your/document.pdf --manual "5,10,56"

Limitation: The automatic mode cannot process image-based (scanned) PDFs.
"""

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import fitz  # PyMuPDF

CONFIG_FILE_NAME = "chapters_config.md"


@dataclass
class Chapter:
    """Represents a single chapter with a title and starting page."""
    title: str
    page: int


def parse_config(config_path: Path) -> Optional[Dict[str, any]]:
    """Parses the chapter style configuration file."""
    config = {}
    try:
        with config_path.open('r', encoding='utf-8') as f:
            for line in f:
                if ':' in line and not line.strip().startswith('#'):
                    key, value = map(str.strip, line.split(':', 1))
                    if key == 'MIN_FONT_SIZE':
                        config[key] = float(value)
                    elif key == 'MUST_BE_BOLD':
                        config[key] = value.lower() == 'true'
                    else:
                        config[key] = value
    except FileNotFoundError:
        print(f"Error: Configuration file not found at '{config_path}'")
        return None
    return config


def find_chapters_by_style(doc: fitz.Document, config: Dict) -> List[Chapter]:
    """Finds chapter start pages by analyzing text style and content."""
    found_chapters = []
    keyword = config.get('CHAPTER_KEYWORD', 'Chapter')
    pattern = re.compile(rf"^{re.escape(keyword)}\s+\d+", re.IGNORECASE)
    min_size = config.get('MIN_FONT_SIZE', 16)
    must_be_bold = config.get('MUST_BE_BOLD', True)

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    is_large_enough = span["size"] >= min_size
                    is_bold = "bold" in span["font"].lower()
                    bold_ok = not must_be_bold or is_bold
                    matches_pattern = pattern.match(text)

                    if is_large_enough and bold_ok and matches_pattern:
                        # Avoid adding duplicate chapters for the same page
                        if not any(c.page == page_num + 1 for c in found_chapters):
                            found_chapters.append(
                                Chapter(title=text, page=page_num + 1)
                            )
    return found_chapters


def perform_split(doc: fitz.Document, chapters: List[Chapter], out_dir: Path):
    """Core logic to split a PDF based on a list of chapters."""
    if not chapters:
        print("\nWarning: No chapters were provided or found to split.")
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    chapters.sort(key=lambda x: x.page)

    print(f"\nFound {len(chapters)} sections. Splitting document...")
    for i, chapter in enumerate(chapters):
        start_page = chapter.page - 1
        end_page = doc.page_count - 1
        if i + 1 < len(chapters):
            end_page = chapters[i + 1].page - 2

        if start_page > end_page or start_page < 0 or start_page >= doc.page_count:
            print(f"Warning: Invalid page range for '{chapter.title}'. Skipping.")
            continue

        safe_title = re.sub(r'[\\/*?:"<>|]', "", chapter.title)
        safe_title = safe_title.replace(' ', '_')
        out_path = out_dir / f"{i + 1:02d}_{safe_title}.pdf"

        with fitz.open() as writer:
            writer.insert_pdf(doc, from_page=start_page, to_page=end_page)
            writer.save(out_path)
        print(f"  - Created '{out_path}' (Pages {start_page + 1}-{end_page + 1})")


def process_pdf_automatic(doc: fitz.Document, config_path: Path) -> List[Chapter]:
    """Orchestrates the automatic PDF splitting process."""
    chapters = []
    config = parse_config(config_path)
    if not config:
        return []

    toc = doc.get_toc()
    if toc:
        print("\nFound bookmarks. Filtering for main sections.")
        kw = config.get('CHAPTER_KEYWORD', 'chapter').lower()
        keywords = {kw, 'appendix', 'index', 'part'}
        chapters = [
            Chapter(title=item[1], page=item[2])
            for item in toc
            if item[0] == 1 and any(k in item[1].lower() for k in keywords)
        ]
    else:
        is_text_based = any(page.get_text("text") for page in doc)
        if not is_text_based:
            print("\nERROR: This PDF appears to be image-based (scanned).")
            print("Automatic mode cannot process it. Please use Manual Mode.")
            return []

        print("\nNo bookmarks found. Analyzing text styles.")
        chapters = find_chapters_by_style(doc, config)

    return chapters


def process_pdf_manual(pages_str: str) -> Optional[List[Chapter]]:
    """Processes a user-provided string of page numbers."""
    if not pages_str:
        return []
    try:
        pages = sorted([int(p.strip()) for p in pages_str.split(',')])
        return [Chapter(title=f'Section_Page_{p}', page=p) for p in pages]
    except ValueError:
        print("Error: Invalid page numbers provided. Please use comma-separated integers.")
        return None


def main() -> None:
    """Entry point for the command-line application."""
    parser = argparse.ArgumentParser(description="Split a PDF document into chapters.")
    parser.add_argument("pdf_file", type=Path, help="Path to the source PDF file.")
    parser.add_argument(
        "--manual",
        metavar="PAGES",
        type=str,
        help="Provide a comma-separated list of starting page numbers.",
    )
    args = parser.parse_args()

    pdf_path: Path = args.pdf_file

    if not pdf_path.is_file() or pdf_path.suffix.lower() != '.pdf':
        print(f"Error: Path '{pdf_path}' is not a valid PDF file.")
        return

    script_dir = Path(__file__).parent.resolve()
    config_file = script_dir / CONFIG_FILE_NAME
    output_folder = pdf_path.parent / f"{pdf_path.stem}_chapters"

    try:
        doc = fitz.open(pdf_path)
    except fitz.fitz.FitzError as e:
        print(f"Error: Could not read '{pdf_path}'. It may be corrupt or invalid. Reason: {e}")
        return

    chapters_to_split = []
    if args.manual is not None:
        print("Running in Manual Mode...")
        chapters_to_split = process_pdf_manual(args.manual)
    else:
        print("Running in Automatic Mode...")
        chapters_to_split = process_pdf_automatic(doc, config_file)

    if chapters_to_split:
        perform_split(doc, chapters_to_split, output_folder)
    else:
        # This branch is hit if process_pdf_manual returns None on error
        print("No valid chapters found or an error occurred.")


    doc.close()
    print("\nProcessing complete.")


if __name__ == '__main__':
    main()
