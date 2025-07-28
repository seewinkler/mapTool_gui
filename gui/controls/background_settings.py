# gui/controls/background_settings.py

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QPushButton, QCheckBox

class BackgroundSettingsGroup(QGroupBox):
    """
    GroupBox für Hintergrund:
      - Farbe wählen
      - Transparenz on/off
    """
    def __init__(self, composer, on_choose_color, on_toggled, parent=None):
        super().__init__("Hintergrund", parent)
        self.composer = composer
        layout = QHBoxLayout(self)

        # ALS ATTRIBUTE anlegen
        self.btn_col = QPushButton("Farbe wählen", self)
        self.btn_col.clicked.connect(on_choose_color)

        self.cb_transp = QCheckBox("Transparent", self)
        self.cb_transp.setChecked(self.composer.background_cfg["transparent"])
        self.cb_transp.stateChanged.connect(on_toggled)

        layout.addWidget(self.btn_col)
        layout.addWidget(self.cb_transp)