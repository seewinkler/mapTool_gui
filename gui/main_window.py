# gui/main_window.py
import logging
from typing import Any, Dict

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QPlainTextEdit,
)

from gui.drop_panel import DropPanel
from gui.map_canvas import MapCanvas
from gui.log_viewer import QTextEditLogger
from gui.controls.map_settings import MapSettingsGroup
from gui.controls.scalebar_settings import ScalebarSettingsGroup
from gui.controls.background_settings import BackgroundSettingsGroup
from gui.controls.layer_selection import LayerSelectionGroup
from gui.controls.export_settings import ExportSettingsGroup


class MainWindow(QMainWindow):
    """
    Hauptfenster der Anwendung.
    Verantwortlich für den Aufbau der UI und das Bereitstellen
    von Widget-Referenzen für den Controller.
    """

    def __init__(self, composer: Any, config: Dict[str, Any]) -> None:
        super().__init__()
        self.composer = composer
        self.config = config

        self._apply_initial_composer_settings()
        self._build_ui()
        self._setup_logging()
        self._apply_config_defaults()

    # ------------------------------------------------------------
    # Initiale Composer-Einstellungen
    # ------------------------------------------------------------
    def _apply_initial_composer_settings(self) -> None:
        """Setzt Hintergrund und Dimensionen im Composer basierend auf CONFIG."""
        bg_cfg = self.config.get("background", {})
        self.composer.set_background(
            color=bg_cfg.get("color", "#ffffff"),
            transparent=bg_cfg.get("transparent", False)
        )

        karte_cfg = self.config.get("karte", {})
        self.composer.set_dimensions(
            karte_cfg.get("breite", 800),
            karte_cfg.get("hoehe", 600)
        )

    # ------------------------------------------------------------
    # UI-Aufbau
    # ------------------------------------------------------------
    def _build_ui(self) -> None:
        ui_cfg = self.config.get("ui", {})
        self.setWindowTitle(ui_cfg.get("window_title", "mapTool GUI"))
        self.setMinimumSize(800, 600)

        central = QWidget(self)
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)

        # DropPanel
        self.drop_panel = DropPanel(copy_to_temp=True)
        main_layout.addWidget(self.drop_panel)

        # Split: Canvas & Controls
        content_layout = QHBoxLayout()
        content_layout.setSpacing(6)
        main_layout.addLayout(content_layout)

        # MapCanvas
        karte_cfg = self.config.get("karte", {})
        w = karte_cfg.get("breite", 800)
        h = karte_cfg.get("hoehe", 600)
        self.map_canvas = MapCanvas(self.composer, width=w, height=h)
        content_layout.addWidget(self.map_canvas, stretch=3)

        # Controls-Palette
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(6)
        content_layout.addLayout(controls_layout, stretch=1)

        # MapSettingsGroup
        self.map_settings = MapSettingsGroup(
            composer=self.composer,
            on_epsg=lambda: None,
            on_dimensions_changed=lambda _: None
        )
        self.btn_epsg = self.map_settings.btn_epsg
        self.sp_w = self.map_settings.sp_w
        self.sp_h = self.map_settings.sp_h
        controls_layout.addWidget(self.map_settings)

        # ScalebarSettingsGroup
        self.scalebar_settings = ScalebarSettingsGroup(
            composer=self.composer,
            on_changed=lambda _: None
        )
        self.cb_sb_show = self.scalebar_settings.cb_sb_show
        self.cmb_sb_pos = self.scalebar_settings.cmb_sb_pos
        controls_layout.addWidget(self.scalebar_settings)

        # BackgroundSettingsGroup
        self.bg_settings = BackgroundSettingsGroup(
            composer=self.composer,
            on_choose_color=lambda: None,
            on_toggled=lambda _: None
        )
        self.btn_col = self.bg_settings.btn_col
        self.cb_transp = self.bg_settings.cb_transp
        controls_layout.addWidget(self.bg_settings)

        # LayerSelectionGroup
        self.layer_selection = LayerSelectionGroup(
            on_layers_changed=lambda _: None,
            on_hide_changed=lambda _: None,
            on_highlight_changed=lambda _: None
        )
        self.lst_layers = self.layer_selection.lst_layers
        self.lst_hide = self.layer_selection.lst_hide
        self.lst_high = self.layer_selection.lst_high
        controls_layout.addWidget(self.layer_selection)

        # ExportSettingsGroup
        self.export_settings = ExportSettingsGroup()
        self.cb_png = self.export_settings.cb_png
        self.cb_svg = self.export_settings.cb_svg
        controls_layout.addWidget(self.export_settings)

        # Log-Widget
        self.log_widget = QPlainTextEdit(self)
        self.log_widget.setReadOnly(True)
        controls_layout.addWidget(self.log_widget, stretch=1)

        # Render-Button
        self.btn_render = QPushButton("Karte rendern", self)
        controls_layout.addWidget(self.btn_render)

    # ------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------
    def _setup_logging(self) -> None:
        """Richtet Logging-Ausgabe ins Log-Widget ein."""
        handler = QTextEditLogger(self.log_widget)
        logging.getLogger().addHandler(handler)
        lvl = self.config.get("logging", {}).get("level", "INFO").upper()
        logging.getLogger().setLevel(getattr(logging, lvl, logging.INFO))

    # ------------------------------------------------------------
    # UI-Defaults aus CONFIG
    # ------------------------------------------------------------
    def _apply_config_defaults(self) -> None:
        """Überträgt Startwerte aus CONFIG in die UI-Elemente."""
        # Hintergrund
        bg_cfg = self.config.get("background", {})
        self.cb_transp.setChecked(bg_cfg.get("transparent", False))
        self.btn_col.hide()

        # Scalebar
        sb = self.config.get("scalebar", {})
        self.cb_sb_show.setChecked(sb.get("show", False))
        self.cmb_sb_pos.setCurrentText(sb.get("position", "bottom-right"))

        # Dimensionen
        karte = self.config.get("karte", {})
        w = karte.get("breite", 800)
        h = karte.get("hoehe", 600)
        self.sp_w.setValue(w)
        self.sp_h.setValue(h)

        self.map_canvas.setFixedSize(w, h)
        self.map_canvas.refresh()