# gui/controls/layer_selection.py

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QListWidget
from PySide6.QtCore import Qt

def toggle_item_check(item):
    if item.checkState() == Qt.Checked:
        item.setCheckState(Qt.Unchecked)
    else:
        item.setCheckState(Qt.Checked)

class LayerSelectionGroup(QGroupBox):
    """Nur Ausgewählter Layer."""
    def __init__(self, on_layers_changed, parent=None):
        super().__init__("Hauptland: Layer", parent)

        outer = QVBoxLayout(self)
        outer.setSpacing(10)

        lbl_layer = QLabel("Ausgewählter Layer")
        lbl_layer.setStyleSheet("font-weight: bold;")
        outer.addWidget(lbl_layer)

        self.lst_layers = QListWidget(self)
        self.lst_layers.itemChanged.connect(on_layers_changed)
        self.lst_layers.itemClicked.connect(toggle_item_check)
        outer.addWidget(self.lst_layers)


class LayerFilterGroup(QGroupBox):
    """Ausblenden und Hervorheben."""
    def __init__(self, on_hide_changed, on_highlight_changed, parent=None):
        super().__init__("Layer-Filter", parent)

        row = QHBoxLayout(self)

        # Ausblenden
        col_hide = QVBoxLayout()
        lbl_hide = QLabel("Ausblenden")
        lbl_hide.setStyleSheet("font-weight: bold;")
        col_hide.addWidget(lbl_hide)

        self.lst_hide = QListWidget(self)
        self.lst_hide.itemChanged.connect(on_hide_changed)
        self.lst_hide.itemClicked.connect(toggle_item_check)
        col_hide.addWidget(self.lst_hide)

        # Hervorheben
        col_high = QVBoxLayout()
        lbl_high = QLabel("Hervorheben")
        lbl_high.setStyleSheet("font-weight: bold;")
        col_high.addWidget(lbl_high)

        self.lst_high = QListWidget(self)
        self.lst_high.itemChanged.connect(on_highlight_changed)
        self.lst_high.itemClicked.connect(toggle_item_check)
        col_high.addWidget(self.lst_high)

        row.addLayout(col_hide)
        row.addLayout(col_high)