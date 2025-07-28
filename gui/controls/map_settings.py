# gui/controls/map_settings.py

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QPushButton, QSpinBox

class MapSettingsGroup(QGroupBox):
    """
    GroupBox für Karten‐Settings:
      - EPSG‐Dialog öffnen
      - Breite / Höhe per SpinBox
    """
    def __init__(self, composer, on_epsg, on_dimensions_changed, parent=None):
        super().__init__("Karte", parent)
        self.composer = composer
        layout = QHBoxLayout(self)

        # ALS ATTRIBUTE anlegen
        self.btn_epsg = QPushButton("EPSG wählen…", self)
        self.btn_epsg.clicked.connect(on_epsg)

        self.sp_w = QSpinBox(self)
        self.sp_w.setRange(100, 5000)
        self.sp_w.setValue(self.composer.width_px)
        self.sp_w.valueChanged.connect(on_dimensions_changed)

        self.sp_h = QSpinBox(self)
        self.sp_h.setRange(100, 5000)
        self.sp_h.setValue(self.composer.height_px)
        self.sp_h.valueChanged.connect(on_dimensions_changed)

        layout.addWidget(self.btn_epsg)
        layout.addWidget(self.sp_w)
        layout.addWidget(self.sp_h)