# changelog.py
from __future__ import annotations

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
DECKLINE_VERSION = "1.0.1"
_CFG_KEY_SEEN = "changelog_seen_version"  # stored inside DeadlineDb().db


def _open_kofi() -> None:
    try:
        QDesktopServices.openUrl(QUrl("https://ko-fi.com/s/d708f4b514"))
    except Exception as e:
        print(f"Deckline changelog openUrl error: {e}")


def _open_stats() -> None:
    try:
        from .ui.stats_dialog import open_deckline_stats_dialog
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

        # Feel free to tweak text here later.
        html = f"""
        <div style="font-size:12.5px; line-height:1.45;">
          <p style="margin-top:0;">
            Welcome to the first definitive version of Deckline: <b>Deckline v{DECKLINE_VERSION}</b> 🎉<br>
            This update is a big polish + UX upgrade — focused on clarity, motivation, and speed.
          </p>
          
          <h3 style="margin:14px 0 6px 0;">🛠️ v1.0.1 — Fixes</h3>
          <ul style="margin:6px 0 0 18px;">
            <li>Fixed: <b>“Show daily progress bar in review screen”</b> toggle now correctly shows/hides the review progress bar.</li>
          </ul>


          <h3 style="margin:14px 0 6px 0;">✅ New Deck Browser view (Cards instead of a table)</h3>
          <ul style="margin:6px 0 0 18px;">
            <li><b>Modern card layout</b> — easier to scan at a glance.</li>
            <li><b>Cleaner badges</b> like <span style="color:#22C55E;"><b>ON TRACK</b></span>,
                <span style="color:#EF4444;"><b>BEHIND</b></span>, <span style="color:#3B82F6;"><b>PENDING</b></span>.</li>
            <li><b>Focus + Sort controls</b> in the new topbar to instantly find what matters.</li>
          </ul>

          <h3 style="margin:14px 0 6px 0;">✨ UI improvements everywhere</h3>
          <ul style="margin:6px 0 0 18px;">
            <li>Smoother spacing, better typography, and consistent styling.</li>
            <li>Tooltips explain <b>Phase 1 (NEW)</b> vs <b>Phase 2 (REVIEW)</b> more clearly.</li>
            <li>Deck icons + accent colors are more consistent and readable.</li>
          </ul>

          <h3 style="margin:14px 0 6px 0;">📈 Premium: Stats dashboard (7-day view)</h3>
          <ul style="margin:6px 0 0 18px;">
            <li>New <b>Deckline Stats</b> window: last 7 days, per deck, done vs target.</li>
            <li>Instant green/red feedback: above/below target.</li>
            <li>Also supports <b>All deadlines (sum)</b> to see your total momentum.</li>
          </ul>

          <h3 style="margin:14px 0 6px 0;">💎 Premium: More motivation + control</h3>
          <ul style="margin:6px 0 0 18px;">
            <li><b>Unlimited deadlines</b> (no cap).</li>
            <li><b>Vacation days</b>: add days off and Deckline adjusts your daily target automatically.</li>
            <li><b>Custom progress colors</b>: auto / solid / gradient.</li>
            <li><b>Celebration animation</b> when you hit 100% for the first time that day.</li>
          </ul>

          <h3 style="margin:14px 0 6px 0;">🧠 Small but important behavior changes</h3>
          <ul style="margin:6px 0 0 18px;">
            <li>Targets stay stable during the day (less “moving goalpost” feeling).</li>
            <li>Better handling of parent decks: the progress bars follow the nearest enabled deadline deck.</li>
            <li>Cleaner “rest day” behavior for skipped days (weekends/vacations).</li>
            <li>You can access the deadline settings by clicking the **icon on the left side of a Deckline card** in the Deck Browser.</li>
          </ul>

          <div style="margin-top:14px; padding:12px; border-radius:12px;
                      background: rgba(255,90,165,0.08); border:1px solid rgba(255,90,165,0.18);">
            <b>Support Deckline</b><br>
            If Deckline helps you stay consistent, consider unlocking Premium to support development
            (Stats + more features now, and more coming). ❤️
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
        self.dontShowAgain.setChecked(True)  # default: once per version
        footer.addWidget(self.dontShowAgain, 0)

        footer.addStretch(1)

        btnSettings = QPushButton("Open settings")
        btnSettings.setCursor(Qt.CursorShape.PointingHandCursor)
        btnSettings.clicked.connect(_open_settings_global)

        btnStats = QPushButton("Open Stats")
        btnStats.setCursor(Qt.CursorShape.PointingHandCursor)
        btnStats.clicked.connect(_open_stats)

        btnPremium = QPushButton("Upgrade to Premium")
        btnPremium.setCursor(Qt.CursorShape.PointingHandCursor)
        btnPremium.setStyleSheet(
            "QPushButton { background: rgba(255, 90, 165, 0.95); color: white; border: 1px solid rgba(255,90,165,0.55);"
            " border-radius: 10px; padding: 6px 12px; font-weight: 900; }"
            "QPushButton:hover { background: rgba(255, 63, 152, 0.98); }"
        )
        btnPremium.clicked.connect(_open_kofi)

        footer.addWidget(btnSettings, 0)
        footer.addWidget(btnStats, 0)
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
