# deck_progress_bar.py
from __future__ import annotations

from datetime import timedelta

from aqt import gui_hooks, mw
from aqt.qt import QDate

from aqt.overview import Overview  # type hint only
from typing import Optional

from ..core import (
    DeadlineDb,
    DeadlineMgr,
    _is_skip_day,
    _count_study_days,
    _planned_remaining_cards,
    _quota_today_constant,
    _progress_color,
    done_today_for_target,
    progress_fill_web,
    apply_daily_target_override,
    deck_accent_rgba,
    phase_split_fill_web,
)


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


def inject_deadline_progress_bar(overview: Overview) -> None:
    try:
      deck = mw.col.decks.current()
      current_deck_id = deck["id"]
  
      db = DeadlineDb()
      if not db.show_daily_progress:
          overview.web.eval(
              "var n=document.getElementById('deadliner-daily-progress'); if(n){n.remove();}"
          )
          return
  
      effective_deck_id = _find_deadline_ancestor_id(current_deck_id)
      if not effective_deck_id:
          overview.web.eval(
              "var n=document.getElementById('deadliner-daily-progress'); if(n){n.remove();}"
          )
          return
  
      dm = DeadlineMgr()
      dm.refresh()
      stats = next((d for d in dm.deadlines if d.deck_id == effective_deck_id), None)
      if not stats or stats.hide_target:
          overview.web.eval(
              "var n=document.getElementById('deadliner-daily-progress'); if(n){n.remove();}"
          )
          return
  
      deck_id = effective_deck_id
  
      today = QDate.currentDate().toPyDate()
      cutoff_date = stats.deadline + timedelta(days=stats.cutoff_offset)
  
      # Skip days (weekends / vacations)
      skip_weekends = bool(getattr(stats, "skip_weekends", False))
      skip_dates = getattr(stats, "skip_dates", set())
      today_is_skip = _is_skip_day(today, skip_weekends, skip_dates)
      start_count = today if not today_is_skip else (today + timedelta(days=1))
  
      # 1) Remaining cards + remaining days
      expected_total, planned_remaining = _planned_remaining_cards(stats)
      learning_phase = (today < cutoff_date) and (
          (stats.new > 0) or (planned_remaining > 0)
      )
  
      if learning_phase:
          remaining_now = stats.new
          remaining_effective = (
              (stats.new + planned_remaining) if expected_total > 0 else stats.new
          )
          remaining_days = max(
              _count_study_days(start_count, cutoff_date, skip_weekends, skip_dates), 1
          )
          existing_now = int(getattr(stats, "mature", 0) or 0) + int(getattr(stats, "young", 0) or 0) + int(getattr(stats, "new", 0) or 0)
          planning_active = (expected_total > 0) and (existing_now < expected_total)
  
          hint = (
              f"NEW (planned) • cutoff {cutoff_date.strftime('%d-%m-%Y')}"
              if planning_active
              else f"NEW • cutoff {cutoff_date.strftime('%d-%m-%Y')}"
          )

      else:
          # After cutoff, leftover NEW cards still need to be finished.
          remaining_now = int(getattr(stats, "young", 0) or 0) + int(getattr(stats, "new", 0) or 0)
          remaining_effective = remaining_now
          remaining_days = max(
              _count_study_days(start_count, stats.deadline, skip_weekends, skip_dates), 1
          )
          hint = f"REVIEW • deadline {stats.deadline.strftime('%d-%m-%Y')}"


  
      # 2) Today's progress (MUST be before quota_today)
      done_today = done_today_for_target(stats) or 0
  
      # 3) Target today (constant during the day)
      quota_raw = _quota_today_constant(remaining_effective, remaining_days, done_today)
      quota_today = quota_raw
      if expected_total > 0:
          quota_today = min(quota_today, max(0, remaining_now + done_today))
  
      if today_is_skip:
          quota_today = 0

      # NEW: apply manual daily target override (per deck)
      quota_today, override_active = apply_daily_target_override(
          stats=stats,
          quota_today=quota_today,
          remaining_now=remaining_now,
          done_today=done_today,
          today_is_skip=today_is_skip,
      )

  
      # 4) Percent
      if quota_today <= 0:
          percent = 0.0 if today_is_skip else (1.0 if done_today > 0 else 0.0)
      else:
          percent = min(done_today / quota_today, 1.0)
  
      cfg = DeadlineDb()
      fill_css = progress_fill_web(percent, cfg)
      
      if fill_css:
          bar_color = fill_css
      else:
          accent = deck_accent_rgba(deck_id)
          bar_color = accent["solid"]

      percent_text = f"{int(percent * 100)}%"
      planned_note = (
          f" (planned {quota_raw})"
          if (expected_total > 0 and quota_today < quota_raw)
          else ""
      )
  
      # Top: only hint + date
      hint_label = f"Rest day (excluded) • {hint}" if today_is_skip else hint
      # Bottom right: only numeric target
      target_short = "Rest day" if today_is_skip else f"{planned_note}"
  
      # 5) HTML
      bar_html = f"""
      <div id="deadliner-daily-progress"
           style="
              margin:20px auto 20px;
              padding:14px 16px;
              max-width:600px;
              border-radius:14px;
              background: rgba(60, 60, 60, 0.5);
              border: 1px solid rgba(0,0,0,0.45);
           ">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;color:#E6E8EB;">
          <div style="font-weight:650;letter-spacing:.2px;">Daily Deckline Progress</div>
          <div style="font-size:12px;color:#A9AFB7;">{hint_label}</div>
        </div>
  
        <div style="
              position:relative;
              width:100%;
              height:22px;
              border-radius:999px;
              background: rgba(255,255,255,0.12);
              box-shadow: inset 0 1px 2px rgba(0,0,0,0.45), inset 0 -1px 0 rgba(255,255,255,0.04);
              overflow:hidden;
           ">
          <div style="
                position:absolute; left:0; top:0; bottom:0;
                width:{percent*100:.1f}%;
                background:{bar_color};
                box-shadow: inset 0 -1px 0 rgba(0,0,0,0.25);
           "></div>
          <div style="
                pointer-events:none;
                position:absolute; left:0; right:0; top:0; height:40%;
                background: linear-gradient(to bottom, rgba(255,255,255,0.18), rgba(255,255,255,0));
           "></div>
        </div>
  
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px; font-size:12px; color:#A9AFB7;">
          <span>Done today: <b style="color:#E6E8EB;">{done_today}/{quota_today}</b></span>
          <span style="display:flex; align-items:center; gap:10px;">
            <span>{target_short}</span>
            <span>{percent_text}</span>
          </span>
        </div>
      </div>
      """.replace("\n", "")
  
      js = f"""
      (function(){{
        var old = document.getElementById('deadliner-daily-progress');
        if (old) old.remove();
  
        var wrapper = document.createElement('div');
        wrapper.innerHTML = `{bar_html}`;
        var node = wrapper.firstElementChild;
  
        var heatmap = document.querySelector('#review-heatmap, #heatmap, #heatmap-container, #cal-heatmap, .heatmap, .review-heatmap');
        if (heatmap && heatmap.parentElement) {{
          heatmap.parentElement.insertBefore(node, heatmap);
          return;
        }}
  
        var overview = document.querySelector('#overview, .overview');
        if (overview && overview.parentElement) {{
            overview.parentElement.insertBefore(node, overview.nextSibling);
            return;
        }}
  
        document.body.appendChild(node);
      }})();
      """
      overview.web.eval(js)

    except Exception:
        # Never break the Overview if something unexpected happens.
        try:
            overview.web.eval(
                "var n=document.getElementById('deadliner-daily-progress'); if(n){n.remove();}"
            )
        except Exception:
            pass
        return



def setup() -> None:
    """Register hooks for this module."""
    gui_hooks.overview_did_refresh.append(inject_deadline_progress_bar)
