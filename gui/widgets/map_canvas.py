from PySide6.QtWidgets import QLabel
from PySide6.QtGui     import QPixmap
from PIL.ImageQt       import ImageQt
from PySide6.QtCore import Qt

class MapCanvas(QLabel):
    def __init__(self, composer, parent=None):
        super().__init__(parent)
        self.composer = composer
        self.setAlignment(Qt.AlignCenter)

    def refresh(self):
        img     = self.composer.render()
        qt_img  = ImageQt(img)
        pixmap  = QPixmap.fromImage(qt_img)
        self.setPixmap(pixmap)
        self.setFixedSize(pixmap.size())