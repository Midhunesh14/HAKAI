"""Console and output widget for HAKAI Studio."""

from __future__ import annotations

from PySide6.QtGui import QColor, QTextCursor
from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWidget


class TerminalWidget(QWidget):
    """Execution output, errors, and terminal console."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

    def write_output(self, text: str, is_error: bool = False) -> None:
        color = "#ff5252" if is_error else "#00e676"
        self.text_area.setTextColor(QColor(color))
        self.text_area.append(text)
        self.text_area.moveCursor(QTextCursor.End)

    def write_info(self, text: str) -> None:
        self.text_area.setTextColor(QColor("#4fc3f7"))
        self.text_area.append(text)
        self.text_area.moveCursor(QTextCursor.End)

    def clear(self) -> None:
        self.text_area.clear()

