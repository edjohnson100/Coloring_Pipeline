# Master Reference for Coloring Pipeline Project Files

This document is a master reference for all essential files in the Coloring Pipeline project, including their purpose and recommended usage. It is designed to prevent accidental overwrites and clarify file roles.

---

## 1. `process_coloring_pipeline.py`
- **Type:** Python script
- **Purpose:** Main pipeline script that:
  - Cleans PNGs with ImageMagick
  - Traces images to SVG with Inkscape
  - Exports PNG and PDF files
  - Automatically creates folder structure if missing
  - Moves PNGs next to the script into `input_png`
- **Usage:**
  ```bash
  python process_coloring_pipeline.py          # Process PNGs
  python process_coloring_pipeline.py --overwrite   # Force reprocessing
  python process_coloring_pipeline.py --?         # Show full README instructions
  python process_coloring_pipeline.py -h          # Show standard usage help
  ```
- **Notes:** Do not rename this file; script references relative paths based on its location.

---

## 2. `README.md`
- **Type:** Markdown documentation
- **Purpose:** User-facing instructions for:
  - Pipeline overview
  - Folder structure
  - Usage instructions (`--?` and `--help`)
  - Notes, best practices, and dependencies
- **Usage:** Users can read it for workflow guidance or view it with `python process_coloring_pipeline.py --?`
- **Important:** Never overwrite this with installation instructions; keep separate from `INSTALLATION.md`.

---

## 3. `INSTALLATION.md`
- **Type:** Markdown documentation
- **Purpose:** Installation and configuration instructions for:
  - Python 3.x
  - ImageMagick (with PNG support)
  - Inkscape
  - PATH verification
- **Platform Coverage:** Windows, macOS, Linux
- **Usage:** Read before running the pipeline for first-time setup.
- **Important:** Keep this file separate from README; do not merge content.

---

## 4. Project Folders (Auto-created by Script)
- **`input_png/`**: Source PNGs to be processed.
- **`cleaned_png/`**: Intermediate PNGs after cleaning and thresholding.
- **`svg/`**: Vector outputs from tracing.
- **`png/`**: Exported PNGs for printing.
- **`pdf/`**: Exported PDFs for printing.

**Notes:**
- Users can drop their images next to `process_coloring_pipeline.py`; the script will auto-move them to `input_png/`.
- These folders are created automatically if missing; do not manually delete unless you intend to clear outputs.

---

## 5. Logging
- **File:** `process.log`
- **Purpose:** Tracks all processing steps and errors.
- **Location:** Project root
- **Notes:** Do not edit manually; review for troubleshooting.

---

## 6. General Best Practices
- Keep `README.md` and `INSTALLATION.md` distinct.
- Avoid placing unrelated files in the script folder to prevent accidental moves.
- Always use `--?` or `-h` to check instructions before processing.
- Maintain a backup of any original images before processing.

---

This master reference ensures that all files are clearly documented, and you have a reliable source to prevent accidental overwrites.

