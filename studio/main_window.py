"""Main Window for HAKAI Studio Desktop IDE."""

from __future__ import annotations

import os
from typing import Dict, Optional
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from studio.editor import CodeEditor
from studio.file_explorer import FileExplorer
from studio.terminal_widget import TerminalWidget
from studio.debugger import ExecutionController
from studio.theme import DARK_THEME_QSS


class StudioMainWindow(QMainWindow):
    """The main desktop IDE window for HAKAI Studio."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("HAKAI Studio 1.0.0")
        self.resize(1200, 800)
        self.setStyleSheet(DARK_THEME_QSS)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self._close_tab)

        self.open_files: Dict[int, str] = {}  # tab_index -> file_path

        self.terminal = TerminalWidget()
        self.file_explorer = FileExplorer(root_dir=os.getcwd())
        self.file_explorer.file_selected.connect(self.open_file)

        self._build_ui()
        self._build_menus()
        self._build_toolbar()

        # Open empty document with template
        self.new_file()

    def _build_ui(self) -> None:
        # Central Horizontal Splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(self.file_explorer)

        # Right Vertical Splitter (Editor on top, Terminal below)
        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(self.tab_widget)
        right_splitter.addWidget(self.terminal)
        right_splitter.setStretchFactor(0, 3)
        right_splitter.setStretchFactor(1, 1)

        main_splitter.addWidget(right_splitter)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 4)

        self.setCentralWidget(main_splitter)
        self.statusBar().showMessage("Ready")

    def _build_menus(self) -> None:
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")
        new_act = QAction("&New File", self)
        new_act.setShortcut("Ctrl+N")
        new_act.triggered.connect(self.new_file)
        file_menu.addAction(new_act)

        open_act = QAction("&Open File...", self)
        open_act.setShortcut("Ctrl+O")
        open_act.triggered.connect(self._open_file_dialog)
        file_menu.addAction(open_act)

        save_act = QAction("&Save", self)
        save_act.setShortcut("Ctrl+S")
        save_act.triggered.connect(self.save_file)
        file_menu.addAction(save_act)

        file_menu.addSeparator()
        exit_act = QAction("E&xit", self)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        # Run Menu
        run_menu = menubar.addMenu("&Run")
        run_act = QAction("&Run Program (Interpreter)", self)
        run_act.setShortcut("F5")
        run_act.triggered.connect(self.run_program)
        run_menu.addAction(run_act)

        build_act = QAction("&Build Bytecode (.hbc)", self)
        build_act.setShortcut("F7")
        build_act.triggered.connect(self.build_program)
        run_menu.addAction(build_act)

        # Help Menu
        help_menu = menubar.addMenu("&Help")
        about_act = QAction("&About HAKAI", self)
        about_act.triggered.connect(self._show_about)
        help_menu.addAction(about_act)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        toolbar.addAction("New", self.new_file)
        toolbar.addAction("Open", self._open_file_dialog)
        toolbar.addAction("Save", self.save_file)
        toolbar.addSeparator()
        toolbar.addAction("▶ Run (F5)", self.run_program)
        toolbar.addAction("🔨 Build (F7)", self.build_program)
        toolbar.addSeparator()
        toolbar.addAction("Clear Output", self.terminal.clear)

    def new_file(self) -> None:
        editor = CodeEditor()
        template = (
            "HAKAI START\n\n"
            "// Welcome to HAKAI Studio!\n"
            'let greeting = "Hello, World!"\n'
            "print(greeting)\n\n"
            "HAKAI END\n"
        )
        editor.setPlainText(template)
        idx = self.tab_widget.addTab(editor, "untitled.hakai")
        self.tab_widget.setCurrentIndex(idx)

    def _open_file_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open HAKAI File", "", "HAKAI Files (*.hakai *.hbc);;All Files (*)"
        )
        if path:
            self.open_file(path)

    def open_file(self, path: str) -> None:
        # Check if already open
        for idx, open_path in self.open_files.items():
            if os.path.abspath(open_path) == os.path.abspath(path):
                self.tab_widget.setCurrentIndex(idx)
                return

        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        editor = CodeEditor()
        editor.setPlainText(content)
        title = os.path.basename(path)
        idx = self.tab_widget.addTab(editor, title)
        self.open_files[idx] = path
        self.tab_widget.setCurrentIndex(idx)
        self.statusBar().showMessage(f"Opened {path}")

    def save_file(self) -> None:
        current_idx = self.tab_widget.currentIndex()
        if current_idx == -1:
            return

        editor: CodeEditor = self.tab_widget.currentWidget()
        path = self.open_files.get(current_idx)

        if not path:
            path, _ = QFileDialog.getSaveFileName(
                self, "Save HAKAI File", "", "HAKAI Files (*.hakai);;All Files (*)"
            )
            if not path:
                return
            self.open_files[current_idx] = path
            self.tab_widget.setTabText(current_idx, os.path.basename(path))

        with open(path, "w", encoding="utf-8") as f:
            f.write(editor.toPlainText())

        self.statusBar().showMessage(f"Saved {path}")

    def _close_tab(self, index: int) -> None:
        self.tab_widget.removeTab(index)
        if index in self.open_files:
            del self.open_files[index]

    def run_program(self) -> None:
        editor: Optional[CodeEditor] = self.tab_widget.currentWidget()
        if not editor:
            return

        source = editor.toPlainText()
        self.terminal.write_info("--- Running HAKAI Program ---")
        output, error = ExecutionController.run_source(source)
        if output:
            self.terminal.write_output(output.rstrip())
        if error:
            self.terminal.write_output(error, is_error=True)
            self.statusBar().showMessage("Execution failed with errors.")
        else:
            self.statusBar().showMessage("Execution completed successfully.")

    def build_program(self) -> None:
        editor: Optional[CodeEditor] = self.tab_widget.currentWidget()
        if not editor:
            return

        source = editor.toPlainText()
        self.terminal.write_info("--- Compiling to HAKAI Bytecode ---")
        bytecode, error = ExecutionController.compile_source(source)
        if error:
            self.terminal.write_output(error, is_error=True)
            self.statusBar().showMessage("Compilation failed.")
        else:
            self.terminal.write_info(f"Bytecode generation successful ({len(bytecode)} bytes).")
            # Verify execution on VM
            vm_out, vm_err = ExecutionController.run_bytecode(bytecode)
            if vm_out:
                self.terminal.write_output(f"[VM Output]\n{vm_out.rstrip()}")
            if vm_err:
                self.terminal.write_output(f"[VM Error] {vm_err}", is_error=True)
            self.statusBar().showMessage("Bytecode compiled and verified on HVM.")

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "About HAKAI Studio",
            "HAKAI Studio v1.0.0\n\n"
            "An independent development environment for the HAKAI programming language.\n"
            "Built with PySide6.",
        )

