# gui/log_viewer.py

import logging
from PySide6.QtCore    import QObject, Signal
from PySide6.QtWidgets import QPlainTextEdit

class QTextEditLogger(logging.Handler, QObject):
    """
    Logging-Handler, der Einträge in ein QPlainTextEdit schreibt.
    """
    newRecord = Signal(str)

    def __init__(self, widget: QPlainTextEdit):
        logging.Handler.__init__(self)
        QObject.__init__(self)
        self.widget = widget
        fmt = "%(asctime)s - %(levelname)s - %(message)s"
        self.setFormatter(logging.Formatter(fmt))
        self.newRecord.connect(self.widget.appendPlainText)

    def emit(self, record: logging.LogRecord):
        msg = self.format(record)
        self.newRecord.emit(msg)