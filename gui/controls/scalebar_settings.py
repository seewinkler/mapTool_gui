# gui/controls/scalebar_settings.py
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QCheckBox, QComboBox
from PySide6.QtCore import Slot

class ScalebarSettingsGroup(QGroupBox):
    """
    GroupBox für Scalebar-Optionen:
    - Anzeigen / Verbergen
    - Position
    """

    def __init__(self, composer, on_changed, parent=None):
        super().__init__("Scalebar", parent)
        self.composer = composer  # enthält session_config
        layout = QHBoxLayout(self)

        # Fallbacks aus Session-Config
        sb_cfg = self.composer.config.get("scalebar", {})
        show_default = sb_cfg.get("show", False)
        pos_default = sb_cfg.get("position", "bottom-right")

        # Checkbox: Anzeigen
        self.cb_sb_show = QCheckBox("Anzeigen", self)
        self.cb_sb_show.setChecked(show_default)
        self.cb_sb_show.stateChanged.connect(self._on_show_changed)

        # Combobox: Position
        self.cmb_sb_pos = QComboBox(self)
        self.cmb_sb_pos.addItems([
            "bottom-left", "bottom-right", "bottom-center",
            "top-left", "top-right", "top-center", "none"
        ])
        self.cmb_sb_pos.setCurrentText(pos_default)
        self.cmb_sb_pos.currentTextChanged.connect(self._on_position_changed)

        layout.addWidget(self.cb_sb_show)
        layout.addWidget(self.cmb_sb_pos)

        # Callback für externe Änderungen (z. B. Preview)
        self.on_changed = on_changed

    @Slot()
    def _on_show_changed(self):
        # Änderung nur in Session-Config
        self.composer.config["scalebar"]["show"] = self.cb_sb_show.isChecked()
        if self.on_changed:
            self.on_changed()

    @Slot()
    def _on_position_changed(self):
        # Änderung nur in Session-Config
        self.composer.config["scalebar"]["position"] = self.cmb_sb_pos.currentText()
        if self.on_changed:
            self.on_changed()