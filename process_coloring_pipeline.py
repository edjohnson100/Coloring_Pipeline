#!/usr/bin/env python3
"""
Coloring Page Processing Pipeline (Potrace Edition)

- Cleans PNGs with ImageMagick
- Traces to SVG with Potrace (Direct binary call)
- Exports PNG and PDF with Inkscape
- Automatically creates folder structure if missing
- Moves PNGs found next to the script into input_png for processing
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
EXPORT_WIDTH_PX = 3000
THRESHOLD_PERCENT = "60%"

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
    """Clean the PNG to pure black and white for better tracing."""
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
    # --turdsize 5: removes noise (speckles) smaller than 5 pixels
    # --alphamax 1: smooths corners

    # This simplifies the curves, reducing node count for Fusion/Laser cutters.
    # Range: 0.0 (exact) to 1.0+ (loose). 0.2 is default. 0.4-0.5 is the sweet spot for CAD.
    # --opttolerance 0.4: simplifies curves (reduces nodes) for Fusion/CNC
    cmd_potrace = [
        "potrace", 
        "-s", 
        "--turdsize", "5", 
        "--alphamax", "1", 
        "--opttolerance", "0.4",
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
    parser = argparse.ArgumentParser(description="Process coloring page PNGs.")
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

    # Create folder structure if missing
    for folder in (INPUT, CLEANED, SVG, PNG, PDF):
        folder.mkdir(exist_ok=True)

    # Move NEW PNGs found next to the script into input_png
    for png_file in ROOT.glob("*.png"):
        if not png_file.is_file():
            continue
        # Skip files that match output names or script components if they happen to be pngs
        if png_file.name in ("input_png", "cleaned_png"):
            continue

        target = INPUT / png_file.name
        if target.exists():
            logging.info(f"PNG already exists in input_png, skipping move: {png_file.name}")
            continue

        logging.info(f"Moving {png_file.name} into input_png/")
        shutil.move(str(png_file), str(target))

    # Check for required tools
    magick = require_tool("magick")
    inkscape = require_tool("inkscape")
    require_tool("potrace") # Verify potrace exists

    logging.info(f"Using ImageMagick: {magick}")
    logging.info(f"Using Inkscape: {inkscape}")

    png_files = sorted(INPUT.glob("*.png"))
    if not png_files:
        logging.warning("No PNG files found in input_png")
        return

    for src_png in png_files:
        stem = src_png.stem
        logging.info(f"Processing: {src_png.name}")

        cleaned_png = CLEANED / f"{stem}.png"
        svg_file = SVG / f"{stem}.svg"
        out_png = PNG / f"{stem}.png"
        out_pdf = PDF / f"{stem}.pdf"

        outputs_exist = all(p.exists() for p in (cleaned_png, svg_file, out_png, out_pdf))
        if outputs_exist and not OVERWRITE:
            logging.info(f"Skipping {src_png.name} (already processed)")
            continue

        try:
            clean_png(magick, src_png, cleaned_png)
            trace_svg(cleaned_png, svg_file)
            export_png(inkscape, svg_file, out_png)
            export_pdf(inkscape, svg_file, out_pdf)
        except Exception as e:
            logging.error(f"Failed processing {src_png.name}: {e}")

    logging.info("Pipeline complete")

if __name__ == "__main__":
    main()