"""Build script for compiling stdlib and example files to HAKAI bytecode."""

import os
import sys

# Ensure root is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from compiler.compiler import Compiler


def build_all():
    compiler = Compiler()
    print("Building HAKAI standard libraries and examples...")

    targets = [
        os.path.join(root_dir, "examples", "hello.hakai"),
        os.path.join(root_dir, "examples", "variables.hakai"),
        os.path.join(root_dir, "examples", "conditions.hakai"),
        os.path.join(root_dir, "examples", "loops.hakai"),
        os.path.join(root_dir, "examples", "functions.hakai"),
        os.path.join(root_dir, "examples", "classes.hakai"),
        os.path.join(root_dir, "examples", "collections.hakai"),
        os.path.join(root_dir, "examples", "modules.hakai"),
    ]

    for target in targets:
        if os.path.isfile(target):
            out_path = compiler.compile_to_file(target)
            print(f"  [OK] Built: {os.path.relpath(out_path, root_dir)}")

    print("\nAll HAKAI bytecode targets built successfully.")


if __name__ == "__main__":
    build_all()

