# settings.py
# UI for Deckline / Deckline settings dialog.

from datetime import datetime, timedelta
from typing import Optional
import os
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo

from .core import DeadlineDeck, refreshDeadliner

class MultiplierSpinBox(QSpinBox):
    """
    A QSpinBox that *displays* a float with 2 decimals (e.g. 2,00×),
    but stores it internally as an int in hundredths (e.g. 200).
    This keeps the nice QSpinBox arrow buttons (same as Expected total cards).
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        # 0.10x .. 10.00x (stored as 10..1000)
        self.setRange(10, 1000)
        self.setSingleStep(10)   # 0.10
        self.setSuffix("×")
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)

    def textFromValue(self, value: int) -> str:
        f = value / 100.0
        # Use locale so NL shows comma: 2,00
        return self.locale().toString(f, "f", 2)

    def valueFromText(self, text: str) -> int:
        t = text.replace("×", "").strip()
        f, ok = self.locale().toDouble(t)
        if not ok:
            # fallback parse
            try:
                f = float(t.replace(",", "."))
            except Exception:
                f = 1.0
        # clamp and convert to hundredths
        f = max(0.10, min(10.00, f))
        return int(round(f * 100))

    def multiplier(self) -> float:
        return float(self.value()) / 100.0

    def setMultiplier(self, val: float) -> None:
        val = max(0.10, min(10.00, float(val)))
        self.setValue(int(round(val * 100)))

# =========================
# Dialog: Deadline settings
# =========================
class DeadlinerDialog(QDialog):
    @staticmethod
    def open_deadliner_dialog(deck_id: Optional[int] = None) -> None:
        # keep signature flexible; your code expects an int downstream
        if deck_id is None:
            return
        dlg = DeadlinerDialog(deck_id)
        dlg.exec()

    def __init__(self, deck_id: int, *, global_mode: bool = False):
        self._global_mode = bool(global_mode)
        super().__init__(parent=mw)

        self.deadlineDeck = DeadlineDeck(deck_id)
        self.db = self.deadlineDeck.db
        self.deck_id = deck_id

        deck_name = mw.col.decks.name(deck_id)

        self.setWindowTitle("Deckline settings")
        self.setSizeGripEnabled(False)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setMinimumWidth(475)


        # ---- Root layout ----
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

       # ---- Header ----
        header = QVBoxLayout()
        header.setSpacing(4)
        
        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        
        deck_name = mw.col.decks.name(deck_id)
        
        self.enabledButton = QCheckBox(f'Enable Deadline for "{deck_name}"')
        self.enabledButton.setChecked(bool(self.deadlineDeck.enabled))
        self.enabledButton.toggled.connect(self.onToggleEnable)
        
        top_row.addWidget(self.enabledButton)
        top_row.addStretch(1)
        
        header.addLayout(top_row)
        root.addLayout(header)


        # ---- Tabs ----
        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        self._build_tab_deadline()
        self._build_tab_optional()
        self._build_tab_feedback()
        self._build_tab_vacation()
        self._build_tab_premium()

        # =========================
        # Global mode: hide per-deck tabs
        # =========================
        if global_mode:
            # Hide the "Enable Deadline for deck" checkbox row
            try:
                self.enabledButton.hide()
            except Exception:
                pass

            # Remove per-deck tabs by name (safer than hardcoding indices)
            try:
                tab_names_to_remove = {"Deadline", "Optional", "Vacation"}
                i = self.tabs.count() - 1
                while i >= 0:
                    if self.tabs.tabText(i) in tab_names_to_remove:
                        self.tabs.removeTab(i)
                    i -= 1
            except Exception:
                pass

            # Make sure user lands on Feedback
            try:
                # After removing tabs, Feedback should exist
                for i in range(self.tabs.count()):
                    if self.tabs.tabText(i) == "Feedback":
                        self.tabs.setCurrentIndex(i)
                        break
            except Exception:
                pass

            # Title for clarity
            try:
                self.setWindowTitle("Deckline settings")
            except Exception:
                pass

        self.tabs.setDisabled(not bool(self.deadlineDeck.enabled))

        # ---- Footer ----
        root.addLayout(self._build_footer())
        
        # ---- Global dialog styling ----
        self.setStyleSheet("""
        QDialog {
            background: palette(window);
        }

        QTabWidget::pane {
            border: 1px solid palette(midlight);
            border-radius: 10px;
            padding: 14px 6px 6px 6px;
        }

        QTabBar::tab {
            padding: 8px 12px;
            margin-right: 6px;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }

        QGroupBox {
            border: 1px solid palette(midlight);
            border-radius: 12px;
            margin-top: 10px;
            padding: 10px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 6px;
            font-weight: 650;
        }

        /* Inputs */
        QLineEdit, QDateEdit, QSpinBox, QDoubleSpinBox, QComboBox, QListWidget {
            min-height: 28px;
            padding: 5px 8px;
            border-radius: 8px;
            border: 1px solid palette(midlight);
            background: palette(base);
            color: palette(text);
        }

        /* Cleaner focus (no harsh outline) */
        QLineEdit:focus, QDateEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QListWidget:focus {
            border: 1px solid palette(highlight);
            outline: none;
        }

        /* ---- ComboBox cleanup ---- */
        QComboBox {
            padding-right: 26px; /* room for the arrow button */
        }
        
        QComboBox::down-arrow {
            width: 20px;
            height: 20px;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 22px;
            border-left: 1px solid palette(midlight);
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
            background: rgba(255,255,255,0.06);
        }

        QComboBox::drop-down:hover {
            background: rgba(255,255,255,0.12);
        }

        /* Popup list for dropdowns */
        QComboBox QAbstractItemView {
            border: 1px solid palette(midlight);
            border-radius: 10px;
            padding: 6px;
            background: palette(base);
            outline: none;
        }

        QComboBox QAbstractItemView::item {
            padding: 6px 10px;
            border-radius: 8px;
        }

        QComboBox QAbstractItemView::item:selected {
            background: palette(highlight);
            color: palette(highlightedText);
        }

        QCheckBox {
            spacing: 8px;
        }

        QPushButton {
            border-radius: 10px;
            padding: 6px 12px;
        }

        QToolButton {
            border-radius: 10px;
            padding: 6px 10px;
            border: 1px solid palette(midlight);
            background: palette(base);
            color: palette(text);
        }

        QToolButton:hover {
            background: palette(alternate-base);
        }

        QToolButton:checked {
            background: palette(highlight);
            color: palette(highlightedText);
            border: 1px solid palette(highlight);
        }

        QListWidget {
            padding: 6px;
        }
        
                /* ---- DateEdit dropdown button: match ComboBox arrow ---- */
        QDateEdit {
            padding-right: 26px; /* room for the calendar drop-down button */
        }

        QDateEdit::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 22px;
            border-left: 1px solid palette(midlight);
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
            background: rgba(255,255,255,0.06);
        }

        QDateEdit::drop-down:hover {
            background: rgba(255,255,255,0.12);
        }

        QDateEdit::down-arrow {
            width: 20px;
            height: 20px;
        }

        
                /* ---- QDoubleSpinBox arrows (make it look like the QSpinBox one) ---- */
        QDoubleSpinBox {
            padding-right: 26px; /* room for the arrows like Expected total cards */
        }

        QDoubleSpinBox::up-button {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 22px;
            border-left: 1px solid palette(midlight);
            border-top-right-radius: 8px;
            background: rgba(255,255,255,0.06);
        }

        QDoubleSpinBox::down-button {
            subcontrol-origin: padding;
            subcontrol-position: bottom right;
            width: 22px;
            border-left: 1px solid palette(midlight);
            border-bottom-right-radius: 8px;
            background: rgba(255,255,255,0.06);
        }

        QDoubleSpinBox::up-button:hover,
        QDoubleSpinBox::down-button:hover {
            background: rgba(255,255,255,0.12);
        }

        QDoubleSpinBox::up-arrow,
        QDoubleSpinBox::down-arrow {
            width: 7px;
            height: 7px;
        }
        """)


        self.adjustSize()

    # ----------------------------
    # Helpers
    # ----------------------------
    def _group(self, title: str) -> QGroupBox:
        g = QGroupBox(title)
        # Default: groups should NOT force the dialog taller.
        g.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return g


    def _form(self, parent: QWidget, margins=(12, 10, 12, 12)) -> QFormLayout:
        f = QFormLayout(parent)
        f.setContentsMargins(*margins)
    
        # Spacing: wat strakker en consistenter
        f.setHorizontalSpacing(12)
        f.setVerticalSpacing(8)
    
        # Velden mogen de breedte pakken, labels blijven netjes links
        f.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
    
        # ✅ Labels LINKS uitlijnen (jouw wens)
        f.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    
        # Hele form bovenaan, links
        f.setFormAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    
        # Voorkom rare wrapping
        f.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
    
        return f

    def _date_edit(self, qdate: QDate) -> QDateEdit:
        de = QDateEdit(qdate)
        de.setCalendarPopup(True)
        de.setDisplayFormat("dd-MM-yyyy")
    
        # Key changes:
        # - remove forced min width
        # - allow expanding so it fills the form field column
        de.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return de

    def _safe_parse_date(self, s: str) -> QDate:
        q = QDate.fromString(s or "", "dd-MM-yyyy")
        return q if q.isValid() else QDate.currentDate()

    # ----------------------------
    # Tabs
    # ----------------------------
    def _build_tab_deadline(self) -> None:
        tab = QWidget()
        outer = QVBoxLayout(tab)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)
    
        # Deadline settings
        deadlineGroup = self._group("Deadline settings")
        form1 = self._form(deadlineGroup)
    
        self.nameEdit = QLineEdit(self.deadlineDeck.name or "")
        self.nameEdit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        form1.addRow("Deck name:", self.nameEdit)
    
        deadline_q = self._safe_parse_date(self.deadlineDeck.deadline)
        start_q = self._safe_parse_date(self.deadlineDeck.start_date)
    
        # Start date
        self.startDateEdit = self._date_edit(start_q)
        form1.addRow("Start date:", self.startDateEdit)
    
        # Cutoff
        cutoff_offset = int(getattr(self.deadlineDeck, "cutoff_offset", -1) or -1)
        self.cutoffDateEdit = self._date_edit(deadline_q.addDays(cutoff_offset))
        cutoff_label = QLabel("Cutoff:<br><i>(hover for details)</i>")
        cutoff_label.setTextFormat(Qt.TextFormat.RichText)
        form1.addRow(cutoff_label, self.cutoffDateEdit)
    
        self.cutoffDateEdit.setToolTip(
            "Deckline works in 2 phases:\n\n"
            "Phase 1 — NEW → Cutoff\n"
            "• Until the cutoff date, your goal is to START new cards.\n"
            "• Daily target counts: NEW cards started today.\n"
            "• Pending shows: remaining NEW cards.\n\n"
            "Phase 2 — REVIEW → Deadline\n"
            "• After the cutoff, your goal is to finish the remaining learning (young) cards.\n"
            "• Daily target counts: reviews done today.\n"
            "• Pending shows: remaining YOUNG cards.\n\n"
            "Tip: Set the cutoff a few days before the deadline so you have time to consolidate."
        )
    
        # Deadline
        self.deadlineDateEdit = self._date_edit(deadline_q)
        form1.addRow("Deadline:", self.deadlineDateEdit)
    
        def _recalc_offset_from_cutoff() -> None:
            dl = self.deadlineDateEdit.date()
            d = self.cutoffDateEdit.date()
            offset = dl.daysTo(d)  # cutoff - deadline
            self.deadlineDeck.cutoff_offset = min(-1, int(offset))
    
        def _move_cutoff_with_deadline() -> None:
            dl = self.deadlineDateEdit.date()
            d = dl.addDays(int(self.deadlineDeck.cutoff_offset))
            self.cutoffDateEdit.blockSignals(True)
            self.cutoffDateEdit.setDate(d)
            self.cutoffDateEdit.blockSignals(False)
    
        self.cutoffDateEdit.dateChanged.connect(_recalc_offset_from_cutoff)
        self.deadlineDateEdit.dateChanged.connect(_move_cutoff_with_deadline)
    
        outer.addWidget(deadlineGroup)
        outer.addStretch(1)
    
        self.tabs.addTab(tab, "Deadline")

    def _build_tab_optional(self) -> None:
        tab = QWidget()
        outer = QVBoxLayout(tab)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)
    
        optionalGroup = self._group("Optional deadline settings")
        form_opt = self._form(optionalGroup)
    
        # Expected total cards
        self.expectedTotalEdit = QSpinBox()
        self.expectedTotalEdit.setRange(0, 200000)
        self.expectedTotalEdit.setValue(int(self.deadlineDeck.expected_total_cards or 0))
        self.expectedTotalEdit.setSuffix(" cards")
        self.expectedTotalEdit.setToolTip(
            "Optional planning hint.\n"
            "If your deck has fewer cards than this number, Deckline assumes more cards will be added later\n"
            "and uses this value to calculate a steadier daily target.\n"
            "0 = off (use actual deck size)."
        )
    
        clear_btn = QPushButton("Clear")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setFixedHeight(28)
        clear_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        clear_btn.clicked.connect(lambda: self.expectedTotalEdit.setValue(0))
    
        row = QWidget()
        row_l = QHBoxLayout(row)
        row_l.setContentsMargins(0, 0, 0, 0)
        row_l.setSpacing(8)
        row_l.addWidget(self.expectedTotalEdit, 1)
        row_l.addWidget(clear_btn, 0)
    
        form_opt.addRow("Expected total cards:", row)
    
        # Daily target override
        self.dailyTargetOverrideEdit = QSpinBox()
        self.dailyTargetOverrideEdit.setRange(0, 200000)
        self.dailyTargetOverrideEdit.setValue(int(getattr(self.deadlineDeck, "daily_target_override", 0) or 0))
        self.dailyTargetOverrideEdit.setSuffix(" cards")
        self.dailyTargetOverrideEdit.setToolTip(
            "Manually override today's target for this deck.\n"
            "0 = automatic (Deckline calculates it).\n"
            "Note: it will never exceed the number of cards that can actually be done today."
        )
        self.dailyTargetOverrideEdit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    
        clear_override_btn = QPushButton("Clear")
        clear_override_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_override_btn.setFixedHeight(28)
        clear_override_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        clear_override_btn.clicked.connect(lambda: self.dailyTargetOverrideEdit.setValue(0))
    
        row2 = QWidget()
        row2_l = QHBoxLayout(row2)
        row2_l.setContentsMargins(0, 0, 0, 0)
        row2_l.setSpacing(8)
        row2_l.addWidget(self.dailyTargetOverrideEdit, 1)
        row2_l.addWidget(clear_override_btn, 0)
    
        form_opt.addRow("Daily target override:", row2)
    
        # Days off (weekends)
        self.skipWeekendsCheckbox = QCheckBox("Skip weekends")
        self.skipWeekendsCheckbox.setChecked(bool(self.deadlineDeck.skip_weekends))
        form_opt.addRow("Days off:", self.skipWeekendsCheckbox)
    
        outer.addWidget(optionalGroup)
        outer.addStretch(1)
    
        self.tabs.addTab(tab, "Optional")


    def _build_tab_feedback(self) -> None:
        tab = QWidget()
        outer = QVBoxLayout(tab)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)
    
        def _bool_box(checked: bool) -> QCheckBox:
            cb = QCheckBox("")
            cb.setChecked(bool(checked))
            cb.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            cb.setStyleSheet("QCheckBox { padding-left: 2px; }")
            return cb
    
        # -------------------------
        # Basic feedback (FREE)
        # -------------------------
        basicGroup = self._group("Feedback")
        basic_form = self._form(basicGroup)
    
        self.dailyProgressCheckbox = _bool_box(self.db.show_daily_progress)
        basic_form.addRow("Show daily progress bar in deck overview:", self.dailyProgressCheckbox)
    
        self.reviewProgressCheckbox = _bool_box(getattr(self.db, "show_review_progress", True))
        basic_form.addRow("Show daily progress bar in review screen:", self.reviewProgressCheckbox)
    
        self.timeMultiplierSpin = MultiplierSpinBox()
        self.timeMultiplierSpin.setMultiplier(float(getattr(self.db, "time_multiplier", 1.0) or 1.0))
        self.timeMultiplierSpin.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.timeMultiplierSpin.setToolTip(
            "Scales the time estimate shown in progress bars.\n"
            "Example: 2.00× means time is shown as double."
        )
        self.timeMultiplierSpin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        basic_form.addRow("Time estimate multiplier:", self.timeMultiplierSpin)
    
        outer.addWidget(basicGroup)
    
        # -------------------------
        # Premium visuals (PREMIUM)
        # -------------------------
        is_premium = bool(getattr(self.db, "is_premium", False))
    
        title = "Premium visuals" if is_premium else "Premium visuals 🔒"
        premiumGroup = self._group(title)
        prem_form = self._form(premiumGroup)
    
        # Bar color (premium)
        cfg = self.db.db.get("progress_fill", {}) if hasattr(self.db, "db") else {}
        if not isinstance(cfg, dict):
            cfg = {}
    
        mode = (cfg.get("mode") or "auto").lower()
        solid = (cfg.get("solid") or "#22C55E").strip()
    
        grad_list = cfg.get("gradient")
        if not isinstance(grad_list, list):
            grad_list = ["#EF4444", "#F59E0B", "#22C55E"]
        grad_list = [str(x).strip() for x in grad_list if str(x).strip()]
        if len(grad_list) < 2:
            grad_list = ["#EF4444", "#F59E0B", "#22C55E"]
        if len(grad_list) > 3:
            grad_list = grad_list[:3]
    
        self.pbColorModeBox = QComboBox()
        self.pbColorModeBox.addItems(["Auto", "Solid", "Gradient"])
        self.pbColorModeBox.setCurrentText(
            "Auto" if mode == "auto" else ("Solid" if mode == "solid" else "Gradient")
        )
        self.pbColorModeBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        prem_form.addRow("Bar color:", self.pbColorModeBox)
    
        # ---- Color swatches (appear under Solid/Gradient) ----
        def _make_swatch_button(hex_color: str) -> QPushButton:
            b = QPushButton("")
            b.setFixedSize(34, 18)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setToolTip(hex_color.upper())
            b.setStyleSheet(
                "QPushButton {"
                f" background: {hex_color};"
                " border: 1px solid rgba(0,0,0,0.35);"
                " border-radius: 4px;"
                "}"
                "QPushButton:hover { border: 1px solid rgba(0,0,0,0.6); }"
            )
            return b
    
        def _pick_into_button(btn: QPushButton, initial_hex: str) -> str:
            current = QColor(initial_hex if initial_hex else "#22C55E")
            col = QColorDialog.getColor(current, self, "Pick color")
            if col.isValid():
                hx = col.name().upper()
                btn.setToolTip(hx)
                btn.setStyleSheet(
                    "QPushButton {"
                    f" background: {hx};"
                    " border: 1px solid rgba(0,0,0,0.35);"
                    " border-radius: 4px;"
                    "}"
                    "QPushButton:hover { border: 1px solid rgba(0,0,0,0.6); }"
                )
                return hx
            return initial_hex
    
        # Storage used by on_accept()
        self._pb_solid_hex = solid.upper()
        self._pb_grad_hexes = [c.upper() for c in grad_list]  # len 2-3
    
        # Solid row (one swatch)
        self.pbSolidSwatch = _make_swatch_button(self._pb_solid_hex)
        self._pb_solid_row = QWidget()
        solid_row = self._pb_solid_row
        solid_l = QHBoxLayout(solid_row)
        solid_l.setContentsMargins(0, 0, 0, 0)
        solid_l.setSpacing(8)
        solid_l.addWidget(self.pbSolidSwatch, 0)
        solid_l.addStretch(1)
    
        self._pb_solid_label = QLabel("Solid color:")
        prem_form.addRow(self._pb_solid_label, solid_row)
    
        def _on_pick_solid() -> None:
            self._pb_solid_hex = _pick_into_button(self.pbSolidSwatch, self._pb_solid_hex)
    
        self.pbSolidSwatch.clicked.connect(_on_pick_solid)
    
        # Gradient row (2-3 swatches + add/remove stop)
        self.pbGradSw1 = _make_swatch_button(self._pb_grad_hexes[0])
        self.pbGradSw2 = _make_swatch_button(self._pb_grad_hexes[1])
        self.pbGradSw3 = _make_swatch_button(
            self._pb_grad_hexes[2] if len(self._pb_grad_hexes) == 3 else "#22C55E"
        )
    
        self.pbGradAddBtn = QPushButton("+")
        self.pbGradAddBtn.setFixedHeight(20)
        self.pbGradAddBtn.setCursor(Qt.CursorShape.PointingHandCursor)
    
        self.pbGradDelBtn = QPushButton("–")
        self.pbGradDelBtn.setFixedHeight(20)
        self.pbGradDelBtn.setCursor(Qt.CursorShape.PointingHandCursor)
    
        self._pb_grad_row = QWidget()
        grad_row = self._pb_grad_row
        grad_l = QHBoxLayout(grad_row)
        grad_l.setContentsMargins(0, 0, 0, 0)
        grad_l.setSpacing(8)
        grad_l.addWidget(self.pbGradSw1, 0)
        grad_l.addWidget(self.pbGradSw2, 0)
        grad_l.addWidget(self.pbGradSw3, 0)
        grad_l.addSpacing(6)
        grad_l.addWidget(self.pbGradAddBtn, 0)
        grad_l.addWidget(self.pbGradDelBtn, 0)
        grad_l.addStretch(1)
    
        self._pb_grad_label = QLabel("Gradient:")
        prem_form.addRow(self._pb_grad_label, grad_row)
    
        def _sync_grad_buttons() -> None:
            has3 = (len(self._pb_grad_hexes) == 3)
            self.pbGradSw3.setVisible(has3)
            self.pbGradDelBtn.setVisible(has3)
            self.pbGradAddBtn.setVisible(not has3)
    
        def _on_pick_g1() -> None:
            self._pb_grad_hexes[0] = _pick_into_button(self.pbGradSw1, self._pb_grad_hexes[0])
    
        def _on_pick_g2() -> None:
            self._pb_grad_hexes[1] = _pick_into_button(self.pbGradSw2, self._pb_grad_hexes[1])
    
        def _on_pick_g3() -> None:
            if len(self._pb_grad_hexes) == 3:
                self._pb_grad_hexes[2] = _pick_into_button(self.pbGradSw3, self._pb_grad_hexes[2])
    
        self.pbGradSw1.clicked.connect(_on_pick_g1)
        self.pbGradSw2.clicked.connect(_on_pick_g2)
        self.pbGradSw3.clicked.connect(_on_pick_g3)
    
        def _add_stop() -> None:
            if len(self._pb_grad_hexes) == 2:
                self._pb_grad_hexes.append(self._pb_grad_hexes[1])
                self.pbGradSw3.setToolTip(self._pb_grad_hexes[2])
                self.pbGradSw3.setStyleSheet(
                    "QPushButton {"
                    f" background: {self._pb_grad_hexes[2]};"
                    " border: 1px solid rgba(0,0,0,0.35);"
                    " border-radius: 4px;"
                    "}"
                    "QPushButton:hover { border: 1px solid rgba(0,0,0,0.6); }"
                )
            _sync_grad_buttons()
    
        def _del_stop() -> None:
            if len(self._pb_grad_hexes) == 3:
                self._pb_grad_hexes = self._pb_grad_hexes[:2]
            _sync_grad_buttons()
    
        self.pbGradAddBtn.clicked.connect(_add_stop)
        self.pbGradDelBtn.clicked.connect(_del_stop)
    
        def _update_color_rows() -> None:
            m = self.pbColorModeBox.currentText().lower()
    
            if m == "solid":
                self._pb_solid_label.setVisible(True)
                self._pb_solid_row.setVisible(True)
                self._pb_grad_label.setVisible(False)
                self._pb_grad_row.setVisible(False)
            elif m == "gradient":
                self._pb_solid_label.setVisible(False)
                self._pb_solid_row.setVisible(False)
                self._pb_grad_label.setVisible(True)
                self._pb_grad_row.setVisible(True)
            else:  # auto
                self._pb_solid_label.setVisible(False)
                self._pb_solid_row.setVisible(False)
                self._pb_grad_label.setVisible(False)
                self._pb_grad_row.setVisible(False)
    
        self.pbColorModeBox.currentTextChanged.connect(lambda _t: _update_color_rows())
        _sync_grad_buttons()
        _update_color_rows()
    
        # Celebration (premium)
        self.showCelebrationCheckbox = _bool_box(getattr(self.db, "show_celebration", True))
        self.showCelebrationCheckbox.setToolTip(
            "Premium: plays a fast rainbow animation (~3 seconds) the FIRST time you reach 100%\n"
            "of today's target while reviewing (per deck, per day)."
        )
        prem_form.addRow("Show celebration:", self.showCelebrationCheckbox)
        
        # Streaks (premium - shown inside Feedback tab)
        self.streaksCheckbox = _bool_box(self.db.enable_streaks)
        prem_form.addRow("Enable streaks:", self.streaksCheckbox)
        
            
        # Lock whole section if free
        if not is_premium:
            lock_tip = "Unlock Premium to use this feature."
            
            # Force visual state for free users (show unchecked)
            if getattr(self, "streaksCheckbox", None):
                self.streaksCheckbox.setChecked(False)

            for w in (
                self.pbColorModeBox,
                self.pbSolidSwatch,
                self.pbGradSw1,
                self.pbGradSw2,
                self.pbGradSw3,
                self.pbGradAddBtn,
                self.pbGradDelBtn,
                self.showCelebrationCheckbox,
                self.streaksCheckbox,
            ):
                try:
                    w.setEnabled(False)
                    w.setToolTip(lock_tip)
                except Exception:
                    pass
    
        outer.addWidget(premiumGroup)
        outer.addStretch(1)
    
        self.tabs.addTab(tab, "Feedback")



    def _build_tab_premium(self) -> None:
        tab = QWidget()
        outer = QVBoxLayout(tab)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)
    
        premiumGroup = self._group("Deckline Premium")
        form = self._form(premiumGroup)
    
        # -------------------------
        # Activation (bovenaan)
        # -------------------------
        self.premiumStatusLabel = QLabel(
            "✅ Premium active" if self.db.is_premium else "🔒 Free version"
        )
        self.premiumStatusLabel.setStyleSheet("font-weight: 800;")
        form.addRow("Status:", self.premiumStatusLabel)
    
        self.premiumCodeEdit = QLineEdit()
        self.premiumCodeEdit.setPlaceholderText("Enter premium code (from Ko-fi)")
        form.addRow("Code:", self.premiumCodeEdit)
    
        btnRow = QWidget()
        btnRowL = QHBoxLayout(btnRow)
        btnRowL.setContentsMargins(0, 0, 0, 0)
        btnRowL.setSpacing(8)
    
        unlockBtn = QPushButton("Unlock")
        unlockBtn.setCursor(Qt.CursorShape.PointingHandCursor)
    
        def _refresh_status() -> None:
            self.premiumStatusLabel.setText(
                "✅ Premium active" if self.db.is_premium else "🔒 Free version"
            )
    
        def _unlock() -> None:
            from .core import verify_premium_code
    
            code = (self.premiumCodeEdit.text() or "").strip()
    
            if verify_premium_code(code):
                self.db.is_premium = True
                self.db.save()
                refreshDeadliner()
                _refresh_status()
                showInfo("Premium unlocked! 🎉\n\nStats + Premium features are now available.")
            else:
                showInfo("Invalid code.\n\nCheck your Ko-fi message and try again.")
    
        unlockBtn.clicked.connect(_unlock)
    
        btnRowL.addWidget(unlockBtn, 0)
        btnRowL.addStretch(1)
    
        form.addRow("", btnRow)
        
        # -------------------------
        # DEV tools (hidden for users)
        # -------------------------
        try:
            is_dev = (os.environ.get("DECKLINE_DEV", "") == "1")
        except Exception:
            is_dev = False

        if is_dev:
            devRow = QWidget()
            devRowL = QHBoxLayout(devRow)
            devRowL.setContentsMargins(0, 0, 0, 0)
            devRowL.setSpacing(8)

            devResetBtn = QPushButton("DEV: Reset to Free")
            devResetBtn.setCursor(Qt.CursorShape.PointingHandCursor)
            devResetBtn.setToolTip("Developer-only: force Premium OFF (sets Free version).")

            def _dev_reset_to_free() -> None:
                # Force premium off
                self.db.is_premium = False

                # Optional: also force premium-only settings back to free-safe defaults
                # (handig om te testen)
                try:
                    self.db.enable_streaks = False
                except Exception:
                    pass
                try:
                    self.db.show_celebration = False
                except Exception:
                    pass

                self.db.save()
                refreshDeadliner()
                _refresh_status()
                showInfo("DEV: Premium disabled (Free version).")

            devResetBtn.clicked.connect(_dev_reset_to_free)

            devRowL.addWidget(devResetBtn, 0)
            devRowL.addStretch(1)

            form.addRow("", devRow)

        # Subtle divider
        spacer = QLabel("")
        spacer.setFixedHeight(6)
        form.addRow(spacer)
    
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Plain)
        divider.setStyleSheet("color: rgba(255,255,255,0.15);")
        form.addRow(divider)
    
        # -------------------------
        # Pitch tekst (onderaan)
        # -------------------------
        pitchTitle = QLabel("❤️ Love Deckline? ❤️")
        f = pitchTitle.font()
        f.setBold(True)
        f.setPointSize(f.pointSize() + 1)
        pitchTitle.setFont(f)
    
        pitchText = QLabel(
            "Upgrade to Premium to support development and unlock:\n\n"
            "• Unlimited deadlines\n"
            "• 7-day Stats dashboard\n"
            "• Custom progress bar colors\n"
            "• Celebration animation\n"
            "• Add vacation days and automatically adjust your daily target\n"
            "• Future premium features"
        )
        pitchText.setWordWrap(True)
    
        form.addRow(pitchTitle)
        form.addRow(pitchText)
    
        outer.addWidget(premiumGroup)
        outer.addStretch(1)
    
        idx = self.tabs.addTab(tab, "⭐ Premium")
    
        # Make Premium tab stand out
        try:
            self.tabs.tabBar().setTabTextColor(idx, QColor(255, 90, 165))
            self.tabs.tabBar().setTabToolTip(idx, "Unlock Premium features (Stats + unlimited deadlines)")
        except Exception:
            pass
    
        # Bold only the Premium tab label
        self.tabs.setStyleSheet("""
        QTabBar::tab {
            padding: 8px 12px;
        }
        QTabBar::tab:selected {
            font-weight: 800;
        }
        """)




    def _build_tab_vacation(self) -> None:
        tab = QWidget()
        outer = QVBoxLayout(tab)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)
    
        is_premium = bool(getattr(self.db, "is_premium", False))
    
        if not is_premium:
            # Locked screen
            box = self._group("Vacation settings")
            v = QVBoxLayout(box)
            v.setContentsMargins(12, 12, 12, 12)
            v.setSpacing(10)
    
            msg = QLabel(
                "🔒 <b>Vacation days are Premium-only</b><br><br>"
                "Unlock Premium to add days off (vacation / exams / busy days) so Deckline adjusts your targets."
            )
            msg.setWordWrap(True)
            msg.setTextFormat(Qt.TextFormat.RichText)
    
            msg2 = QLabel("Tip: Premium also unlocks custom bar colors + celebration + stats + unlimited deadlines.")
            msg2.setWordWrap(True)
    
            v.addWidget(msg)
            v.addWidget(msg2)
            v.addStretch(1)
    
            outer.addWidget(box)
            outer.addStretch(1)
    
            idx = self.tabs.addTab(tab, "Vacation 🔒")
            try:
                self.tabs.setTabToolTip(idx, "Unlock Premium to enable Vacation days.")
            except Exception:
                pass
            return
    
        # ---- Premium: original Vacation UI ----
        group = self._group("Vacation settings")
        inner = QVBoxLayout(group)
        inner.setContentsMargins(12, 12, 12, 12)
        inner.setSpacing(10)
    
        # Single day
        r1 = QHBoxLayout()
        r1.setSpacing(8)
        self.vacSingleDate = self._date_edit(QDate.currentDate())
        btnAddDay = QPushButton("Add day")
        btnAddDay.setCursor(Qt.CursorShape.PointingHandCursor)
        r1.addWidget(self.vacSingleDate, 1)
        r1.addWidget(btnAddDay, 0)
        r1.addStretch(1)
        inner.addLayout(r1)
    
        # Range
        r2 = QHBoxLayout()
        r2.setSpacing(8)
        self.vacRangeStart = self._date_edit(QDate.currentDate())
        self.vacRangeEnd = self._date_edit(QDate.currentDate())
        btnAddRange = QPushButton("Add range")
        btnAddRange.setCursor(Qt.CursorShape.PointingHandCursor)
    
        r2.addWidget(self.vacRangeStart, 1)
        r2.addWidget(QLabel("to"), 0)
        r2.addWidget(self.vacRangeEnd, 1)
        r2.addWidget(btnAddRange, 0)
        r2.addStretch(1)
        inner.addLayout(r2)
    
        # List
        self.vacList = QListWidget()
        self.vacList.setMinimumHeight(50)
        self.vacList.setMaximumHeight(100)
        self.vacList.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.vacList.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        inner.addWidget(self.vacList)
    
        # Actions
        r3 = QHBoxLayout()
        r3.setSpacing(8)
        btnRemove = QPushButton("Remove selected")
        btnRemove.setCursor(Qt.CursorShape.PointingHandCursor)
        btnClear = QPushButton("Clear")
        btnClear.setCursor(Qt.CursorShape.PointingHandCursor)
        r3.addWidget(btnRemove)
        r3.addWidget(btnClear)
        r3.addStretch(1)
        inner.addLayout(r3)
    
        # Load existing entries
        for s in (self.deadlineDeck.skip_dates or []):
            s = (s or "").strip()
            if s:
                self.vacList.addItem(s)
    
        def _list_contains(val: str) -> bool:
            for i in range(self.vacList.count()):
                if self.vacList.item(i).text() == val:
                    return True
            return False
    
        def _add_day() -> None:
            d = self.vacSingleDate.date().toPyDate().strftime("%d-%m-%Y")
            if not _list_contains(d):
                self.vacList.addItem(d)
    
        def _add_range() -> None:
            a = self.vacRangeStart.date().toPyDate()
            b = self.vacRangeEnd.date().toPyDate()
            if b < a:
                a, b = b, a
            s = "%s/%s" % (a.strftime("%d-%m-%Y"), b.strftime("%d-%m-%Y"))
            if not _list_contains(s):
                self.vacList.addItem(s)
    
        def _remove_selected() -> None:
            for it in self.vacList.selectedItems():
                self.vacList.takeItem(self.vacList.row(it))
    
        def _clear_all() -> None:
            self.vacList.clear()
    
        btnAddDay.clicked.connect(_add_day)
        btnAddRange.clicked.connect(_add_range)
        btnRemove.clicked.connect(_remove_selected)
        btnClear.clicked.connect(_clear_all)
    
        outer.addWidget(group)
        outer.addStretch(1)
    
        idx = self.tabs.addTab(tab, "Vacation")
        try:
            self.tabs.setTabToolTip(idx, "Vacation days off (Premium).")
        except Exception:
            pass


    # ----------------------------
    # Footer
    # ----------------------------
    def _build_footer(self) -> QHBoxLayout:
        BTN_H = 40

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.on_accept)
        btns.rejected.connect(self.reject)

        for b in (btns.button(QDialogButtonBox.StandardButton.Save), btns.button(QDialogButtonBox.StandardButton.Cancel)):
            if b:
                b.setFixedHeight(BTN_H)
                b.setMinimumWidth(80)
                f = b.font()
                f.setBold(True)
                b.setFont(f)
                b.setStyleSheet(
                    "QPushButton { min-height: %dpx; max-height: %dpx; padding: 0 18px; font-weight: 800; }"
                    % (BTN_H, BTN_H)
                )

        kofi_btn = QPushButton("Upgrade to premium")
        kofi_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        kofi_btn.setFixedHeight(BTN_H)
        kofi_btn.setMaximumWidth(190)
        kofi_btn.setStyleSheet(
            """
            QPushButton { background: #FF5AA5; color: white; border: none; border-radius: 12px;
                         padding: 0 16px; font-size: 14px; font-weight: 800; }
            QPushButton:hover { background: #FF3F98; }
            """
        )
        kofi_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://ko-fi.com/s/d708f4b514")))

        review_btn = QToolButton()
        review_btn.setText("👍")
        # Ensure the emoji renders (fallback fonts can turn it into ellipsis)
        try:
            f = QFont()
            f.setFamilies(["Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", "Segoe UI Symbol"])
            review_btn.setFont(f)
        except Exception:
            pass
        review_btn.setToolTip("Leave a review on AnkiWeb")
        review_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        review_btn.setFixedSize(BTN_H, BTN_H)
        review_btn.setStyleSheet(
            """
            QToolButton { background: #22C55E; color: white; border: none; border-radius: 12px;
              font-weight: 800; font-size: 18px; padding: 0px; }
            QToolButton:hover { background: #16A34A; }
            """
        )
        review_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://ankiweb.net/shared/review/1517382883")))

        support_row = QHBoxLayout()
        support_row.setSpacing(8)
        support_row.addWidget(kofi_btn)
        support_row.addWidget(review_btn)

        footer = QHBoxLayout()
        footer.setSpacing(10)
        footer.addWidget(btns)
        footer.addStretch(1)
        footer.addLayout(support_row)
        return footer

    # ----------------------------
    # Behavior
    # ----------------------------
    def onToggleEnable(self, enabled: bool) -> None:
        self.deadlineDeck.enabled = bool(enabled)
        if getattr(self, "tabs", None):
            self.tabs.setDisabled(not bool(enabled))

    def on_accept(self) -> None:
            # Deadline tab
            self.deadlineDeck.name = self.nameEdit.text().strip() or self.deadlineDeck.name
            self.deadlineDeck.deadline = self.deadlineDateEdit.date().toPyDate().strftime("%d-%m-%Y")
            self.deadlineDeck.start_date = self.startDateEdit.date().toPyDate().strftime("%d-%m-%Y")
    
            offset = self.deadlineDateEdit.date().daysTo(self.cutoffDateEdit.date())
            self.deadlineDeck.cutoff_offset = min(-1, int(offset))
    
            self.deadlineDeck.expected_total_cards = int(self.expectedTotalEdit.value()) if getattr(self, "expectedTotalEdit", None) else 0
    
            # daily target override (0 = off)
            self.deadlineDeck.daily_target_override = int(self.dailyTargetOverrideEdit.value()) if getattr(self, "dailyTargetOverrideEdit", None) else 0
            self.deadlineDeck.skip_weekends = bool(self.skipWeekendsCheckbox.isChecked())
    
            # Vacation list
            lines = []
            if getattr(self, "vacList", None):
                for i in range(self.vacList.count()):
                    t = (self.vacList.item(i).text() or "").strip()
                    if t:
                        lines.append(t)
            self.deadlineDeck.skip_dates = lines
    
            # ----------------------------
            # Feedback settings (global)
            # ----------------------------
            if getattr(self, "progressStyleBox", None):
                self.db.progress_style = self.progressStyleBox.currentText()
    
            if getattr(self, "todayRowCheckbox", None):
                self.db.show_today_row = bool(self.todayRowCheckbox.isChecked())
    
            if getattr(self, "dailyProgressCheckbox", None):
                self.db.show_daily_progress = bool(self.dailyProgressCheckbox.isChecked())
    
            # ✅ Review screen progress bar toggle
            if getattr(self, "reviewProgressCheckbox", None):
                self.db.show_review_progress = bool(self.reviewProgressCheckbox.isChecked())
    
            is_premium = bool(getattr(self.db, "is_premium", False))
    
            # --- PREMIUM: celebration + bar colors ---
            if is_premium:
                if getattr(self, "showCelebrationCheckbox", None):
                    self.db.show_celebration = bool(self.showCelebrationCheckbox.isChecked())
    
                mode_txt = self.pbColorModeBox.currentText().lower() if getattr(self, "pbColorModeBox", None) else "auto"
                mode = "auto"
                if mode_txt == "solid":
                    mode = "solid"
                elif mode_txt == "gradient":
                    mode = "gradient"
    
                solid = getattr(self, "_pb_solid_hex", "#22C55E")
                grad = getattr(self, "_pb_grad_hexes", ["#EF4444", "#F59E0B", "#22C55E"])
                if not isinstance(grad, list) or len(grad) < 2:
                    grad = ["#EF4444", "#F59E0B", "#22C55E"]
    
                self.db.db["progress_fill"] = {
                    "mode": mode,
                    "solid": str(solid),
                    "gradient": [str(x) for x in grad[:3]],
                }
            else:
                # Free users: keep consistent defaults
                self.db.show_celebration = False
                self.db.enable_streaks = False
                self.db.db["progress_fill"] = {
                    "mode": "auto",
                    "solid": "#22C55E",
                    "gradient": ["#EF4444", "#F59E0B", "#22C55E"],
                }

    
            if getattr(self, "timeMultiplierSpin", None):
                self.db.time_multiplier = float(self.timeMultiplierSpin.multiplier())
    
            # --- If NOT global mode → save per-deck deadline ---
            if not self._global_mode:
                ok = self.deadlineDeck.save()
                if not ok:
                    # Save blocked by free limit → keep dialog open
                    return
    
            # Always save global config (feedback, colors, etc.)
            self.db.save()
    
            refreshDeadliner()
    
            # ✅ Apply show/hide immediately if the reviewer is open
            try:
                from .ui import review_progress_bar
                review_progress_bar.refresh_visibility()
            except Exception:
                pass
    
            self.accept()
    
    
    
