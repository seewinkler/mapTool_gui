# gui/controllers/main_controller.py

from typing import Any
import sys
import logging

from fiona import listlayers
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication

from data_processing.layers import merge_hauptland_layers
from gui.auswahlfenster import AuswahlFenster
from utils.config import save_config, CONFIG

from .file_controller import FileController
from .layer_controller import LayerController
from .settings_controller import SettingsController
from .appearance_controller import AppearanceController
from .export_controller import ExportController
from .epsg_controller import EpsgController


class MainController:
    """
    Zentraler Orchestrator der Anwendung.
    Verbindet View (MainWindow) mit den einzelnen Funktions-Controllern.
    """

    def __init__(self, composer: Any, view: Any) -> None:
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.composer = composer
        self.view = view
        self.config = view.config

        self._init_subcontrollers()

    # ------------------------------------------------------------
    # Initialisierung
    # ------------------------------------------------------------
    def _init_subcontrollers(self) -> None:
        """Erzeugt alle Subcontroller."""
        self.file_ctrl = FileController(self.composer, self.view)
        self.layer_ctrl = LayerController(self.composer, self.view)
        self.settings_ctrl = SettingsController(self.composer, self.view, self.config)
        self.appearance_ctrl = AppearanceController(self.composer, self.view, self.config, self.view)
        self.export_ctrl = ExportController(self.composer, self.view, self.config, self.view)
        self.epsg_ctrl = EpsgController(self.composer, self.view, self.config, self.view)

    # ------------------------------------------------------------
    # Signal-Verbindungen
    # ------------------------------------------------------------
    def _connect_file_signals(self) -> None:
        dp = self.view.drop_panel
        dp.drop_main.dropChanged.connect(self.file_ctrl.handle_files_changed)
        dp.drop_sub.dropChanged.connect(self.file_ctrl.handle_files_changed)

    def _connect_layer_signals(self) -> None:
        self.view.lst_layers.itemChanged.connect(self.layer_ctrl.handle_primary_selection)
        self.view.lst_hide.itemChanged.connect(self.layer_ctrl.handle_hide_changed)
        self.view.lst_high.itemChanged.connect(self.layer_ctrl.handle_highlight_changed)

    def _connect_settings_signals(self) -> None:
        self.view.sp_w.valueChanged.connect(self.settings_ctrl.handle_dimensions_changed)
        self.view.sp_h.valueChanged.connect(self.settings_ctrl.handle_dimensions_changed)
        self.view.cb_sb_show.stateChanged.connect(self.settings_ctrl.handle_scalebar_changed)
        self.view.cmb_sb_pos.currentTextChanged.connect(self.settings_ctrl.handle_scalebar_changed)

    def _connect_appearance_signals(self) -> None:
        self.view.btn_col.clicked.connect(self.appearance_ctrl.choose_bg_color)
        self.view.cb_transp.stateChanged.connect(self.appearance_ctrl.background_changed)

    def _connect_export_signals(self) -> None:
        self.view.btn_render.clicked.connect(self.export_ctrl.render_clicked)

    def _connect_epsg_signals(self) -> None:
        self.view.btn_epsg.clicked.connect(self.epsg_ctrl.select_epsg)

    def _connect_all_signals(self) -> None:
        """Verbindet alle Signalgruppen."""
        self._connect_file_signals()
        self._connect_layer_signals()
        self._connect_settings_signals()
        self._connect_appearance_signals()
        self._connect_export_signals()
        self._connect_epsg_signals()

    # ------------------------------------------------------------
    # Laufsteuerung
    # ------------------------------------------------------------
    def run(self) -> int:
        """Startet die Anwendung."""
        self._connect_all_signals()
        self.view.show()
        # Optional: initiale Vorschau, falls schon Daten geladen sind
        self.view.map_canvas.refresh(preview=True)
        return self.app.exec()