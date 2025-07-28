# utils/autocomplete.py

from typing import List
from PySide6.QtWidgets import QLineEdit, QCompleter
from PySide6.QtCore import Qt, QStringListModel, QSortFilterProxyModel

def setup_autocomplete(line_edit: QLineEdit, options: List[str]) -> QCompleter:
    """
    Baut für das gegebene QLineEdit einen QCompleter auf, der bei jedem
    Tastendruck filtert und das Popup sofort anzeigt.
    """
    sorted_list  = sorted(options, key=str.lower)
    source_model = QStringListModel(sorted_list, parent=line_edit)

    proxy_model = QSortFilterProxyModel(parent=line_edit)
    proxy_model.setSourceModel(source_model)
    proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
    proxy_model.setFilterRole(Qt.DisplayRole)
    proxy_model.setFilterKeyColumn(0)

    completer = QCompleter(proxy_model, line_edit)
    completer.setCaseSensitivity(Qt.CaseInsensitive)
    completer.setCompletionMode(QCompleter.PopupCompletion)

    line_edit.setCompleter(completer)

    def on_text_edited(text: str):
        proxy_model.setFilterFixedString(text)
        completer.complete()

    line_edit.textEdited.connect(on_text_edited)

    return completer
