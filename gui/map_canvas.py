# gui/map_canvas.py

import logging
from typing import Optional, Any
from PySide6.QtWidgets import QLabel, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PIL.ImageQt import ImageQt


class MapCanvas(QLabel):
    """
    QLabel, das das von MapComposer gerenderte PIL-Image als QPixmap anzeigt.
    Unterstützt transparente oder farbige Hintergründe und zeigt einen
    Platzhaltertext, solange keine Karte geladen ist.
    """

    def __init__(
        self,
        composer: Any,
        width: Optional[int] = None,
        height: Optional[int] = None,
        parent: Optional[Any] = None
    ) -> None:
        super().__init__(parent)
        self.composer = composer

        # Wenn Breite und Höhe übergeben, feste Größe setzen
        if width is not None and height is not None:
            self.setFixedSize(width, height)

        # Platzhalter-Text, solange keine Datei geladen ist
        self._placeholder = "Keine Karte geladen"

        # Standard-Hintergrund aus Composer-Config übernehmen
        bg_cfg = getattr(self.composer, "background_cfg", {})
        self._bg_color = bg_cfg.get("color", "#ffffff")
        self._bg_transparent = bg_cfg.get("transparent", False)

        self._init_ui()
        self._apply_background()
        self._show_placeholder()

    def _init_ui(self) -> None:
        """Initialisiert Ausrichtung, Text und Größen-Policy."""
        self.setText(self._placeholder)
        self.setAlignment(Qt.AlignCenter)
        # Bei festen Größen kann Expanding entfernt werden, hier bleibt es optional
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _apply_background(self) -> None:
        """
        Setzt das QLabel-Stylesheet entsprechend der
        Transparenz- und Farb-Einstellung.
        """
        if self._bg_transparent:
            self.setStyleSheet("background: transparent;")
        else:
            self.setStyleSheet(f"background-color: {self._bg_color};")

    def set_background(
        self,
        *,
        color: Optional[str] = None,
        transparent: Optional[bool] = None
    ) -> None:
        """
        Wird vom Controller aufgerufen:
        - transparent=True  -> QLabel ist durchsichtig
        - transparent=False -> QLabel zeigt die angegebene Farbe
        """
        if color is not None:
            self._bg_color = color
        if transparent is not None:
            self._bg_transparent = transparent

        self._apply_background()
        self.refresh()

    def refresh(self, preview: bool = True) -> None:
        """
        Lädt mit composer.render() die aktuelle Karte neu und zeigt
        sie als QPixmap an.

        Parameter:
        - preview=True: schnelle Vorschau (halbierte Pixelmaße, vereinfachte Geometrien)
        - preview=False: volle Qualität (z. B. für Exportanzeige)

        Bei Fehlern oder falls noch kein main_gpkg gesetzt ist,
        wird der Platzhaltertext angezeigt.
        """
        if not getattr(self.composer, "main_gpkg", None):
            self._show_placeholder()
            return

        try:
            pil_img = self.composer.render(preview_mode=preview)
        except Exception as e:
            logging.error("Fehler beim Rendern der Karte: %s", e)
            self._show_placeholder()
            return

        if pil_img is None:
            self._show_placeholder()
            return

        self._show_image(pil_img)

    def _show_placeholder(self) -> None:
        """Zeigt den Platzhalter-Text an."""
        self.clear()
        self.setText(self._placeholder)

    def _show_image(self, img) -> None:
        """
        Konvertiert ein PIL.Image in ein QPixmap und zeigt es.
        """
        qt_img = ImageQt(img)
        pixmap = QPixmap.fromImage(qt_img)
        self.clear()
        self.setPixmap(pixmap)
        self.setAlignment(Qt.AlignCenter)