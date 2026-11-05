"""Command implementations and routing for HAKAI CLI."""

from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional
from compiler.compiler import Compiler
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic_analyzer import SemanticAnalyzer
from compiler.errors import HakaiError
from interpreter.interpreter import Interpreter
from interpreter.runtime import RuntimeContext
from interpreter.values import hakai_to_str
from virtual_machine.vm import VirtualMachine
from cli.terminal import BANNER, print_banner, print_error, print_info, print_success


VERSION = "1.0.0"


def cmd_version() -> int:
    print(f"HAKAI Programming Language v{VERSION}")
    print("Toolchain components:")
    print("  * Frontend: Lexer & Recursive-Descent Parser")
    print("  * AST Interpreter & Scoped Runtime")
    print("  * Bytecode Compiler & Optimizer")
    print("  * Stack-based Virtual Machine (HVM)")
    print("  * HAKAI Studio Desktop IDE (PySide6)")
    print("  * HPM Package Manager")
    return 0


def cmd_run(filepath: str) -> int:
    if not os.path.isfile(filepath):
        print_error(f"File not found: {filepath}")
        return 1

    _, ext = os.path.splitext(filepath)

    if ext == ".hbc":
        # Execute bytecode via Virtual Machine
        try:
            vm = VirtualMachine()
            vm.run_file(filepath)
            return 0
        except HakaiError as err:
            print(err.format(), file=sys.stderr)
            return 1
        except Exception as e:
            print_error(f"VM Execution error: {e}")
            return 1

    # Execute source via Interpreter
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()

        base_dir = os.path.dirname(os.path.abspath(filepath))
        ctx = RuntimeContext()
        tokens = Lexer(code, filename=filepath).tokenize()
        program = Parser(tokens, source_code=code).parse()
        interp = Interpreter(runtime_context=ctx, base_dir=base_dir)
        interp.interpret(program)
        return 0
    except HakaiError as err:
        print(err.format(), file=sys.stderr)
        return 1
    except Exception as e:
        print_error(f"Runtime error: {e}")
        return 1


def cmd_build(filepath: str, output: Optional[str] = None) -> int:
    if not os.path.isfile(filepath):
        print_error(f"Source file not found: {filepath}")
        return 1

    try:
        compiler = Compiler()
        out_file = compiler.compile_to_file(filepath, output_path=output)
        print_success(f"Compiled successfully -> {out_file}")
        return 0
    except HakaiError as err:
        print(err.format(), file=sys.stderr)
        return 1
    except Exception as e:
        print_error(f"Compilation error: {e}")
        return 1


def cmd_check(filepath: str) -> int:
    if not os.path.isfile(filepath):
        print_error(f"File not found: {filepath}")
        return 1

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()

        tokens = Lexer(code, filename=filepath).tokenize()
        ast = Parser(tokens, source_code=code).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        print_success(f"Check passed: {filepath} syntax and semantics are valid.")
        return 0
    except HakaiError as err:
        print(err.format(), file=sys.stderr)
        return 1


def cmd_repl() -> int:
    print_banner()
    print("Type 'exit' to quit, 'help' for quick reference.\n")

    interp = Interpreter()
    prompt = ">>> "

    while True:
        try:
            line = input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting HAKAI REPL.")
            break

        if not line:
            continue
        if line == "exit":
            break
        if line == "help":
            print("Enter expressions or statements (e.g. 'let x = 10', 'x + 20', 'print(x)')")
            continue

        try:
            tokens = Lexer(line, filename="<repl>").tokenize()
            program = Parser(tokens, source_code=line).parse()
            result = interp.interpret(program)
            # If the single statement was an expression, show its value
            if result is not None:
                print(hakai_to_str(result))
        except HakaiError as err:
            print(err.format(), file=sys.stderr)
        except Exception as e:
            print_error(f"Error: {e}")

    return 0


def cmd_new(project_name: str) -> int:
    if os.path.exists(project_name):
        print_error(f"Directory '{project_name}' already exists.")
        return 1

    os.makedirs(project_name, exist_ok=True)
    src_file = os.path.join(project_name, "main.hakai")
    with open(src_file, "w", encoding="utf-8") as f:
        f.write(
            "HAKAI START\n\n"
            f'// {project_name} application\n'
            f'print("Hello from {project_name}!")\n\n'
            "HAKAI END\n"
        )

    from package_manager.installer import PackageInstaller
    installer = PackageInstaller(project_dir=project_name)
    installer.init_project(project_name)

    print_success(f"Created new HAKAI project '{project_name}'.")
    print_info(f"To run your project:\n  cd {project_name}\n  hakai run main.hakai")
    return 0


def cmd_format(filepath: str) -> int:
    if not os.path.isfile(filepath):
        print_error(f"File not found: {filepath}")
        return 1

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    formatted_lines = []
    indent_level = 0
    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            formatted_lines.append("\n")
            continue

        if stripped.startswith("}"):
            indent_level = max(0, indent_level - 1)

        formatted_lines.append("    " * indent_level + stripped + "\n")

        if stripped.endswith("{"):
            indent_level += 1

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(formatted_lines)

    print_success(f"Formatted: {filepath}")
    return 0


def cmd_studio() -> int:
    try:
        from studio import launch_studio
        return launch_studio()
    except ImportError:
        print_error(
            "HAKAI Studio requires PySide6 GUI libraries.\n"
            "Install HAKAI with Studio support via:\n"
            "  pip install \"hakai-lang[studio]\""
        )
        return 1


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hakai",
        description="The HAKAI Programming Language Toolchain",
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"HAKAI Programming Language v{VERSION}",
        help="Print HAKAI toolchain version",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="HAKAI commands")

    # version
    subparsers.add_parser("version", help="Print HAKAI toolchain version")

    # run
    run_p = subparsers.add_parser("run", help="Execute a .hakai source file or .hbc bytecode file")
    run_p.add_argument("file", help="File to run")

    # build
    build_p = subparsers.add_parser("build", help="Compile .hakai file into .hbc bytecode")
    build_p.add_argument("file", help="Source file")
    build_p.add_argument("-o", "--output", default=None, help="Output bytecode path")

    # check
    check_p = subparsers.add_parser("check", help="Statically check syntax and semantics")
    check_p.add_argument("file", help="File to check")

    # repl
    subparsers.add_parser("repl", help="Launch interactive REPL")

    # new
    new_p = subparsers.add_parser("new", help="Create a new HAKAI project")
    new_p.add_argument("project_name", help="Project folder name")

    # format
    format_p = subparsers.add_parser("format", help="Format a .hakai file")
    format_p.add_argument("file", help="File to format")

    # studio
    subparsers.add_parser("studio", help="Launch HAKAI Studio desktop IDE")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_cli_parser()
    args = parser.parse_args(argv)

    if not args.subcommand:
        parser.print_help()
        return 0

    if args.subcommand == "version":
        return cmd_version()
    elif args.subcommand == "run":
        return cmd_run(args.file)
    elif args.subcommand == "build":
        return cmd_build(args.file, args.output)
    elif args.subcommand == "check":
        return cmd_check(args.file)
    elif args.subcommand == "repl":
        return cmd_repl()
    elif args.subcommand == "new":
        return cmd_new(args.project_name)
    elif args.subcommand == "format":
        return cmd_format(args.file)
    elif args.subcommand == "studio":
        return cmd_studio()

    return 0

