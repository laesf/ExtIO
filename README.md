<div align="center">

<br/>

```
  ⬡  ExtIO
```

# ExtIO

**A modern, dark-themed desktop GUI for extracting compressed archives.**  
Built with Python and Tkinter. No Electron. No bloat. Just Python.

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B_recommended-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Python Min](https://img.shields.io/badge/Python-3.7%2B_minimum-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)]()
[![GUI](https://img.shields.io/badge/GUI-Tkinter-orange?style=flat-square)]()

<br/>

</div>

---

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Supported Formats](#supported-formats)
- [Interface Guide](#interface-guide)
  - [Header — Status Badges](#header--status-badges)
  - [Archive Selection](#archive-selection)
  - [Destination Folder](#destination-folder)
  - [Preview Button](#preview-button)
  - [Extract Button](#extract-button)
  - [Progress Bar & Status Bar](#progress-bar--status-bar)
- [Troubleshooting](#troubleshooting)
- [Platform Notes](#platform-notes)
- [Project Structure](#project-structure)

---

## Overview

**ExtIO** is a lightweight, self-contained desktop application for decompressing archive files. It provides a clean dark-themed interface with real-time extraction progress, archive content preview, and automatic dependency detection — all without any external frameworks or GUI toolkits beyond Python's standard library.

The application is designed to be portable: a single `.py` file that runs directly on any machine with Python installed.

---

## Requirements

### Python Version

| Version | Status |
|---------|--------|
| **Python 3.10+** | **Recommended** — full type hint support (`str \| None`, `list[dict]`) |
| Python 3.7 – 3.9 | Supported — requires the `typing` import patch (see [Troubleshooting](#troubleshooting)) |
| Python < 3.7 | Not supported |

> **Recommendation:** Use **Python 3.10 or later** to avoid any compatibility issues with modern type hint syntax used throughout the codebase. Python 3.12+ is also fully supported and offers improved error messages and performance.

Download the latest Python at: https://www.python.org/downloads/

### Core Dependencies (built-in — no installation needed)

These are part of Python's standard library and require **no installation**:

| Module | Purpose |
|--------|---------|
| `tkinter` | GUI framework |
| `zipfile` | ZIP archive support |
| `tarfile` | TAR / TAR.GZ / TAR.BZ2 / TAR.XZ support |
| `gzip` | GZ single-file decompression |
| `bz2` | BZ2 single-file decompression |
| `threading` | Non-blocking extraction |
| `pathlib` | Cross-platform path handling |
| `shutil` | File copy operations |

> **Linux users:** `tkinter` is often not included in the system Python. Install it with:
> ```bash
> sudo apt install python3-tk       # Debian / Ubuntu
> sudo dnf install python3-tkinter  # Fedora
> sudo pacman -S tk                  # Arch
> ```

### Optional Dependencies (extend format support)

These libraries unlock additional archive formats. They are **not required** to run the app — missing libraries are gracefully handled and clearly indicated in the [header badges](#header--status-badges).

| Library | Format | Install |
|---------|--------|---------|
| [`py7zr`](https://github.com/miurahr/py7zr) | `.7z` | `pip install py7zr` |
| [`rarfile`](https://github.com/markokr/rarfile) | `.rar` | `pip install rarfile` |

> **Note for RAR support:** `rarfile` requires the `unrar` binary to be installed on your system in addition to the Python package.
> - **Windows:** Download from https://www.rarlab.com/rar_add.htm and add to PATH
> - **macOS:** `brew install rar`
> - **Linux:** `sudo apt install unrar` or `sudo dnf install unrar`

---

## Installation

### Option A — Run directly (no installation)

```bash
# 1. Clone or download the repository
git clone https://github.com/yourusername/extio.git
cd extio

# 2. (Optional) Install extra format support
pip install py7zr rarfile

# 3. Run
python extractor.py
```

### Option B — Install in a virtual environment (recommended)

```bash
git clone https://github.com/yourusername/extio.git
cd extio

python -m venv .venv

# Activate the environment:
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

pip install -r requirements.txt

python extractor.py
```

### `requirements.txt`

```
# Core GUI (standard library — listed for documentation only)
# tkinter  <- comes with Python

# Optional — comment out if not needed
py7zr>=0.20.0
rarfile>=4.1
```

---

## Running the App

```bash
python extractor.py
```

The application window opens immediately. No configuration files, no first-run setup.

---

## Supported Formats

| Format | Extension(s) | Library | Requires install? |
|--------|-------------|---------|-------------------|
| ZIP | `.zip` | `zipfile` | ❌ Built-in |
| TAR | `.tar` | `tarfile` | ❌ Built-in |
| TAR + GZip | `.tar.gz`, `.tgz` | `tarfile` | ❌ Built-in |
| TAR + BZip2 | `.tar.bz2` | `tarfile` | ❌ Built-in |
| TAR + XZ | `.tar.xz` | `tarfile` | ❌ Built-in |
| GZip (single file) | `.gz` | `gzip` | ❌ Built-in |
| BZip2 (single file) | `.bz2` | `bz2` | ❌ Built-in |
| 7-Zip | `.7z` | `py7zr` | ✅ `pip install py7zr` |
| RAR | `.rar` | `rarfile` | ✅ `pip install rarfile` + `unrar` binary |

---

## Interface Guide

### Header — Status Badges

The top-right corner of the application header displays **three colored badges** that reflect the current state of format support at startup:

```
┌─────────────────────────────────────────────────────┐
│  ⬡  ExtIO                    [ZIP/TAR] [7Z] [RAR]  │
└─────────────────────────────────────────────────────┘
```

| Badge | Color | Meaning |
|-------|-------|---------|
| `ZIP/TAR` | 🟢 Green | Always available — built into Python's standard library |
| `7Z` | 🟢 Green | `py7zr` is installed and `.7z` extraction is available |
| `7Z` | 🔴 Red | `py7zr` is **not** installed — `.7z` files cannot be extracted |
| `RAR` | 🟢 Green | `rarfile` is installed and `.rar` extraction is available |
| `RAR` | 🔴 Red | `rarfile` is **not** installed — `.rar` files cannot be extracted |

The badges update only at **launch time**. If you install a missing library while the app is running, restart it to refresh the badge states.

To fix a red badge, install the corresponding library:

```bash
pip install py7zr      # fixes the 7Z badge
pip install rarfile    # fixes the RAR badge (also install unrar binary)
```

---

### Archive Selection

```
ARCHIVIO
┌──────────────────────────────────────┐  ┌───────────┐
│  /path/to/your/archive.zip           │  │ 📂 Sfoglia │
└──────────────────────────────────────┘  └───────────┘
```

- Click **📂 Sfoglia** to open a file picker dialog filtered by supported extensions.
- Alternatively, **type or paste a path** directly into the input field.
- When an archive is selected, the **Destination** field is **automatically populated** with a suggested folder path derived from the archive's name and parent directory (e.g., `/downloads/archive.zip` → `/downloads/archive/`).
- The content preview table is **cleared** whenever a new archive is selected, prompting you to load a fresh preview.

---

### Destination Folder

```
DESTINAZIONE
┌──────────────────────────────────────┐  ┌───────────┐
│  /path/to/output/folder              │  │ 📁 Scegli  │
└──────────────────────────────────────┘  └───────────┘
```

- Click **📁 Scegli** to open a folder picker dialog.
- You can also type any valid path manually.
- The destination folder is **created automatically** if it does not exist at extraction time.
- If left empty, the extraction will be blocked and a warning displayed in the status bar.

---

### Preview Button

```
                         [  Anteprima ]  [  ESTRAI TUTTO ]
```

The **Preview** button reads the archive's **table of contents without extracting any files**. This is useful for inspecting what an archive contains before committing to extraction.

**What happens when you click Preview:**

1. The app validates that a valid archive path has been set.
2. The archive type is detected from the file extension.
3. The content listing runs in a **background thread** so the UI remains responsive.
4. The file list is populated in the table below, showing:
   - An **icon** representing the file type (📂 for folders, 📦 for zip, 📄 for generic files, etc.)
   - The **full relative path** of each entry inside the archive.
   - The **uncompressed file size**, formatted automatically (B / KB / MB / GB).
5. A **summary line** appears above the table: `N file  •  total size`.
6. The status bar updates to confirm the number of entries loaded.

> **Note:** For `.gz` and `.bz2` single-file archives, the preview shows only the resulting filename (the archive stem), since these formats do not contain a directory structure.

**Error states:**

| Situation | Status bar message |
|-----------|-------------------|
| No archive selected | ⚠ Seleziona prima un archivio valido. |
| Extension not recognized | ⚠ Formato non riconosciuto. |
| Corrupt or unreadable archive | ❌ Errore lettura: [details] |

---

### Extract Button

```
                                          [ ⚡ ESTRAI TUTTO ]
```

The **Extract** button starts the full decompression of the selected archive into the destination folder.

**Extraction workflow:**

1. The app validates both the source archive and the destination path.
2. If the format requires an optional library (`py7zr` for `.7z`, `rarfile` for `.rar`) and that library is not installed, an **error dialog** is shown with the exact `pip install` command to fix it.
3. Extraction runs in a **background thread** — the UI stays fully responsive during the process.
4. **Progress is reported file by file**: the progress bar fills incrementally, and the status bar shows the current percentage and the name of the file being extracted.
5. On completion, the status bar displays the full path of the output folder.
6. On error, the status bar turns red and a dialog describes the failure.

**The button is disabled (no-op) while an extraction is already running** — clicking it multiple times has no effect until the current job finishes.

---

### Progress Bar & Status Bar

```
┌──────────────────────────────────────────────────────┐
│  ✔ Estrazione completata → /path/to/output     ████ │
└──────────────────────────────────────────────────────┘
```

The **footer** contains two elements:

**Status bar (left):**

| Color | Meaning |
|-------|---------|
| Grey | Idle / informational message |
| 🟣 Purple | Operation in progress |
| 🟢 Green | Success |
| 🟡 Yellow | Warning (missing input, unrecognized format) |
| 🔴 Red | Error during extraction or file reading |

**Progress bar (right):**
A slim horizontal bar that fills from left to right as each file is extracted. It resets to zero at the start of each new extraction job and reaches 100% on completion.

---

## Troubleshooting

### `TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'`

You are running **Python 3.9 or earlier**. The `str | None` union syntax for type hints requires Python 3.10+.

**Fix A — Upgrade Python (recommended):**
```bash
# Download Python 3.10+ from https://www.python.org/downloads/
python --version   # verify after install
```

**Fix B — Patch the file for older Python:**
Replace the affected type hint lines:
```python
# Before (Python 3.10+ syntax)
def detect_archive_type(path: str) -> str | None:
def list_archive(path: str) -> list[dict]:

# After (Python 3.7+ compatible)
from typing import Optional, List, Dict
def detect_archive_type(path: str) -> Optional[str]:
def list_archive(path: str) -> List[Dict]:
```

---

### `ModuleNotFoundError: No module named 'tkinter'`

Tkinter is not bundled with the system Python on some Linux distributions.

```bash
sudo apt install python3-tk       # Debian / Ubuntu / Mint
sudo dnf install python3-tkinter  # Fedora / RHEL
sudo pacman -S tk                  # Arch / Manjaro
```

---

### RAR extraction fails even with `rarfile` installed

The `rarfile` Python package is a **wrapper** — it still requires the native `unrar` binary on your system:

```bash
# macOS
brew install rar

# Debian / Ubuntu
sudo apt install unrar

# Fedora
sudo dnf install unrar

# Windows — download from https://www.rarlab.com and add to PATH
```

---

### 7Z extraction produces no output

Ensure `py7zr` is correctly installed in the **same Python environment** used to run the script:

```bash
python -m pip install py7zr
python -c "import py7zr; print(py7zr.__version__)"
```

---

## Platform Notes

| Platform | Notes |
|----------|-------|
| **Windows** | Works out of the box. Tkinter and all standard modules are included with the official Python installer from python.org. |
| **macOS** | Works out of the box with the official Python installer. The system Python bundled with Xcode may lack Tkinter — use the official installer or `brew install python-tk`. |
| **Linux** | Requires separate `python3-tk` installation (see above). All other functionality is identical. |

---

## Project Structure

```
extio/
├── extractor.py        ← Single-file application (entire app lives here)
└── README.md           ← This file
```

