# gui/controls/export_settings.py

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QCheckBox

class ExportSettingsGroup(QGroupBox):
    """
    GroupBox für Export‐Formate:
      - PNG, SVG, …
    """
    def __init__(self, parent=None):
        super().__init__("Export-Formate", parent)
        layout = QHBoxLayout(self)

        self.cb_png = QCheckBox("PNG", self)
        self.cb_png.setChecked(True)

        self.cb_svg = QCheckBox("SVG", self)

        layout.addWidget(self.cb_png)
        layout.addWidget(self.cb_svg)