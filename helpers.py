# core/helpers.py
import math
import colorsys
from datetime import datetime, timedelta
from typing import Optional, Any

from aqt import mw
from aqt.qt import QDate

from .config import DeadlineDb


# =========================
# Helpers - deck ids
# =========================
def _deck_children_ids(deck_id: int) -> list[int]:
    ids = [child[1] for child in mw.col.decks.children(deck_id)]
    ids.append(deck_id)
    return ids


def _deck_ids_str(deck_id: int) -> str:
    ids = _deck_children_ids(deck_id)
    return "(" + ", ".join(str(i) for i in ids) + ")"


# =========================
# Helpers - time
# =========================
def deck_accent_rgba(deck_id: int) -> dict:
    """
    Deterministic accent colors per deck_id.
    Returns RGBA strings for backgrounds + a bright solid for dots/bars.
    """
    try:
        n = int(deck_id)
    except Exception:
        n = 0

    h = ((n * 0.61803398875) % 1.0)
    s = 0.55
    v = 0.92
    r, g, b = colorsys.hsv_to_rgb(h, s, v)

    def rgba(a: float) -> str:
        return f"rgba({int(r*255)},{int(g*255)},{int(b*255)},{a:.3f})"

    solid = f"rgba({int(r*255)},{int(g*255)},{int(b*255)},1.0)"

    return {
        "bg": rgba(0.075),
        "bar": rgba(0.55),
        "dot": rgba(0.95),
        "solid": solid,
    }
    
# =========================
# UI helpers - color utils
# =========================
import re

_PHASE_CUTOFF = 0.67  # the 67% marker

def _css_color_to_rgb_tuple(css: str) -> tuple[int, int, int]:
    s = (css or "").strip()

    # rgba(...) or rgb(...)
    m = re.search(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", s)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))

    # #RRGGBB
    m = re.search(r"#([0-9a-fA-F]{6})", s)
    if m:
        hx = m.group(1)
        return (int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16))

    # fallback: white-ish
    return (230, 232, 235)


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    r, g, b = rgb
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


def _lighten_rgb(rgb: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    """
    Mix color toward white by `amount` (0..1).
    0 = unchanged, 1 = white.
    """
    a = max(0.0, min(1.0, float(amount or 0.0)))
    r, g, b = rgb
    r2 = int(round(r + (255 - r) * a))
    g2 = int(round(g + (255 - g) * a))
    b2 = int(round(b + (255 - b) * a))
    return (r2, g2, b2)


def phase_split_fill_web(progress: float, base_css: str) -> str:
    """
    For deck-accent fills:
    - <= 67%: solid base
    - > 67%: split inside the filled portion:
        left part = base
        right part = slightly lighter
    """
    try:
        p = float(progress or 0.0)
    except Exception:
        p = 0.0
    p = max(0.0, min(1.0, p))

    if p <= _PHASE_CUTOFF or p <= 0.0:
        return base_css

    base_rgb = _css_color_to_rgb_tuple(base_css)
    light_rgb = _lighten_rgb(base_rgb, 0.18)
    base_hex = _rgb_to_hex(base_rgb)
    light_hex = _rgb_to_hex(light_rgb)

    # Inside the filled width, the cutoff position is at (0.67 / p)
    split = _PHASE_CUTOFF / p
    split_pct = max(0.0, min(1.0, split)) * 100.0

    return (
        f"linear-gradient(to right, {base_hex} 0%, {base_hex} {split_pct:.2f}%, "
        f"{light_hex} {split_pct:.2f}%, {light_hex} 100%)"
    )


def phase_split_fill_qt(progress: float, base_css: str) -> str:
    """
    Same idea as phase_split_fill_web(), but returns Qt qlineargradient.
    """
    try:
        p = float(progress or 0.0)
    except Exception:
        p = 0.0
    p = max(0.0, min(1.0, p))

    base_rgb = _css_color_to_rgb_tuple(base_css)
    light_rgb = _lighten_rgb(base_rgb, 0.18)
    base_hex = _rgb_to_hex(base_rgb)
    light_hex = _rgb_to_hex(light_rgb)

    if p <= _PHASE_CUTOFF or p <= 0.0:
        return base_hex

    split = _PHASE_CUTOFF / p
    split = max(0.0, min(1.0, split))

    # NOTE: duplicate stop at split to create a hard(ish) phase change
    return (
        "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        f"stop:0 {base_hex}, stop:{split:.4f} {base_hex}, "
        f"stop:{split:.4f} {light_hex}, stop:1 {light_hex})"
    )



def _today_epoch_ms_range() -> tuple[int, int]:
    start = datetime.combine(datetime.today().date(), datetime.min.time())
    end = start + timedelta(days=1)
    return int(start.timestamp() * 1000), int(end.timestamp() * 1000)


def reviews_today_for_deck(deck_id: int) -> int:
    """How many DISTINCT cards were reviewed today (not revlog rows)."""
    ids_str = _deck_ids_str(deck_id)
    start_ms, end_ms = _today_epoch_ms_range()
    return mw.col.db.scalar(f"""
        SELECT COUNT(DISTINCT cid)
        FROM revlog
        WHERE id >= {start_ms} AND id < {end_ms}
          AND cid IN (SELECT id FROM cards WHERE did IN {ids_str})
    """) or 0


def revlog_entries_today_for_deck(deck_id: int) -> int:
    """Raw revlog rows today (includes learning steps)."""
    ids_str = _deck_ids_str(deck_id)
    start_ms, end_ms = _today_epoch_ms_range()
    return mw.col.db.scalar(f"""
        SELECT COUNT(*)
        FROM revlog
        WHERE id >= {start_ms} AND id < {end_ms}
          AND cid IN (SELECT id FROM cards WHERE did IN {ids_str})
    """) or 0


def new_cards_started_today_for_deck(deck_id: int) -> int:
    """Count cards whose first-ever revlog entry is today (i.e., started today)."""
    ids_str = _deck_ids_str(deck_id)
    start_ms, end_ms = _today_epoch_ms_range()
    return mw.col.db.scalar(f"""
        SELECT COUNT(*)
        FROM (
            SELECT cid
            FROM revlog
            WHERE cid IN (SELECT id FROM cards WHERE did IN {ids_str})
            GROUP BY cid
            HAVING MIN(id) >= {start_ms} AND MIN(id) < {end_ms}
        )
    """) or 0



# =========================
# Helpers - skip days
# =========================
def _parse_skip_dates(date_strs: list[str]) -> set:
    out: set = set()
    for raw in (date_strs or []):
        s = (raw or "").strip()
        if not s:
            continue

        # single day: "12-02-2026"
        # range: "12-02-2026/16-02-2026" or "12-02-2026.16-02-2026"
        sep = "." if "." in s else ("/" if "/" in s else None)
        if sep:
            a, b = [x.strip() for x in s.split(sep, 1)]
            try:
                start = datetime.strptime(a, "%d-%m-%Y").date()
                end = datetime.strptime(b, "%d-%m-%Y").date()
            except Exception:
                continue
            if end < start:
                start, end = end, start
            d = start
            while d <= end:
                out.add(d)
                d += timedelta(days=1)
            continue

        try:
            out.add(datetime.strptime(s, "%d-%m-%Y").date())
        except Exception:
            continue

    return out


def _is_skip_day(d, skip_weekends: bool, skip_dates: set) -> bool:
    if skip_weekends and getattr(d, "weekday", lambda: 0)() >= 5:
        return True
    return d in (skip_dates or set())


def _count_study_days(start_incl, end_excl, skip_weekends: bool, skip_dates: set) -> int:
    d = start_incl
    n = 0
    while d < end_excl:
        if not _is_skip_day(d, skip_weekends, skip_dates):
            n += 1
        d += timedelta(days=1)
    return n


def _is_skip_day(d, skip_weekends: bool, skip_dates: set) -> bool:
    if skip_weekends and getattr(d, "weekday", lambda: 0)() >= 5:
        return True
    return d in skip_dates


def _count_study_days(start_incl, end_excl, skip_weekends: bool, skip_dates: set) -> int:
    d = start_incl
    n = 0
    while d < end_excl:
        if not _is_skip_day(d, skip_weekends, skip_dates):
            n += 1
        d += timedelta(days=1)
    return n


# =========================
# Quota helpers
# =========================
def _planned_remaining_cards(stats: "DeadlineStats") -> tuple[int, int]:
    expected_total = int(getattr(stats, "expected_total_cards", 0) or 0)
    if expected_total <= 0:
        return 0, 0

    existing_now = (
        int(getattr(stats, "mature", 0) or 0)
        + int(getattr(stats, "young", 0) or 0)
        + int(getattr(stats, "new", 0) or 0)
    )
    planned_remaining = max(expected_total - existing_now, 0)
    return expected_total, planned_remaining


def _quota_today_constant(remaining_effective: int, remaining_days: int, done_today: int) -> int:
    remaining_days = max(int(remaining_days), 1)
    remaining_at_start = max(0, int(remaining_effective) + int(done_today))
    return max(0, int(math.ceil(remaining_at_start / remaining_days)))


def done_today_for_target(stats: "DeadlineStats") -> int:
    try:
        today = QDate.currentDate().toPyDate()
    except Exception:
        today = datetime.today().date()

    cutoff_date = stats.deadline + timedelta(days=int(getattr(stats, "cutoff_offset", -5) or -5))

    expected_total, planned_remaining = _planned_remaining_cards(stats)

    learning_phase = (today < cutoff_date) and (
        (int(getattr(stats, "new", 0) or 0) > 0) or (planned_remaining > 0)
    )

    if learning_phase:
        return new_cards_started_today_for_deck(int(getattr(stats, "deck_id")))
    else:
        return reviews_today_for_deck(int(getattr(stats, "deck_id")))


def apply_daily_target_override(
    stats: "DeadlineStats",
    quota_today: int,
    remaining_now: int,
    done_today: int,
    today_is_skip: bool,
) -> tuple[int, bool]:
    if today_is_skip:
        return 0, False

    available = max(0, int(remaining_now or 0) + int(done_today or 0))
    if available <= 0:
        return 0, False

    override = int(getattr(stats, "daily_target_override", 0) or 0)
    if override > 0:
        return min(override, available), True

    qt = max(0, int(quota_today or 0))
    return min(qt, available), False


# =========================
# UI helpers (progress fill)
# =========================
def _progress_color(progress: float) -> str:
    try:
        p = float(progress or 0.0)
    except Exception:
        p = 0.0

    p = max(0.0, min(1.0, p))

    hue_deg = 120.0 * p
    h = hue_deg / 360.0

    s = 0.85
    v = 0.85

    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))


def _sanitize_hex_color(s: str, fallback: str) -> str:
    if not s:
        return fallback
    t = s.strip()
    if not t.startswith("#"):
        t = "#" + t
    if len(t) != 7:
        return fallback
    for ch in t[1:]:
        if ch not in "0123456789abcdefABCDEF":
            return fallback
    return t.upper()


def _sanitize_gradient_list(colors: Any, fallback: list[str]) -> list[str]:
    if not isinstance(colors, list):
        return fallback
    cleaned = []
    for c in colors:
        if not isinstance(c, str):
            continue
        cleaned.append(_sanitize_hex_color(c, ""))
    cleaned = [c for c in cleaned if c]
    if len(cleaned) < 2:
        return fallback
    if len(cleaned) > 3:
        cleaned = cleaned[:3]
    return cleaned


def get_progress_fill_cfg(db: Optional["DeadlineDb"] = None) -> dict:
    if db is None:
        db = DeadlineDb()

    raw = db.db.get("progress_fill", {}) if hasattr(db, "db") else {}
    if not isinstance(raw, dict):
        raw = {}

    mode = (raw.get("mode") or "auto").strip().lower()
    if mode not in ("auto", "solid", "gradient"):
        mode = "auto"

    solid = _sanitize_hex_color(raw.get("solid", ""), "#22C55E")
    gradient = _sanitize_gradient_list(raw.get("gradient"), ["#EF4444", "#F59E0B", "#22C55E"])

    # --- PREMIUM GATE ---
    # Free users are always forced to Auto (deck accent).
    try:
        if not bool(getattr(db, "is_premium", False)):
            mode = "auto"
    except Exception:
        mode = "auto"

    return {"mode": mode, "solid": solid, "gradient": gradient}



def fill_to_transparent_rgba(fill_css: str, alpha: float = 0.18) -> str:
    import re

    a = max(0.0, min(1.0, float(alpha or 0.0)))
    s = (fill_css or "").strip()

    def _hex_to_rgba(hx: str) -> str:
        h = hx.strip()
        if h.startswith("#"):
            h = h[1:]
        if len(h) != 6:
            return f"rgba(255,255,255,{a:.3f})"
        try:
            r = int(h[0:2], 16)
            g = int(h[2:4], 16)
            b = int(h[4:6], 16)
            return f"rgba({r},{g},{b},{a:.3f})"
        except Exception:
            return f"rgba(255,255,255,{a:.3f})"

    if s.startswith("#"):
        return _hex_to_rgba(s)

    m = re.search(r"#([0-9a-fA-F]{6})", s)
    if m:
        return _hex_to_rgba(m.group(0))

    m = re.search(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([0-9.]+)\s*\)", s)
    if m:
        r, g, b = m.group(1), m.group(2), m.group(3)
        return f"rgba({r},{g},{b},{a:.3f})"

    m = re.search(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", s)
    if m:
        r, g, b = m.group(1), m.group(2), m.group(3)
        return f"rgba({r},{g},{b},{a:.3f})"

    return f"rgba(255,255,255,{a:.3f})"


def progress_fill_web(progress: float, db: Optional["DeadlineDb"] = None) -> str:
    cfg = get_progress_fill_cfg(db)
    mode = cfg["mode"]

    # AUTO = use deck accent color (handled elsewhere)
    if mode == "auto":
        return ""

    if mode == "solid":
        return cfg["solid"]

    cols = cfg["gradient"]
    if len(cols) == 2:
        return f"linear-gradient(to right, {cols[0]} 0%, {cols[1]} 100%)"
    return f"linear-gradient(to right, {cols[0]} 0%, {cols[1]} 50%, {cols[2]} 100%)"


def progress_fill_qt(progress: float, db: Optional["DeadlineDb"] = None) -> str:
    cfg = get_progress_fill_cfg(db)
    mode = cfg["mode"]

    # AUTO = use deck accent color (handled elsewhere)
    if mode == "auto":
        return ""

    if mode == "solid":
        return cfg["solid"]

    cols = cfg["gradient"]
    if len(cols) == 2:
        return (
            "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            f"stop:0 {cols[0]}, stop:1 {cols[1]})"
        )

    return (
        "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        f"stop:0 {cols[0]}, stop:0.5 {cols[1]}, stop:1 {cols[2]})"
    )



def total_progress_pill_web(
    progress: float,
    db: Optional["DeadlineDb"] = None,
    *,
    disabled: bool = False,
    variant: str = "default",
    fill_override: Optional[str] = None,
    show_phase_marker: bool = True,
) -> str:
    try:
        p = float(progress or 0.0)
    except Exception:
        p = 0.0
    p = max(0.0, min(1.0, p))

    if disabled:
        fill = "rgba(255,255,255,0.22)"
        width_pct = 0.0
    else:
        cfg = get_progress_fill_cfg(db)
        mode = cfg["mode"]
        
        if mode == "auto":
            base_fill = fill_override or _progress_color(p)
        else:
            base_fill = progress_fill_web(p, db)

        # NEW: if we're using a deck accent override, apply the 67% phase split
        fill = phase_split_fill_web(p, base_fill) if fill_override else base_fill
        width_pct = p * 100.0

    marker_html = ""
    if show_phase_marker:
        marker_html = """
        <span style="
            position:absolute;
            left:67%;
            top:1px;
            bottom:1px;
            width:2px;
            background: rgba(255,255,255,0.20);
            border-radius: 999px;
            transform: translateX(-1px);
            pointer-events:none;
        "></span>
        """.replace("\n", "")

    if variant == "bubble":
        outer_track = "rgba(255,255,255,0.10)"
        inner_track = "rgba(255,255,255,0.06)"

        left_radius = "999px" if width_pct > 0.0 else "0px"
        right_radius = "999px" if width_pct >= 99.9 else "0px"

        return f"""
        <span style="
            display:inline-block;
            vertical-align:middle;
            width:75px;
            height:15px;
            border-radius:999px;
            background:{outer_track};
            overflow:hidden;
            box-sizing:border-box;
            padding:1px;
            position:relative;
        ">
          <span style="
              display:block;
              width:100%;
              height:100%;
              border-radius:999px;
              background:{inner_track};
              position:relative;
              overflow:hidden;
          ">
            <span style="
                position:absolute;
                left:0;
                top:0;
                height:100%;
                width:{width_pct:.1f}%;
                background:{fill};
                border-top-left-radius:{left_radius};
                border-bottom-left-radius:{left_radius};
                border-top-right-radius:{right_radius};
                border-bottom-right-radius:{right_radius};
            "></span>
            {marker_html}
          </span>
        </span>
        """.replace("\n", "")

    return f"""
    <span style="
        display:inline-block;
        vertical-align:middle;
        width:120px;
        height:16px;
        border-radius:999px;
        background: rgba(255,255,255,0.10);
        overflow:hidden;
        box-sizing:border-box;
        position:relative;
    ">
      <span style="
        display:block;
        width:{width_pct:.1f}%;
        height:100%;
        background:{fill};
      "></span>
      {marker_html}
    </span>
    """.replace("\n", "")



# =========================
# Stats / Computations
# =========================
def avg_hours_per_learning_review(deck_id: int) -> float:
    deck_ids_str = _deck_ids_str(deck_id)
    avg_seconds = mw.col.db.scalar(f"""
        SELECT AVG(time)/1000.0
        FROM revlog
        WHERE cid IN (SELECT id FROM cards WHERE did IN {deck_ids_str})
          AND type IN (0, 1, 2)
    """)
    if avg_seconds is None or avg_seconds < 1:
        return 12.0 / 3600.0
    return avg_seconds / 3600.0


# =========================
# Daily log (Stats feature)
# =========================

from datetime import date
from typing import Dict, List, Any, Optional, Tuple


_DAILY_LOG_KEY = "daily_log"
_DAILY_LOG_MAX_DAYS = 30


def _cfg_root() -> dict:
    from .config import CFG_KEY  # local import to avoid cycles
    cfg = mw.col.get_config(CFG_KEY, default=None) or {}
    if not isinstance(cfg, dict):
        cfg = {}
    return cfg


def _cfg_save(cfg: dict) -> None:
    from .config import CFG_KEY  # local import to avoid cycles
    mw.col.set_config(CFG_KEY, cfg)


def _get_daily_log(cfg: Optional[dict] = None) -> dict:
    if cfg is None:
        cfg = _cfg_root()
    log = cfg.get(_DAILY_LOG_KEY) or {}
    if not isinstance(log, dict):
        log = {}
    return log


def _set_daily_log(cfg: dict, log: dict) -> None:
    cfg[_DAILY_LOG_KEY] = log


def _today_iso() -> str:
    try:
        return QDate.currentDate().toPyDate().isoformat()
    except Exception:
        return datetime.today().date().isoformat()


def _compute_today_done_target_phase(stats: "DeadlineStats") -> Tuple[int, int, str]:
    """
    Returns (done_today, target_today, phase)
    phase: 'pending' | 'new' | 'review' | 'rest'
    """
    # If not started yet, still log "pending" so the chart can show it.
    if bool(getattr(stats, "hide_target", False)):
        done_today = int(done_today_for_target(stats) or 0)
        return done_today, 0, "pending"

    try:
        today = QDate.currentDate().toPyDate()
    except Exception:
        today = datetime.today().date()

    cutoff_date = stats.deadline + timedelta(days=int(getattr(stats, "cutoff_offset", -5) or -5))

    skip_weekends = bool(getattr(stats, "skip_weekends", False))
    skip_dates = getattr(stats, "skip_dates", set())
    today_is_skip = _is_skip_day(today, skip_weekends, skip_dates)
    if today_is_skip:
        done_today = int(done_today_for_target(stats) or 0)
        return done_today, 0, "rest"

    start_count = today

    expected_total, planned_remaining = _planned_remaining_cards(stats)
    learning_phase = (today < cutoff_date) and (
        (int(getattr(stats, "new", 0) or 0) > 0) or (planned_remaining > 0)
    )

    if learning_phase:
        remaining_now = int(getattr(stats, "new", 0) or 0)
        remaining_effective = (remaining_now + planned_remaining) if expected_total > 0 else remaining_now
        remaining_days = max(_count_study_days(start_count, cutoff_date, skip_weekends, skip_dates), 1)
        phase = "new"
    else:
        remaining_now = int(getattr(stats, "young", 0) or 0) + int(getattr(stats, "new", 0) or 0)
        remaining_effective = remaining_now
        remaining_days = max(_count_study_days(start_count, stats.deadline, skip_weekends, skip_dates), 1)
        phase = "review"

    done_today = int(done_today_for_target(stats) or 0)

    quota_raw = _quota_today_constant(int(remaining_effective), int(remaining_days), int(done_today))
    quota_today = int(quota_raw)

    # clamp when planning active
    if expected_total > 0:
        quota_today = min(quota_today, max(0, int(remaining_now) + int(done_today)))

    # manual override (keeps "historical target never recalculated" because we store the result)
    quota_today, _override_active = apply_daily_target_override(
        stats=stats,
        quota_today=quota_today,
        remaining_now=remaining_now,
        done_today=done_today,
        today_is_skip=False,
    )

    quota_today = max(0, int(quota_today))
    return done_today, quota_today, phase


def log_daily_snapshot_for_deck(stats: "DeadlineStats") -> None:
    """
    Write at most one snapshot per day per deck:
      {date, done, target, phase}
    Keep max 30 days per deck.
    """
    if not mw.col:
        return

    day = _today_iso()
    deck_id = int(getattr(stats, "deck_id", 0) or 0)
    if deck_id <= 0:
        return

    done_today, target_today, phase = _compute_today_done_target_phase(stats)

    cfg = _cfg_root()
    log = _get_daily_log(cfg)

    key = str(deck_id)
    entries = log.get(key) or []
    if not isinstance(entries, list):
        entries = []

    # already logged today? -> overwrite today's entry so stats can update live
    for e in entries:
        if isinstance(e, dict) and e.get("date") == day:
            e["done"] = int(done_today)
            e["target"] = int(target_today)
            e["phase"] = str(phase)
            log[key] = entries
            _set_daily_log(cfg, log)
            _cfg_save(cfg)
            return



    entries.append(
        {
            "date": day,
            "done": int(done_today),
            "target": int(target_today),
            "phase": str(phase),
        }
    )

    # keep last N by date (stable, and prevents infinite growth)
    def _safe_date(d: Any) -> str:
        try:
            return str(d)
        except Exception:
            return ""

    entries.sort(key=lambda x: _safe_date((x or {}).get("date")))
    if len(entries) > _DAILY_LOG_MAX_DAYS:
        entries = entries[-_DAILY_LOG_MAX_DAYS :]

    log[key] = entries
    _set_daily_log(cfg, log)
    _cfg_save(cfg)


def log_daily_snapshots_for_all_deadlines() -> None:
    """
    Call this at startup (and optionally when deck browser renders).
    Only writes missing 'today' entries, so it's cheap.
    """
    if not mw.col:
        return
    try:
        from .models import DeadlineMgr  # local import
        dm = DeadlineMgr()
        dm.refresh()
        for stats in (dm.deadlines or []):
            try:
                log_daily_snapshot_for_deck(stats)
            except Exception:
                continue
    except Exception:
        return


def get_daily_log_entries(deck_id: int) -> list[dict]:
    """
    Read raw stored log entries for a deck.
    """
    if not mw.col:
        return []
    cfg = _cfg_root()
    log = _get_daily_log(cfg)
    entries = log.get(str(int(deck_id))) or []
    if not isinstance(entries, list):
        return []
    out = [e for e in entries if isinstance(e, dict)]
    out.sort(key=lambda x: str(x.get("date", "")))
    return out
  
def calculate_current_streak(entries: list[dict]) -> int:
    """
    Calculate current streak (per deck) using the daily log entries.

    Rules:
    - Only days with target > 0 count as "streak days".
    - If target == 0 (rest/skip day, pending), the streak is frozen (does not increase, does not break).
    - If a day with target > 0 exists and done < target, streak breaks.
    - If a date is missing from the log, we break (we can't know if it was a skip/vacation day).
    """
    if not entries:
        return 0

    def _parse_iso(d: str):
        try:
            return datetime.strptime(str(d), "%Y-%m-%d").date()
        except Exception:
            return None

    # Build date -> entry map (keep last if duplicates)
    m: dict[str, dict] = {}
    for e in entries:
        if isinstance(e, dict) and e.get("date"):
            m[str(e.get("date"))] = e

    # Start from today
    try:
        today = QDate.currentDate().toPyDate()
    except Exception:
        today = datetime.today().date()

    streak = 0
    cur = today

    # Walk backward day-by-day
    for _ in range(3650):  # hard safety cap (~10 years)
        key = cur.isoformat()
        e = m.get(key)
        if not e:
            break

        try:
            done = int(e.get("done") or 0)
        except Exception:
            done = 0
        try:
            target = int(e.get("target") or 0)
        except Exception:
            target = 0

        # skip/rest day: freeze streak, don't increment, don't break
        if target <= 0:
            cur = cur - timedelta(days=1)
            continue

        # study day: must meet target
        if done >= target:
            streak += 1
            cur = cur - timedelta(days=1)
            continue

        break

    return int(streak)

