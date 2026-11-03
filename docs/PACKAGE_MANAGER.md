# HPM: HAKAI Package Manager

HPM manages dependencies and packages for HAKAI applications.

## Manifest: `hakai.toml`
```toml
[package]
name = "my_app"
version = "1.0.0"
description = "Sample HAKAI Project"
entry = "main.hakai"

[dependencies]
math_extra = "1.0.0"
```

## Commands
- `hpm init`: Initialize a new `hakai.toml` in the current directory.
- `hpm install <package>`: Install a package from local path or configured directory.
- `hpm install`: Install all dependencies defined in `hakai.toml`.
- `hpm uninstall <package>`: Remove a package from dependencies.
- `hpm list`: List installed packages.
- `hpm info <package>`: Display package metadata.
- `hpm search <query>`: Search available packages.
