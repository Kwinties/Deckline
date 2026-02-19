from __future__ import annotations

from datetime import timedelta, date
from typing import Optional
import time
import colorsys

from aqt import gui_hooks, mw
from aqt.qt import (
    QDockWidget,
    QProgressBar,
    QWidget,
    QVBoxLayout,
    Qt,
    QSizePolicy,
    QSplitter,
    QTimer,
)

from ..core import (
    DeadlineDb,
    DeadlineMgr,
    _is_skip_day,
    _count_study_days,
    _planned_remaining_cards,
    _quota_today_constant,
    done_today_for_target,
    progress_fill_qt,
    apply_daily_target_override,
    deck_accent_rgba,
    phase_split_fill_qt,
)


# -------------------------
# Internal singleton widget
# -------------------------
_DOCK: Optional[QDockWidget] = None
_BAR: Optional[QProgressBar] = None

_BAR_BASE_QSS = """
QProgressBar {
    border: 0px;
    background: rgba(255,255,255,0.10);
    border-radius: 7px;
    color: rgba(230,232,235,0.95);
    font-size: 11px;
    text-align: center;
    margin: 0px;
    padding: 0px;
}
QProgressBar::chunk {
    border-radius: 7px;
    margin: 0px;
}
"""

# -------------------------
# Celebration state (rainbow)
# -------------------------
_CELEBRATION_TIMER: Optional[QTimer] = None
_CELEBRATION_ACTIVE: bool = False
_CELEBRATION_START_MONO: float = 0.0
_CELEBRATED_KEY: Optional[str] = None  # "YYYY-MM-DD:deck_id"
_LAST_PERCENT: int = 0


def _set_bar_fill_css(fill_css: str) -> None:
    """Apply chunk background quickly."""
    global _BAR
    if _BAR is None:
        return
    _BAR.setStyleSheet(_BAR_BASE_QSS + f"\nQProgressBar::chunk {{ background: {fill_css}; }}\n")


def _stop_celebration() -> None:
    global _CELEBRATION_TIMER, _CELEBRATION_ACTIVE
    if _CELEBRATION_TIMER is not None:
        try:
            _CELEBRATION_TIMER.stop()
        except Exception:
            pass
    _CELEBRATION_ACTIVE = False


def _maybe_start_celebration(deck_id: int, percent: int) -> None:
    """
    Start rainbow animation for ~3 seconds when we hit 100% for the first time today (per deck).
    """
    global _CELEBRATION_TIMER, _CELEBRATION_ACTIVE, _CELEBRATION_START_MONO, _CELEBRATED_KEY, _LAST_PERCENT

    # Only when we CROSS into 100%
    crossed_to_100 = (percent >= 100 and _LAST_PERCENT < 100)
    _LAST_PERCENT = percent

    if not crossed_to_100:
        return

    today_key = f"{date.today().isoformat()}:{deck_id}"
    if _CELEBRATED_KEY == today_key:
        return

    _CELEBRATED_KEY = today_key

    # If already animating (rare), restart cleanly
    _stop_celebration()

    _CELEBRATION_ACTIVE = True
    _CELEBRATION_START_MONO = time.monotonic()

    if _CELEBRATION_TIMER is None:
        _CELEBRATION_TIMER = QTimer()
        _CELEBRATION_TIMER.setInterval(60)  # fast color changes

        def _tick() -> None:
            global _CELEBRATION_ACTIVE
            if _BAR is None or not _CELEBRATION_ACTIVE:
                return

            elapsed_ms = (time.monotonic() - _CELEBRATION_START_MONO) * 1000.0
            if elapsed_ms >= 3000.0:
                # End: revert to normal styling by re-running the bar update
                _stop_celebration()
                _update_bar()
                return

            # Rainbow: cycle hue quickly
            # 0..1 hue, ~10 full cycles over 3 seconds
            hue = (elapsed_ms / 300.0) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            hx = "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))

            _set_bar_fill_css(hx)

        _CELEBRATION_TIMER.timeout.connect(_tick)

    _CELEBRATION_TIMER.start()


def _redock_if_needed() -> None:
    """If our dock gets floated or moved, force it back to the bottom area."""
    global _DOCK
    if not _DOCK:
        return
    try:
        bottom = Qt.DockWidgetArea.BottomDockWidgetArea
        if _DOCK.isFloating() or mw.dockWidgetArea(_DOCK) != bottom:
            _DOCK.setFloating(False)
            mw.addDockWidget(bottom, _DOCK)
            _DOCK.show()
    except Exception:
        pass


def _find_deadline_ancestor_id(start_did: int) -> Optional[int]:
    """Return the nearest enabled parent deck id (or itself).

    Uses mw.col.decks.parents() when available, and falls back to
    name-splitting if that API is missing/behaves differently.
    """
    db = DeadlineDb()

    # check current deck
    cfg = db.deadlines.get(str(start_did))
    if cfg and cfg.get("enabled", False):
        return start_did

    # ---- Preferred: parents() API (if present) ----
    try:
        parents_fn = getattr(mw.col.decks, "parents", None)
        if callable(parents_fn):
            parents = parents_fn(start_did) or []
            for p in parents:
                pid = p.get("id") if isinstance(p, dict) else None
                if not pid:
                    continue
                pcfg = db.deadlines.get(str(pid))
                if pcfg and pcfg.get("enabled", False):
                    return int(pid)
            return None
    except Exception:
        # fall through to name-based fallback
        pass

    # ---- Fallback: split deck name by "::" and walk upwards ----
    try:
        full_name = mw.col.decks.name(start_did) or ""
        parts = full_name.split("::")
        for i in range(len(parts) - 1, 0, -1):
            parent_name = "::".join(parts[:i])
            pid = mw.col.decks.id(parent_name)
            if not pid:
                continue
            pcfg = db.deadlines.get(str(pid))
            if pcfg and pcfg.get("enabled", False):
                return int(pid)
    except Exception:
        pass

    return None



def _fix_splitter_handle_between_docks(dock_a: QDockWidget, dock_b: QDockWidget) -> None:
    """
    If two dock widgets are split vertically, Qt places them in an internal QSplitter.
    We find that splitter and make its handle effectively invisible.
    """
    try:
        w = dock_b.parentWidget()
        while w is not None:
            if isinstance(w, QSplitter):
                docks_inside = w.findChildren(QDockWidget)
                if dock_a in docks_inside and dock_b in docks_inside:
                    w.setHandleWidth(1)
                    w.setContentsMargins(0, 0, 0, 0)
                    w.setStyleSheet(
                        "QSplitter::handle { background: transparent; }"
                        "QSplitter::handle:horizontal { height: 1px; }"
                        "QSplitter::handle:vertical { width: 1px; }"
                    )
                    return
            w = w.parentWidget()
    except Exception:
        pass


def _force_hide_mainwindow_separators() -> None:
    """
    Hide dock separators WITHOUT breaking cursor behavior.
    """
    try:
        ss = mw.styleSheet() or ""
        marker = "/* deckline_force_hide_separators */"
        if marker in ss:
            return

        ss += "\n" + marker + "\n" + """
        QMainWindow::separator {
            background: transparent;
            width: 1px;
            height: 1px;
            margin: 0px;
            padding: 0px;
        }
        """
        mw.setStyleSheet(ss)
    except Exception:
        pass



def _ensure_dock() -> None:
    """Create a bottom-docked progress bar that spans full width (Shige-style)."""
    global _DOCK, _BAR
    if _DOCK is not None and _BAR is not None:
        return

    dock_area = Qt.DockWidgetArea.BottomDockWidgetArea

    existing = [
        w for w in mw.findChildren(QDockWidget)
        if mw.dockWidgetArea(w) == dock_area
    ]

    dock = QDockWidget(mw)
    dock.setObjectName("deadlinerReviewProgressDock")
    dock.setTitleBarWidget(QWidget())
    dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
    dock.setAllowedAreas(dock_area)

    dock.setStyleSheet("QDockWidget { border: 0px; padding: 0px; margin: 0px; }")

    bar = QProgressBar()
    bar.setTextVisible(True)
    bar.setMinimum(0)
    bar.setMaximum(100)
    bar.setValue(0)

    bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    bar.setFixedHeight(14)
    bar.setStyleSheet(_BAR_BASE_QSS)

    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    layout.addWidget(bar)
    dock.setWidget(container)

    mw.addDockWidget(dock_area, dock)

    if existing:
        mw.setDockNestingEnabled(True)
        mw.splitDockWidget(existing[0], dock, Qt.Orientation.Vertical)
        _fix_splitter_handle_between_docks(existing[0], dock)

    _redock_if_needed()
    _force_hide_mainwindow_separators()

    dock.hide()
    _DOCK, _BAR = dock, bar


def _hide() -> None:
    if _DOCK:
        _DOCK.hide()


def _show() -> None:
    if _DOCK:
        _DOCK.show()


def _update_bar() -> None:
    """Compute today's Deckline progress and update the bottom bar."""
    global _LAST_PERCENT

    if not mw.col:
        return

    _ensure_dock()
    if _BAR is None:
        return

    db = DeadlineDb()
    if not getattr(db, "show_review_progress", True):
        _hide()
        return

    try:
        current_deck_id = mw.col.decks.current()["id"]
    except Exception:
        _hide()
        return

    effective_deck_id = _find_deadline_ancestor_id(current_deck_id)
    if not effective_deck_id:
        _hide()
        return

    dm = DeadlineMgr()
    dm.refresh()
    stats = next((d for d in dm.deadlines if d.deck_id == effective_deck_id), None)
    if not stats or stats.hide_target:
        _hide()
        return

    py_today = __import__("aqt.qt").qt.QDate.currentDate().toPyDate()
    cutoff_date = stats.deadline + timedelta(days=stats.cutoff_offset)

    skip_weekends = bool(getattr(stats, "skip_weekends", False))
    skip_dates = getattr(stats, "skip_dates", set())
    today_is_skip = _is_skip_day(py_today, skip_weekends, skip_dates)
    start_count = py_today if not today_is_skip else (py_today + timedelta(days=1))

    expected_total, planned_remaining = _planned_remaining_cards(stats)
    learning_phase = (py_today < cutoff_date) and ((stats.new > 0) or (planned_remaining > 0))

    if learning_phase:
        remaining_now = stats.new
        remaining_effective = (stats.new + planned_remaining) if expected_total > 0 else stats.new
        remaining_days = max(_count_study_days(start_count, cutoff_date, skip_weekends, skip_dates), 1)
        existing_now = (
            int(getattr(stats, "mature", 0) or 0)
            + int(getattr(stats, "young", 0) or 0)
            + int(getattr(stats, "new", 0) or 0)
        )
        planning_active = (expected_total > 0) and (existing_now < expected_total)

        hint = (
            f"planned new • cutoff {cutoff_date.strftime('%d-%m-%Y')}"
            if planning_active
            else f"new • cutoff {cutoff_date.strftime('%d-%m-%Y')}"
        )
    else:
        remaining_now = int(getattr(stats, "young", 0) or 0) + int(getattr(stats, "new", 0) or 0)
        remaining_effective = remaining_now
        remaining_days = max(_count_study_days(start_count, stats.deadline, skip_weekends, skip_dates), 1)
        hint = f"young + new • deadline {stats.deadline.strftime('%d-%m-%Y')}"

    done_today = done_today_for_target(stats) or 0

    quota_raw = _quota_today_constant(remaining_effective, remaining_days, done_today)
    quota_today = quota_raw
    if expected_total > 0:
        quota_today = min(quota_today, max(0, remaining_now + done_today))
    if today_is_skip:
        quota_today = 0

    auto_quota_today = int(quota_today or 0)

    quota_today, override_active = apply_daily_target_override(
        stats=stats,
        quota_today=quota_today,
        remaining_now=remaining_now,
        done_today=done_today,
        today_is_skip=today_is_skip,
    )

    if quota_today <= 0:
        percent = 0 if today_is_skip else (100 if done_today > 0 else 0)
        denom_for_text = max(1, done_today) if not today_is_skip else 0
        label = "Rest day" if today_is_skip else f"{done_today} / {denom_for_text} (100%)"
    else:
        percent = int(min((done_today / quota_today) * 100, 100))
        label = f"{done_today} / {quota_today} ({percent}%)"

    _BAR.setMinimum(0)
    _BAR.setMaximum(100)
    _BAR.setValue(percent)
    _BAR.setFormat(label)

    # Normal fill (unless celebration is currently active)
    if not _CELEBRATION_ACTIVE:
        cfg = DeadlineDb()
        fill_css = progress_fill_qt(percent / 100.0, cfg)
    
        if fill_css:
            _set_bar_fill_css(fill_css)
        else:
            # auto mode → deck accent
            accent = deck_accent_rgba(effective_deck_id)
            _set_bar_fill_css(accent["solid"])


    planned_note = f" (planned {quota_raw})" if (expected_total > 0 and quota_today < quota_raw) else ""

    override_note = ""
    if override_active and not today_is_skip:
        delta = int(quota_today) - int(auto_quota_today)
        override_note = f" • Override: {quota_today} ({delta:+d} vs auto)" if delta else f" • Override: {quota_today}"

    target_short = "Rest day" if today_is_skip else f"Target: {quota_today}{planned_note}"
    _BAR.setToolTip(f"{target_short}{override_note} • {hint}")

    _force_hide_mainwindow_separators()
    _redock_if_needed()
    _show()

    if (not today_is_skip) and bool(getattr(db, "is_premium", False)) and bool(getattr(db, "show_celebration", True)):
        _maybe_start_celebration(effective_deck_id, percent)

# -------------------------
# Hooks
# -------------------------
def _on_reviewer_show_question(*_args) -> None:
    _update_bar()


def _on_reviewer_show_answer(*_args) -> None:
    _update_bar()


def _on_reviewer_will_end(*_args) -> None:
    _hide()
    _stop_celebration()

def refresh_visibility() -> None:
    """
    Apply current config immediately:
    - if enabled: update & show
    - if disabled: hide
    Safe to call anytime (also when not reviewing).
    """
    try:
        db = DeadlineDb()
        if getattr(db, "show_review_progress", True):
            _update_bar()
        else:
            _hide()
    except Exception:
        pass

def setup() -> None:
    gui_hooks.reviewer_did_show_question.append(_on_reviewer_show_question)
    gui_hooks.reviewer_did_show_answer.append(_on_reviewer_show_answer)
    gui_hooks.reviewer_will_end.append(_on_reviewer_will_end)

    try:
        db = DeadlineDb()
        if not getattr(db, "show_review_progress", True):
            _hide()
    except Exception:
        pass
