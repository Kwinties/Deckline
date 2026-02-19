# core/models.py
from datetime import datetime, timedelta
from typing import Optional

from aqt import mw
from aqt.qt import QDate

from .config import DeadlineDb, QUEUE_TYPE_NEW
from .helpers import (
    _deck_ids_str,
    _parse_skip_dates,
    avg_hours_per_learning_review,
)


# =========================
# Core refresh
# =========================
def refreshDeadliner() -> None:
    DeadlineMgr().refresh()
    mw.reset()


# =========================
# Deadline deck model
# =========================
class DeadlineDeck:
    def __init__(self, deck_id: int):
        self.deck_id = deck_id
        self.db = DeadlineDb()
        deck = mw.col.decks.get(deck_id, default=None)

        self.deck_key = str(deck_id)
        if self.deck_key in self.db.deadlines:
            self.cfg = self.db.deadlines[self.deck_key]
        else:
            dl = QDate.currentDate().addDays(7).toPyDate().strftime("%d-%m-%Y")
            start = QDate.currentDate().addDays(-10).toPyDate().strftime("%d-%m-%Y")
            self.cfg = {
                "enabled": True,
                "name": deck["name"] if deck else f"Deck {deck_id}",
                "deadline": dl,
                "start_date": start,
                "cutoff_offset": -5,
                "skip_weekends": False,
                "skip_dates": [],
                "expected_total_cards": 0,
                "daily_target_override": 0,
            }

        self.name = self.cfg.get("name", deck["name"] if deck else f"Deck {deck_id}")
        self.enabled = bool(self.cfg.get("enabled", True))
        self.deadline = self.cfg.get("deadline")
        self.start_date = self.cfg.get("start_date", QDate.currentDate().addDays(-10).toPyDate().strftime("%d-%m-%Y"))
        self.cutoff_offset = int(self.cfg.get("cutoff_offset", -5))

        self.skip_weekends = bool(self.cfg.get("skip_weekends", False))
        self.skip_dates = list(self.cfg.get("skip_dates", []) or [])

        self.expected_total_cards = int(self.cfg.get("expected_total_cards", 0) or 0)
        self.daily_target_override = int(self.cfg.get("daily_target_override", 0) or 0)

    def save(self) -> bool:
        # --- Premium limit check ---
        db = self.db
        is_new = self.deck_key not in db.deadlines

        if is_new and not db.is_premium:
            if len(db.deadlines) >= 2:
                from aqt.qt import QMessageBox
                from aqt import mw
                import webbrowser
            
                msg = QMessageBox(mw)
                msg.setWindowTitle("Deckline Free Version")
                msg.setIcon(QMessageBox.Icon.Information)
            
                msg.setText(
                    "You can only create 2 deadlines in the free version.\n\n"
                    "Upgrade to support development of Deckline and to unlock unlimited deadlines."
                )
            
                ok_button = msg.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
                kofi_button = msg.addButton("Unlock premium on KO-FI ☕", QMessageBox.ButtonRole.ActionRole)
            
                # Let Qt compute the right height, then force width
                msg.adjustSize()
                msg.setFixedWidth(300)
            
                msg.exec()
                if msg.clickedButton() == kofi_button:
                    webbrowser.open("https://ko-fi.com/s/d708f4b514")
                
                return False


        self.cfg["enabled"] = bool(self.enabled)
        self.cfg["name"] = self.name
        self.cfg["deadline"] = self.deadline
        self.cfg["start_date"] = self.start_date
        self.cfg["cutoff_offset"] = int(self.cutoff_offset)
        self.cfg["skip_weekends"] = bool(self.skip_weekends)
        self.cfg["skip_dates"] = self.skip_dates
        self.cfg["expected_total_cards"] = int(self.expected_total_cards or 0)
        self.cfg["daily_target_override"] = int(self.daily_target_override or 0)

        self.db.deadlines[self.deck_key] = self.cfg
        self.db.save()
        return True



# =========================
# Stats / Computations
# =========================
class DeadlineStats:
    def __init__(self, deck_id: int, name: str, deadline: str):
        self.name = name
        self.deck_id = deck_id
        self.deadline = datetime.strptime(deadline, "%d-%m-%Y").date()

        db = DeadlineDb()
        cfg = db.deadlines.get(str(deck_id), {})

        self.expected_total_cards = int(cfg.get("expected_total_cards", 0) or 0)
        self.daily_target_override = int(cfg.get("daily_target_override", 0) or 0)

        self.skip_weekends = bool(cfg.get("skip_weekends", False))
        self.skip_dates = _parse_skip_dates(list(cfg.get("skip_dates", [])))

        today = QDate.currentDate().toPyDate()
        self.daysLeft = (self.deadline - today).days

        self.cutoff_offset = int(cfg.get("cutoff_offset", -5))
        self.start_date = self._parse_date(cfg.get("start_date"), today)
        self.hide_target = self.start_date > today

        self.progress = 0.0
        self.todoLearnN = 0
        self.todoTime = 0.0
        self.hasEstimate = False
        self.avgLearnedPerDay = 0.0
        self.totalCards = 0

        mature, young, new, susp = self.count_cards()
        if mature is None:
            mature = young = new = susp = 0

        self.mature = mature
        self.young = young
        self.new = new
        self.susp = susp

        denom = mature + young + new
        self.totalCards = mature + young + new + susp

        cutoff_date = self.deadline + timedelta(days=self.cutoff_offset)
        days_since_start = max((today - self.start_date).days, 1)
        days_since_cutoff = max((today - cutoff_date).days, 1)

        if denom > 0:
            if new == 0:
                self.progress = 0.67 + ((mature / denom) * 0.33)
            else:
                expected_total = int(self.expected_total_cards or 0)
                denom_expected = expected_total if expected_total > 0 else denom
                denom_expected = max(denom_expected, denom)

                started_ratio = (mature + young) / denom_expected
                if started_ratio > 1.0:
                    started_ratio = 1.0

                self.progress = started_ratio * 0.67

        todo = new if new != 0 else young
        self.todoLearnN = todo

        learned = mature + young + susp
        if new == 0 and denom > 0:
            self.avgLearnedPerDay = mature / days_since_cutoff
        else:
            self.avgLearnedPerDay = learned / days_since_start

        avg_hours = avg_hours_per_learning_review(deck_id)
        self.hasEstimate = True

        remaining = todo
        days = max(self.daysLeft, 1)
        daily_cards = remaining / days
        self.todoTime = daily_cards * avg_hours

    @staticmethod
    def _parse_date(s: Optional[str], fallback):
        if not s:
            return fallback
        try:
            return datetime.strptime(s, "%d-%m-%Y").date()
        except Exception:
            return fallback

    def count_cards(self):
        deck_ids = _deck_ids_str(self.deck_id)
        return mw.col.db.first(f"""
            SELECT
            SUM(CASE WHEN queue >= {QUEUE_TYPE_NEW} AND type=2 AND ivl >= 21 THEN 1 ELSE 0 END),
            SUM(CASE WHEN queue >= {QUEUE_TYPE_NEW} AND ((type=2 AND ivl < 21) OR type IN (1, 3)) THEN 1 ELSE 0 END),
            SUM(CASE WHEN queue >= {QUEUE_TYPE_NEW} AND type=0 THEN 1 ELSE 0 END),
            SUM(CASE WHEN queue < {QUEUE_TYPE_NEW} THEN 1 ELSE 0 END)
            FROM cards WHERE did IN {deck_ids}
        """)


def findDeadlines():
    db = DeadlineDb()
    out = []
    for k, v in db.deadlines.items():
        if v.get("enabled"):
            try:
                out.append(DeadlineStats(int(k), v["name"], v["deadline"]))
            except Exception:
                continue
    return out


# =========================
# Manager (singleton-ish)
# =========================
class DeadlineMgr:
    __it__ = None

    def __new__(cls, *args, **kwargs):
        if cls.__it__ is None:
            cls.__it__ = super().__new__(cls)
            cls.__it__._deadlines = None
        return cls.__it__

    @property
    def deadlines(self):
        if self._deadlines is None:
            self.refresh()
        return self._deadlines

    def refresh(self):
        self._deadlines = findDeadlines()
