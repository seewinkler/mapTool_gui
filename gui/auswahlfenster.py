# gui/auswahlfenster.py

from typing        import Dict, Any, List
from PySide6.QtCore    import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QHBoxLayout
)
from utils.autocomplete import setup_autocomplete
import logging

logger = logging.getLogger("gui.auswahlfenster")
print("▶ gui/auswahlfenster.py wird geladen")


class AuswahlFenster(QDialog):
    """
    Dialog zum Auswählen eines Landes/Alias und Übernehmen der
    zugehörigen EPSG-Projektion. Schließt sich nach OK oder sofort,
    wenn per Autocomplete ein gültiger Eintrag gewählt wurde.
    """

    def __init__(self, epsg_list: List[Dict[str, Any]], parent=None):
        super().__init__(parent)
        self.epsg_list       = epsg_list
        self.epsg_lookup     : Dict[str, Dict[str, Any]] = {}
        self.selected_entry  : Dict[str, Any]            = {}
        self._build_ui()
        logger.debug("EPSG-Liste geladen mit %d Einträgen", len(epsg_list))

    def _build_ui(self):
        self.setWindowTitle("Länderauswahl mit EPSG")
        layout = QVBoxLayout(self)

        # Label + Eingabe + Ausgabe
        layout.addWidget(QLabel("Wähle ein Land oder Alias"))
        self.input = QLineEdit()
        layout.addWidget(self.input)

        self.output = QLabel("")
        self.output.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.output)

        # Lookup-Map + Suchbegriffe sammeln
        suchbegriffe: List[str] = []
        for eintrag in self.epsg_list:
            name = eintrag["land"]
            self.epsg_lookup[name.lower()] = eintrag
            suchbegriffe.append(name)
            for alias in eintrag.get("aliases", []):
                self.epsg_lookup[alias.lower()] = eintrag
                suchbegriffe.append(alias)

        # Autocomplete einrichten
        completer = setup_autocomplete(self.input, suchbegriffe)
        completer.activated[str].connect(self._on_text_selected_and_close)

        # Freitext/Enter validieren
        self.input.textChanged.connect(self._on_text_changed)
        self.input.returnPressed.connect(
            lambda: self._on_text_changed(self.input.text())
        )

        # OK/Abbrechen Buttons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self._on_ok)
        btn_cancel = QPushButton("Abbrechen")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def _on_text_selected(self, text: str):
        logger.debug("Vorschlag ausgewählt: %s", text)
        self.input.setText(text)
        self._on_text_changed(text)

    def _on_text_selected_and_close(self, text: str):
        logger.debug("Vorschlag ausgewählt (mit sofortigem Schließen): %s", text)
        self.input.setText(text)
        self._on_text_changed(text)
        if self.selected_entry:
            self.accept()

    def _on_text_changed(self, text: str):
        logger.debug("Text geändert: %s", text)
        eintrag = self.epsg_lookup.get(text.lower())
        if eintrag:
            self.selected_entry = {
                "land": eintrag["land"],
                "epsg": f"EPSG:{eintrag['epsg']}",
                "projektion": eintrag.get("projektion", ""),
                "hinweis": eintrag.get("hinweis", "")
            }
            self.output.setText(
                f"EPSG: {self.selected_entry['epsg']}\n"
                f"Projektion: {self.selected_entry['projektion']}"
            )
        else:
            self.selected_entry = {}
            self.output.setText("")

    def _on_ok(self):
        text = self.input.text().strip().lower()
        logger.debug("OK gedrückt – aktueller Text: '%s'", text)

        eintrag = self.epsg_lookup.get(text)
        if not eintrag:
            logger.warning("Kein gültiger Eintrag für '%s'", text)
            self.output.setText("Bitte ein gültiges Land auswählen.")
            self.selected_entry = {}
            return

        self.selected_entry = {
            "land": eintrag["land"],
            "epsg": f"EPSG:{eintrag['epsg']}",
            "projektion": eintrag.get("projektion", ""),
            "hinweis": eintrag.get("hinweis", "")
        }

        logger.debug("Gültiger Eintrag bestätigt: %s", self.selected_entry)
        self.accept()
