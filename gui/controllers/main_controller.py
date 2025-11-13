# gui/controllers/main_controller.py

from typing import Any
import sys
import logging

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication

from utils.config import CONFIG

from .file_controller import FileController
from .layer_controller import LayerController
from .settings_controller import SettingsController
from .appearance_controller import AppearanceController
from .export_controller import ExportController
from .epsg_controller import EpsgController
from .reset_service import ResetService

class MainController:
    """
    Zentraler Orchestrator der Anwendung.
    Verbindet View (MainWindow) mit den einzelnen Funktions-Controllern.
    """

    def __init__(self, composer: Any, view: Any) -> None:
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.composer = composer
        self.view = view
        self.config = CONFIG  # Verwende globale CONFIG (SESSION_CONFIG in main.py)
        self.reset_service = ResetService(self.composer, self.view)


        # Vorschau-Steuerung
        self.preview_dirty: bool = False

        self._init_subcontrollers()

    # ------------------------------------------------------------
    # Initialisierung
    # ------------------------------------------------------------
    def _init_subcontrollers(self) -> None:
        """Erzeugt alle Subcontroller und gibt main_ctrl mit."""
        self.file_ctrl = FileController(self.composer, self.view, main_ctrl=self)
        self.layer_ctrl = LayerController(self.composer, self.view, main_ctrl=self)
        self.settings_ctrl = SettingsController(self.composer, self.view, self.config, main_ctrl=self)
        self.appearance_ctrl = AppearanceController(self.composer, self.view, self.config, self.view, main_ctrl=self)
        self.export_ctrl = ExportController(self.composer, self.view, self.config, self.view, main_ctrl=self)
        self.epsg_ctrl = EpsgController(self.composer, self.view, self.config, self.view, main_ctrl=self)

    # ------------------------------------------------------------
    # Signal-Verbindungen
    # ------------------------------------------------------------
    def _connect_file_signals(self) -> None:
        dp = self.view.drop_panel
        if hasattr(dp, "drop_main"):
            dp.drop_main.dropChanged.connect(self._on_files_changed)
        if hasattr(dp, "drop_sub"):
            dp.drop_sub.dropChanged.connect(self._on_files_changed)

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

    def _connect_control_buttons(self) -> None:
        if hasattr(self.view, "btn_preview_update"):
            self.view.btn_preview_update.clicked.connect(self.refresh_preview_clicked)
        if hasattr(self.view, "btn_reset"):
            self.view.btn_reset.clicked.connect(self.reset_app)

    def _connect_all_signals(self) -> None:
        self._connect_file_signals()
        self._connect_layer_signals()
        self._connect_settings_signals()
        self._connect_appearance_signals()
        self._connect_export_signals()
        self._connect_epsg_signals()
        self._connect_control_buttons()

    # ------------------------------------------------------------
    # Laufsteuerung
    # ------------------------------------------------------------
    def run(self) -> int:
        self._connect_all_signals()
        self.view.show()
        self.preview_dirty = True
        return self.app.exec()

    # ------------------------------------------------------------
    # Vorschau-Steuerung
    # ------------------------------------------------------------
    @Slot()
    def mark_preview_dirty(self, *args, **kwargs) -> None:
        self.preview_dirty = True
        if hasattr(self.view, "set_preview_dirty_indicator"):
            try:
                self.view.set_preview_dirty_indicator(True)
            except Exception:
                pass

    @Slot()
    def refresh_preview_clicked(self) -> None:
        if not self.preview_dirty:
            logging.debug("Preview ist aktuell – kein Refresh nötig.")
            return
        try:
            self.view.map_canvas.refresh(preview=True)
            self.preview_dirty = False
            if hasattr(self.view, "set_preview_dirty_indicator"):
                try:
                    self.view.set_preview_dirty_indicator(False)
                except Exception:
                    pass
            logging.debug("Preview aktualisiert.")
        except Exception as e:
            logging.error("Fehler beim Aktualisieren der Vorschau: %s", e)

    # ------------------------------------------------------------
    # Dateien geändert
    # ------------------------------------------------------------
    @Slot()
    def _on_files_changed(self) -> None:
        """
        Wird getriggert, wenn im Drop-Panel Dateien geändert werden.
        Lädt neue Daten und markiert Preview als dirty.
        """
        try:
            self.file_ctrl.handle_files_changed()
            self.mark_preview_dirty()
            logging.debug("Dateien geändert – Preview als dirty markiert.")
        except Exception as e:
            logging.error("Fehler beim Verarbeiten von Dateiänderungen: %s", e)
            self.preview_dirty = True
                    
    # ------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------
    @Slot()
    def reset_app(self) -> None:
        ok = self.reset_service.reset()
        # Preview-Status zurücksetzen
        self.preview_dirty = not ok
        if ok and hasattr(self.view, "set_preview_dirty_indicator"):
            try:
                self.view.set_preview_dirty_indicator(False)
            except Exception:
                pass