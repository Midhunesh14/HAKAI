# HAKAI Packaging & Distribution Audit Report (Phase 1)

Date: 2026-11-05
Author: Senior Packaging & Compiler Infrastructure Engineer
Branch: `distribution/packaging-and-installers`

## 1. Directory Structure & Packages
- Core modules: `cli/`, `compiler/`, `interpreter/`, `package_manager/`, `virtual_machine/`, `studio/`.
- Standard library: `stdlib/` contains `.hakai` files (`collections.hakai`, `files.hakai`, `io.hakai`, `math.hakai`, `strings.hakai`, `system.hakai`) but lacked `__init__.py` and was not configured as a packaged resource.
- Executable entry points: `main.py`, `hakai.bat`, `hpm.bat`.

## 2. Dependencies & Separation of Concerns
- **Core CLI & Compiler**: Completely self-contained standard Python 3.10+ (`dataclasses`, `enum`, `typing`, `json`, etc.). Does NOT require GUI libraries.
- **PySide6**: Currently declared as a mandatory dependency in `pyproject.toml`. This inflates package installation from ~1MB to ~250MB.
- **Audit Action**: Move `PySide6` to `[project.optional-dependencies] -> studio = ["PySide6>=6.6.0"]`. CLI, compiler, VM, and HPM become ultra-lightweight.

## 3. Standard Library Resource Resolution
- **Issue**: `RuntimeContext.load_module` only checked `current_dir`. If executed from another working directory or when installed via pip into `site-packages`, standard library `.hakai` files could not be located.
- **Audit Action**:
  1. Add `stdlib/__init__.py`.
  2. Configure setuptools `package_data` for `stdlib = ["*.hakai"]`.
  3. Update `RuntimeContext` with multi-tier resolution:
     - Check in-memory builtins.
     - Check active script directory / `current_dir`.
     - Check `HAKAI_STDLIB_PATH` environment variable.
     - Check `sys._MEIPASS` (PyInstaller frozen mode).
     - Check `importlib.resources.files("stdlib")` (wheel / site-packages mode).
     - Check local project repository root.

## 4. CLI Usability & Compatibility
- `hakai --version` / `hakai -v` currently raises `unrecognized arguments: --version` because only the subcommand `hakai version` was registered.
- `cmd_studio()` will crash with raw `ModuleNotFoundError` if `PySide6` is not installed.
- `cmd_new` instructed users to run `python main.py run main.hakai` instead of `hakai run main.hakai`.
- **Audit Action**:
  1. Add `--version` / `-v` to root `argparse.ArgumentParser` in `cli/commands.py` and `package_manager/cli.py`.
  2. Gracefully catch `ImportError` in `cmd_studio` and prompt: `pip install "hakai-lang[studio]"`.
  3. Modernize project generation templates.

## 5. Build, Test & CI/CD Tooling
- Missing `.github/workflows/ci.yml` for multi-OS CI testing (Windows, Ubuntu, macOS, Python 3.10-3.13).
- Missing `.github/workflows/release.yml` with PyPI Trusted Publishing and cross-platform standalone executable artifacts.
- Missing PyInstaller build specifications for creating standalone executables.

