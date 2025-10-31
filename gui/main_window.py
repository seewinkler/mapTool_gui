# gui/main_window.py
import logging
from typing import Any, Dict

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QPlainTextEdit, QTabWidget, QLabel, QGroupBox, QFormLayout, QGridLayout,
    QDoubleSpinBox, QCheckBox, QColorDialog, QListWidgetItem
)
from PySide6.QtCore import Qt

from gui.drop_widgets import DropPanel
from gui.map_canvas import MapCanvas
from gui.log_viewer import QTextEditLogger
from gui.controls.map_settings import MapSettingsGroup
from gui.controls.scalebar_settings import ScalebarSettingsGroup
from gui.controls.background_settings import BackgroundSettingsGroup
from gui.controls.layer_selection import LayerSelectionGroup, LayerFilterGroup
from gui.controls.export_settings import ExportSettingsGroup
from gui.controls.boundary_settings import BoundarySettingsGroup


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

        # Temporärer Speicher für ausgewählte Overlay-Farben (erst bei Vorschau übernehmen)
        self._overlay_colors: Dict[str, str] = {}

        self._apply_initial_composer_settings()
        self.layers = []
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
        self.setMinimumSize(1100, 720)

        central = QWidget(self)
        self.setCentralWidget(central)

        # Haupt-Container: zwei Spalten
        root = QHBoxLayout(central)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # ========== LINKE SPALTE ==========
        left_col = QVBoxLayout()
        left_col.setSpacing(8)
        root.addLayout(left_col, stretch=1)
        self._left_col_layout = left_col  # für Logging-Widget

        # Datei-Upload (Hauptland, Nebenländer, Overlay)
        self.drop_panel = DropPanel(copy_to_temp=True)
        left_col.addWidget(self.drop_panel, stretch=1)

        # Karten-Vorschau
        karte_cfg = self.config.get("karte", {})
        w = karte_cfg.get("breite", 800)
        h = karte_cfg.get("hoehe", 600)
        self.map_canvas = MapCanvas(self.composer, width=w, height=h)
        left_col.addWidget(self.map_canvas, stretch=2)

        # ========== RECHTE SPALTE ==========
        right_col = QVBoxLayout()
        right_col.setSpacing(8)
        root.addLayout(right_col, stretch=1)

        # Tabs
        tabs = QTabWidget()
        right_col.addWidget(tabs, stretch=1)

        # -- Tab 1: Hauptfunktionen --
        tab_main = QWidget()
        tabs.addTab(tab_main, "Hauptfunktionen")
        main_tab_layout = QVBoxLayout(tab_main)
        main_tab_layout.setSpacing(8)

        # EPSG, Breite, Höhe
        self.map_settings = MapSettingsGroup(
            composer=self.composer,
            on_epsg=lambda: None,
            on_dimensions_changed=lambda _: None
        )
        self.btn_epsg = self.map_settings.btn_epsg
        self.sp_w = self.map_settings.sp_w
        self.sp_h = self.map_settings.sp_h
        main_tab_layout.addWidget(self.map_settings)

        # Ausgewählte Layer
        self.layer_selection = LayerSelectionGroup(
            on_layers_changed=self._on_layers_changed
        )
        self.lst_layers = self.layer_selection.lst_layers
        main_tab_layout.addWidget(self.layer_selection)

        # Beispiel: Layerliste initial füllen (falls keine dynamische Quelle vorhanden)
        for layer in []:
            item = QListWidgetItem(layer)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.lst_layers.addItem(item)

        # Scalebar
        self.scalebar_settings = ScalebarSettingsGroup(
            composer=self.composer,
            on_changed=lambda _: None
        )
        self.cb_sb_show = self.scalebar_settings.cb_sb_show
        self.cmb_sb_pos = self.scalebar_settings.cmb_sb_pos
        main_tab_layout.addWidget(self.scalebar_settings)

        # Hintergrund
        self.bg_settings = BackgroundSettingsGroup(
            composer=self.composer,
            on_choose_color=lambda: None,
            on_toggled=lambda _: None
        )
        self.btn_col = self.bg_settings.btn_col
        self.cb_transp = self.bg_settings.cb_transp
        main_tab_layout.addWidget(self.bg_settings)

        main_tab_layout.addStretch(1)

        # -- Tab 2: Zusatzfunktionen --
        tab_extra = QWidget()
        tabs.addTab(tab_extra, "Zusatzfunktionen")
        extra_tab_layout = QVBoxLayout(tab_extra)
        extra_tab_layout.setSpacing(8)

        # Ausblenden/Hervorheben
        self.layer_filter = LayerFilterGroup(
            on_hide_changed=lambda _: None,
            on_highlight_changed=lambda _: None
        )
        self.lst_hide = self.layer_filter.lst_hide
        self.lst_high = self.layer_filter.lst_high
        extra_tab_layout.addWidget(self.layer_filter)

        # Grenzen
        self.boundary_settings = BoundarySettingsGroup(self.config, levels=[])
        extra_tab_layout.addWidget(self.boundary_settings)

        # Overlay-Optionen – erweitert
        self.group_overlay = QGroupBox("Overlay")
        ov_layout = QFormLayout(self.group_overlay)

        # Füllfarbe
        self.btn_overlay_fill = QPushButton("Füllfarbe wählen")
        self.btn_overlay_fill.clicked.connect(lambda: self._choose_overlay_color("fill_color"))

        # Linienfarbe
        self.btn_overlay_line = QPushButton("Linienfarbe wählen")
        self.btn_overlay_line.clicked.connect(lambda: self._choose_overlay_color("line_color"))

        # Linienbreite (0 = keine Linie)
        self.sp_overlay_line_width = QDoubleSpinBox()
        self.sp_overlay_line_width.setRange(0, 10)
        self.sp_overlay_line_width.setSingleStep(0.5)
        self.sp_overlay_line_width.setValue(self.config.get("overlay_style", {}).get("line_width", 1.0))

        # Linien anzeigen
        self.cb_overlay_show_lines = QCheckBox("Linien anzeigen")
        self.cb_overlay_show_lines.setChecked(self.config.get("overlay_style", {}).get("show_lines", True))

        ov_layout.addRow("Füllfarbe:", self.btn_overlay_fill)
        ov_layout.addRow("Linienfarbe:", self.btn_overlay_line)
        ov_layout.addRow("Linienbreite (px):", self.sp_overlay_line_width)
        ov_layout.addRow(self.cb_overlay_show_lines)

        extra_tab_layout.addWidget(self.group_overlay)
        self.group_overlay.setVisible(False)

        # Verbindung: DropZone-Änderung → Sichtbarkeit aktualisieren + Overlay laden
        self.drop_panel.drop_overlay.dropChanged.connect(self._on_overlay_dropped)

        # Positionierung
        group_pan = QGroupBox("Positionierung")
        grid = QGridLayout(group_pan)
        grid.addWidget(QPushButton("↑"), 0, 1)
        grid.addWidget(QPushButton("←"), 1, 0)
        grid.addWidget(QPushButton("→"), 1, 2)
        grid.addWidget(QPushButton("↓"), 2, 1)
        grid.addWidget(QLabel("X-Offset:"), 3, 0)
        grid.addWidget(QLabel("Y-Offset:"), 4, 0)
        grid.addWidget(QPushButton("Position zurücksetzen"), 5, 0, 1, 3)
        extra_tab_layout.addWidget(group_pan)

        extra_tab_layout.addStretch(1)

        # Unterer Bereich rechts
        bottom_panel = QVBoxLayout()
        bottom_panel.setSpacing(6)
        right_col.addLayout(bottom_panel, stretch=0)

        self.export_settings = ExportSettingsGroup()
        self.cb_png = self.export_settings.cb_png
        self.cb_svg = self.export_settings.cb_svg
        bottom_panel.addWidget(self.export_settings)

        btn_row = QHBoxLayout()
        self.btn_preview_update = QPushButton("Vorschau aktualisieren", self)
        self.btn_reset = QPushButton("Zurücksetzen", self)
        btn_row.addWidget(self.btn_preview_update)
        btn_row.addWidget(self.btn_reset)
        bottom_panel.addLayout(btn_row)

        # Neue Verbindung: Overlay-Style erst bei Klick übernehmen
        self.btn_preview_update.clicked.connect(self._on_preview_update_clicked)
        self.btn_reset.clicked.connect(self._on_reset_clicked)

        self.btn_render = QPushButton("Karte rendern", self)
        bottom_panel.addWidget(self.btn_render)

        # Startzustand Overlay-Optionen setzen
        self._update_overlay_visibility()

    # ------------------------------------------------------------
    # Overlay-Helfer
    # ------------------------------------------------------------
    def _choose_overlay_color(self, target: str) -> None:
        """Öffnet einen Farbwähler und speichert die Auswahl temporär."""
        col = QColorDialog.getColor()
        if col.isValid():
            self._overlay_colors[target] = col.name()

    # ------------------------------------------------------------
    # Overlay-Optionen sichtbar/unsichtbar schalten
    # ------------------------------------------------------------
    def _update_overlay_visibility(self):
        has_overlay = bool(self.drop_panel.get_overlay_paths())
        self.group_overlay.setVisible(has_overlay)

    # ------------------------------------------------------------
    # Overlay-Drop-Handler
    # ------------------------------------------------------------
    def _on_overlay_dropped(self):
        """Wird aufgerufen, wenn in die Overlay-Drop-Zone eine Datei gelegt oder entfernt wird."""
        paths = self.drop_panel.get_overlay_paths()

        if paths:
            # Overlay setzen
            self.composer.set_overlay(paths[0])
            logging.info(f"Overlay geladen: {paths[0]}")
        else:
            logging.info("Kein Overlay geladen.")
            # Extra-Schutz: nur aufrufen, wenn der Composer damit umgehen kann
            if hasattr(self.composer, "clear_overlay"):
                try:
                    self.composer.clear_overlay()
                    logging.info("Overlay im Composer entfernt.")
                except Exception as e:
                    logging.warning(f"Overlay konnte nicht entfernt werden: {e}")
            else:
                logging.debug("Composer hat keine clear_overlay()-Methode – kein Entfernen nötig.")

        self._update_overlay_visibility()
        self.map_canvas.refresh(preview=True)

    # ------------------------------------------------------------
    # Vorschau aktualisieren
    # ------------------------------------------------------------
    def _on_preview_update_clicked(self) -> None:
        """
        Übernimmt aktuelle Overlay- und Boundary-Optionen in die Config
        und rendert die Vorschau.
        """
        # -----------------------------
        # Overlay-Style übernehmen
        # -----------------------------
        style_cfg = dict(self.config.get("overlay_style", {}))

        # Aus temporären Farbwahlen übernehmen (wenn gesetzt), sonst bisherige Werte behalten
        if "fill_color" in self._overlay_colors:
            style_cfg["fill_color"] = self._overlay_colors["fill_color"]
        else:
            style_cfg.setdefault("fill_color", "#2896BA")

        if "line_color" in self._overlay_colors:
            style_cfg["line_color"] = self._overlay_colors["line_color"]
        else:
            style_cfg.setdefault("line_color", "#0000ff")

        # Breite und Sichtbarkeit aus Controls
        style_cfg["line_width"] = float(self.sp_overlay_line_width.value())
        style_cfg["show_lines"] = self.cb_overlay_show_lines.isChecked()

        # Zurück in die Config
        self.config["overlay_style"] = style_cfg

        # -----------------------------
        # Boundary-Settings übernehmen
        # -----------------------------
        if hasattr(self, "boundary_settings"):
            # schreibt die Werte aus den Controls in self.config["boundaries"]
            self.boundary_settings.apply_to_config()

        # -----------------------------
        # Vorschau neu rendern
        # -----------------------------
        self.map_canvas.refresh(preview=True)

    # ------------------------------------------------------------
    # Reset-Handler
    # ------------------------------------------------------------
    def _on_reset_clicked(self):
        """Setzt die UI auf den Ausgangszustand zurück."""
        # Drop-Zonen leeren
        self.drop_panel.clear()

        # Overlay-Optionen ausblenden
        self.composer.set_overlay(None)
        self._update_overlay_visibility()

        # Karten-Vorschau zurücksetzen
        karte_cfg = self.config.get("karte", {})
        w = karte_cfg.get("breite", 800)
        h = karte_cfg.get("hoehe", 600)
        self.map_canvas.setFixedSize(w, h)
        self.map_canvas.refresh(preview=True)

        # Hintergrund zurücksetzen
        bg_cfg = self.config.get("background", {})
        self.cb_transp.setChecked(bg_cfg.get("transparent", False))
        self.btn_col.hide()

        # Scalebar zurücksetzen
        sb = self.config.get("scalebar", {})
        self.cb_sb_show.setChecked(sb.get("show", False))
        self.cmb_sb_pos.setCurrentText(sb.get("position", "bottom-right"))

        # Dimensionen zurücksetzen
        self.sp_w.setValue(w)
        self.sp_h.setValue(h)

        # Layer-Listen leeren
        self.lst_layers.clear()
        self.lst_hide.clear()
        self.lst_high.clear()

        # Export-Formate zurücksetzen
        self.cb_png.setChecked(False)
        self.cb_svg.setChecked(False)

        # Overlay-UI zurücksetzen (auf Config-Defaults)
        style_cfg = self.config.get("overlay_style", {})
        self._overlay_colors.clear()
        self.sp_overlay_line_width.setValue(style_cfg.get("line_width", 1.0))
        self.cb_overlay_show_lines.setChecked(style_cfg.get("show_lines", True))

        # Log leeren
        if hasattr(self, "log_widget"):
            self.log_widget.clear()

    # ------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------
    def _setup_logging(self) -> None:
        """Richtet Logging-Ausgabe ins Log-Widget ein."""
        self.log_widget = QPlainTextEdit(self)
        self.log_widget.setReadOnly(True)
        handler = QTextEditLogger(self.log_widget)
        logging.getLogger().addHandler(handler)
        lvl = self.config.get("logging", {}).get("level", "INFO").upper()
        logging.getLogger().setLevel(getattr(logging, lvl, logging.INFO))

        # Log-Widget in der linken Spalte unter der Vorschau anzeigen
        if hasattr(self, "_left_col_layout"):
            self._left_col_layout.addWidget(self.log_widget, stretch=0)

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

        # Overlay-UI-Defaults aus Config laden
        style_cfg = self.config.get("overlay_style", {})
        self.sp_overlay_line_width.setValue(style_cfg.get("line_width", 1.0))
        self.cb_overlay_show_lines.setChecked(style_cfg.get("show_lines", True))
        # Farben bleiben bis zur Auswahl im Dialog in _overlay_colors leer

        # Canvas initial dimensionieren und Preview rendern
        self.map_canvas.setFixedSize(w, h)
        self.map_canvas.refresh(preview=True)

    # ------------------------------------------------------------
    # Layer-Auswahl → Grenzen-Controls
    # ------------------------------------------------------------
    def _on_layers_changed(self, _=None):
        """Wird aufgerufen, wenn sich die Layer-Auswahl im GUI ändert."""
        from utils.constants import LAYER_TO_BOUNDARY

        # 1) Ausgewählte Layer (nur Qt.Checked) einsammeln
        selected = []
        for i in range(self.lst_layers.count()):
            item = self.lst_layers.item(i)
            if item.checkState() == Qt.Checked:
                selected.append(item.text())

        print("[DEBUG] Ausgewählte Layer (roh):", selected)

        # 2) Namen normalisieren und mappen
        levels = []
        for name in selected:
            key = name.lower().strip()
            if key in LAYER_TO_BOUNDARY:
                levels.append(LAYER_TO_BOUNDARY[key])
            else:
                print(f"[DEBUG] Kein Mapping für Layer '{name}' (normalisiert: '{key}') – wird ignoriert.")

        print("[DEBUG] Abgeleitete Levels:", levels)

        # 3) Auswahl speichern und GUI aktualisieren
        self.layers = selected
        self.boundary_settings.update_levels(levels)
