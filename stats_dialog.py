from __future__ import annotations
import os

from datetime import date, timedelta
from typing import Dict, List

from aqt import mw
from aqt.qt import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    Qt,
    QWidget,
    QPainter,
    QPen,
    QBrush,
    QColor,
    QFont,
    QFrame,
    QPixmap,
    QLinearGradient,
)


from ..core import (
    DeadlineMgr,
    DeadlineDb,
    get_daily_log_entries,
    log_daily_snapshot_for_deck,
    calculate_current_streak,  # ✅ add
)


def _iso(d: date) -> str:
    return d.isoformat()


def _last_n_days(n: int) -> List[date]:
    today = date.today()
    return [today - timedelta(days=i) for i in range(n - 1, -1, -1)]


def _sum_series(series_list: List[List[dict]]) -> List[dict]:
    by_date: Dict[str, Dict[str, int]] = {}
    for series in series_list:
        for e in series:
            ds = str(e.get("date", ""))
            if not ds:
                continue
            by_date.setdefault(ds, {"done": 0, "target": 0})
            by_date[ds]["done"] += int(e.get("done", 0) or 0)
            by_date[ds]["target"] += int(e.get("target", 0) or 0)

    out = [{"date": d, "done": v["done"], "target": v["target"]} for d, v in by_date.items()]
    out.sort(key=lambda x: x["date"])
    return out


def _build_7day_window(entries: List[dict]) -> List[dict]:
    want_days = _last_n_days(7)
    lookup = {str(e.get("date", "")): e for e in entries if isinstance(e, dict)}

    out: List[dict] = []
    for d in want_days:
        ds = _iso(d)
        e = lookup.get(ds) or {}
        out.append(
            {
                "date": ds,
                "done": int(e.get("done", 0) or 0),
                "target": int(e.get("target", 0) or 0),
                "phase": str(e.get("phase", "")) if isinstance(e, dict) else "",
            }
        )
    return out


class DecklineChartWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(420)
        self._title = "Deckline Stats"
        self._points: List[dict] = []

    def set_data(self, title: str, points: List[dict]) -> None:
        self._title = title
        self._points = points
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    
        w = self.width()
        h = self.height()
    
        # ---------- Background (subtle gradient) ----------
        bg = QLinearGradient(0, 0, 0, h)
        bg.setColorAt(0.0, QColor(28, 28, 32))
        bg.setColorAt(1.0, QColor(18, 18, 20))
        painter.fillRect(0, 0, w, h, bg)
    
        # ---------- Header ----------
        painter.setPen(QColor(235, 237, 240))
        painter.setFont(QFont("Segoe UI", 11, 700))
        painter.drawText(14, 26, self._title)
    
        # ---------- Legend (cleaner, aligned) ----------
        painter.setFont(QFont("Segoe UI", 9, 600))
        legend_y = 48
    
        def _legend_item(x: int, dot: QColor, text: str) -> int:
            painter.setPen(dot)
            painter.drawText(x, legend_y, "●")
            painter.setPen(QColor(205, 208, 214))
            painter.drawText(x + 14, legend_y, text)
            return x + 14 + painter.fontMetrics().horizontalAdvance(text) + 22
    
        x = 14
        x = _legend_item(x, QColor(34, 197, 94), "Above target")
        x = _legend_item(x, QColor(239, 68, 68), "Below target")
        x = _legend_item(x, QColor(99, 102, 241), "Daily target")
    
        # ---------- Card area ----------
        card_x = 14
        card_y = 60
        card_w = w - 28
        card_h = h - 74
    
        # shadow-ish backdrop (simple)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 60)))
        painter.drawRoundedRect(card_x + 2, card_y + 4, card_w, card_h, 16, 16)
    
        painter.setPen(QPen(QColor(255, 255, 255, 22), 1))
        painter.setBrush(QBrush(QColor(255, 255, 255, 10)))
        painter.drawRoundedRect(card_x, card_y, card_w, card_h, 16, 16)
    
        # ---------- Inner plotting area ----------
        # more left padding to fit Y-axis labels
        pad_l = 58
        pad_r = 18
        pad_t = 18
        pad_b = 56
    
        x0 = card_x + pad_l
        y0 = card_y + pad_t
        x1 = card_x + card_w - pad_r
        y1 = card_y + card_h - pad_b
    
        inner_w = max(1, x1 - x0)
        inner_h = max(1, y1 - y0)
    
        points = self._points or []
        if not points:
            painter.setPen(QColor(240, 240, 240))
            painter.setFont(QFont("Segoe UI", 10, 600))
            painter.drawText(card_x + 18, card_y + 30, "No data to display.")
            return
    
        # ---------- Scale ----------
        raw_max = 1
        for p in points:
            raw_max = max(raw_max, int(p.get("done", 0) or 0), int(p.get("target", 0) or 0))
    
        # Nice max rounding (10/25/50 style steps)
        def _nice_max(v: int) -> int:
            if v <= 10:
                return 10
            # choose step based on magnitude
            if v <= 50:
                step = 10
            elif v <= 150:
                step = 25
            elif v <= 400:
                step = 50
            else:
                step = 100
            return int(((v + step - 1) // step) * step)
    
        max_y = _nice_max(raw_max)
    
        # ---------- Axes + grid ----------
        # Y axis line
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        painter.drawLine(x0, y0, x0, y1)
    
        # X axis line
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
        painter.drawLine(x0, y1, x1, y1)
    
        # Y ticks + grid lines
        ticks = 5  # 0..max in 5 steps
        painter.setFont(QFont("Segoe UI", 8, 600))
        for i in range(ticks + 1):
            frac = i / ticks
            val = int(round(max_y * (1.0 - frac)))
            y = int(y0 + inner_h * frac)
    
            # grid line
            painter.setPen(QPen(QColor(255, 255, 255, 18), 1))
            painter.drawLine(x0, y, x1, y)
    
            # tick label
            painter.setPen(QColor(230, 232, 235, 170))
            label = str(val)
            tw = painter.fontMetrics().horizontalAdvance(label)
            painter.drawText(x0 - 10 - tw, y + 4, label)
    
            # small tick mark
            painter.setPen(QPen(QColor(255, 255, 255, 35), 1))
            painter.drawLine(x0 - 4, y, x0, y)
    
        # ---------- Bars + labels ----------
        n = len(points)
        step = inner_w / max(1, n)
        bar_w = max(8, int(step * 0.58))
    
        for i, p in enumerate(points):
            done = int(p.get("done", 0) or 0)
            target = int(p.get("target", 0) or 0)
    
            good = (target > 0 and done >= target) or (target == 0 and done > 0)
            bar_color = QColor(34, 197, 94, 210) if good else QColor(239, 68, 68, 210)
    
            bh = int((done / max_y) * inner_h) if max_y > 0 else 0
            bx = int(x0 + (i + 0.5) * step - (bar_w / 2))
            by = int(y0 + inner_h - bh)
    
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(bar_color))
            painter.drawRoundedRect(bx, by, bar_w, bh, 9, 9)
    
            # Date label (MM-DD)
            dstr = str(p.get("date", ""))  # expected "YYYY-MM-DD"

            if len(dstr) >= 10:
                ds = f"{dstr[8:10]}-{dstr[5:7]}"
            else:
                ds = dstr

            painter.setPen(QColor(230, 232, 235, 180))
            painter.setFont(QFont("Segoe UI", 8, 500))
            painter.drawText(bx, y1 + 22, bar_w, 14, Qt.AlignmentFlag.AlignHCenter, ds)
    
            # Done/Target label
            painter.setPen(QColor(230, 232, 235, 235))
            painter.setFont(QFont("Segoe UI", 8, 700))
            painter.drawText(bx, y1 + 38, bar_w, 14, Qt.AlignmentFlag.AlignHCenter, f"{done}/{target}")
    
        # ---------- Target line ----------
        line_pen = QPen(QColor(99, 102, 241, 235), 2)
        painter.setPen(line_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
    
        prev_x = None
        prev_y = None
        for i, p in enumerate(points):
            target = int(p.get("target", 0) or 0)
            x = int(x0 + (i + 0.5) * step)
            y = int(y0 + (1.0 - (target / max_y)) * inner_h) if max_y > 0 else y1
    
            if prev_x is not None:
                painter.drawLine(prev_x, prev_y, x, y)
    
            painter.setPen(QPen(QColor(99, 102, 241, 245), 1))
            painter.setBrush(QBrush(QColor(99, 102, 241, 245)))
            painter.drawEllipse(x - 3, y - 3, 6, 6)
    
            painter.setPen(line_pen)
            prev_x, prev_y = x, y
    
        # ---------- Y axis label (vertical, centered) ----------
        painter.save()
        
        painter.setPen(QColor(230, 232, 235, 120))
        painter.setFont(QFont("Segoe UI", 9, 700))
        
        label = "Cards"
        
        # center vertically in the plot area
        cy = int((y0 + y1) / 2)
        
        # place label a bit left of the y-axis ticks
        x_label = int(x0 - 44)
        
        # rotate around (x_label, cy)
        painter.translate(x_label, cy)
        painter.rotate(-90)
        
        # after rotation, draw centered at (0,0)
        fm = painter.fontMetrics()
        tw = fm.horizontalAdvance(label)
        th = fm.height()
        painter.drawText(int(-tw / 2), int(th / 2), label)
        
        painter.restore()




class DecklineBgFrame(QFrame):
    def __init__(self, img_path: str, parent=None) -> None:
        super().__init__(parent)
        self._pix = QPixmap(img_path)

    def paintEvent(self, event) -> None:
        # Let QFrame paint its frame first (doesn't wipe our image)
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        # Draw image scaled to cover
        if not self._pix.isNull():
            w = self.width()
            h = self.height()
            pw = self._pix.width()
            ph = self._pix.height()

            if pw > 0 and ph > 0:
                scale = max(w / pw, h / ph)
                sw = int(pw * scale)
                sh = int(ph * scale)

                x = int((w - sw) / 2)
                y = int((h - sh) / 2)

                painter.drawPixmap(x, y, sw, sh, self._pix)
        else:
            painter.fillRect(self.rect(), QColor(25, 25, 25))



class DecklineStatsDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent or mw)

        self.db = DeadlineDb()
        self._is_premium = bool(self.db.is_premium)

        self.setWindowTitle("Deckline Stats")
        if self._is_premium:
            self.setMinimumWidth(900)
            self.setMinimumHeight(560)
        else:
            # Smaller paywall dialog (does not affect premium chart dialog)
            self.setFixedWidth(760)
            self.setMinimumHeight(520)


        # Subtle global styling for this dialog
        self.setStyleSheet("""
            QDialog { background: palette(window); }
            QLabel { font-size: 12px; }
            QPushButton {
                border-radius: 12px;
                padding: 8px 14px;
                font-weight: 800;
            }
            QPushButton:hover { opacity: 0.96; }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        
        # Free version: show only the lockscreen (no extra header bar)
        if not self._is_premium:
            outer.addWidget(self._build_blurred_locked_screen_widget(), 1)
            return
        
        # Premium version continues below (normal header + chart)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(12)
        
        # --- Header row (title + badge + buttons) ---
        header = QHBoxLayout()
        header.setSpacing(10)
        
        title = QLabel("Deckline Stats")
        f = title.font()
        f.setPointSize(14)
        f.setBold(True)
        title.setFont(f)
        header.addWidget(title, 0)
        
        badge = QLabel("ACTIVE")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedHeight(22)
        badge.setStyleSheet(
            "padding: 0 10px; border-radius: 999px; font-weight: 900; letter-spacing: 1px;"
            "background: rgba(34,197,94,0.14); color: rgba(187,247,208,0.98); border: 1px solid rgba(34,197,94,0.25);"
        )
        header.addWidget(badge, 0)
        
        header.addStretch(1)
        
        closeBtn = QPushButton("Close")
        closeBtn.setCursor(Qt.CursorShape.PointingHandCursor)
        closeBtn.clicked.connect(self.accept)
        header.addWidget(closeBtn, 0)
        
        outer.addLayout(header)


        # --- If NOT premium: show paywall and stop here ---
        if not self._is_premium:
            outer.addWidget(self._build_blurred_locked_screen_widget(), 1)
            return


        # --- Premium UI (chart) ---
        top = QHBoxLayout()
        top.setSpacing(10)

        top.addWidget(QLabel("<b>Deck:</b>"))

        self.deckBox = QComboBox()
        self.deckBox.setMinimumWidth(380)
        top.addWidget(self.deckBox, 1)

        self.refreshBtn = QPushButton("Refresh")
        self.refreshBtn.setCursor(Qt.CursorShape.PointingHandCursor)
        top.addWidget(self.refreshBtn, 0)

        # ✅ Total streaks (all decks)
        self.totalStreakLabel = QLabel("")
        self.totalStreakLabel.setStyleSheet("color: rgba(205, 208, 214, 0.95); font-weight: 700;")
        top.addWidget(self.totalStreakLabel, 0)

        outer.addLayout(top)


        self.chart = DecklineChartWidget(self)
        outer.addWidget(self.chart, 1)

        self._deck_ids: List[int] = []
        self._load_decks()

        self.deckBox.currentIndexChanged.connect(self._render)
        self.refreshBtn.clicked.connect(self._refresh_and_render)

        self._render()

    # ----------------------------
    # Paywall UI
    # ----------------------------
    def _build_paywall(self) -> QWidget:
        holder = QWidget()
        holder_l = QVBoxLayout(holder)
        holder_l.setContentsMargins(0, 0, 0, 0)
        holder_l.setSpacing(0)
    
        holder_l.addStretch(1)
    
        card = QFrame()
        card.setFrameShape(QFrame.Shape.NoFrame)
        card.setStyleSheet("""
            QFrame {
                border-radius: 20px;
                background: rgba(30,30,30,0.94);
                border: 1px solid rgba(255,255,255,0.07);
            }
        """)

    
        card_l = QVBoxLayout(card)
        card_l.setContentsMargins(28, 22, 28, 22)  # more left/right padding
        card_l.setSpacing(14)
    
        # Title
        h = QLabel("Unlock Stats with Deckline Premium")
        hf = h.font()
        hf.setPointSize(15)
        hf.setBold(True)
        h.setFont(hf)
        h.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    
        # Subtitle (centered)
        sub = QLabel(
            "See your progress for the last 7 days per deck,\n"
            "and instantly spot if you're on track."
        )
        sub.setWordWrap(True)
        sub.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        sub.setStyleSheet("color: rgba(200,205,212,0.95);")
    
        # Bullets (slightly indented, but not stuck to the edge)
        bullets = QLabel(
            "• 7-day progress per deck (done vs target)\n"
            "• Clear above/below target feedback\n"
            "• Filter by deck (or view total)\n"
            "• Unlimited deadlines (Premium)\n"
        )
        bullets.setWordWrap(True)
        bullets.setStyleSheet("color: rgba(230,232,235,0.95);")
        bullets.setAlignment(Qt.AlignmentFlag.AlignLeft)
    
        bullets_wrap = QFrame()
        bullets_wrap.setFrameShape(QFrame.Shape.NoFrame)
        bullets_wrap.setStyleSheet("""
            QFrame {
                border-radius: 14px;
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.07);
            }
        """)
        bullets_l = QVBoxLayout(bullets_wrap)
        bullets_l.setContentsMargins(18, 14, 18, 14)
        bullets_l.addWidget(bullets)
    
        # Primary CTA only
        cta = QPushButton("Unlock Premium – Support development")
        cta.setCursor(Qt.CursorShape.PointingHandCursor)
        cta.setMinimumHeight(42)
        cta.setStyleSheet("""
            QPushButton {
                background: rgba(255, 90, 165, 0.95);
                color: white;
                border: 1px solid rgba(255, 90, 165, 0.55);
            }
            QPushButton:hover { background: rgba(255, 63, 152, 0.98); }
        """)
    
        # Small hint (centered)
        small = QLabel(
            "Already bought Premium?\n"
            "Open Deckline settings → Premium tab and paste your code."
        )
        small.setWordWrap(True)
        small.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        small.setTextFormat(Qt.TextFormat.RichText)
        small.setStyleSheet("color: rgba(169,175,183,0.95);")
    
        card_l.addWidget(h)
        card_l.addWidget(sub)
        card_l.addWidget(bullets_wrap)
        card_l.addSpacing(4)
        card_l.addWidget(cta)
        card_l.addWidget(small)
    
        def _open_kofi() -> None:
            try:
                from aqt.qt import QDesktopServices, QUrl
                QDesktopServices.openUrl(QUrl("https://ko-fi.com/s/d708f4b514"))
            except Exception as e:
                print(f"Deckline paywall openUrl error: {e}")
    
        cta.clicked.connect(_open_kofi)
    
        # Center card horizontally and keep it compact
        row = QWidget()
        row_l = QHBoxLayout(row)
        row_l.setContentsMargins(0, 0, 0, 0)
        row_l.addStretch(1)
        row_l.addWidget(card, 0)
        row_l.addStretch(1)
    
        card.setMaximumWidth(560)
        card.setMinimumWidth(520)
    
        holder_l.addWidget(row, 0)
        holder_l.addStretch(1)
    
        return holder


    # ----------------------------
    # Lockscreen (blurred background)
    # ----------------------------
    def _build_blurred_locked_screen_widget(self) -> QWidget:
        from aqt.qt import QDesktopServices, QUrl

        img_path = os.path.join(os.path.dirname(__file__), "assets", "stats_blur.png")

        root = DecklineBgFrame(img_path)
        root.setStyleSheet("""
            QFrame {
                border-radius: 18px;
            }
        """)

        # Overlay
        overlay = QFrame(root)
        overlay.setStyleSheet("""
            QFrame {
                border-radius: 18px;
                background: rgba(15,15,15,0.70);
                border: 1px solid rgba(255,255,255,0.06);
            }
        """)

        # Root layout
        root_l = QVBoxLayout(root)
        root_l.setContentsMargins(0, 0, 0, 0)
        root_l.setSpacing(0)
        root_l.addWidget(overlay, 1)

        # Overlay layout (centers the card)
        lay = QVBoxLayout(overlay)
        lay.setContentsMargins(28, 26, 28, 22)
        lay.setSpacing(14)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Card (more modern, less boxy)
        card = QFrame()
        card.setFrameShape(QFrame.Shape.NoFrame)
        card.setStyleSheet("""
            QFrame {
                border-radius: 20px;
                background: rgba(30,30,30,0.95);
                border: 1px solid rgba(255,255,255,0.07);
            }
        """)
        card_l = QVBoxLayout(card)
        card_l.setContentsMargins(26, 22, 26, 22)
        card_l.setSpacing(12)

        # Title (no background/border)
        title = QLabel("Unlock Stats with Deckline Premium")
        tf = title.font()
        tf.setPointSize(15)
        tf.setBold(True)
        title.setFont(tf)
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setStyleSheet("color: rgba(230,232,235,0.98); background: transparent; border: none;")

        # Subtitle (no background/border)
        desc = QLabel(
            "See your progress for the last 7 days per deck,\n"
            "and instantly spot if you're on track."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        desc.setStyleSheet("color: rgba(169,175,183,0.95); background: transparent; border: none;")

        # Bullets wrap (soft pill box, no harsh lines)
        bullets_wrap = QFrame()
        bullets_wrap.setFrameShape(QFrame.Shape.NoFrame)
        bullets_wrap.setStyleSheet("""
            QFrame {
                border-radius: 16px;
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.05);
            }
        """)
        bw_l = QVBoxLayout(bullets_wrap)
        bw_l.setContentsMargins(18, 14, 18, 14)
        bw_l.setSpacing(0)

        bullets = QLabel(
            "• 7-day progress per deck (done vs target)\n"
            "• Clear above/below target feedback\n"
            "• Filter by deck (or view total)\n"
            "• Unlimited deadlines (Premium)"
        )
        bullets.setWordWrap(True)
        bullets.setStyleSheet("color: rgba(230,232,235,0.92); background: transparent; border: none;")
        bw_l.addWidget(bullets)

        # CTA
        cta = QPushButton("Unlock Premium – Support development")
        cta.setCursor(Qt.CursorShape.PointingHandCursor)
        cta.setMinimumHeight(42)
        cta.setStyleSheet("""
            QPushButton {
                background: rgba(255, 90, 165, 0.95);
                color: white;
                border: 1px solid rgba(255, 90, 165, 0.55);
                border-radius: 12px;
                font-weight: 900;
            }
            QPushButton:hover { background: rgba(255, 63, 152, 0.98); }
        """)

        # Hint (no background/border)
        hint = QLabel(
            "Already bought Premium?\n"
            "Open Deckline settings → Premium tab and paste your code."
        )
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        hint.setStyleSheet("color: rgba(169,175,183,0.90); background: transparent; border: none;")

        def _open_kofi() -> None:
            QDesktopServices.openUrl(QUrl("https://ko-fi.com/s/d708f4b514"))

        cta.clicked.connect(_open_kofi)

        # Assemble card
        card_l.addWidget(title)
        card_l.addWidget(desc)
        card_l.addWidget(bullets_wrap)
        card_l.addSpacing(4)
        card_l.addWidget(cta)
        card_l.addWidget(hint)

        # Center card
        row = QWidget()
        row_l = QHBoxLayout(row)
        row_l.setContentsMargins(0, 0, 0, 0)
        row_l.addStretch(1)
        row_l.addWidget(card, 0)
        row_l.addStretch(1)

        card.setMaximumWidth(560)
        card.setMinimumWidth(520)

        lay.addStretch(1)
        lay.addWidget(row, 0)
        lay.addStretch(1)

        return root



    # ----------------------------
    # Premium chart logic
    # ----------------------------
    def _load_decks(self) -> None:
        dm = DeadlineMgr()
        dm.refresh()
        decks = list(dm.deadlines or [])

        self._deck_ids = [int(d.deck_id) for d in decks]
        self.deckBox.clear()

        self.deckBox.addItem("All deadlines (sum)", -1)
        for d in decks:
            self.deckBox.addItem(str(d.name), int(d.deck_id))

    def _refresh_and_render(self) -> None:
        dm = DeadlineMgr()
        dm.refresh()
        for s in (dm.deadlines or []):
            try:
                log_daily_snapshot_for_deck(s)
            except Exception:
                continue
        self._render()

    def _render(self) -> None:
        did = int(self.deckBox.currentData() or -1)

        # ----------------------------
        # ✅ Total streaks across ALL decks
        # (active decks + total streak days)
        # ----------------------------
        active_decks = 0
        total_days = 0
        try:
            for x in (self._deck_ids or []):
                entries_x = get_daily_log_entries(int(x))
                s = int(calculate_current_streak(entries_x) or 0)
                if s > 0:
                    active_decks += 1
                    total_days += s
        except Exception:
            active_decks = 0
            total_days = 0

        if hasattr(self, "totalStreakLabel"):
            if total_days > 0:
                self.totalStreakLabel.setText(f"🔥 {active_decks} active · {total_days} days")
            else:
                self.totalStreakLabel.setText("")

        # ----------------------------
        # Chart data
        # ----------------------------
        if did == -1:
            series_list = [get_daily_log_entries(x) for x in self._deck_ids]
            entries = _sum_series(series_list)
            points = _build_7day_window(entries)
            title = "All deadlines (sum)"
        else:
            entries = get_daily_log_entries(did)
            points = _build_7day_window(entries)
            try:
                title = mw.col.decks.name(did)
            except Exception:
                title = f"Deck {did}"

        self.chart.set_data(title, points)





def open_deckline_stats_dialog() -> None:
    dlg = DecklineStatsDialog(mw)
    dlg.exec()
