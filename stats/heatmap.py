from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from aqt.qt import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    Qt,
    QTimer,
    QVBoxLayout,
    QWidget,
)


_GRID_COLS = 7
_CARD_TARGET_WIDTH = 260
_DAY_LABELS = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


def _heatmap_span() -> List[date]:
    total_days = 35  # 5 weeks
    today = date.today()
    this_monday = today - timedelta(days=today.weekday())
    # Keep current week as the 4th row: 3 weeks before + current + 1 week after.
    start = this_monday - timedelta(weeks=3)
    return [start + timedelta(days=i) for i in range(total_days)]


@dataclass
class HeatmapDeckData:
    deck_id: int
    name: str
    start_date: Optional[date]
    deadline: Optional[date]
    cutoff_offset: int
    entries: List[dict]


class HeatmapDayCell(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("decklineHeatmapCell")
        self.setFixedSize(24, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class DecklineHeatmapWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.content = QWidget()
        self.cards_grid = QGridLayout(self.content)
        self.cards_grid.setContentsMargins(6, 6, 6, 6)
        self.cards_grid.setHorizontalSpacing(10)
        self.cards_grid.setVerticalSpacing(10)
        self.cards_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.scroll.setWidget(self.content)
        root.addWidget(self.scroll, 1)

        self._decks: List[HeatmapDeckData] = []
        self._rebuild_scheduled = False
        self._last_cols = 0

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if not self._decks:
            return

        cols = max(1, self.scroll.viewport().width() // _CARD_TARGET_WIDTH)
        if cols != self._last_cols:
            self._schedule_rebuild()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if self._decks:
            self._schedule_rebuild()

    def set_decks(self, decks: List[HeatmapDeckData]) -> None:
        self._decks = list(decks or [])
        self._schedule_rebuild()

    def _schedule_rebuild(self) -> None:
        if self._rebuild_scheduled:
            return
        self._rebuild_scheduled = True
        QTimer.singleShot(0, self._rebuild_cards)

    def _clear_cards(self) -> None:
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

    def _rebuild_cards(self) -> None:
        self._rebuild_scheduled = False
        self.setUpdatesEnabled(False)
        self._clear_cards()

        if not self._decks:
            lbl = QLabel("No deck deadlines found.")
            lbl.setStyleSheet("color: rgba(205,208,214,0.92);")
            self.cards_grid.addWidget(lbl, 0, 0)
            self._last_cols = 0
            self.setUpdatesEnabled(True)
            return

        viewport_w = max(1, self.scroll.viewport().width(), self.scroll.width(), self.width())
        cols = max(1, viewport_w // _CARD_TARGET_WIDTH)
        self._last_cols = cols

        for idx, deck in enumerate(self._decks):
            row = idx // cols
            col = idx % cols
            card = self._build_deck_card(deck)
            self.cards_grid.addWidget(card, row, col)

        for c in range(cols):
            self.cards_grid.setColumnStretch(c, 1)

        rows = (len(self._decks) + cols - 1) // cols
        self.cards_grid.setRowStretch(rows, 1)
        self.setUpdatesEnabled(True)

    @staticmethod
    def _phase_for_day(day: date, raw_phase: str, deck: HeatmapDeckData) -> str:
        phase = str(raw_phase or "").lower()
        if day < (deck.start_date or day):
            return "pending"
        if phase and phase != "pending":
            return phase

        if deck.deadline:
            cutoff_date = deck.deadline + timedelta(days=int(deck.cutoff_offset or -5))
            return "new" if day < cutoff_date else "review"

        return "new"

    def _build_deck_card(self, deck: HeatmapDeckData) -> QWidget:
        card = QFrame()
        card.setObjectName("decklineHeatmapCard")
        card.setMinimumWidth(_CARD_TARGET_WIDTH - 8)
        card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        card.setStyleSheet(
            "#decklineHeatmapCard {"
            " border: 1px solid rgba(255,255,255,0.08);"
            " border-radius: 12px;"
            " background: rgba(255,255,255,0.03);"
            "}"
        )

        lay = QVBoxLayout(card)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(4)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        title = QLabel(deck.name)
        title.setStyleSheet("font-size: 16px; font-weight: 800; color: rgba(235,237,240,0.96);")
        title.setWordWrap(False)
        title.setToolTip(deck.name)
        header.addWidget(title, 1)

        span = _heatmap_span()
        span_txt = f"{span[0].strftime('%d %b')} → {span[-1].strftime('%d %b')}"
        subtitle = QLabel(span_txt)
        subtitle.setStyleSheet("color: rgba(169,175,183,0.94); font-size: 11px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        subtitle.setMinimumWidth(0)
        header.addWidget(subtitle, 0)

        lay.addLayout(header)

        grid_wrap = QWidget()
        grid = QGridLayout(grid_wrap)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(6)

        label_style = "color: rgba(169,175,183,0.90); font-size: 10px;"

        for col in range(_GRID_COLS):
            day_lbl = QLabel(_DAY_LABELS[col])
            day_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            day_lbl.setStyleSheet(label_style)
            day_lbl.setFixedWidth(22)
            grid.addWidget(day_lbl, 0, col + 1)

        entry_map = self._entry_map(deck.entries)
        streak_ord = self._streak_ordinals(deck.entries)
        today = date.today()

        for idx, day in enumerate(span):
            row = idx // _GRID_COLS
            col = idx % _GRID_COLS

            if col == 0:
                week_lbl = QLabel(str(day.isocalendar()[1]))
                week_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                week_lbl.setStyleSheet(label_style)
                week_lbl.setFixedWidth(18)
                grid.addWidget(week_lbl, row + 1, 0)

            if (deck.start_date and day < deck.start_date) or (deck.deadline and day > deck.deadline):
                empty = QWidget(grid_wrap)
                empty.setFixedSize(18, 18)
                grid.addWidget(empty, row + 1, col + 1)
                continue

            dkey = day.isoformat()
            e = entry_map.get(dkey, {})

            done = int(e.get("done", 0) or 0)
            target = int(e.get("target", 0) or 0)
            phase = self._phase_for_day(day, str(e.get("phase", "") or ""), deck)

            is_deadline = bool(deck.deadline and deck.deadline == day)
            is_today = day == today

            fill = self._fill_color(done=done, target=target, phase=phase)
            border = self._border_color(is_deadline=is_deadline, is_today=is_today)
            hover_border = self._hover_border(is_deadline=is_deadline, is_today=is_today)

            streak_txt = "-"
            if dkey in streak_ord:
                streak_txt = str(streak_ord[dkey])

            tip = (
                f"Date: {dkey}\n"
                f"Done: {done}\n"
                f"Target: {target}\n"
                f"Phase: {phase.upper()}\n"
                f"Streak day: {streak_txt}"
            )
            
            if is_deadline:
                tip = f"{tip}\nDEADLINE"

            border_width = 2 if is_today else 1

            cell = HeatmapDayCell(grid_wrap)
            cell.setToolTip(tip)
            cell.setStyleSheet(
                "#decklineHeatmapCell {"
                f" background: {fill};"
                f" border: {border_width}px solid {border};"
                " border-radius: 4px;"
                "}"
                "#decklineHeatmapCell:hover {"
                f" border: {border_width}px solid {hover_border};"
                "}"
            )
            
            if is_deadline:
                deadline_emoji = QLabel("🚨", cell)
                deadline_emoji.setAlignment(Qt.AlignmentFlag.AlignCenter)
                deadline_emoji.setGeometry(0, 0, cell.width(), cell.height())
                deadline_emoji.setStyleSheet("background: transparent; font-size: 11px;")
                deadline_emoji.show()


            grid.addWidget(cell, row + 1, col + 1)

        grid_wrap.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        lay.addWidget(grid_wrap, 0, Qt.AlignmentFlag.AlignHCenter)
        lay.addWidget(self._build_legend_row(), 0, Qt.AlignmentFlag.AlignHCenter)
        return card

    @staticmethod
    def _legend_item(color: str, label: str) -> QWidget:
        item = QWidget()
        row = QHBoxLayout(item)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)

        swatch = QFrame(item)
        swatch.setFixedSize(10, 10)
        swatch.setStyleSheet(
            "background: " + color + "; border: 1px solid rgba(255,255,255,0.15); border-radius: 3px;"
        )

        txt = QLabel(label, item)
        txt.setStyleSheet("color: rgba(169,175,183,0.92); font-size: 10px;")

        row.addWidget(swatch, 0)
        row.addWidget(txt, 0)
        return item

    def _build_legend_row(self) -> QWidget:
        legend = QWidget()
        row = QHBoxLayout(legend)
        row.setContentsMargins(0, 2, 0, 0)
        row.setSpacing(8)

        row.addWidget(self._legend_item("rgba(34,197,94,0.92)", "Done"), 0)
        row.addWidget(self._legend_item("rgba(250,204,21,0.92)", "Partial"), 0)
        row.addWidget(self._legend_item("rgba(239,68,68,0.92)", "Miss"), 0)
        row.addWidget(self._legend_item("rgba(148,163,184,0.55)", "No target/rest"), 0)
        return legend
      
    @staticmethod
    def _entry_map(entries: List[dict]) -> Dict[str, dict]:
        out: Dict[str, dict] = {}
        for e in entries or []:
            if not isinstance(e, dict):
                continue
            d = str(e.get("date", "") or "")
            if d:
                out[d] = e
        return out

    @staticmethod
    def _fill_color(done: int, target: int, phase: str) -> str:
        ph = (phase or "").lower()

        if target <= 0:
            return "rgba(148,163,184,0.55)"
        if ph == "rest":
            return "rgba(148,163,184,0.55)"

        if done >= target:
            return "rgba(34,197,94,0.92)"
        if done > 0:
            return "rgba(250,204,21,0.92)"
        return "rgba(239,68,68,0.92)"

    @staticmethod
    def _border_color(is_deadline: bool, is_today: bool) -> str:
        if is_deadline:
            return "rgba(239,68,68,0.98)"
        if is_today:
            return "rgba(59,130,246,0.95)"  # blue highlight for today
        return "rgba(255,255,255,0.0)"  # remove all other borders

    @staticmethod
    def _hover_border(is_deadline: bool, is_today: bool) -> str:
        if is_deadline:
            return "rgba(239,68,68,1.0)"
        if is_today:
            return "rgba(96,165,250,1.0)"
        return "rgba(255,255,255,0.0)"

    @staticmethod
    def _streak_ordinals(entries: List[dict]) -> Dict[str, int]:
        if not entries:
            return {}

        by_date: Dict[str, dict] = {}
        for e in entries:
            if isinstance(e, dict) and e.get("date"):
                by_date[str(e.get("date"))] = e

        cur = date.today()
        streak_dates: List[str] = []

        for _ in range(3650):
            key = cur.isoformat()
            e = by_date.get(key)
            if not e:
                break

            done = int(e.get("done", 0) or 0)
            target = int(e.get("target", 0) or 0)

            if target <= 0:
                cur = cur - timedelta(days=1)
                continue

            if done >= target:
                streak_dates.append(key)
                cur = cur - timedelta(days=1)
                continue

            break

        streak_dates.reverse()
        return {d: i + 1 for i, d in enumerate(streak_dates)}


def _to_date(val) -> Optional[date]:
    if isinstance(val, date):
        return val
    if not val:
        return None

    s = str(val)
    for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            continue
    return None


def make_heatmap_deck_data(
    deck_id: int,
    deck_name: str,
    deck_deadline: Optional[str],
    entries: List[dict],
    deck_start_date: Optional[str] = None,
    deck_cutoff_offset: int = -5,
) -> HeatmapDeckData:
    return HeatmapDeckData(
        deck_id=int(deck_id),
        name=str(deck_name),
        start_date=_to_date(deck_start_date),
        deadline=_to_date(deck_deadline),
        cutoff_offset=int(deck_cutoff_offset or -5),
        entries=list(entries or []),
    )
