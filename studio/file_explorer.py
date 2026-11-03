"""Project file tree explorer for HAKAI Studio."""

from __future__ import annotations

import os
from PySide6.QtCore import QDir, Signal
from PySide6.QtWidgets import QFileSystemModel, QTreeView, QVBoxLayout, QWidget


class FileExplorer(QWidget):
    """File explorer panel for navigating project files."""

    file_selected = Signal(str)

    def __init__(self, root_dir: str = ".", parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.model = QFileSystemModel()
        self.model.setRootPath(root_dir)
        self.model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(root_dir))
        self.tree.setColumnHidden(1, True)  # Size
        self.tree.setColumnHidden(2, True)  # Type
        self.tree.setColumnHidden(3, True)  # Date modified
        self.tree.setHeaderHidden(True)
        self.tree.doubleClicked.connect(self._on_item_double_clicked)

        layout.addWidget(self.tree)

    def _on_item_double_clicked(self, index) -> None:
        path = self.model.filePath(index)
        if os.path.isfile(path):
            self.file_selected.emit(path)

    def set_root_path(self, path: str) -> None:
        self.model.setRootPath(path)
        self.tree.setRootIndex(self.model.index(path))

