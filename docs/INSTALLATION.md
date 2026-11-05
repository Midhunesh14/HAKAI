# HAKAI Installation and Distribution Guide

This guide covers installing and running the **HAKAI** programming language (v1.0.0) across Windows, Linux, and macOS.

HAKAI is distributed through two primary channels:
1. **Python Package Distribution (`hakai-lang`)**: Lightweight pip packages for systems with Python 3.10+.
2. **Standalone Public Installers**: Precompiled self-contained executables and bundles that require **no Python installation**.

---

## 1. Python Package Distribution (PyPI)

### Quick Install with pip

The core HAKAI distribution includes the compiler, recursive-descent parser, AST optimizer, tree-walk interpreter, HAKAI Virtual Machine (`HVM`), `.hbc` bytecode engine, HAKAI Package Manager (`HPM`), and standard library.

```bash
# Install core HAKAI compiler, VM, and HPM CLI
pip install hakai-lang
```

### Installing HAKAI Studio (Desktop IDE)

To keep the core package lightweight (~35 KB wheel), GUI dependencies (PySide6 / Qt6) are optional. To include HAKAI Studio desktop IDE:

```bash
# Install core HAKAI + HAKAI Studio GUI IDE
pip install "hakai-lang[studio]"
```

### Development Extra

To install development and testing tools (pytest, build, twine, pyinstaller):

```bash
pip install "hakai-lang[dev]"
```

---

## 2. Standalone Public Installers (No Python Required)

Pre-built standalone releases for 64-bit systems are available from the GitHub Releases page:
[https://github.com/Midhunesh14/HAKAI/releases](https://github.com/Midhunesh14/HAKAI/releases)

### Windows 10 / 11 (64-bit)

#### Option A: One-Click Installer (`HAKAI-1.0.0-Windows-Installer.bat`)
1. Download `HAKAI-1.0.0-Windows-x64-Portable.zip` and `HAKAI-1.0.0-Windows-Installer.bat` from GitHub Releases into the same folder.
2. Double-click `HAKAI-1.0.0-Windows-Installer.bat` (or run it in Command Prompt / PowerShell).
3. The installer extracts HAKAI to `%LOCALAPPDATA%\HAKAI` and adds the directory to your user `PATH`.
4. Open a new terminal window and run `hakai --version`.

#### Option B: Portable ZIP (`HAKAI-1.0.0-Windows-x64-Portable.zip`)
1. Download and extract `HAKAI-1.0.0-Windows-x64-Portable.zip` to your preferred folder (e.g., `C:\Program Files\HAKAI` or `C:\HAKAI`).
2. The archive includes:
   - `hakai.exe` (Compiler, VM, REPL, CLI)
   - `hpm.exe` (HAKAI Package Manager)
   - `stdlib/` (Standard library modules: `math.hakai`, `strings.hakai`, `collections.hakai`, etc.)
   - `examples/` (Sample programs)
3. Add the extracted directory to your Windows `PATH` environment variable.

#### Option C: Standalone HAKAI Studio (`HAKAI-Studio-1.0.0-Windows-x64.zip`)
1. Download and extract `HAKAI-Studio-1.0.0-Windows-x64.zip`.
2. Run `hakai-studio.exe` to launch the full graphical IDE directly.

---

### Linux (64-bit x86_64)

#### Portable Binary Bundle
1. Download `HAKAI-1.0.0-Linux-x64.tar.gz` from GitHub Releases.
2. Extract the archive:
   ```bash
   tar -xzf HAKAI-1.0.0-Linux-x64.tar.gz
   cd HAKAI-1.0.0-Linux-x64
   ```
3. Move binaries to `/usr/local/bin` (or `~/.local/bin`):
   ```bash
   sudo cp bin/hakai bin/hpm /usr/local/bin/
   sudo chmod +x /usr/local/bin/hakai /usr/local/bin/hpm
   ```
4. Verify:
   ```bash
   hakai --version
   hpm --version
   ```

---

### macOS (Intel & Apple Silicon)

1. Download `HAKAI-1.0.0-macOS-universal.tar.gz` from GitHub Releases.
2. Extract the archive:
   ```bash
   tar -xzf HAKAI-1.0.0-macOS-universal.tar.gz
   cd HAKAI-1.0.0-macOS
   ```
3. Install to `/usr/local/bin` or `~/.local/bin`:
   ```bash
   cp bin/hakai bin/hpm ~/.local/bin/
   chmod +x ~/.local/bin/hakai ~/.local/bin/hpm
   ```
4. On macOS Gatekeeper prompt for downloaded binaries:
   ```bash
   xattr -d com.apple.quarantine ~/.local/bin/hakai ~/.local/bin/hpm
   ```

---

## 3. Verifying Installation

Verify that `hakai` and `hpm` are available on your system path:

```bash
# Verify HAKAI language toolchain
hakai --version
# Expected: HAKAI Programming Language v1.0.0

# Verify HAKAI Package Manager
hpm --version
# Expected: HAKAI Package Manager (HPM) v1.0.0
```

### Run a Test Script

Create `test.hakai`:
```hakai
HAKAI START

import math
import strings

let greeting = "Welcome to HAKAI 1.0.0!"
print(strings.upper(greeting))
print("Pi approx: " + str(math.PI))

HAKAI END
```

Execute with the AST interpreter:
```bash
hakai run test.hakai
```

Compile to `.hbc` bytecode and run on the HAKAI Virtual Machine (HVM):
```bash
hakai build test.hakai
hakai run test.hbc
```

---

## 4. CLI Command Reference

### `hakai` Command Line Interface

| Command | Usage | Description |
| :--- | :--- | :--- |
| `hakai run <file.hakai>` | `hakai run script.hakai` | Execute source file using the AST interpreter |
| `hakai build <file.hakai>` | `hakai build script.hakai` | Compile source file into `.hbc` bytecode |
| `hakai run <file.hbc>` | `hakai run script.hbc` | Execute compiled bytecode on HAKAI Virtual Machine |
| `hakai check <file.hakai>` | `hakai check script.hakai` | Perform static syntax and semantic validation |
| `hakai repl` | `hakai repl` | Start interactive Read-Eval-Print-Loop |
| `hakai studio` | `hakai studio` | Launch HAKAI Studio IDE (requires `hakai-lang[studio]`) |
| `hakai --version` / `-v` | `hakai -v` | Display version information |
| `hakai --help` / `-h` | `hakai --help` | Display command-line options and usage help |

### `hpm` Package Manager Interface

| Command | Usage | Description |
| :--- | :--- | :--- |
| `hpm init [name]` | `hpm init my_pkg` | Create a new `hakai.toml` project manifest |
| `hpm install` | `hpm install` | Install dependencies from `hakai.toml` |
| `hpm install <name>` | `hpm install pkg` | Install a specific package |
| `hpm uninstall <name>` | `hpm uninstall pkg` | Remove an installed package |
| `hpm list` | `hpm list` | List installed packages in current project |
| `hpm info <name>` | `hpm info pkg` | Show detailed package metadata |
| `hpm search <query>` | `hpm search math` | Search package repository |
| `hpm update` | `hpm update` | Update installed project packages |

---

## 5. Building and Installing from Source

If you clone the repository directly from GitHub:

```bash
git clone https://github.com/Midhunesh14/HAKAI.git
cd HAKAI

# Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install in editable mode with development & IDE extras
pip install -e ".[dev,studio]"

# Run tests
python -m pytest tests/ -v
```

### Building Distribution Wheels Locally

```bash
# Build wheel and sdist
python -m build

# Validate package distribution files
python -m twine check dist/*
```

---

## 6. Verifying SHA256 Checksums

Every release includes a `SHA256SUMS.txt` file. Verify downloaded archives before installation:

### Windows (PowerShell)
```powershell
Get-FileHash -Algorithm SHA256 HAKAI-1.0.0-Windows-x64-Portable.zip
```

### Linux / macOS
```bash
sha256sum -c SHA256SUMS.txt
```

---

## 7. Troubleshooting & PATH Configuration

### Issue: `'hakai' is not recognized as an internal or external command`

- **Python pip installation**:
  - Ensure the Python `Scripts` directory is in your user `PATH`.
  - Windows: `%USERPROFILE%\AppData\Local\Programs\Python\Python310\Scripts` (adjust for your Python version)
  - Linux/macOS: `~/.local/bin`
- **Standalone installation**:
  - Verify that the directory where `hakai.exe` was extracted is included in your system or user `PATH`.

### Issue: `HAKAI Studio requires PySide6 GUI libraries`

- The lightweight core package does not bundle PySide6. Install the studio extra:
  ```bash
  pip install "hakai-lang[studio]"
  ```
- Alternatively, download the standalone `HAKAI-Studio-1.0.0-Windows-x64.zip` which bundles all Qt dependencies.

### Uninstallation

- **Pip package**:
  ```bash
  pip uninstall hakai-lang
  ```
- **Standalone installer (Windows)**:
  - Delete `%LOCALAPPDATA%\HAKAI`
  - Remove `%LOCALAPPDATA%\HAKAI` from your user `PATH` environment variable.
- **Standalone binaries (Linux/macOS)**:
  ```bash
  sudo rm -f /usr/local/bin/hakai /usr/local/bin/hpm
  ```
