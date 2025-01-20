import sys
import threading
import math
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QObject
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QApplication, QWidget
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw


class EyesWidget(QWidget):
    trigger_happy = pyqtSignal()  # Signal pour déclencher l'état "heureux"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yeux qui clignent (fluide et naturel)")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: black;")
        
        # Place la fenêtre toujours au-dessus des autres
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # Variables pour les yeux
        self.eye1_x = 80
        self.eye1_y = 100
        self.eye1_radius = 50

        self.eye2_x = 220
        self.eye2_y = 100
        self.eye2_radius = 50

        # Variables pour le clignement
        self.is_blinking = False
        self.blink_step = 0
        self.total_blink_steps = 8
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.animate_blink)

        self.blink_interval_timer = QTimer(self)
        self.blink_interval_timer.timeout.connect(self.start_blinking)
        self.blink_interval_timer.start(6000)

        # Variables pour l'animation "heureuse"
        self.is_happy = False  # Indicateur pour savoir si les yeux sont "heureux"

        # Connecte le signal "trigger_happy" à la méthode "happy"
        self.trigger_happy.connect(self.happy)

    def start_blinking(self):
        if not self.is_blinking:
            self.is_blinking = True
            self.blink_step = 0
            self.blink_timer.start(int(18.75))

    def animate_blink(self):
        self.blink_step += 1
        if self.blink_step > self.total_blink_steps:
            self.blink_timer.stop()
            self.is_blinking = False
            self.blink_step = 0
        self.update()

    def happy(self):
        """Déclenche l'état 'heureux' sans animation."""
        self.is_happy = not self.is_happy  # Toggle entre True et False
        self.repaint()  # Force un redessin de la fenêtre immédiatement


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        eye_color = QColor(0, 255, 255)  # Cyan

        if self.is_happy:  # Si l'état est "heureux"
            # Dessiner des demi-cercles remplis pour les yeux
            painter.setBrush(eye_color)  # Cyan pour les demi-cercles
            painter.setPen(Qt.NoPen)  # Pas de contour

            # Dessiner le demi-cercle pour le premier œil
            painter.drawPie(
                self.eye1_x,  # Centrer l'arc sur l'œil
                self.eye1_y,  # Positionner l'arc en haut de l'œil
                self.eye1_radius * 2,  # Largeur de l'arc
                self.eye1_radius * 2,  # Hauteur de l'arc
                0 * 16,  # Début de l'arc (0°)
                180 * 16  # Demi-cercle vers le haut (180°)
            )

            # Dessiner le demi-cercle pour le second œil
            painter.drawPie(
                self.eye2_x,  # Centrer l'arc sur le second œil
                self.eye2_y,  # Positionner l'arc en haut de l'œil
                self.eye2_radius * 2,  # Largeur de l'arc
                self.eye2_radius * 2,  # Hauteur de l'arc
                0 * 16,  # Début de l'arc (0°)
                180 * 16  # Demi-cercle vers le haut (180°)
            )

        else:  # Si l'état n'est pas "heureux", dessiner les yeux pleins
            # Clignement
            if self.is_blinking:
                progress = self.blink_step / self.total_blink_steps
                blink_factor = math.sin(progress * math.pi)
            else:
                blink_factor = 0

            height_reduction = blink_factor * self.eye1_radius * 2

            # Dessiner les yeux pleins
            painter.setBrush(eye_color)

            painter.drawEllipse(
                int(self.eye1_x),
                int(self.eye1_y + height_reduction / 2),
                int(self.eye1_radius * 2),
                int(max(0, self.eye1_radius * 2 - height_reduction))
            )

            painter.drawEllipse(
                int(self.eye2_x),
                int(self.eye2_y + height_reduction / 2),
                int(self.eye2_radius * 2),
                int(max(0, self.eye2_radius * 2 - height_reduction))
            )



def create_image():
    """Créer une icône pour le plateau système."""
    image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((8, 8, 56, 56), fill=(0, 255, 255))
    return image


def show_message(window):
    """Action déclenchée par le bouton 'Happy'."""
    print("Happy button clicked!")
    window.trigger_happy.emit()  # Émet un signal pour déclencher l'état "heureux"


def start_tray(app, window):
    """Lance le menu du plateau système."""
    menu = Menu(
        MenuItem("Happy", lambda: show_message(window)),
        MenuItem("Quitter", lambda: quit_app(app))
    )
    icon = Icon("Eyes App", create_image(), menu=menu)
    icon.run()


def quit_app(app):
    """Quitte l'application."""
    app.quit()
    sys.exit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EyesWidget()
    window.show()

    # Lancer Pystray dans un thread séparé
    tray_thread = threading.Thread(target=start_tray, args=(app, window), daemon=True)
    tray_thread.start()

    sys.exit(app.exec_())
