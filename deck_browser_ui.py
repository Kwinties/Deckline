# deck_browser_ui.py
import html
from datetime import timedelta
from aqt import mw
from aqt.qt import QDate

from ..core import (
    DeadlineDb,
    DeadlineMgr,
    DeadlineStats,
    _is_skip_day,
    _count_study_days,
    _planned_remaining_cards,
    _quota_today_constant,
    reviews_today_for_deck,
    revlog_entries_today_for_deck,
    new_cards_started_today_for_deck,
    done_today_for_target,
    apply_daily_target_override,
    total_progress_pill_web,
    deck_accent_rgba,
    get_deckline_ui_state,

    # ✅ add these
    get_daily_log_entries,
    log_daily_snapshot_for_deck,
    calculate_current_streak,
)


addon_package = mw.addonManager.addonFromModule(__name__)
base_url = f"/_addons/{addon_package}"


def _html_title(text: str) -> str:
    """
    Convert multiline tooltip text to something that works inside HTML title="...".
    - Escape quotes/&/< > safely
    - Convert \n to &#10; so the browser shows line breaks in tooltips
    """
    t = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    t = html.escape(t, quote=True)
    return t.replace("\n", "&#10;")


def _tempo_badge(text: str, *, tone: str) -> str:
    """
    Calm pill badge:
    - low background opacity
    - no inner shadow
    - status communicated mainly via bright dot + slightly tinted text
    tone: 'ok' | 'late' | 'rest' | 'wait'
    """
    if tone == "ok":
        bg = "rgba(34,197,94,0.09)"
        fg = "rgba(187,247,208,0.95)"   # a bit softer than before
        dot = "rgba(34,197,94,0.98)"
    elif tone == "late":
        bg = "rgba(239,68,68,0.09)"
        fg = "rgba(254,202,202,0.95)"
        dot = "rgba(239,68,68,0.98)"
    elif tone == "wait":
        bg = "rgba(59,130,246,0.09)"
        fg = "rgba(191,219,254,0.95)"
        dot = "rgba(59,130,246,0.98)"
    else:  # rest
        bg = "rgba(148,163,184,0.08)"
        fg = "rgba(226,232,240,0.92)"
        dot = "rgba(148,163,184,0.95)"

    return (
        "<span style='"
        "display:inline-flex;"
        "align-items:center;"
        "gap:8px;"
        "padding:2px 10px;"
        "border-radius:999px;"
        "font-size:12px;"
        "font-weight:750;"
        "letter-spacing:.2px;"
        f"background:{bg};"
        "border:1px solid rgba(255,255,255,0.06);"
        f"color:{fg};"
        "'>"
        f"<span style='width:8px;height:8px;border-radius:999px;background:{dot};display:inline-block;'></span>"
        f"{text}"
        "</span>"
    )



def _render_card(
    dl: DeadlineStats,
    original_name: str,
    cutoff_tooltip: str,
    pending_value: int,
    pending_phase_label: str,
    streak_days: int,
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
    *,
    cutoff_date,
    study_days_to_cutoff: int,
    study_days_to_deadline: int,
    today_is_skip: bool,
) -> str:
    db = DeadlineDb()

    # ✅ Streak pill (minimal, left of tempo)
    show_streaks = bool(getattr(db, "enable_streaks", False))
    if show_streaks:
        streak_html = (
            "<span "
            "title='Daily target streak' "
            "style=\"display:inline-flex;align-items:center;gap:6px;"
            "margin-right:10px;padding:2px 8px;border-radius:999px;"
            "font-size:12px;font-weight:750;letter-spacing:.2px;"
            "background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.06);"
            "color:rgba(255,206,120,0.92);\""
            f">🔥 {int(streak_days or 0)}</span>"
        )
    else:
        streak_html = ""

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

    # Phase (NEW / REVIEW) + tooltip (more specific)
    is_new_phase = (phase_short == "🌱")

    cutoff_s = cutoff_date.strftime("%d-%m-%Y")
    deadline_s = dl.deadline.strftime("%d-%m-%Y")

    if is_new_phase:
        phase_label = "NEW"
        phase_class = "phase-new"

        if today_is_skip:
            switch_line = f"Phase switches after your next study day (Cutoff: {cutoff_s})"
        else:
            switch_line = f"Phase switches in {max(int(study_days_to_cutoff), 0)} study day(s) (Cutoff: {cutoff_s})"

        phase_tooltip = (
            "PHASE 1 — NEW (before cutoff)\n"
            f"{switch_line}\n"
            "\n"
            "Goal:\n"
            "• Review (blue/red) new cards before the cutoff.\n"
            "\n"
            "Today counts as:\n"
            "• New cards STARTED today (first-ever review today)."
        )
    else:
        phase_label = "REVIEW"
        phase_class = "phase-review"

        if today_is_skip:
            end_line = f"Deadline after your next study day (Deadline: {deadline_s})"
        else:
            end_line = f"Deadline in {max(int(study_days_to_deadline), 0)} study day(s) (Deadline: {deadline_s})"

        phase_tooltip = (
            "PHASE 2 — REVIEW (after cutoff)\n"
            f"{end_line}\n"
            f"Cutoff was: {cutoff_s}\n"
            "\n"
            "Goal:\n"
            "• Finish remaining (green) young cards before the deadline.\n"
            "\n"
            "Today counts as:\n"
            "• DISTINCT cards reviewed today."
        )

    pending_tooltip = f"Pending cards: {pending_value}"

    today_tooltip = (
        "Today\n"
        f"- Done: {today_done}\n"
        f"- Target: {quota_today}\n"
        f"- {percent_today}% of today's target"
    )

    # ---- Time estimate (clean) ----
    time_html = ""
    if bool(getattr(dl, "hasEstimate", False)) and (not bool(getattr(dl, "hide_target", False))):
        hours_per_day = float(getattr(dl, "todoTime", 0.0) or 0.0)
        mult = float(getattr(db, "time_multiplier", 1.0) or 1.0)

        mins = int(round(hours_per_day * 60.0 * mult))
        if mins > 0:
            h = mins // 60
            m = mins % 60

            if h > 0:
                t = f"{h}h {m:02d}m/day" if m else f"{h}h/day"
            else:
                t = f"{m}m"

            tooltip = (
                "Estimated time needed per day.\n"
                "Based on your recent average review speed in this deck.\n"
                f"Multiplier: {mult:.2f}×"
            )

            time_html = (
                "<span class='deckline-dot'>•</span>"
                f"<span class='deckline-time' title='{_html_title(tooltip)}'>"
                f"⏱ {t}</span>"
            )

    accent = deck_accent_rgba(dl.deck_id)
    icon_bg = accent["bg"]
    icon_bar = accent["bar"]
    deck_fill = accent["solid"]
    bubble_bg = accent["bg"]

    if dl.hide_target:
        bubble_bg = "rgba(255,255,255,0.06)"

    tone_class = "tone-ok"
    if tempo_tone == "late":
        tone_class = "tone-late"
    elif tempo_tone == "rest":
        tone_class = "tone-rest"
    elif tempo_tone == "wait":
        tone_class = "tone-wait"

    deck_name_safe = html.escape(dl.name or "deck")

    icon_html = (
        f"<div class='deckline-icon {tone_class}' "
        f"role='button' tabindex='0' "
        f"title='Open Deckline settings' "
        f"onclick='pycmd(\"deadlineSettings:{dl.deck_id}\"); return false;' "
        f"onkeydown='if(event.key===\"Enter\"||event.key===\" \"){{pycmd(\"deadlineSettings:{dl.deck_id}\"); return false;}}' "
        f"style='background:{icon_bg}; --deckbar:{icon_bar}; cursor:pointer;' "
        f"aria-label='Open Deckline settings for {deck_name_safe}'"
        f"></div>"
    )

    pill = total_progress_pill_web(
        progress_total,
        db,
        disabled=bool(dl.hide_target),
        variant="bubble",
        fill_override=deck_fill,
    )

    # ✅ IMPORTANT: close all divs properly (prevents layout "leaking")
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
          <span class="deckline-phase {phase_class}" title="{_html_title(phase_tooltip)}">
            {phase_label}
          </span>
        </div>

        <div class="deckline-sub2">
          <span class="deckline-meta" title="{_html_title(pending_tooltip)}">Pending <b>{pending_value}</b></span>
          <span class="deckline-dot">•</span>
          <span class="deckline-meta" title="{_html_title(today_tooltip)}">Today <b>{today_done}/{quota_today}</b></span>
          {time_html}
        </div>
      </div>

      <div class="deckline-right">
        <div class="deckline-bubble" style="background:{bubble_bg};" title="{_html_title(progress_tooltip)}">
          <span class="deckline-pct">{progress_total_percent}%</span>
          {pill}
        </div>

        <div class="deckline-status" title="{_html_title(tempo_title)}">
          {streak_html}{tempo_badge_html}
        </div>
      </div>
    </div>
    """.replace("\n", "")


def display_footer(deck_browser, content) -> None:
    # Only render Deckline cards in the Deck Browser
    try:
        if not mw.state == "deckBrowser":
            return
    except Exception:
        return

    dm = DeadlineMgr()
    dm.refresh()
    deadlines = dm.deadlines
    db = DeadlineDb()

        # --- Premium: stats button ---
    stats_button_html = ""
    try:
        # --- Stats button: always opens stats dialog.
        # The dialog itself will show either the chart (premium) or the paywall (free).
        if db.is_premium:
            stats_icon = "📈"
            stats_title = "Open Stats"
        else:
            stats_icon = "🔒"
            stats_title = "Stats locked (Premium)"
    
        stats_button_html = (
            "<button class='deckline-topbtn deckline-topbtn-stats' "
            f"title='{stats_title}' "
            "onclick='pycmd(\"deckline_ui:open_stats:\")'>"
            f"{stats_icon}</button>"
        )

    except Exception:
        # If premium flag is missing for any reason, default to locked button
        stats_button_html = (
            "<button class='deckline-topbtn deckline-topbtn-stats' "
            "onclick='pycmd(\"deckline_ui:upgrade:\")'>🔒</button>"
        )

    ui = get_deckline_ui_state()
    focus_mode = bool(ui.get("focus_mode", False))
    focused_did = ui.get("focused_did", None)
    sort_mode = (ui.get("sort_mode", "deadline") or "deadline").lower()
    only_behind = bool(ui.get("only_behind", False))
    # Default so we never crash even if the HTML is built earlier by accident
    focus_label = "All"


    res = f"<link rel='stylesheet' type='text/css' href='{base_url}/deckline.css'>"

    # Cursor fix for clickable deck links
    res += (
        "<style>"
        ".deadline-deck-link{color:inherit;text-decoration:none;font-weight:normal;cursor:pointer;}"
        ".deadline-deck-link:hover{text-decoration:underline;}"
        "</style>"
    )

    # ---- Minimal topbar CSS (keep it compact to avoid quote mistakes) ----
    # ---- Topbar + dropdown CSS ----
    res += (
        "<style>"
        ".deckline-dropdown{position:relative;display:inline-block;}"
        
        ".deckline-dropdown-button{"
        "display:flex;"                
        "align-items:center;"
        "gap:8px;"
        "height:26px;"
        "padding:3px 10px;"
        "border-radius:999px;"
        "background:rgba(255,255,255,.06);"
        "border:1px solid rgba(255,255,255,.10);"
        "color:rgba(230,232,235,.95);"
        "font-size:12px;"
        "font-weight:750;"
        "cursor:pointer;"
        "user-select:none;"
        "max-width:130px;"               
        "}"


        ".deckline-dd-text{"
        "flex:1 1 auto;"
        "min-width:0;"
        "overflow:hidden;"
        "text-overflow:ellipsis;"
        "white-space:nowrap;"
        "}"
        
        ".deckline-dd-arrow{"
        "flex:0 0 auto;"
        "opacity:.75;"
        "}"

        ".deckline-dropdown-button:hover{background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.14);}"

        ".deckline-dropdown-menu{"
        "display:none;"
        "position:absolute;"
        "top:34px;"
        "right:0;"
        "min-width:190px;"
        "max-width:260px;"
        "padding:6px;"
        "background:rgba(32,32,32,.94);"
        "border:1px solid rgba(255,255,255,.08);"
        "border-radius:14px;"
        "box-shadow:0 14px 36px rgba(0,0,0,.48);"
        "backdrop-filter:blur(12px);"
        "z-index:1000;"
        "}"
        ".deckline-dropdown-menu.open{display:block;}"

        ".deckline-dropdown-item{"
        "padding:8px 8px;"
        "font-size:12px;"
        "font-weight:750;"
        "color:rgba(230,232,235,.95);"
        "cursor:pointer;"
        "text-align:left;"
        "white-space:nowrap;"
        "overflow:hidden;"
        "text-overflow:ellipsis;"
        "border-radius:5px;"
        "display:flex;"
        "align-items:center;"
        "justify-content:space-between;"
        "gap:10px;"
        "}"
        ".deckline-dropdown-item:hover{background:rgba(255,255,255,.08);}"
        ".deckline-dropdown-divider{height:1px;margin:6px 6px;background:rgba(255,255,255,.08);}"
        ".deckline-dropdown-header{padding:8px 8px;font-size:11px;font-weight:850;letter-spacing:.6px;text-transform:uppercase;color:rgba(230,232,235,.55);cursor:default;user-select:none;}"
        ".deckline-dropdown-check{opacity:.95;color:rgba(230,232,235,.9);font-weight:900;}"

        ".deckline-topbar-title{"
        "font-size:20px;"
        "font-weight:700;"
        "letter-spacing:.6px;"
        "color:rgba(230,232,235,.98);"
        "text-align:left;"
        "margin-bottom:8px;"
        "padding-left:6px;"
        "}"
        
        ".deckline-topbtn{display:inline-flex;align-items:center;gap:8px;height:26px;padding:3px 10px;border-radius:999px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.10);color:rgba(230,232,235,.95);font-size:12px;font-weight:750;cursor:pointer;white-space:nowrap;user-select:none;}"
        ".deckline-topbtn:hover{background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.14);}"
        ".deckline-topbtn-stats{padding:3px 8px;}"



        ".deckline-cards{margin:14px auto 8px;max-width:600px;}"
        ".deckline-topbar{margin:0 0 8px 0;padding:8px 10px;border-radius:16px;"
        "background:linear-gradient(180deg,rgba(60,60,60,.45),rgba(45,45,45,.45));"
        "border:1px solid rgba(255,255,255,.06);box-shadow:0 6px 14px rgba(0,0,0,.28);}"

        ".deckline-topbar-row{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:nowrap;}"
        ".deckline-stats{display:flex;align-items:center;gap:10px;flex-wrap:nowrap;font-size:12px;color:rgba(169,175,183,.95);"
        "flex:1 1 auto;min-width:0;}"
        ".deckline-stat{display:inline-flex;align-items:center;gap:6px;height:26px;padding:0 10px;border-radius:999px;"
        "background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.06);font-weight:700;letter-spacing:.2px;}"
        ".deckline-stat b{color:rgba(230,232,235,.95);font-weight:900;}"
        ".deckline-stat-dot{width:10px;height:10px;border-radius:999px;display:inline-block;flex:0 0 auto;}"
        ".deckline-stat-dot-blue{background:rgba(59,130,246,0.95);box-shadow:0 0 0 2px rgba(59,130,246,0.18);}"
        ".deckline-stat-dot-red{background:rgba(239,68,68,0.95);box-shadow:0 0 0 2px rgba(239,68,68,0.18);}"
       ".deckline-stat-dot-green{background:rgba(34,197,94,0.95);box-shadow:0 0 0 2px rgba(34,197,94,0.18);}"


        ".deckline-controls{display:flex;align-items:center;gap:6px;flex-wrap:nowrap;justify-content:flex-end;flex:0 0 auto;}"

        ".deckline-card{display:flex;align-items:center;justify-content:space-between;gap:16px;"
        "padding:16px 18px;margin:0 0 10px 0;border-radius:18px;"
        "background:linear-gradient(180deg,rgba(60,60,60,.55),rgba(45,45,45,.55));"
        "border:1px solid rgba(255,255,255,.06);box-shadow:0 10px 22px rgba(0,0,0,.35);}"

        ".deckline-left{min-width:0;flex:1 1 auto;padding-top:1px;}"
        ".deckline-right{display:flex;flex-direction:column;align-items:flex-end;justify-content:flex-start;gap:6px;"
        "min-width:210px;flex:0 0 auto;padding-top:1px;}"

        ".deckline-title{font-size:16px;font-weight:850;color:rgba(230,232,235,.95);margin-bottom:4px;"
        "text-align:left;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.15;}"

        ".deckline-sub1,.deckline-sub2{font-size:12px;color:rgba(169,175,183,.95);display:flex;flex-wrap:wrap;"
        "gap:6px;align-items:center;line-height:1.2;}"
        ".deckline-sub1{margin-bottom:3px;}"
        ".deckline-dot{opacity:.55;margin:0 2px;}"

        ".deckline-phase{"
        "font-size:11px;"
        "letter-spacing:.6px;"
        "padding:2px 8px;"
        "border-radius:999px;"
        "font-weight:700;"
        "border:1px solid rgba(255,255,255,.10);"
        "background:transparent;"
        "}"
        
        ".phase-new{"
        "color:rgba(148,163,184,.95);"
        "}"
        
        ".phase-review{color:#A7BFB5;}"



        ".deckline-meta b{color:rgba(230,232,235,.95);font-weight:850;}"
        ".deckline-time{color:rgba(200,205,212,.95);font-weight:750;}"
        ".deckline-time b{color:rgba(230,232,235,.95);font-weight:850;}"

        ".deckline-bubble{display:inline-flex;align-items:center;gap:10px;padding:8px 14px;border-radius:999px;"
        "border:1px solid rgba(255,255,255,.02);box-shadow:0 2px 8px rgba(0,0,0,.10);width:fit-content;}"

        ".deckline-pct{display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:500;color:rgba(230,232,235,.96);"
        "line-height:1;white-space:nowrap;letter-spacing:.2px;}"

        ".deckline-icon{width:34px;height:34px;border-radius:10px;position:relative;flex:0 0 auto;overflow:hidden;"
        "display:flex;align-items:center;justify-content:center;"
        "box-shadow:inset 0 1px 0 rgba(255,255,255,.08),0 8px 16px rgba(0,0,0,.25);}"

        ".deckline-icon::before{content:'';position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);"
        "width:16px;height:4px;border-radius:999px;background:var(--deckbar,rgba(255,255,255,.40));"
        "box-shadow:0 7px 0 var(--deckbar,rgba(255,255,255,.34)),0 -7px 0 var(--deckbar,rgba(255,255,255,.28));}"
        "</style>"
    )



    if not deadlines:
        content.stats = (res + "<p>No upcoming deadlines!</p>") + (content.stats or "")
        return

    # ---- Build rows ----
    rows = []
    today = QDate.currentDate().toPyDate()

    for dl in deadlines:
                # ✅ always initialize (prevents UnboundLocalError)
        streak_days = 0

        cutoff_date = dl.deadline + timedelta(days=dl.cutoff_offset)

        today_is_skip = _is_skip_day(today, dl.skip_weekends, dl.skip_dates)
        start_count = today if not today_is_skip else (today + timedelta(days=1))

        study_days_to_cutoff = _count_study_days(start_count, cutoff_date, dl.skip_weekends, dl.skip_dates)
        study_days_to_deadline = _count_study_days(start_count, dl.deadline, dl.skip_weekends, dl.skip_dates)

        if today < cutoff_date:
            cutoff_tooltip = (
                f"Your deadline is due on {dl.deadline.strftime('%d-%m-%Y')}\n"
                f"New cards should be finished in {study_days_to_cutoff} days"
            )
        else:
            cutoff_tooltip = (
                f"Your deadline is due on {dl.deadline.strftime('%d-%m-%Y')}\n"
                f"Young cards should be finished in {max(study_days_to_deadline, 0)} days"
            )

        new = int(getattr(dl, "new", 0) or 0)
        young = int(getattr(dl, "young", 0) or 0)
        mature = int(getattr(dl, "mature", 0) or 0)

        expected_total, planned_remaining = _planned_remaining_cards(dl)
        learning_phase = (today < cutoff_date) and ((new > 0) or (planned_remaining > 0))
        pending_value = new if learning_phase else (young + new)

        done_today = done_today_for_target(dl) or 0

        if learning_phase:
            remaining_now = new
            remaining_effective = (new + planned_remaining) if expected_total > 0 else new
            remaining_days = max(study_days_to_cutoff, 1)
        else:
            remaining_now = young + new
            remaining_effective = young
            remaining_days = max(study_days_to_deadline, 1)

        quota_raw = _quota_today_constant(remaining_effective, remaining_days, done_today)
        quota_today = quota_raw
        if not learning_phase:
            quota_today = int(quota_today) + int(new or 0)

        if expected_total > 0:
            quota_today = min(quota_today, max(0, remaining_now + done_today))
        if today_is_skip and not dl.hide_target:
            quota_today = 0

        quota_today, _override_active = apply_daily_target_override(
            stats=dl,
            quota_today=quota_today,
            remaining_now=remaining_now,
            done_today=done_today,
            today_is_skip=(today_is_skip and not dl.hide_target),
        )

        if quota_today <= 0:
            percent_today = 0 if today_is_skip else (100 if done_today > 0 else 0)
        else:
            percent_today = int(min(done_today / quota_today, 1) * 100)

        # behind logic
        if dl.hide_target or today_is_skip:
            is_behind = False
        else:
            is_behind = (done_today < int(quota_today))

        # tempo badge/title (reuse your existing helper)
        if dl.hide_target:
            tempo_tone = "wait"
            tempo_badge = _tempo_badge("PENDING", tone="wait")
            tempo_title = "Studying not started yet."
        elif today_is_skip:
            tempo_tone = "rest"
            tempo_badge = _tempo_badge("REST", tone="rest")
            tempo_title = "Rest day."
        else:
            if is_behind:
                tempo_tone = "late"
                tempo_badge = _tempo_badge("BEHIND", tone="late")
                tempo_title = "Behind today"
            else:
                tempo_tone = "ok"
                tempo_badge = _tempo_badge("ON TRACK", tone="ok")
                tempo_title = "On track today ✅"

        denom_real = new + young + mature
        denom_expected = denom_real
        if new > 0 and expected_total and expected_total > 0:
            denom_expected = max(int(expected_total), denom_real)

        started = young + mature
        bar_percent = int(round(max(0.0, min(1.0, float(getattr(dl, "progress", 0.0) or 0.0))) * 100))
        if new > 0:
            progress_tooltip = f"Total progress: {bar_percent}%\nNew cards learned: {started}/{denom_expected}"
        else:
            progress_tooltip = f"Total progress: {bar_percent}%\nYoung cards learned: {mature}/{denom_real}"

        deck = mw.col.decks.get(dl.deck_id, default=None)
        original_name = deck["name"] if deck else dl.name
        phase_short = "🌱" if learning_phase else "🔁"

        p_total = max(0.0, min(1.0, float(getattr(dl, "progress", 0.0) or 0.0)))
        p_total_pct = int(round(p_total * 100))
        
        # ---- Time estimate minutes/day (for sorting) ----
        mins_today_est = 0
        if bool(getattr(dl, "hasEstimate", False)) and (not bool(getattr(dl, "hide_target", False))):
            hours_per_day = float(getattr(dl, "todoTime", 0.0) or 0.0)
            mult = float(getattr(db, "time_multiplier", 1.0) or 1.0)
            mins_today_est = int(round(hours_per_day * 60.0 * mult))
            if mins_today_est < 0:
                mins_today_est = 0
                
        # ✅ ensure today's daily-log snapshot exists, then compute current streak
        streak_days = 0
        if bool(getattr(db, "enable_streaks", False)):
            try:
                log_daily_snapshot_for_deck(dl)
                entries = get_daily_log_entries(int(dl.deck_id))
                streak_days = int(calculate_current_streak(entries) or 0)
            except Exception:
                streak_days = 0



        rows.append({
            "dl": dl,
            "original_name": original_name,
            "cutoff_tooltip": cutoff_tooltip,
            "pending_value": pending_value,
            "phase_short": phase_short,
            "today_done": done_today,
            "quota_today": int(quota_today),
            "percent_today": int(percent_today),
            "tempo_badge_html": tempo_badge,
            "tempo_tone": tempo_tone,
            "tempo_title": tempo_title,
            "progress_total": p_total,
            "progress_total_percent": p_total_pct,
            "progress_tooltip": progress_tooltip,
            "mins_today_est": int(mins_today_est),
            "is_behind": bool(is_behind),
            "streak_days": int(streak_days),
            "cutoff_date": cutoff_date,
            "study_days_to_cutoff": int(study_days_to_cutoff),
            "study_days_to_deadline": int(study_days_to_deadline),
            "today_is_skip": bool(today_is_skip),

        })

    # focus filter
    visible = rows
    if focus_mode:
        try:
            fdid = int(focused_did) if focused_did is not None else None
        except Exception:
            fdid = None
        if fdid:
            visible = [r for r in visible if int(r["dl"].deck_id) == int(fdid)]

    # only behind filter
    if only_behind:
        visible = [r for r in visible if r["is_behind"]]

    # sorting
    if sort_mode == "name":
        visible.sort(key=lambda r: (r["dl"].name or "").lower())
    elif sort_mode == "progress":
        visible.sort(key=lambda r: float(r["progress_total"]), reverse=True)
    elif sort_mode == "today":
        visible.sort(key=lambda r: int(r["percent_today"]))
    elif sort_mode == "time":
        # Most time per day -> least time per day
        # Decks without estimate should go to the bottom.
        visible.sort(
            key=lambda r: (
                0 if int(r.get("mins_today_est", 0)) > 0 else 1,   # estimated first
                -int(r.get("mins_today_est", 0)),                  # then high -> low
            )
        )
    else:
        visible.sort(key=lambda r: int(getattr(r["dl"], "daysLeft", 0)))


    # stats
    total_n = len(visible)
    behind_n = sum(1 for r in visible if r["is_behind"])
    ontrack_n = sum(1 for r in visible if (not r["is_behind"]) and (not r["dl"].hide_target))
    pending_n = sum(1 for r in visible if bool(getattr(r["dl"], "hide_target", False)))


    # ---- Sort dropdown ----
    sort_labels = {
        "deadline": "Deadline",
        "name": "Name",
        "progress": "Progress",
        "today": "Today",
        "time": "Time estimate",
    }


    sort_label = sort_labels.get(sort_mode, "Deadline")

    def _dd_item(label: str, cmd: str, active: bool) -> str:
        check = "<span class='deckline-dropdown-check'>✓</span>" if active else "<span></span>"
        return (
            "<div class='deckline-dropdown-item' "
            f"onclick='pycmd(\"{cmd}\")'>"
            f"<span>{label}</span>{check}</div>"
        )
        
    def _dd_header(label: str) -> str:
        return f"<div class='deckline-dropdown-header'>{html.escape(label)}</div>"


    sort_select_html = (
        "<div class='deckline-dropdown'>"
          f"<div class='deckline-dropdown-button'>"
          f"<span class='deckline-dd-text'>Sort: {html.escape(sort_label)}</span>"
          f"<span class='deckline-dd-arrow'>▾</span>"
          f"</div>"
          "<div class='deckline-dropdown-menu'>"
            + _dd_item("Deadline", "deckline_ui:set_sort:deadline", sort_mode == "deadline")
            + _dd_item("Name", "deckline_ui:set_sort:name", sort_mode == "name")
            + _dd_item("Progress", "deckline_ui:set_sort:progress", sort_mode == "progress")
            + _dd_item("Today", "deckline_ui:set_sort:today", sort_mode == "today")
            + _dd_item("Time estimate", "deckline_ui:set_sort:time", sort_mode == "time")
          + "</div>"
        "</div>"
    )



    # ---- Filter dropdown (All / Only behind / Decks) ----
    filter_value = "all"
    try:
        if only_behind:
            filter_value = "behind"
        elif focus_mode and focused_did is not None:
            filter_value = f"deck:{int(focused_did)}"
    except Exception:
        filter_value = "all"

    # Build deck list from ALL rows so you can switch decks even if filtered
    deck_opts = []
    for r in rows:
        did = int(r["dl"].deck_id)
        name = html.escape(r["dl"].name or f"Deck {did}")
        deck_opts.append((did, name))
    deck_opts.sort(key=lambda x: x[1].lower())

    # Focus label for button (compute real label)
    focus_label = "All"
    if only_behind:
        focus_label = "Behind"
    elif focus_mode and focused_did is not None:
        try:
            fdid = int(focused_did)
            nm = next((name for did, name in deck_opts if did == fdid), None)
            if nm:
                focus_label = html.unescape(nm)
        except Exception:
            focus_label = "All"

    # Deck items for dropdown
    deck_items_html = "".join(
        _dd_item(
            name,
            f"deckline_ui:set_filter:deck:{did}",
            (focus_mode and (focused_did is not None) and int(focused_did) == did),
        )
        for did, name in deck_opts
    )


    filter_select_html = (
        "<div class='deckline-dropdown'>"
          "<div class='deckline-dropdown-button'>"
            f"<span class='deckline-dd-text'>Focus: {html.escape(focus_label)}</span>"
            "<span class='deckline-dd-arrow'>▾</span>"
          "</div>"
          "<div class='deckline-dropdown-menu'>"
            + _dd_item("All", "deckline_ui:set_filter:all", (not only_behind and not focus_mode))
            + _dd_item("Behind", "deckline_ui:set_filter:behind", bool(only_behind))
            + "<div class='deckline-dropdown-divider'></div>"
            + deck_items_html +
          "</div>"
        "</div>"
    )


    
    # Close dropdowns on outside click + keep only one open
    res += (
        "<script>"
        "document.addEventListener('click', function(e){"
        "  const btn = e.target.closest('.deckline-dropdown-button');"
        "  const dd = e.target.closest('.deckline-dropdown');"
        "  document.querySelectorAll('.deckline-dropdown-menu.open').forEach(function(m){"
        "    if(!dd || m !== dd.querySelector('.deckline-dropdown-menu')){"
        "      m.classList.remove('open');"
        "    }"
        "  });"
        "  if(btn){"
        "    const menu = btn.nextElementSibling;"
        "    if(menu){ menu.classList.toggle('open'); }"
        "    e.stopPropagation();"
        "  }"
        "});"
        "</script>"
    )

    total_tt = _html_title("Total deadlines currently visible after filtering.")
    behind_tt = _html_title("Decks that are currently behind today's target.")
    ontrack_tt = _html_title("Decks that have met today's target.")
    pending_tt = _html_title("Total pending cards across the shown decks.")


    # header + topbar
    res += (
        "<div class='deckline-cards'>"
        "<div class='deckline-topbar'>"
          "<div class='deckline-topbar-title'>Deckline</div>"
          "<div class='deckline-topbar-row'>"
            "<div class='deckline-stats'>"
              f"<span class='deckline-stat' title='{total_tt}'>📅<b>{total_n}</b></span>"
              f"<span class='deckline-stat' title='{behind_tt}'><span class='deckline-stat-dot deckline-stat-dot-red'></span><b>{behind_n}</b></span>"
              f"<span class='deckline-stat' title='{ontrack_tt}'><span class='deckline-stat-dot deckline-stat-dot-green'></span><b>{ontrack_n}</b></span>"
              f"<span class='deckline-stat deckline-stat-pending' title='{pending_tt}'><span class='deckline-stat-dot deckline-stat-dot-blue'></span><b>{pending_n}</b></span>"
            "</div>"
            "<div class='deckline-controls'>"
              f"{filter_select_html}"
              f"{sort_select_html}"
              f"{stats_button_html}"
            "</div>"
          "</div>"
        "</div>"
    )


    if not visible:
        res += (
            "<div style='padding:12px 14px;border-radius:14px;background:rgba(255,255,255,.04);"
            "border:1px solid rgba(255,255,255,.06);color:rgba(169,175,183,.95);font-size:12px;"
            "font-weight:700;text-align:center;margin-bottom:14px;'>"
            "No decks match the current filter."
            "</div>"
        )

    for r in visible:
        dl = r["dl"]
        res += _render_card(
            dl=dl,
            original_name=r["original_name"],
            cutoff_tooltip=r["cutoff_tooltip"],
            pending_value=r["pending_value"],
            pending_phase_label="",
            phase_short=r["phase_short"],
            today_done=r["today_done"],
            quota_today=r["quota_today"],
            percent_today=r["percent_today"],
            tempo_badge_html=r["tempo_badge_html"],
            tempo_tone=r["tempo_tone"],
            tempo_title=r["tempo_title"],
            progress_total=r["progress_total"],
            progress_total_percent=r["progress_total_percent"],
            progress_tooltip=r["progress_tooltip"],
            cutoff_date=r["cutoff_date"],
            study_days_to_cutoff=r["study_days_to_cutoff"],
            study_days_to_deadline=r["study_days_to_deadline"],
            today_is_skip=r["today_is_skip"],
            streak_days=r.get("streak_days", 0),

        )


    res += "</div>"
    content.stats = res + (content.stats or "")


