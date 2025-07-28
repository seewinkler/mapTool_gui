from typing       import Any
import sys, logging
from fiona           import listlayers
from PySide6.QtCore    import Qt, Slot
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QColorDialog,
    QListWidgetItem,
    QDialog,
)

from data_processing.layers       import merge_hauptland_layers
from gui.auswahlfenster           import AuswahlFenster
from utils.config                 import save_config, CONFIG
from .file_controller             import FileController
from .layer_controller            import LayerController
from .settings_controller         import SettingsController
from .appearance_controller       import AppearanceController
from .export_controller           import ExportController
from .epsg_controller             import EpsgController


class MainController:
    def __init__(self, composer: Any, view: Any) -> None:
        self.app        = QApplication.instance() or QApplication(sys.argv)
        self.composer   = composer
        self.view       = view
        self.config     = view.config

        # Subcontroller instanziieren
        self.file_ctrl       = FileController(self.composer, self.view)
        self.layer_ctrl      = LayerController(self.composer, self.view)
        self.settings_ctrl   = SettingsController(self.composer, self.view, self.config)
        self.appearance_ctrl = AppearanceController(self.composer, self.view, self.config, self.view)
        self.export_ctrl     = ExportController(self.composer, self.view, self.config, self.view)
        self.epsg_ctrl       = EpsgController(self.composer, self.view, self.config, self.view)

    def _connect_signals(self) -> None:
        dp = self.view.drop_panel
        dp.drop_main.dropChanged.connect(self.file_ctrl.handle_files_changed)
        dp.drop_sub .dropChanged.connect(self.file_ctrl.handle_files_changed)

        self.view.lst_layers.itemChanged .connect(self.layer_ctrl.handle_primary_selection)
        self.view.lst_hide.itemChanged   .connect(self.layer_ctrl.handle_hide_changed)
        self.view.lst_high.itemChanged   .connect(self.layer_ctrl.handle_highlight_changed)

        self.view.sp_w.valueChanged      .connect(self.settings_ctrl.handle_dimensions_changed)
        self.view.sp_h.valueChanged      .connect(self.settings_ctrl.handle_dimensions_changed)

        self.view.cb_sb_show.stateChanged          .connect(self.settings_ctrl.handle_scalebar_changed)
        self.view.cmb_sb_pos.currentTextChanged    .connect(self.settings_ctrl.handle_scalebar_changed)

        self.view.btn_col.clicked             .connect(self.appearance_ctrl.choose_bg_color)
        self.view.cb_transp.stateChanged      .connect(self.appearance_ctrl.background_changed)

        self.view.btn_render.clicked          .connect(self.export_ctrl.render_clicked)
        self.view.btn_epsg.clicked            .connect(self.epsg_ctrl.select_epsg)

    def run(self) -> int:
        # nach dem Instanziieren aller Subcontroller die Signale verbinden
        self._connect_signals()
        self.view.show()
        return self.app.exec()