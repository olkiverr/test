import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QApplication, QWidget
import math

class EyesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yeux qui clignent (fluide et naturel)")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: black;")
        
        # Variables pour les yeux
        self.eye1_x = 80  # Position x du premier œil
        self.eye1_y = 100  # Position y du premier œil
        self.eye1_radius = 50  # Rayon du premier œil

        self.eye2_x = 220  # Position x du second œil
        self.eye2_y = 100  # Position y du second œil
        self.eye2_radius = 50  # Rayon du second œil

        # Variables pour le clignement
        self.is_blinking = False
        self.blink_step = 0  # Étape actuelle de l'animation
        self.total_blink_steps = 8  # Nombre total d'étapes pour un clignement complet
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.animate_blink)

        # Timer pour déclencher le clignement périodiquement
        self.blink_interval_timer = QTimer(self)
        self.blink_interval_timer.timeout.connect(self.start_blinking)
        self.blink_interval_timer.start(6000)  # Clignement toutes les 3 secondes

    def start_blinking(self):
        """Démarre l'animation de clignement."""
        if not self.is_blinking:
            self.is_blinking = True
            self.blink_step = 0
            self.blink_timer.start(int(18.75))  # Intervalle entre chaque étape (arrondi à un entier)

    def animate_blink(self):
        """Anime le clignement des yeux avec une interpolation non linéaire."""
        self.blink_step += 1  # Progression de l'animation
        if self.blink_step > self.total_blink_steps:  # Si l'animation est terminée
            self.blink_timer.stop()
            self.is_blinking = False
            self.blink_step = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Couleur des yeux (cyan)
        eye_color = QColor(0, 255, 255)

        # Calcul du facteur de clignement (0 = ouvert, 1 = fermé)
        if self.is_blinking:
            progress = self.blink_step / self.total_blink_steps  # Normalisation de 0 à 1
            blink_factor = math.sin(progress * math.pi)  # Courbe sinus pour non-linéarité
        else:
            blink_factor = 0

        # Hauteur ajustée des yeux pendant le clignement
        height_reduction = blink_factor * self.eye1_radius * 2  # Réduction en fonction du clignement

        # Dessiner le premier œil
        painter.setBrush(eye_color)
        painter.drawEllipse(
            int(self.eye1_x),
            int(self.eye1_y + height_reduction / 2),  # Ajuste la position verticale
            int(self.eye1_radius * 2),
            int(max(0, self.eye1_radius * 2 - height_reduction))  # Ajuste la hauteur
        )

        # Dessiner le second œil
        painter.drawEllipse(
            int(self.eye2_x),
            int(self.eye2_y + height_reduction / 2),  # Ajuste la position verticale
            int(self.eye2_radius * 2),
            int(max(0, self.eye2_radius * 2 - height_reduction))  # Ajuste la hauteur
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EyesWidget()
    window.show()
    sys.exit(app.exec_())
