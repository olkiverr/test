import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QApplication, QWidget

class EyesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yeux Fixes")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: black;")
        
        # Variables pour les yeux
        self.eye1_x = 80  # Position x du premier œil
        self.eye1_y = 100  # Position y du premier œil
        self.eye1_radius = 50  # Rayon du premier œil

        self.eye2_x = 220  # Position x du second œil
        self.eye2_y = 100  # Position y du second œil
        self.eye2_radius = 50  # Rayon du second œil

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Couleur des yeux (cyan)
        eye_color = QColor(0, 255, 255)

        # Dessiner les yeux (cercles cyan)
        painter.setBrush(eye_color)
        painter.drawEllipse(self.eye1_x, self.eye1_y, self.eye1_radius * 2, self.eye1_radius * 2)  # Premier œil
        painter.drawEllipse(self.eye2_x, self.eye2_y, self.eye2_radius * 2, self.eye2_radius * 2)  # Deuxième œil

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EyesWidget()
    window.show()
    sys.exit(app.exec_())
