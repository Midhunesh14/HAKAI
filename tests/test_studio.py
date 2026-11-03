"""Tests for HAKAI Studio IDE components."""

import os
import pytest

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from studio.debugger import ExecutionController
from studio.editor import CodeEditor
from studio.syntax_highlighter import HakaiSyntaxHighlighter
from studio.main_window import StudioMainWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app


def test_execution_controller_run():
    source = 'print("Hello Studio")'
    out, err = ExecutionController.run_source(source)
    assert out.strip() == "Hello Studio"
    assert err is None


def test_execution_controller_compile_and_vm():
    source = 'let x = 100\nprint(x * 2)'
    bc, err = ExecutionController.compile_source(source)
    assert err is None
    assert bc is not None

    vm_out, vm_err = ExecutionController.run_bytecode(bc)
    assert vm_err is None
    assert vm_out.strip() == "200"


def test_studio_widgets(qapp):
    editor = CodeEditor()
    editor.setPlainText('let s = "HAKAI"')
    assert "HAKAI" in editor.toPlainText()

    # Test main window instantiation
    window = StudioMainWindow()
    assert "HAKAI Studio" in window.windowTitle()
    assert window.tab_widget.count() >= 1
    window.close()

