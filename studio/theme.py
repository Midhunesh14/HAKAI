"""Modern dark developer theme styling for HAKAI Studio."""

DARK_THEME_QSS = """
QMainWindow {
    background-color: #1e1e24;
    color: #e0e0e0;
}

QMenuBar {
    background-color: #18181c;
    color: #cccccc;
    border-bottom: 1px solid #2d2d34;
}

QMenuBar::item:selected {
    background-color: #2d2d34;
    color: #ffffff;
}

QToolBar {
    background-color: #23232a;
    border-bottom: 1px solid #2d2d34;
    spacing: 6px;
    padding: 4px;
}

QToolButton {
    background-color: #2b2b36;
    color: #e0e0e0;
    border: 1px solid #3c3c4a;
    border-radius: 4px;
    padding: 5px 12px;
    font-weight: bold;
}

QToolButton:hover {
    background-color: #3b3b4a;
    border: 1px solid #55556a;
}

QToolButton:pressed {
    background-color: #1a1a24;
}

QTreeView {
    background-color: #18181c;
    color: #d0d0d0;
    border: none;
    border-right: 1px solid #2d2d34;
}

QTreeView::item:hover {
    background-color: #25252e;
}

QTreeView::item:selected {
    background-color: #2d3142;
    color: #00d2ff;
}

QTabWidget::pane {
    border: none;
    background-color: #1e1e24;
}

QTabBar::tab {
    background-color: #18181c;
    color: #999999;
    padding: 8px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #1e1e24;
    color: #00d2ff;
    font-weight: bold;
    border-bottom: 2px solid #00d2ff;
}

QPlainTextEdit {
    background-color: #1a1a20;
    color: #e6e6e6;
    border: none;
    font-family: 'Consolas', 'Cascadia Code', 'Courier New', monospace;
    font-size: 13px;
    selection-background-color: #2d3b50;
}

QTextEdit {
    background-color: #141418;
    color: #00e676;
    border: none;
    font-family: 'Consolas', 'Cascadia Code', 'Courier New', monospace;
    font-size: 12px;
}

QSplitter::handle {
    background-color: #2d2d34;
}

QStatusBar {
    background-color: #18181c;
    color: #888888;
    border-top: 1px solid #2d2d34;
}
"""
