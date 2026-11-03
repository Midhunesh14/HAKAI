"""Tests for HPM (HAKAI Package Manager)."""

import os
import tempfile
from package_manager.package import PackageMetadata
from package_manager.installer import PackageInstaller
from package_manager.cli import main as hpm_main


def test_package_metadata_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        toml_path = os.path.join(tmpdir, "hakai.toml")
        meta = PackageMetadata(
            name="demo-pkg",
            version="1.2.3",
            description="Testing HPM package",
            dependencies={"math_extra": "1.0.0"},
        )
        meta.save(toml_path)

        loaded = PackageMetadata.from_toml_file(toml_path)
        assert loaded.name == "demo-pkg"
        assert loaded.version == "1.2.3"
        assert loaded.dependencies.get("math_extra") == "1.0.0"


def test_package_installer_workflow():
    with tempfile.TemporaryDirectory() as workspace:
        # Create a sample library package
        lib_dir = os.path.join(workspace, "my_math")
        os.makedirs(lib_dir, exist_ok=True)
        lib_meta = PackageMetadata(
            name="my_math",
            version="0.1.0",
            entry="math_helper.hakai",
        )
        lib_meta.save(os.path.join(lib_dir, "hakai.toml"))
        with open(os.path.join(lib_dir, "math_helper.hakai"), "w", encoding="utf-8") as f:
            f.write("function square(x) { return x * x }\n")

        # Create consumer application
        app_dir = os.path.join(workspace, "my_app")
        os.makedirs(app_dir, exist_ok=True)

        installer = PackageInstaller(project_dir=app_dir)
        installer.init_project("my_app")
        assert os.path.exists(os.path.join(app_dir, "hakai.toml"))

        # Install local package
        installer.install(package_source=lib_dir)

        # Verify installed files and lockfile
        installed = installer.list_installed()
        assert "my_math" in installed
        assert os.path.exists(installer.lockfile_path)
        assert os.path.exists(os.path.join(app_dir, ".hakai_packages", "my_math", "math_helper.hakai"))

        # Test uninstall
        installer.uninstall("my_math")
        installed_after = installer.list_installed()
        assert "my_math" not in installed_after
        assert not os.path.exists(os.path.join(app_dir, ".hakai_packages", "my_math"))
