# deck_browser_dialogs.py
import json
import os
from datetime import datetime, timedelta
from typing import Any

from aqt import mw
from aqt.qt import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    Qt,
    QHeaderView,
)
from aqt.utils import showInfo

from .core import DeadlineDb, refreshDeadliner


class ClearDeadlinesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle("Clear selected deadlines")
        self.resize(520, 460)

        self.db = DeadlineDb()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(10)

        title = QLabel("<b>Select which deadlines to remove</b>")
        outer.addWidget(title)
        

        self.searchBox = QLineEdit()
        self.searchBox.setPlaceholderText("Search deck name or date…")
        self.searchBox.setClearButtonEnabled(True)
        self.searchBox.setMinimumHeight(28)
        outer.addWidget(self.searchBox)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Deck", "Deadline"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setUniformRowHeights(True)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tree.header().setStretchLastSection(False)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.header().setSortIndicatorShown(True)
        self.tree.header().setSortIndicator(1, Qt.SortOrder.AscendingOrder)
        self.tree.setMinimumHeight(280)
        outer.addWidget(self.tree)

        btnRow = QHBoxLayout()
        btnRow.addStretch(1)
        btnAll = QPushButton("Select all")
        btnNone = QPushButton("Select none")
        btnInvert = QPushButton("Invert selection")
        for b in (btnAll, btnNone, btnInvert):
            b.setMinimumHeight(26)
        btnRow.addWidget(btnAll)
        btnRow.addWidget(btnNone)
        btnRow.addWidget(btnInvert)
        outer.addLayout(btnRow)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        outer.addWidget(buttons)

        self.items: list[QTreeWidgetItem] = []
        for deck_id_str, cfg in self.db.deadlines.items():
            deck_id = int(deck_id_str)
            deck = mw.col.decks.get(deck_id, default=None)

            shown_name = cfg.get("name") or (deck["name"] if deck else f"Deck {deck_id}")
            deadline = cfg.get("deadline", "?")

            it = QTreeWidgetItem([shown_name, deadline])
            it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            it.setCheckState(0, Qt.CheckState.Unchecked)
            it.setData(0, Qt.ItemDataRole.UserRole, deck_id_str)

            self.tree.addTopLevelItem(it)
            self.items.append(it)

        self.tree.sortItems(1, Qt.SortOrder.AscendingOrder)

        self.setStyleSheet("""
            QLineEdit { padding: 6px 8px; border-radius: 6px; }
            QTreeWidget { border: 1px solid palette(midlight); border-radius: 6px; }
            QHeaderView::section { padding: 6px 8px; font-weight: 600; }
            QPushButton { padding: 4px 10px; border-radius: 6px; }
        """)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        def filter_rows(text: str):
            t = text.strip().lower()
            for it in self.items:
                name = it.text(0).lower()
                date = it.text(1).lower()
                it.setHidden(False if not t else (t not in name and t not in date))

        self.searchBox.textChanged.connect(filter_rows)

        def select_all():
            for it in self.items:
                if not it.isHidden():
                    it.setCheckState(0, Qt.CheckState.Checked)

        def select_none():
            for it in self.items:
                if not it.isHidden():
                    it.setCheckState(0, Qt.CheckState.Unchecked)

        def invert_sel():
            for it in self.items:
                if not it.isHidden():
                    it.setCheckState(
                        0,
                        Qt.CheckState.Unchecked if it.checkState(0) == Qt.CheckState.Checked
                        else Qt.CheckState.Checked
                    )

        btnAll.clicked.connect(select_all)
        btnNone.clicked.connect(select_none)
        btnInvert.clicked.connect(invert_sel)

    def selected_ids(self) -> list[str]:
        ids = []
        for it in self.items:
            if it.checkState(0) == Qt.CheckState.Checked and not it.isHidden():
                ids.append(it.data(0, Qt.ItemDataRole.UserRole))
        return ids


def clear_selected_deadlines() -> None:
    dlg = ClearDeadlinesDialog(mw)
    if dlg.exec() != int(QDialog.DialogCode.Accepted):
        return

    ids = dlg.selected_ids()
    if not ids:
        showInfo("No decks selected.")
        return

    db = DeadlineDb()
    removed = 0
    for deck_id_str in ids:
        if deck_id_str in db.deadlines:
            del db.deadlines[deck_id_str]
            removed += 1

    db.save()
    refreshDeadliner()
    showInfo(f"Removed: {removed} deadline(s).")
