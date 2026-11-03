"""Syntax highlighter for HAKAI source code in PySide6."""

from __future__ import annotations

import re
from PySide6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat


class HakaiSyntaxHighlighter(QSyntaxHighlighter):
    """Highlights keywords, literals, types, and comments for HAKAI."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.highlighting_rules = []

        # Keyword format (Cyan / Blue)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#4fc3f7"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            r"\bHAKAI\b", r"\bSTART\b", r"\bEND\b",
            r"\blet\b", r"\bconst\b", r"\bfunction\b", r"\bclass\b",
            r"\bextends\b", r"\bstatic\b", r"\bself\b", r"\bsuper\b",
            r"\bif\b", r"\belse\b", r"\belseif\b", r"\bwhile\b",
            r"\brepeat\b", r"\bbreak\b", r"\bcontinue\b", r"\breturn\b",
            r"\bimport\b", r"\bfrom\b", r"\bas\b", r"\band\b",
            r"\bor\b", r"\bnot\b", r"\btrue\b", r"\bfalse\b", r"\bnull\b"
        ]
        for kw in keywords:
            self.highlighting_rules.append((re.compile(kw), keyword_format))

        # Builtins format (Purple)
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#ba68c8"))
        builtins = [
            r"\bprint\b", r"\bprintln\b", r"\binput\b", r"\blen\b",
            r"\btype\b", r"\bstr\b", r"\bint\b", r"\bfloat\b", r"\bbool\b",
            r"\brange\b", r"\bopen\b"
        ]
        for b in builtins:
            self.highlighting_rules.append((re.compile(b), builtin_format))

        # Number format (Orange)
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#ffb74d"))
        self.highlighting_rules.append((re.compile(r"\b\d+(\.\d+)?\b"), number_format))

        # String format (Green)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#aed581"))
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.highlighting_rules.append((re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))

        # Single-line comment format (Grey italic)
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#78909c"))
        self.comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r"//[^\n]*"), self.comment_format))

    def highlightBlock(self, text: str) -> None:
        for pattern, fmt in self.highlighting_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)

