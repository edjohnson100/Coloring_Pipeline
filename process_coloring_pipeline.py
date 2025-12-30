#!/usr/bin/env python3
"""
Coloring Page Processing Pipeline (Potrace Edition)

- Cleans Images (PNG, JPG, WEBP, etc.) with ImageMagick
- Traces to SVG with Potrace (Direct binary call)
- Exports PNG and PDF with Inkscape
- Automatically creates folder structure if missing
- Moves supported images found next to the script into input_png for processing
- Plug-and-play: drop script + README + images into a folder
"""

from pathlib import Path
import subprocess
import shutil
import sys
import logging
import argparse

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
# export width: 3000 is good for 8.5" x 11" prints
EXPORT_WIDTH_PX = 3000
# Threshold: 55% - 65% is a good range for black and white art
THRESHOLD_PERCENT = "60%"
# turdsize 5: removes noise (speckles) smaller than 5 pixels
TURDSIZE = "5"
# opttolerance 0.4: simplifies curves, reducing node count for Fusion/Laser cutters.
# Range: 0.0 (exact) to 1.0+ (loose). 0.2 is default. 0.4-0.5 is the sweet spot for CAD.
OPTTOLERANCE = "0.5"

# -----------------------------------------------------------------------------
# Paths (relative to script)
# -----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "input_png"
CLEANED = ROOT / "cleaned_png"
SVG = ROOT / "svg"
PNG = ROOT / "png"
PDF = ROOT / "pdf"
LOGFILE = ROOT / "process.log"
README = ROOT / "README.md"

# -----------------------------------------------------------------------------
# Logging setup
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGFILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------
def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        logging.error(f"Required tool not found on PATH: {name}")
        if sys.platform == "win32":
            logging.error(f"Please ensure the folder containing {name}.exe is in your System PATH.")
        sys.exit(1)
    return path

def run(cmd: list[str]):
    logging.info("Running: %s", " ".join(cmd))
    subprocess.run(cmd, check=True)

# -----------------------------------------------------------------------------
# Pipeline steps
# -----------------------------------------------------------------------------
def clean_png(magick: str, src: Path, dst: Path):
    """Clean the image to pure black and white for better tracing."""
    run([
        magick, str(src),
        "-alpha", "remove",
        "-alpha", "off",
        "-colorspace", "Gray",
        "-threshold", THRESHOLD_PERCENT,
        str(dst)
    ])

def trace_svg(src: Path, dst: Path):
    """
    Trace PNG to SVG using Potrace directly.
    Streams image data from ImageMagick -> Potrace to avoid temp files.
    """
    # 1. ImageMagick streams PNM format (Potrace native input) to stdout
    cmd_magick = ["magick", str(src), "pnm:-"]
    
    # 2. Potrace reads from stdin and writes SVG to file
    cmd_potrace = [
        "potrace", 
        "-s", 
        "--turdsize", TURDSIZE, 
        "--alphamax", "1", 
        "--opttolerance", OPTTOLERANCE,
        "-o", str(dst)
    ]

    logging.info(f"Tracing {src.name} with Potrace...")
    
    try:
        # Create the pipe
        p1 = subprocess.Popen(cmd_magick, stdout=subprocess.PIPE)
        # Run potrace, connecting its input to p1's output
        p2 = subprocess.run(cmd_potrace, stdin=p1.stdout, check=True)
        p1.wait() # Ensure magick finishes
    except subprocess.CalledProcessError as e:
        logging.error(f"Tracing failed for {src.name}: {e}")
        raise

def export_png(inkscape: str, src: Path, dst: Path):
    run([
        inkscape, str(src),
        f"--export-width={EXPORT_WIDTH_PX}",
        "--export-type=png",
        "--export-area-drawing",  # Export only the vectors, not the whole page
        f"--export-filename={dst}"
    ])

def export_pdf(inkscape: str, src: Path, dst: Path):
    run([
        inkscape, str(src),
        "--export-type=pdf",
        "--export-area-drawing",  # Export only the vectors
        f"--export-filename={dst}"
    ])

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Process coloring page images.")
    parser.add_argument('-o', '--overwrite', action='store_true', help='Force reprocessing all files')
    parser.add_argument('--?', action='store_true', help='Show usage info (README)')

    args = parser.parse_args()

    # Show README content if requested
    if args.__dict__.get('?'):
        if README.exists():
            print(README.read_text(encoding='utf-8'))
        else:
            print("README.md not found.")
        sys.exit(0)

    OVERWRITE = args.overwrite

    logging.info("Starting coloring pipeline")
    logging.info("=========================================")
    logging.info(f"EXPORT_WIDTH_PX = {EXPORT_WIDTH_PX}")
    logging.info(f"THRESHOLD_PERCENT = {THRESHOLD_PERCENT}")
    logging.info(f"TURDSIZE = {TURDSIZE}")
    logging.info(f"OPTTOLERANCE = {OPTTOLERANCE}")
    logging.info("=========================================")

    # Create folder structure if missing
    for folder in (INPUT, CLEANED, SVG, PNG, PDF):
        folder.mkdir(exist_ok=True)

    # Supported extensions (lowercase)
    SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp"}

    # Move NEW images found next to the script into input_png
    for file_path in ROOT.iterdir():
        if not file_path.is_file():
            continue
        # Skip script and readme explicitly
        if file_path.name in ("process_coloring_pipeline.py", "README.md"):
            continue
        
        # Check if extension is supported
        if file_path.suffix.lower() not in SUPPORTED_EXTS:
            continue

        target = INPUT / file_path.name
        if target.exists():
            logging.info(f"File already exists in input_png, skipping move: {file_path.name}")
            continue

        logging.info(f"Moving {file_path.name} into input_png/")
        shutil.move(str(file_path), str(target))

    # Check for required tools
    magick = require_tool("magick")
    inkscape = require_tool("inkscape")
    require_tool("potrace") # Verify potrace exists

    logging.info(f"Using ImageMagick: {magick}")
    logging.info(f"Using Inkscape: {inkscape}")

    # Gather all supported images from input_png
    input_files = sorted([
        f for f in INPUT.iterdir() 
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS
    ])

    if not input_files:
        logging.warning("No supported image files found in input_png")
        return

    for src_file in input_files:
        stem = src_file.stem
        logging.info(f"Processing: {src_file.name}")

        cleaned_png = CLEANED / f"{stem}.png"
        svg_file = SVG / f"{stem}.svg"
        out_png = PNG / f"{stem}.png"
        out_pdf = PDF / f"{stem}.pdf"

        outputs_exist = all(p.exists() for p in (cleaned_png, svg_file, out_png, out_pdf))
        if outputs_exist and not OVERWRITE:
            logging.info(f"Skipping {src_file.name} (already processed)")
            continue

        try:
            clean_png(magick, src_file, cleaned_png)
            trace_svg(cleaned_png, svg_file)
            export_png(inkscape, svg_file, out_png)
            export_pdf(inkscape, svg_file, out_pdf)
        except Exception as e:
            logging.error(f"Failed processing {src_file.name}: {e}")

    logging.info("Pipeline complete")

if __name__ == "__main__":
    main()