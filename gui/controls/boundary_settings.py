from PySide6.QtWidgets import (
    QGroupBox, QFormLayout, QCheckBox, QPushButton,
    QDoubleSpinBox, QComboBox, QColorDialog
)
from utils.config import config_manager


class BoundarySettingsGroup(QGroupBox):
    def __init__(self, levels=None, parent=None):
        """
        Dynamische Gruppe für die Admin-Grenzen.
        :param levels: Liste der Levels, z. B. ["ADM_1", "ADM_2"]
        """
        super().__init__("Grenzen", parent)
        self.session_config = config_manager.get_session()
        self.levels = levels or []
        self.controls = {}

        layout = QFormLayout(self)

        # Linienstile aus Config oder Defaults
        self.line_styles = ["solid", "dashed", "dotted", "dashdot"]

        for level in self.levels:
            # NEU: Zugriff auf styles -> hauptland_boundaries
            cfg = (
                self.session_config.get("styles", {})
                .get("hauptland_boundaries", {})
                .get(level, {})
            )
            row = {}

            # Sichtbarkeit
            cb_show = QCheckBox("anzeigen")
            cb_show.setChecked(cfg.get("show", False))
            row["show"] = cb_show

            # Farbe
            btn_color = QPushButton("Farbe wählen")
            btn_color.setStyleSheet(f"background-color: {cfg.get('color', '#000000')};")
            btn_color.clicked.connect(lambda _, l=level: self._choose_color(l))
            row["color"] = btn_color

            # Linienbreite
            sp_width = QDoubleSpinBox()
            sp_width.setRange(0.1, 10.0)
            sp_width.setValue(cfg.get("width", 1.0))
            row["width"] = sp_width

            # Linienstil
            cmb_style = QComboBox()
            cmb_style.addItems(self.line_styles)
            cmb_style.setCurrentText(cfg.get("style", self.line_styles[0]))
            row["style"] = cmb_style

            # GUI zusammenbauen
            layout.addRow(f"{level}:", cb_show)
            layout.addRow("Farbe:", btn_color)
            layout.addRow("Linienbreite:", sp_width)
            layout.addRow("Linienstil:", cmb_style)

            self.controls[level] = row

    def _choose_color(self, level: str):
        col = QColorDialog.getColor()
        if col.isValid():
            self.controls[level]["color"].setStyleSheet(f"background-color: {col.name()};")
            self.controls[level]["color_value"] = col.name()  # Farbe speichern
            # NEU: Direkt in styles -> hauptland_boundaries schreiben
            self.session_config["styles"]["hauptland_boundaries"][level]["color"] = col.name()

    def apply_to_config(self):
        # NEU: Keine alte Struktur mehr, direkt in styles -> hauptland_boundaries
        for level, row in self.controls.items():
            self.session_config["styles"]["hauptland_boundaries"][level].update({
                "show": row["show"].isChecked(),
                "width": row["width"].value(),
                "style": row["style"].currentText(),
                "color": row.get("color_value", self.session_config["styles"]["hauptland_boundaries"][level]["color"]),
            })

    def update_levels(self, levels):
        """Ersetzt die Controls basierend auf neuen Levels."""
        # alte Controls entfernen
        for i in reversed(range(self.layout().count())):
            widget = self.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.controls.clear()

        # neue Levels setzen
        self.levels = levels

        for level in self.levels:
            cfg = (
                self.session_config.get("styles", {})
                .get("hauptland_boundaries", {})
                .get(level, {})
            )
            row = {}

            cb_show = QCheckBox("anzeigen")
            cb_show.setChecked(cfg.get("show", False))
            row["show"] = cb_show

            btn_color = QPushButton("Farbe wählen")
            btn_color.setStyleSheet(f"background-color: {cfg.get('color', '#000000')};")
            btn_color.clicked.connect(lambda _, l=level: self._choose_color(l))
            row["color"] = btn_color

            sp_width = QDoubleSpinBox()
            sp_width.setRange(0.1, 10.0)
            sp_width.setValue(cfg.get("width", 1.0))
            row["width"] = sp_width

            cmb_style = QComboBox()
            cmb_style.addItems(self.line_styles)
            cmb_style.setCurrentText(cfg.get("style", self.line_styles[0]))
            row["style"] = cmb_style

            self.layout().addRow(f"{level}:", cb_show)
            self.layout().addRow("Farbe:", btn_color)
            self.layout().addRow("Linienbreite:", sp_width)
            self.layout().addRow("Linienstil:", cmb_style)

            self.controls[level] = row