#!/usr/bin/env python3
"""
Coloring Page Processing Pipeline (Potrace Edition)
Now with Auto-Leveling for better contrast!

- Cleans PNGs/JPGs/WEBP/TIFF/BMP with ImageMagick
    - Auto-Levels: Stretches contrast (black/white points) to fix muddy images
    - B&W Mode: Standard thresholding
    - Color Mode: Flattens gradients to solid colors before thresholding
- Traces to SVG with Potrace (Direct binary call)
- Exports PNG and PDF with Inkscape
- Automatically creates folder structure if missing
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
# Threshold: 50% often works better for comics than 60%
THRESHOLD_PERCENT = "65%"
# For color images: Max colors to reduce to before B&W conversion.
# 8 colors creates simpler, chunkier shapes (better for comics/stained glass styles)
POSTERIZE_COLORS = "8" 
# Level adjustment: "10%,90%" means pixels darker than 10% become black, 
# lighter than 90% become white. Stretches the middle.
LEVEL_ADJUSTMENT = "0%,80%"

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
def detect_color_mode(magick: str, src: Path) -> str:
    """
    Inspects image saturation to determine if it is Color or B&W.
    Returns: 'color' or 'bw'
    """
    # We extract the Saturation channel (HSL) and get the mean average (0.0 - 1.0)
    cmd = [
        magick, str(src), 
        "-colorspace", "HSL", 
        "-channel", "S", 
        "-separate", 
        "-format", "%[fx:mean]", 
        "info:"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        saturation = float(result.stdout.strip())
        # If average saturation is > 5%, treat as color
        if saturation > 0.05:
            return 'color'
        return 'bw'
    except (subprocess.CalledProcessError, ValueError):
        logging.warning(f"Could not auto-detect color for {src.name}, defaulting to bw")
        return 'bw'

def clean_png(magick: str, src: Path, dst: Path, mode: str = 'auto', invert_mode: str = 'off'):
    """
    Clean the PNG for tracing.
    - mode='auto': Detects saturation.
    - mode='color': Flattens gradients (-dither None -colors X) -> Gray -> Threshold.
    - mode='bw': Standard Gray -> Threshold.
    - invert_mode: 'on' force inverts colors (negate). Default 'off'.
    """
    
    # Resolve auto mode
    if mode == 'auto':
        mode = detect_color_mode(magick, src)
        logging.info(f"Auto-detection for {src.name}: {mode.upper()}")
    else:
        logging.info(f"Processing {src.name} using forced mode: {mode.upper()}")

    cmd = [magick, str(src)]
    
    # 1. Apply Levels (Contrast Stretch) FIRST to fix muddy blacks/whites
    # This helps "Metro Dance" style images where the black isn't quite black.
    cmd.extend(["-level", LEVEL_ADJUSTMENT])

    # 2. Apply Invert if manually requested
    if invert_mode == 'on':
        logging.info(f"Applying INVERT to {src.name}")
        cmd.append("-negate")

    if mode == 'color':
        # COLOR STRATEGY:
        # 1. -dither None -colors 8:  Snaps gradients to nearest solid color.
        # 2. -colorspace Gray: Converts those solid blocks to gray.
        # 3. -threshold: Converts to black/white.
        cmd.extend([
            "-dither", "None",
            "-colors", POSTERIZE_COLORS, 
            "-colorspace", "Gray",
            "-threshold", THRESHOLD_PERCENT
        ])
    else:
        # B&W STRATEGY:
        # Simple thresholding.
        cmd.extend([
            "-alpha", "remove",
            "-alpha", "off",
            "-colorspace", "Gray",
            "-threshold", THRESHOLD_PERCENT
        ])

    cmd.append(str(dst))
    run(cmd)

def trace_svg(src: Path, dst: Path):
    """
    Trace PNG to SVG using Potrace directly.
    Streams image data from ImageMagick -> Potrace to avoid temp files.
    """
    cmd_magick = ["magick", str(src), "pnm:-"]
    
    # --opttolerance 0.4: simplifies curves (reduces nodes) for Fusion/CNC
    cmd_potrace = [
        "potrace", 
        "-s", 
        "--turdsize", "5", 
        "--alphamax", "1", 
        "--opttolerance", "0.5",
        "-o", str(dst)
    ]

    logging.info(f"Tracing {src.name} with Potrace...")
    
    try:
        p1 = subprocess.Popen(cmd_magick, stdout=subprocess.PIPE)
        p2 = subprocess.run(cmd_potrace, stdin=p1.stdout, check=True)
        p1.wait() 
    except subprocess.CalledProcessError as e:
        logging.error(f"Tracing failed for {src.name}: {e}")
        raise

def export_png(inkscape: str, src: Path, dst: Path):
    run([
        inkscape, str(src),
        f"--export-width={EXPORT_WIDTH_PX}",
        "--export-type=png",
        "--export-area-drawing", 
        f"--export-filename={dst}"
    ])

def export_pdf(inkscape: str, src: Path, dst: Path):
    run([
        inkscape, str(src),
        "--export-type=pdf",
        "--export-area-drawing", 
        f"--export-filename={dst}"
    ])

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Batch process images (PNG, JPG, etc.) into clean SVG/PDF coloring pages.",
        epilog="Supported formats: PNG, JPG, JPEG, BMP, TIFF, WEBP"
    )
    parser.add_argument('-o', '--overwrite', action='store_true', help='Force reprocessing of all existing files.')
    parser.add_argument('--?', action='store_true', help='Display the full README.md file with detailed usage instructions.')
    parser.add_argument('--mode', choices=['auto', 'color', 'bw'], default='auto', 
                        help='Trace mode. "color": posterizes gradients (comic style). "bw": standard threshold. "auto": detects saturation (default).')
    parser.add_argument('--invert', choices=['on', 'off'], default='off',
                        help='Invert colors (negate). Use "on" if input has white lines on black background.')

    args = parser.parse_args()

    # Show README content if requested
    if args.__dict__.get('?'):
        if README.exists():
            print(README.read_text(encoding='utf-8'))
        else:
            print("README.md not found.")
        sys.exit(0)

    OVERWRITE = args.overwrite
    MODE = args.mode
    INVERT = args.invert

    logging.info(f"Starting coloring pipeline (Mode: {MODE}, Invert: {INVERT})")

    # Create folder structure if missing
    for folder in (INPUT, CLEANED, SVG, PNG, PDF):
        folder.mkdir(exist_ok=True)

    # Move NEW images found next to the script into input_png
    # Supported extensions (lowercase)
    SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp"}

    for file_path in ROOT.iterdir():
        if not file_path.is_file():
            continue
        # Skip script and readme explicitly if they happen to match somehow
        if file_path.name in ("process_coloring_pipeline.py", "README.md"):
            continue
        
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
    require_tool("potrace") 

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

        # All outputs force .png/.svg/.pdf extension, effectively converting inputs
        cleaned_png = CLEANED / f"{stem}.png"
        svg_file = SVG / f"{stem}.svg"
        out_png = PNG / f"{stem}.png"
        out_pdf = PDF / f"{stem}.pdf"

        outputs_exist = all(p.exists() for p in (cleaned_png, svg_file, out_png, out_pdf))
        if outputs_exist and not OVERWRITE:
            logging.info(f"Skipping {src_file.name} (already processed)")
            continue

        try:
            # clean_png now accepts the mode and invert arguments
            clean_png(magick, src_file, cleaned_png, mode=MODE, invert_mode=INVERT)
            trace_svg(cleaned_png, svg_file)
            export_png(inkscape, svg_file, out_png)
            export_pdf(inkscape, svg_file, out_pdf)
        except Exception as e:
            logging.error(f"Failed processing {src_file.name}: {e}")

    logging.info("Pipeline complete")

if __name__ == "__main__":
    main()