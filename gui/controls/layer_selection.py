# gui/controls/layer_selection.py

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QListWidget, QListWidgetItem
from PySide6.QtCore    import Qt

class LayerSelectionGroup(QGroupBox):
    """
    GroupBox für Layer-Listen:
      - Alle Layer auflisten
      - Ausblenden
      - Hervorheben
    """
    def __init__(self, on_layers_changed, on_hide_changed, on_highlight_changed, parent=None):
        super().__init__("Layer / Gebiete", parent)
        layout = QHBoxLayout(self)

        self.lst_layers = QListWidget(self)
        self.lst_layers.itemChanged.connect(on_layers_changed)

        self.lst_hide = QListWidget(self)
        self.lst_hide.itemChanged.connect(on_hide_changed)

        self.lst_high = QListWidget(self)
        self.lst_high.itemChanged.connect(on_highlight_changed)

        layout.addWidget(self.lst_layers)
        layout.addWidget(self.lst_hide)
        layout.addWidget(self.lst_high)