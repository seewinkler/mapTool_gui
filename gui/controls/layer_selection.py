# gui/controls/layer_selection.py

from PySide6.QtWidgets import (
    QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, QListWidget
)
from PySide6.QtCore import Qt

class LayerSelectionGroup(QGroupBox):
    """
    GroupBox für Layer-Listen:
      - Haupttitel
      - Ausgewählter Layer
      - Ausblenden
      - Hervorheben
    """
    def __init__(self, on_layers_changed, on_hide_changed, on_highlight_changed, parent=None):
        super().__init__("Hauptland: Layer und Gebiete", parent)

        outer = QVBoxLayout(self)
        outer.setSpacing(10)

        # Layer-Bereich
        lbl_layer = QLabel("Ausgewählter Layer")
        lbl_layer.setStyleSheet("font-weight: bold;")
        outer.addWidget(lbl_layer)

        self.lst_layers = QListWidget(self)
        self.lst_layers.itemChanged.connect(on_layers_changed)
        outer.addWidget(self.lst_layers)

        # Ausblenden / Hervorheben nebeneinander
        row = QHBoxLayout()

        # Ausblenden-Spalte
        col_hide = QVBoxLayout()
        lbl_hide = QLabel("Ausblenden")
        lbl_hide.setStyleSheet("font-weight: bold;")
        col_hide.addWidget(lbl_hide)

        self.lst_hide = QListWidget(self)
        self.lst_hide.itemChanged.connect(on_hide_changed)
        col_hide.addWidget(self.lst_hide)

        # Hervorheben-Spalte
        col_high = QVBoxLayout()
        lbl_high = QLabel("Hervorheben")
        lbl_high.setStyleSheet("font-weight: bold;")
        col_high.addWidget(lbl_high)

        self.lst_high = QListWidget(self)
        self.lst_high.itemChanged.connect(on_highlight_changed)
        col_high.addWidget(self.lst_high)

        row.addLayout(col_hide)
        row.addLayout(col_high)

        outer.addLayout(row)