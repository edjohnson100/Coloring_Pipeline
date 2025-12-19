# Coloring Pipeline (Potrace Edition)

## Overview

This project provides a high-performance pipeline for converting black-and-white PNG coloring pages into clean vector SVGs and print-ready PNG/PDF files.

**Key Features:**

* **New Tracing Engine:** Now uses **Potrace** directly instead of Inkscape's internal tracer. This results in faster processing, no "blank file" errors, and significantly cleaner geometry.
* **CAD/Fusion/Laser Ready:** Includes optimization to reduce node counts, making the resulting SVGs much easier to import into **Autodesk Fusion** sketches or **XTool Creative Space** for your S1 laser.
* **Plug-and-Play:** Automatically handles folder creation and file moving.

## Folder Structure

The project expects the following folder structure (auto-created if missing):

```text
<project folder>/
├── input_png/      # Source PNG images (auto-populated if images are next to the script)
├── cleaned_png/    # Temporary folder for thresholded black/white PNGs
├── svg/            # Traced vector output files (Optimized for CAD/Laser)
├── png/            # Exported PNGs for printing (High Res)
├── pdf/            # Exported PDFs for printing
├── process_coloring_pipeline.py  # Main processing script
├── run_pipeline.bat             # Windows wrapper
├── run_pipeline.sh              # macOS/Linux wrapper
└── README.md       # This file
```

> **Note:** Simply drop your source PNGs in the root folder next to the script; the pipeline will automatically move them into `input_png` and process them.

## Usage

### 1. The Easy Way (One-Click Wrappers)

These scripts allow you to run the pipeline without opening a terminal manually. They also automatically detect and use a Python virtual environment (`venv`) if you have created one.

**Windows:**
1. Double-click `run_pipeline.bat`.
2. The console will open, run the processing, and stay open so you can read the logs.

**macOS / Linux:**
1. **First time setup:** You must tell the system the script is safe to execute. Open your Terminal, navigate to the folder, and run:
   ```bash
   chmod +x run_pipeline.sh
   ```
2. **Running:** Double-click `run_pipeline.sh` (or run `./run_pipeline.sh` from the terminal).

### 2. Using Python Directly (Manual)

Open your terminal/command prompt in the project folder:

```bash
python process_coloring_pipeline.py
```
*(Note: On macOS/Linux, you may need to use `python3` instead of `python`)*

* **Force Reprocessing:**
  ```bash
  python process_coloring_pipeline.py --overwrite
  ```
  Useful if you have changed the optimization settings and want to update existing files.

* **View Instructions:**
  ```bash
  python process_coloring_pipeline.py --?
  ```

## Configuration & Tuning

You can open `process_coloring_pipeline.py` in VSCode to adjust these settings at the top of the file:

* `EXPORT_WIDTH_PX`: Resolution of the final PNG export (default: 3000).
* `THRESHOLD_PERCENT`: The cutoff for converting gray pixels to black or white (default: 60%).
* `--opttolerance`: (Found inside the `trace_svg` function). Default is `0.4`.
    * **Increase (e.g., 0.6)** for simpler curves and fewer points (better for Fusion sketches and faster processing in XTool).
    * **Decrease (e.g., 0.2)** for stricter adherence to the pixel data (better for artistic printing).

## Dependencies & Installation

All tools must be installed and accessible via your system PATH.

### 1. Python 3.x
* **All OS:** Download from [Python.org](https://www.python.org/) or use your package manager (e.g., `brew install python` on macOS).

### 2. ImageMagick (for cleaning)
* **Windows:** Download the **DLL version** from [ImageMagick.org](https://imagemagick.org/script/download.php#windows).
    * **IMPORTANT:** During installation, check the box **"Install legacy utilities (e.g. convert)"** and **"Add to PATH"**.
* **macOS:**
  ```bash
  brew install imagemagick
  ```
* **Linux:**
  ```bash
  sudo apt install imagemagick
  ```

### 3. Potrace (for vectorizing)
This is the new engine that handles the tracing.

* **Windows:**
  1. Download the **Windows (64-bit)** zip from [SourceForge](https://potrace.sourceforge.net/#downloading).
  2. Extract the zip. You will see `potrace.exe`.
  3. Move the extracted folder to a permanent location (e.g., `C:\Program Files\potrace`).
  4. Add that folder to your System **PATH** environment variable.
  5. Verify by opening a terminal and typing `potrace --version`.
* **macOS:**
  ```bash
  brew install potrace
  ```
* **Linux:**
  ```bash
  sudo apt install potrace
  ```

### 4. Inkscape (for exporting PNG/PDF)
* **Windows:** Download the MSI/EXE from [Inkscape.org](https://inkscape.org/).
* **macOS:**
  ```bash
  brew install --cask inkscape
  ```
* **Linux:**
  ```bash
  sudo apt install inkscape
  ```

---
Happy coloring, scaling, and making! 🎨