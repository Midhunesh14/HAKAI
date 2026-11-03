"""Setup script for HAKAI 1.0."""

from setuptools import setup, find_packages

setup(
    name="hakai-lang",
    version="1.0.0",
    description="The HAKAI Programming Language - Independent compiler, interpreter, VM, IDE, and package manager.",
    author="HAKAI Architecture Team",
    packages=find_packages(),
    install_requires=[
        "PySide6>=6.6.0",
        "pytest>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "hakai = cli.commands:main",
            "hpm = package_manager.cli:main",
        ],
    },
    python_requires=">=3.10",
)
