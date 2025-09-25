# Pdfpy: Automated PDF Chapter Extraction

A Python utility for partitioning PDF documents into discrete files based on chapter divisions.

Pdfpy employs a dual-method approach for chapter detection. It prioritizes the document's bookmark hierarchy for high-accuracy splitting. If bookmarks are absent, it falls back to a configurable, style-based heuristic analysis, identifying chapter titles by font properties and keywords. The tool is operated via a simple drag-and-drop command-line interface on Windows.

**NotebookLM Tip**: Combine the book chapter with the lecture video and slides.

---

## Features

- **Bookmark-Based Splitting**  
  Accurately identifies and splits chapters using the top-level bookmark structure.

- **Heuristic Style Analysis**  
  A fallback mechanism that detects chapters based on user-defined text properties (font size, weight, keywords) specified in an external configuration file.

- **External Configuration**  
  Heuristic parameters are managed in `chapters_config.md`, separating rules from the core application logic for easy tuning.

- **Drag-and-Drop Interface**  
  Includes simple batch files (`run_automatic.bat`, `run_manual`.bat) for easy use on Windows.

---

## Limitations
- **Image-Based PDFs**: The automatic detection mode requires the PDF to contain selectable, embedded text. It cannot process scanned documents where text is part of an image. For such files, **Manual Mode** (`run_manual`) is the required workaround.

---

## Requirements

- **Python 3.7+** — accessible from the command line as `python` and `pip`.  
- **Dependencies** — listed in `requirements.txt`.  
- **OS** — Tested on Windows. The provided `run_pdfpy.bat` is Windows-specific.

---

## Usage

1. **Install dependencies**

    pip install -r requirements.txt

2. **Run the tool**  
   Drag a PDF file and drop it onto `run_pdfpy.bat`. The batch script will pass the file to the Python utility and start processing.

3. **Output**  
   The resulting chapter files are saved to a new `*_chapters` directory created next to the input PDF (one file per detected chapter, or according to any naming convention you configure).

---

## Configuration

The heuristic analysis is configured in `chapters_config.md`. Typical parameters:

- **CHAPTER_KEYWORD** — The term(s) used to identify chapter headings (e.g., `"Chapter"`, `"Section"`).  
- **MIN_FONT_SIZE** — The minimum font size that qualifies text as a potential chapter title.  
- **MUST_BE_BOLD** — `true` / `false` boolean to require bold styling for chapter headers.

Combine these rules to reduce false positives; keeping them in the config file lets you change behavior without editing the main codebase.

---

## Use Cases

- **Academic reading** — Break large textbooks, theses, or reports into chapter-sized files for easier navigation.  
- **Research preprocessing** — Prepare chapter-level inputs for text mining, indexing, or LLM ingestion.  
- **Publishing workflows** — Extract chapters for reformatting, conversion, or republishing.  
- **Automation** — Integrate into batch pipelines that require chapter-level PDFs or text outputs.

---

## Getting Help

If you encounter bugs or want new features, open an issue on the project repository and include a short sample PDF or relevant `chapters_config.md` settings to help reproduce the problem.

---

## License

This project is distributed under the MIT License. See the `LICENSE` file for full details.
