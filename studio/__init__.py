"""HAKAI Studio Desktop IDE Package."""

import sys
from PySide6.QtWidgets import QApplication
from studio.main_window import StudioMainWindow


def launch_studio() -> int:
    """Launch the HAKAI Studio PySide6 GUI desktop application."""
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    window = StudioMainWindow()
    window.show()
    return app.exec()


__all__ = ["launch_studio", "StudioMainWindow"]
