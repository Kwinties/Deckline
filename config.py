# core/config.py
from typing import NewType

from aqt import mw
from typing import Optional


# =========================
# Types / Constants
# =========================
CardQueue = NewType("CardQueue", int)

QUEUE_TYPE_NEW = CardQueue(0)
QUEUE_TYPE_SUSPENDED = CardQueue(-1)

CFG_KEY = "deadliner_cfg"

# =========================
# UI State (Deckline topbar etc.)
# =========================
_UI_KEY = "deckline_ui"

def get_deckline_ui_state() -> dict:
    """
    Returns a dict of UI state for the Deckline UI:
      - focus_mode: bool
      - focused_did: int | None
      - sort_mode: str
      - only_behind: bool
    """
    cfg = mw.col.get_config(CFG_KEY, default=None) or {}
    ui = cfg.get(_UI_KEY) or {}
    if not isinstance(ui, dict):
        ui = {}

    # defaults (keep stable keys)
    if "focus_mode" not in ui:
        ui["focus_mode"] = False
    if "focused_did" not in ui:
        ui["focused_did"] = None
    if "sort_mode" not in ui:
        ui["sort_mode"] = "deadline"
    if "only_behind" not in ui:
        ui["only_behind"] = False

    return ui


def set_deckline_ui_state(patch: dict) -> None:
    cfg = mw.col.get_config(CFG_KEY, default=None) or {}
    ui = cfg.get(_UI_KEY) or {}
    if not isinstance(ui, dict):
        ui = {}

    ui.update(patch or {})
    cfg[_UI_KEY] = ui
    mw.col.set_config(CFG_KEY, cfg)


def toggle_focus_mode() -> bool:
    ui = get_deckline_ui_state()
    new_val = not bool(ui.get("focus_mode", False))

    # If turning OFF focus mode, also clear the focused deck.
    if not new_val:
        set_deckline_ui_state({"focus_mode": False, "focused_did": None})
    else:
        set_deckline_ui_state({"focus_mode": True})

    return new_val
  
def set_focus_mode(enabled: bool) -> None:
    enabled = bool(enabled)
    if not enabled:
        # turning off focus also clears selected deck
        set_deckline_ui_state({"focus_mode": False, "focused_did": None})
    else:
        set_deckline_ui_state({"focus_mode": True})



def set_focused_deck_id(did: "Optional[int]") -> None:
    set_deckline_ui_state({"focused_did": did})


def clear_focus() -> None:
    set_deckline_ui_state({"focused_did": None})


def set_sort_mode(mode: str) -> None:
    set_deckline_ui_state({"sort_mode": (mode or "deadline").lower()})


def toggle_only_behind() -> bool:
    ui = get_deckline_ui_state()
    new_val = not bool(ui.get("only_behind", False))
    set_deckline_ui_state({"only_behind": new_val})
    return new_val


def set_only_behind(v: bool) -> None:
    set_deckline_ui_state({"only_behind": bool(v)})


# =========================
# DB / Config
# =========================
class DeadlineDb:
    def __init__(self):
        self.db = mw.col.get_config(CFG_KEY, default=None)
        if not self.db:
            self.db = {}

        # Defaults (keep backwards compatibility with older configs)
        self.db.setdefault("deadlines", {})
        self.db.setdefault("premium", False)
        self.db.setdefault("version", 1)
        self.db.setdefault("progress_style", "Bar + Percentage")
        self.db.setdefault("show_today_row", True)
        self.db.setdefault("enable_streaks", False)

        # Overview / overview-like daily progress bar (deck overview page)
        self.db.setdefault("show_daily_progress", True)

        # Reviewer bottom progress bar (review screen)
        self.db.setdefault("show_review_progress", True)
        # Celebration (rainbow) when hitting 100% in reviewer
        self.db.setdefault("show_celebration", True)
        self.db.setdefault("time_multiplier", 1.0)

        # Shared progress fill style for both bars
        self.db.setdefault(
            "progress_fill",
            {
                "mode": "auto",  # auto | solid | gradient
                "solid": "#22C55E",
                "gradient": ["#EF4444", "#F59E0B", "#22C55E"],
            },
        )

        self.deadlines = self.db.get("deadlines", {})

        # prune non-existing decks
        for k in list(self.deadlines.keys()):
            try:
                did = int(k)
            except Exception:
                del self.deadlines[k]
                continue
            if not mw.col.decks.get(did, default=False):
                del self.deadlines[k]

    # global flags
    @property
    def progress_style(self) -> str:
        return self.db.get("progress_style", "Bar + Percentage")

    @progress_style.setter
    def progress_style(self, v: str) -> None:
        self.db["progress_style"] = v

    @property
    def show_today_row(self) -> bool:
        return bool(self.db.get("show_today_row", True))

    @show_today_row.setter
    def show_today_row(self, v: bool) -> None:
        self.db["show_today_row"] = bool(v)

    @property
    def enable_streaks(self) -> bool:
        return bool(self.db.get("enable_streaks", False))

    @enable_streaks.setter
    def enable_streaks(self, v: bool) -> None:
        self.db["enable_streaks"] = bool(v)

    @property
    def show_daily_progress(self) -> bool:
        return bool(self.db.get("show_daily_progress", True))

    @show_daily_progress.setter
    def show_daily_progress(self, v: bool) -> None:
        self.db["show_daily_progress"] = bool(v)

    @property
    def show_review_progress(self) -> bool:
        return bool(self.db.get("show_review_progress", True))

    @show_review_progress.setter
    def show_review_progress(self, v: bool) -> None:
        self.db["show_review_progress"] = bool(v)

    @property
    def show_celebration(self) -> bool:
        return bool(self.db.get("show_celebration", True))

    @show_celebration.setter
    def show_celebration(self, v: bool) -> None:
        self.db["show_celebration"] = bool(v)

    @property
    def time_multiplier(self) -> float:
        try:
            v = float(self.db.get("time_multiplier", 1.0) or 1.0)
        except Exception:
            v = 1.0
        return max(0.1, min(v, 10.0))

    @time_multiplier.setter
    def time_multiplier(self, v: float) -> None:
        try:
            vf = float(v)
        except Exception:
            vf = 1.0
        self.db["time_multiplier"] = max(0.1, min(vf, 10.0))
    
    @property
    def is_premium(self) -> bool:
        return bool(self.db.get("premium", False))

    @is_premium.setter
    def is_premium(self, value: bool) -> None:
        self.db["premium"] = bool(value)

    
    def save(self) -> None:
        self.db["deadlines"] = self.deadlines
        mw.col.set_config(CFG_KEY, self.db)
