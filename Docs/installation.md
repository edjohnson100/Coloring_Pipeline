# Coloring Pipeline Installation and Prerequisites

This document provides detailed instructions for installing and configuring all necessary dependencies for the Coloring Pipeline on **Windows**, **macOS**, and **Linux**, including optional Python virtual environment setup (venv) and one-click wrappers.

---

## Prerequisites

The pipeline requires the following software:

1. **Python 3.x**
2. **ImageMagick** (with command-line tools and delegates for PNG)
3. **Inkscape** (version 1.2+ recommended)
4. **Potrace** (New tracing engine)

All dependencies must be available in your system `PATH`.

---

## Windows Installation

### Python 3.x
1. Download from [python.org](https://www.python.org/downloads/windows/)
2. During installation, ensure **"Add Python to PATH"** is checked.
3. Verify installation:
```powershell
python --version
```

### ImageMagick
1. Download the Windows installer from [ImageMagick Downloads](https://imagemagick.org/script/download.php#windows)
2. Choose the **dynamic release** that includes `Install legacy utilities (e.g., convert)`
3. During installation, check **"Add to PATH"**
4. Verify delegates and path:
```powershell
magick -list format | findstr PNG
```

### Potrace (Required)
1. Download the **Windows (64-bit)** zip from [SourceForge Potrace Downloads](https://potrace.sourceforge.net/#downloading).
2. Extract the zip file. You will see `potrace.exe`.
3. Move the extracted folder to a permanent location (e.g., `C:\Program Files\potrace`).
4. **Add to PATH:**
   - Press the `Windows Key` and type "env". Select **"Edit the system environment variables"**.
   - Click **"Environment Variables"**.
   - Under **"System variables"**, find `Path` and click **"Edit"**.
   - Click **"New"** and paste the path to your folder (e.g., `C:\Program Files\potrace`).
   - Click OK -> OK -> OK.
5. Verify installation:
```powershell
potrace --version
```

### Inkscape
1. Download from [Inkscape Downloads](https://inkscape.org/release/)
2. Install and ensure the option **"Add to PATH"** is selected
3. Verify installation:
```powershell
inkscape --version
```

### Optional: Python Virtual Environment (venv)
1. Navigate to your project folder containing `process_coloring_pipeline.py`:
```powershell
cd G:\Path\To\coloring_pipeline
```
2. Create a venv folder:
```powershell
python -m venv venv
```
3. Activate the venv:
```powershell
.\venv\Scripts\Activate.ps1
```
4. Deactivate when done:
```powershell
deactivate
```

> Note: The provided wrapper `run_pipeline.bat` automatically activates the venv if it exists.

---

## macOS Installation

### Python 3.x
macOS 12+ comes with Python pre-installed, but we recommend using Homebrew:
```bash
/bin/bash -c "$(curl -fsSL [https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh](https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh))"
brew install python
python3 --version
```

### ImageMagick
```bash
brew install imagemagick
magick -list format | grep PNG
```

### Potrace (Required)
```bash
brew install potrace
potrace --version
```

### Inkscape
```bash
brew install --cask inkscape
inkscape --version
```

### Optional: Python Virtual Environment (venv)
```bash
cd /path/to/coloring_pipeline
python3 -m venv venv
source venv/bin/activate
# Deactivate after use
deactivate
```
> Note: The shell script wrapper `run_pipeline.sh` will automatically activate the venv if it exists.

### Make the Wrapper Executable
```bash
chmod +x run_pipeline.sh
```
This step is required once so the shell script can be run by double-clicking or from Terminal.

---

## Linux Installation (Debian/Ubuntu)

### Python 3.x
```bash
sudo apt update
sudo apt install python3 python3-pip
python3 --version
```

### ImageMagick
```bash
sudo apt install imagemagick
magick -list format | grep PNG
```

### Potrace (Required)
```bash
sudo apt install potrace
potrace --version
```

### Inkscape
```bash
sudo apt install inkscape
inkscape --version
```

### Optional: Python Virtual Environment (venv)
```bash
cd /path/to/coloring_pipeline
python3 -m venv venv
source venv/bin/activate
# Deactivate after use
deactivate
```
> Note: The shell script wrapper `run_pipeline.sh` will automatically activate the venv if it exists.

---

## PATH Verification

To confirm all tools are properly installed and available in PATH:
```bash
python --version
magick -version
potrace --version
inkscape --version
```

If any command fails, check that the installation folder is added to your system PATH and restart your terminal/command prompt.

---

This completes the installation and configuration steps. After this, the Coloring Pipeline script and optional wrappers should run without any additional setup.