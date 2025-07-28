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
from utils.config import CONFIG


class MainWindow(QMainWindow):
    def __init__(self, composer: Any, config: Dict[str, Any]) -> None:
        super().__init__()
        self.composer = composer
        self.config   = config

        # -- Setze initial Hintergrund im Composer --
        bg_cfg = self.config.get("background", {})
        self.composer.set_background(
            color=bg_cfg.get("color", "#ffffff"),
            transparent=bg_cfg.get("transparent", False)
        )

        # -- Setze initial Dimensionen im Composer --
        karte_cfg = self.config.get("karte", {})
        self.composer.set_dimensions(
            karte_cfg.get("breite", 800),
            karte_cfg.get("hoehe", 600)
        )

        self._build_ui()
        self._setup_logging()
        self._apply_config_defaults()

    def _build_ui(self) -> None:
        ui_cfg = self.config.get("ui", {})
        self.setWindowTitle(ui_cfg.get("window_title", "mapTool GUI"))
        self.setMinimumSize(800, 600)

        central = QWidget(self)
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)

        # 1) DropPanel
        self.drop_panel = DropPanel(copy_to_temp=True)
        main_layout.addWidget(self.drop_panel)

        # 2) Split Canvas & Controls
        content_layout = QHBoxLayout()
        content_layout.setSpacing(6)
        main_layout.addLayout(content_layout)

        # 2a) MapCanvas (nutzt composer.background_cfg & dimensions)
        karte_cfg = self.config.get("karte", {})
        w = karte_cfg.get("breite", 800)
        h = karte_cfg.get("hoehe", 600)
        self.map_canvas = MapCanvas(self.composer, width=w, height=h)
        content_layout.addWidget(self.map_canvas, stretch=3)

        # 2b) Controls-Palette
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(6)
        content_layout.addLayout(controls_layout, stretch=1)

        # MapSettingsGroup
        self.map_settings = MapSettingsGroup(
            composer=self.composer,
            on_epsg=lambda: None,
            on_dimensions_changed=self._on_dimensions_changed
        )
        self.btn_epsg = self.map_settings.btn_epsg
        self.sp_w     = self.map_settings.sp_w
        self.sp_h     = self.map_settings.sp_h
        controls_layout.addWidget(self.map_settings)

        # ScalebarSettingsGroup
        self.scalebar_settings = ScalebarSettingsGroup(
            composer=self.composer,
            on_changed=lambda _: None
        )
        self.cb_sb_show = self.scalebar_settings.cb_sb_show
        self.cmb_sb_pos = self.scalebar_settings.cmb_sb_pos
        controls_layout.addWidget(self.scalebar_settings)

        # BackgroundSettingsGroup (Button bleibt, ruft nun map_canvas an)
        self.bg_settings = BackgroundSettingsGroup(
            composer=self.composer,
            on_choose_color=lambda: None,
            on_toggled=lambda _: None
        )
        self.btn_col   = self.bg_settings.btn_col
        self.cb_transp = self.bg_settings.cb_transp
        controls_layout.addWidget(self.bg_settings)

        # LayerSelectionGroup
        self.layer_selection = LayerSelectionGroup(
            on_layers_changed=lambda _: None,
            on_hide_changed=lambda _: None,
            on_highlight_changed=lambda _: None
        )
        self.lst_layers = self.layer_selection.lst_layers
        self.lst_hide   = self.layer_selection.lst_hide
        self.lst_high   = self.layer_selection.lst_high
        controls_layout.addWidget(self.layer_selection)

        # ExportSettingsGroup
        self.export_settings = ExportSettingsGroup()
        self.cb_png = self.export_settings.cb_png
        self.cb_svg = self.export_settings.cb_svg
        controls_layout.addWidget(self.export_settings)

        # Log + Render
        self.log_widget = QPlainTextEdit(self)
        self.log_widget.setReadOnly(True)
        controls_layout.addWidget(self.log_widget, stretch=1)

        self.btn_render = QPushButton("Karte rendern", self)
        controls_layout.addWidget(self.btn_render)
        self.btn_render.clicked.connect(self.map_canvas.refresh)

    def _setup_logging(self) -> None:
        handler = QTextEditLogger(self.log_widget)
        logging.getLogger().addHandler(handler)
        lvl = self.config.get("logging", {}).get("level", "INFO").upper()
        logging.getLogger().setLevel(getattr(logging, lvl, logging.INFO))

    def _apply_config_defaults(self) -> None:
        # Hinter­grund-Checkbox & Farb­button
        bg_cfg = self.config.get("background", {})
        self.cb_transp.setChecked(bg_cfg.get("transparent", False))
        self.btn_col.hide()

        # Scalebar
        sb = self.config.get("scalebar", {})
        self.cb_sb_show.setChecked(sb.get("show", False))
        self.cmb_sb_pos.setCurrentText(sb.get("position", "bottom-right"))

        # Dimensionen in Spin­boxes & Preview
        karte = self.config.get("karte", {})
        w = karte.get("breite", 800)
        h = karte.get("hoehe", 600)
        self.sp_w.setValue(w)
        self.sp_h.setValue(h)

        self.map_canvas.setFixedSize(w, h)
        self.map_canvas.refresh()

    def _on_dimensions_changed(self, _val: int) -> None:
        w = self.sp_w.value()
        h = self.sp_h.value()
        self.composer.set_dimensions(w, h)
        self.config["karte"]["breite"] = w
        self.config["karte"]["hoehe"]  = h
        self.map_canvas.setFixedSize(w, h)
        self.map_canvas.refresh()