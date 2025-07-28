# gui/controls/scalebar_settings.py

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QCheckBox, QComboBox
from PySide6.QtCore    import Slot

class ScalebarSettingsGroup(QGroupBox):
    """
    GroupBox für Scalebar‐Optionen:
      - Anzeigen / Verbergen
      - Position
    """
    def __init__(self, composer, on_changed, parent=None):
        super().__init__("Scalebar", parent)
        self.composer = composer
        layout = QHBoxLayout(self)

        self.cb_sb_show = QCheckBox("Anzeigen", self)
        self.cb_sb_show.setChecked(self.composer.scalebar_cfg["show"])
        self.cb_sb_show.stateChanged.connect(on_changed)

        self.cmb_sb_pos = QComboBox(self)
        self.cmb_sb_pos.addItems(
            ["bottom-left", "bottom-right", "bottom-center", "none"]
        )
        self.cmb_sb_pos.setCurrentText(self.composer.scalebar_cfg["position"])
        self.cmb_sb_pos.currentTextChanged.connect(on_changed)

        layout.addWidget(self.cb_sb_show)
        layout.addWidget(self.cmb_sb_pos)