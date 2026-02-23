import math
import json
import os
import html
from datetime import datetime, timedelta
from typing import NewType, Optional, Any
from aqt import gui_hooks, mw
from aqt.qt import *
from aqt.utils import showInfo
from aqt.qt import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLineEdit, QDateEdit,
    QSpinBox, QCheckBox, QPushButton, QHBoxLayout, QSizePolicy, Qt
)
from .ui import deck_progress_bar
from .ui import review_progress_bar
from .ui.deck_browser_ui import display_footer
from .clear_deadlines import clear_selected_deadlines
from .settings import DeadlinerDialog
from .core import (
    DeadlineDb, 
    DeadlineMgr, 
    DeadlineStats, 
    findDeadlines,
    _deck_ids_str, 
    _today_epoch_ms_range,
    reviews_today_for_deck, 
    revlog_entries_today_for_deck, 
    new_cards_started_today_for_deck,
    _is_skip_day, 
    _count_study_days,
    _planned_remaining_cards, 
    _quota_today_constant,
    _progress_color,
    refreshDeadliner,
    avg_hours_per_learning_review,
    done_today_for_target,
    apply_daily_target_override,
    total_progress_pill_web,
    deck_accent_rgba,
    progress_fill_web,
    fill_to_transparent_rgba,
    get_deckline_ui_state,
    toggle_focus_mode,
    set_focused_deck_id,
    set_sort_mode,
    get_deckline_ui_state,
    log_daily_snapshots_for_all_deadlines
)


# =========================
# Deck browser UI
# =========================
addon_package = mw.addonManager.addonFromModule(__name__)
base_url = f"/_addons/{addon_package}"



def _render_card(
    dl: DeadlineStats,
    original_name: str,
    cutoff_tooltip: str,
    pending_value: int,
    pending_phase_label: str,
    phase_short: str,
    today_done: int,
    quota_today: int,
    percent_today: int,
    tempo_badge_html: str,
    tempo_tone: str,
    tempo_title: str,
    progress_total: float,
    progress_total_percent: int,
    progress_tooltip: str,
) -> str:
    # Clean deadline label
    if dl.daysLeft < 0:
        deadline_text = "Overdue"
        deadline_color = "#F87171"
    elif dl.daysLeft == 0:
        deadline_text = "Today"
        deadline_color = "rgba(230,232,235,0.95)"
    elif dl.daysLeft == 1:
        deadline_text = "in 1 day"
        deadline_color = "rgba(169,175,183,0.95)"
    else:
        deadline_text = f"in {dl.daysLeft} days"
        deadline_color = "rgba(169,175,183,0.95)"

    # Clickable deck name
    deck_link = f"""
        <span
           role="link"
           tabindex="0"
           onclick='pycmd("deadlineOpen:{dl.deck_id}"); return false;'
           onkeydown='if(event.key==="Enter"||event.key===" "){{pycmd("deadlineOpen:{dl.deck_id}"); return false;}}'
           class="deadline-deck-link">
           {dl.name}
        </span>"""

    # Tooltips (use \n here; we'll convert to HTML-friendly in title="")
    if phase_short == "Phase 1":
        phase_tooltip = (
            "Phase 1: You are still introducing and learning new cards."
        )
    else:
        phase_tooltip = (
            "Phase 2: You are now focusing on reviewing young cards."
        )

    pending_tooltip = f"Pending cards: {pending_value}"

    today_tooltip = (
        "Today\n"
        f"- Done: {today_done}\n"
        f"- Target: {quota_today}\n"
        f"- {percent_today}% of today's target"
    )

    accent = deck_accent_rgba(dl.deck_id)
    icon_bg = accent["bg"]
    icon_bar = accent["bar"]
    deck_fill = accent["solid"]   # non-transparent accent for the bar fill
    bubble_bg = accent["bg"]      # transparent accent for the bubble background

    # If studying hasn't started, keep bubble neutral
    if dl.hide_target:
        bubble_bg = "rgba(255,255,255,0.06)"

    # Icon tone (left)
    tone_class = "tone-ok"
    if tempo_tone == "late":
        tone_class = "tone-late"
    elif tempo_tone == "rest":
        tone_class = "tone-rest"
    elif tempo_tone == "wait":
        tone_class = "tone-wait"

    icon_html = (
        f"<div class='deckline-icon {tone_class}' "
        f"style='background:{icon_bg}; --deckbar:{icon_bar};' "
        f"aria-hidden='true'></div>"
    )
    

    # Progress pill
    pill = total_progress_pill_web(
        progress_total,
        DeadlineDb(),
        disabled=bool(dl.hide_target),
        variant="bubble",
        fill_override=deck_fill,
    )

    return f"""
    <div class="deckline-card">
      {icon_html}

      <div class="deckline-left">
        <div class="deckline-title" title="{_html_title(original_name)}">{deck_link}</div>

        <div class="deckline-sub1">
          <span class="deckline-deadline" style="color:{deadline_color};" title="{_html_title(cutoff_tooltip)}">
            Deadline {deadline_text}
          </span>
          <span class="deckline-dot">•</span>
          <span class="deckline-phase" title="{_html_title(phase_tooltip)}">{phase_short}</span>
        </div>

        <div class="deckline-sub2">
          <span class="deckline-meta" title="{_html_title(pending_tooltip)}">Pending <b>{pending_value}</b></span>
          <span class="deckline-dot">•</span>
          <span class="deckline-meta" title="{_html_title(today_tooltip)}">Today <b>{today_done}/{quota_today}</b></span>
        </div>
      </div>

      <div class="deckline-right">
        <div class="deckline-bubble" style="background:{bubble_bg};" title="{_html_title(progress_tooltip)}">
          <span class="deckline-pct">{progress_total_percent}%</span>
          {pill}
        </div>

        <div class="deckline-status" title="{_html_title(tempo_title)}">
          {tempo_badge_html}
        </div>
      </div>
    </div>
    """.replace("\n", "")


# =========================
# Custom pycmd handler (Deck Assesment)
# =========================
def on_js_message(handled: tuple[bool, Any], message: str, context: Any):
    """
    Intercepts the 'pycmd("deadlineOpen:ID")' message sent by the HTML,
    selects the corresponding deck and switches to the Overview view.

    On some macOS/QtWebEngine builds, switching views inside the web callback
    can hard-crash the app. We defer navigation a bit longer to let QtWebEngine
    finish handling the click/focus/accessibility machinery.
    """
    # --- Deckline UI actions (topbar) ---
    # --- Deckline UI actions (topbar) ---
    if message.startswith("deckline_ui:"):
        # message format: "deckline_ui:<action>:<value>"
        parts = message.split(":", 2)
        action = parts[1] if len(parts) > 1 else ""
        value = parts[2] if len(parts) > 2 else ""

        if action == "open_stats":
            try:
                from .ui.stats_dialog import open_deckline_stats_dialog
                open_deckline_stats_dialog()
            except Exception as e:
                print(f"Deckline stats dialog error: {e}")
            return (True, None)


        if action == "upgrade":
            try:
                from aqt.qt import QDesktopServices, QUrl
                QDesktopServices.openUrl(QUrl("https://ko-fi.com/s/d708f4b514"))
            except Exception as e:
                print(f"Deckline upgrade openUrl error: {e}")
            return (True, None)

        if action == "toggle_focus":
            toggle_focus_mode()
            refreshDeadliner()
            return (True, None)

        if action == "set_focus":
            try:
                did = int(value)
            except Exception:
                did = None
            set_focused_deck_id(did)
            refreshDeadliner()
            return (True, None)

        if action == "clear_focus":
            set_focused_deck_id(None)
            refreshDeadliner()
            return (True, None)

        if action == "set_sort":
            set_sort_mode(value or "deadline")
            refreshDeadliner()
            return (True, None)

        if action == "toggle_behind":
            from .core import toggle_only_behind  # local import avoids circular surprises
            toggle_only_behind()
            refreshDeadliner()
            return (True, None)

        if action == "set_filter":
            from .core import set_only_behind, set_focus_mode

            v = (value or "").strip()

            if v == "all":
                set_only_behind(False)
                set_focus_mode(False)
                set_focused_deck_id(None)
                refreshDeadliner()
                return (True, None)

            if v == "behind":
                set_only_behind(True)
                set_focus_mode(False)
                set_focused_deck_id(None)
                refreshDeadliner()
                return (True, None)

            if v.startswith("deck:"):
                try:
                    did = int(v.split(":", 1)[1])
                except Exception:
                    did = None

                set_only_behind(False)
                if did:
                    set_focus_mode(True)
                    set_focused_deck_id(did)
                else:
                    set_focus_mode(False)
                    set_focused_deck_id(None)

                refreshDeadliner()
                return (True, None)

        return (True, None)

    if message.startswith("deadlineSettings:"):
        try:
            deck_id = int(message.split(":", 1)[1])
    
            if not mw.col.decks.get(deck_id, default=None):
                return (True, None)
    
            def _open():
                try:
                    DeadlinerDialog(deck_id).exec()
                except Exception as e:
                    print(f"Deckline error opening settings: {e}")
    
            # Defer a bit (same reason as deadlineOpen)
            QTimer.singleShot(150, _open)
            return (True, None)
    
        except Exception as e:
            print(f"Deckline error parsing deadlineSettings: {e}")
            return (True, None)


    if not message.startswith("deadlineOpen:"):
        return handled

    try:
        deck_id = int(message.split(":")[1])

        # Validate deck exists
        if not mw.col.decks.get(deck_id, default=None):
            return (True, None)

        def _go():
            try:
                mw.col.decks.select(deck_id)

                # Prefer moveToState if available (often safer), else fallback.
                move = getattr(mw, "moveToState", None)
                if callable(move):
                    move("overview")
                else:
                    mw.onOverview()
            except Exception as e:
                print(f"Deckline error opening deck (deferred): {e}")

        # Give WebEngine time to fully finish the click handling on macOS
        QTimer.singleShot(150, _go)
        return (True, None)

    except Exception as e:
        print(f"Deckline error opening deck: {e}")
        return (True, None)



# =========================
# Final warning (3 days left)
# =========================
def show_final_deadline_warning():
    db = DeadlineDb()
    shown_path = os.path.join(mw.pm.profileFolder(), "deadliner_warned_once.json")

    try:
        with open(shown_path, "r", encoding="utf-8") as f:
            shown_log = json.load(f)
    except Exception:
        shown_log = {}

    for deck_id_str, cfg in db.deadlines.items():
        if not cfg.get("enabled", False):
            continue

        try:
            deadline = datetime.strptime(cfg["deadline"], "%d-%m-%Y").date()
        except Exception:
            continue

        days_left = (deadline - datetime.today().date()).days

        if days_left == 3 and shown_log.get(deck_id_str) != "shown":
            deck_name = cfg.get("name", "this deck")
            showInfo(f"Your exam for <b>{deck_name}</b> is in 3 days.<br><br><i>Time to focus!</i>")
            shown_log[deck_id_str] = "shown"

    try:
        with open(shown_path, "w", encoding="utf-8") as f:
            json.dump(shown_log, f)
    except Exception:
        pass


# =========================
# Init
# =========================
def on_init():
    review_progress_bar.setup()
    deck_progress_bar.setup()

    # Log 1 snapshot per deck per day (cheap: it no-ops if already logged today)
    try:
        log_daily_snapshots_for_all_deadlines()
    except Exception as e:
        print(f"Deckline daily log error: {e}")

    refreshDeadliner()
    show_final_deadline_warning()

    # NEW: show changelog once after updating to Deckline v1.0
    try:
        from .changelog import maybe_show_changelog
        maybe_show_changelog(delay_ms=700)
    except Exception as e:
        print(f"Deckline changelog startup error: {e}")


# =========================
# Hooks
# =========================
def on_deck_browser_will_show_options_menu(menu, deck_id):
    menu.addSeparator()
    action = menu.addAction("Deadline")
    action.triggered.connect(lambda _, deck_id=deck_id: DeadlinerDialog(deck_id).exec())
    clear_selected_action = menu.addAction("Clear")
    clear_selected_action.triggered.connect(clear_selected_deadlines)


gui_hooks.deck_browser_will_show_options_menu.append(on_deck_browser_will_show_options_menu)
gui_hooks.deck_browser_will_render_content.append(display_footer)
gui_hooks.main_window_did_init.append(on_init)
gui_hooks.webview_did_receive_js_message.append(on_js_message)


# =========================
# Tools menu: Deckline Settings
# =========================
def _open_deckline_global_settings() -> None:
    """
    Open Deckline settings without tying it to a specific deck.
    We pass the current deck id just to construct the dialog,
    but the user will use only global tabs (Feedback / Premium).
    """
    try:
        current = mw.col.decks.current()
        did = current["id"] if current else None
        if did is None:
            return

        dlg = DeadlinerDialog(did, global_mode=True)


        # Default to Feedback tab (global settings)
        try:
            dlg.tabs.setCurrentIndex(2)  # 0=Deadline, 1=Optional, 2=Feedback
        except Exception:
            pass

        dlg.exec()

    except Exception as e:
        print(f"Deckline global settings error: {e}")


def _add_deckline_to_tools_menu() -> None:
    """
    Add 'Deckline settings' to Anki Tools menu.
    """
    try:
        action = QAction("Deckline settings", mw)
        action.triggered.connect(_open_deckline_global_settings)
        mw.form.menuTools.addAction(action)
    except Exception as e:
        print(f"Deckline menu injection error: {e}")


# Register after main window is ready
gui_hooks.main_window_did_init.append(_add_deckline_to_tools_menu)
