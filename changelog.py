# changelog.py
from __future__ import annotations
from pathlib import Path
from aqt import mw
from aqt.qt import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QTextBrowser,
    QFrame,
    Qt,
    QDesktopServices,
    QUrl,
    QTimer,
)

from .core import DeadlineDb


# =========================
# Deckline changelog config
# =========================
DECKLINE_VERSION = "1.2.1"
_CFG_KEY_SEEN = "changelog_seen_version"  # stored inside DeadlineDb().db


def _open_kofi() -> None:
    try:
        QDesktopServices.openUrl(QUrl("https://ko-fi.com/s/d708f4b514"))
    except Exception as e:
        print(f"Deckline changelog openUrl error: {e}")


def _open_stats() -> None:
    try:
        from .stats.stats_dialog import open_deckline_stats_dialog
        open_deckline_stats_dialog()
    except Exception as e:
        print(f"Deckline changelog open_stats error: {e}")


def _open_settings_global() -> None:
    """
    Open Deckline settings in global mode (Feedback/Premium),
    without tying it to a specific deck deadline.
    """
    try:
        from .settings import DeadlinerDialog

        current = mw.col.decks.current()
        did = current["id"] if current else None
        if did is None:
            return

        dlg = DeadlinerDialog(did, global_mode=True)

        # Try to land on Feedback tab (if it exists)
        try:
            for i in range(dlg.tabs.count()):
                if dlg.tabs.tabText(i) == "Feedback":
                    dlg.tabs.setCurrentIndex(i)
                    break
        except Exception:
            pass

        dlg.exec()
    except Exception as e:
        print(f"Deckline changelog open_settings error: {e}")


class DecklineChangelogDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent or mw)
        self.setWindowTitle(f"Deckline v{DECKLINE_VERSION} — What's new")
        self.setMinimumWidth(720)
        self.setMinimumHeight(520)

        self.db = DeadlineDb()

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # -------------------------
        # Header
        # -------------------------
        header = QHBoxLayout()
        header.setSpacing(10)

        title = QLabel(f"Deckline <span style='opacity:.9;'>v{DECKLINE_VERSION}</span>")
        title.setTextFormat(Qt.TextFormat.RichText)
        f = title.font()
        f.setPointSize(16)
        f.setBold(True)
        title.setFont(f)

        badge = QLabel("NEW UPDATE")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedHeight(22)
        badge.setStyleSheet(
            "padding: 0 10px; border-radius: 999px; font-weight: 900; letter-spacing: 1px;"
            "background: rgba(59,130,246,0.14); color: rgba(191,219,254,0.98);"
            "border: 1px solid rgba(59,130,246,0.25);"
        )

        header.addWidget(title, 0)
        header.addWidget(badge, 0)
        header.addStretch(1)

        closeTop = QPushButton("Close")
        closeTop.setCursor(Qt.CursorShape.PointingHandCursor)
        closeTop.clicked.connect(self.accept)
        header.addWidget(closeTop, 0)

        root.addLayout(header)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("color: rgba(255,255,255,0.10);")
        root.addWidget(div)

        # -------------------------
        # Body (scrollable rich text)
        # -------------------------
        body = QTextBrowser()
        body.setOpenExternalLinks(True)
        body.setStyleSheet(
            "QTextBrowser {"
            "  border-radius: 14px;"
            "  padding: 14px;"
            "  background: rgba(255,255,255,0.04);"
            "  border: 1px solid rgba(255,255,255,0.06);"
            "}"
        )

        stats_img = (Path(__file__).resolve().parent / "deckline_heatmap.png").as_uri()

        # Feel free to tweak text here later.
        html = f"""
        <div style="font-size:12.5px; line-height:1.45;">
           <p style="margin-top:0;">
            Welcome to <b>Deckline v{DECKLINE_VERSION}</b> 🎉
          </p>

          <h3 style="margin:14px 0 6px 0;">🍎 Mac fix: Premium code input</h3>
          <ul style="margin:6px 0 0 18px;">
            <li>Hopefully fixed an issue on <b>macOS</b> where the Premium code input field was not working correctly.</li>
            <li>You can now paste and submit your Premium code normally on Mac.</li>
          </ul>

          <h3 style="margin:14px 0 6px 0;">From v1.2</h3>
          <p style="margin:6px 0 0 0;">
            This update also includes the improvements introduced in v1.2.
          </p>
          
          <h3 style="margin:14px 0 6px 0;">🗺️ NEW: Heatmap tab in Stats</h3>
          <ul style="margin:6px 0 0 18px;">
            <li>The Stats window now includes a dedicated <b>Heatmap</b> tab that shows your recent study pattern per deck.</li>
            <li>Each day tile reflects how much of your daily target you completed in the <b>New</b> and <b>Review</b> phases.</li>
            <li>You can instantly see consistency, weak days, and momentum without opening individual deck details.</li>
          </ul>

          <h3 style="margin:14px 0 6px 0;">🎯 Better deadline awareness</h3>
          <ul style="margin:6px 0 0 18px;">
            <li>Heatmap cells now make it easier to spot <b>deadline pressure</b>, pacing shifts, and where catch-up is needed.</li>
            <li>Tooltips provide per-day details like done, target, phase, and streak-day context for quick diagnostics.</li>
          </ul>
          
          <div style="margin:10px 0 12px 0; padding:10px; border-radius:12px;">
            <img src="{stats_img}"
                 alt="Deckline heatmap"
                 style="width:100%; max-width:620px; border-radius:10px; display:block; margin:0 auto;" />
          </div>

          <div style="margin-top:14px; padding:12px; border-radius:12px;
                      background: rgba(255,90,165,0.08); border:1px solid rgba(255,90,165,0.18);">
            <b>Support Deckline</b><br>
            If Deckline helps you stay consistent, consider unlocking Premium to support development
            (More deadlines, charts and customizaton features now, and more coming). ❤️
          </div>
        </div>
        """
        body.setHtml(html)
        root.addWidget(body, 1)

        # -------------------------
        # Footer row
        # -------------------------
        footer = QHBoxLayout()
        footer.setSpacing(10)
        
        self.dontShowAgain = QCheckBox("Don’t show this again")
        self.dontShowAgain.setChecked(True)
        footer.addWidget(self.dontShowAgain, 0)
        
        footer.addStretch(1)
        
        btnPremium = QPushButton("Upgrade to Premium")
        btnPremium.setCursor(Qt.CursorShape.PointingHandCursor)
        btnPremium.setStyleSheet(
            "QPushButton { background: rgba(255, 90, 165, 0.95); color: white; border: 1px solid rgba(255,90,165,0.55);"
            " border-radius: 10px; padding: 6px 12px; font-weight: 900; }"
            "QPushButton:hover { background: rgba(255, 63, 152, 0.98); }"
        )
        btnPremium.clicked.connect(_open_kofi)
        
        footer.addWidget(btnPremium, 0)


        root.addLayout(footer)

        # Overall dialog style (subtle)
        self.setStyleSheet(
            "QDialog { background: palette(window); }"
            "QPushButton { border-radius: 10px; padding: 6px 12px; font-weight: 800; }"
        )

    def accept(self) -> None:
        # If user chose “Don’t show again” we store that this version is seen
        try:
            if self.dontShowAgain.isChecked():
                self.db.db[_CFG_KEY_SEEN] = DECKLINE_VERSION
                self.db.save()
        except Exception as e:
            print(f"Deckline changelog save error: {e}")

        super().accept()


def maybe_show_changelog(*, parent=None, delay_ms: int = 500) -> None:
    """
    Show the changelog once per DECKLINE_VERSION.
    Safe to call on startup.
    """
    try:
        if not mw or not mw.col:
            return

        db = DeadlineDb()
        seen = str(db.db.get(_CFG_KEY_SEEN, "") or "")

        if seen == DECKLINE_VERSION:
            return

        # Defer showing so Anki finishes loading the UI
        def _show() -> None:
            try:
                dlg = DecklineChangelogDialog(parent or mw)
                dlg.exec()
            except Exception as e:
                print(f"Deckline changelog dialog error: {e}")

        QTimer.singleShot(max(0, int(delay_ms)), _show)

    except Exception as e:
        print(f"Deckline changelog maybe_show error: {e}")
