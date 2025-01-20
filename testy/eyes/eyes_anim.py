import sys
import threading
import math
import random
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QRect, QPointF, QPoint
from PyQt5.QtGui import QPainter, QColor, QTransform
from PyQt5.QtWidgets import QApplication, QWidget
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import win32api, win32con

class EyesWidget(QWidget):
    trigger_happy = pyqtSignal()
    trigger_wink = pyqtSignal()
    trigger_sad = pyqtSignal()
    trigger_looking = pyqtSignal()
    trigger_move = pyqtSignal() # New signal

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clignement synchronisé")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: black;")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        

        # Variables pour les yeux   
        self.eye1_x = 80  # Oeil gauche
        self.eye1_y = 100
        self.eye1_radius = 50

        self.eye2_x = 220  # Oeil droit
        self.eye2_y = 100
        self.eye2_radius = 50

        # Variables pour le clignement (les deux yeux)
        self.is_blinking = False
        self.blink_step = 0
        self.total_blink_steps = 8
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.animate_blink)

        self.blink_interval_timer = QTimer(self)
        self.blink_interval_timer.timeout.connect(self.start_blinking)
        self.blink_interval_timer.start(6000)

        # Variables pour le clin d'oeil (oeil droit)
        self.is_winking = False
        self.wink_step = 0
        self.total_wink_steps = 8
        self.wink_timer = QTimer(self)
        self.wink_timer.timeout.connect(self.animate_wink)

        # Variables pour l'animation "heureuse"
        self.is_happy = False
        self.trigger_happy.connect(self.happy)
        self.trigger_wink.connect(self.wink)
        
        # Variables pour l'animation "triste"
        self.is_sad = False
        self.trigger_sad.connect(self.sad)

        #Variable pour le mode "regarde"
        self.is_looking = False
        self.trigger_looking.connect(self.looking)
        
        # New variable for "move" mode
        self.is_moving = False
        self.trigger_move.connect(self.move)

        # Timer to track the mouse position
        self.mouse_timer = QTimer(self)
        self.mouse_timer.timeout.connect(self.update_eye_positions)
        self.mouse_timer.start(30)  # Update every 30 milliseconds
        
        self.last_mouse_x, self.last_mouse_y = win32api.GetCursorPos()
        self.default_window_pos = self.frameGeometry().topLeft()

    def start_blinking(self):
        if not self.is_blinking and not self.is_winking:
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
        self.is_happy = not self.is_happy
        self.is_sad = False
        self.repaint()
    
    def sad(self):
        self.is_sad = not self.is_sad
        self.is_happy = False
        self.repaint()

    def wink(self):
        if not self.is_blinking and not self.is_winking:
            self.is_winking = True
            self.wink_step = 0
            self.wink_timer.start(30)
    
    def animate_wink(self):
        self.wink_step += 1
        if self.wink_step > self.total_wink_steps:
            self.wink_timer.stop()
            self.is_winking = False
            self.wink_step = 0
        self.update()

    def looking(self):
        self.is_looking = not self.is_looking
        self.repaint()
    
    def move(self):
        self.is_moving = not self.is_moving
        self.repaint()
    
    def update_eye_positions(self):
        mouse_x, mouse_y = win32api.GetCursorPos() #Get real position of the mouse
        window_pos = self.frameGeometry().topLeft() #Get the window's coordinates
        
        # Transform the mouse coordinates to the window coordinates
        mouse_x -= window_pos.x()
        mouse_y -= window_pos.y()
        
        if self.is_moving:
            
            # Calculate the center of the window
            window_center_x = self.default_window_pos.x() + self.width() / 2
            window_center_y = self.default_window_pos.y() + self.height() / 2

            # Calculate the desired movement vector (from window center to mouse)
            delta_x = mouse_x - (self.width() / 2)
            delta_y = mouse_y - (self.height() / 2)
            
            # Calculate the distance between window center and mouse
            distance = math.sqrt(delta_x**2 + delta_y**2)
           
            if distance > 0:
                normalized_x = delta_x / distance
                normalized_y = delta_y / distance
            else:
                normalized_x, normalized_y = 0,0

            # Calculate the new window position without any radius.
            new_window_x =  window_center_x - self.width()/2 + normalized_x * distance
            new_window_y =  window_center_y - self.height() / 2 + normalized_y * distance
            
            # Move window
            super().move(QPoint(int(new_window_x), int(new_window_y)))
                
        # Calculate the delta (vector) between the mouse and the eye
        delta_x1 = mouse_x - (self.eye1_x + self.eye1_radius)
        delta_y1 = mouse_y - (self.eye1_y + self.eye1_radius)

        delta_x2 = mouse_x - (self.eye2_x + self.eye2_radius)
        delta_y2 = mouse_y - (self.eye2_y + self.eye2_radius)

        # Normalize the vector
        distance1 = math.sqrt(delta_x1**2 + delta_y1**2)
        if distance1 > 0:
            normalized_x1 = delta_x1 / distance1
            normalized_y1 = delta_y1 / distance1
        else:
            normalized_x1, normalized_y1 = 0, 0
        
        distance2 = math.sqrt(delta_x2**2 + delta_y2**2)
        if distance2 > 0:
            normalized_x2 = delta_x2 / distance2
            normalized_y2 = delta_y2 / distance2
        else:
            normalized_x2, normalized_y2 = 0,0

        # Limit the movement of the eyes within a range 
        move_x1 = min(max(normalized_x1 * self.eye1_radius / 2, -self.eye1_radius/2), self.eye1_radius/2)
        move_y1 = min(max(normalized_y1 * self.eye1_radius / 2, -self.eye1_radius/2), self.eye1_radius/2)

        move_x2 = min(max(normalized_x2 * self.eye2_radius/2, -self.eye2_radius/2), self.eye2_radius/2)
        move_y2 = min(max(normalized_y2 * self.eye2_radius/2, -self.eye2_radius/2), self.eye2_radius/2)
        

        # Set the new coordinates
        self.eye1_x =  80 + move_x1 # move eye1 horizontally
        self.eye1_y = 100 + move_y1 # move eye1 vertically

        self.eye2_x = 220 + move_x2 # move eye2 horizontally
        self.eye2_y = 100 + move_y2  # move eye2 vertically
        
        if not self.is_looking:
            self.eye1_x = 80
            self.eye1_y = 100
            self.eye2_x = 220
            self.eye2_y = 100
        self.update()
                
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw a semi-transparent background
        painter.setBrush(QColor(0, 0, 0, 50))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        eye_color = QColor(0, 255, 255)

        # Gestion du clignement (les deux yeux)
        if self.is_blinking:
            progress = self.blink_step / self.total_blink_steps
            blink_factor = math.sin(progress * math.pi)
        else:
            blink_factor = 0

        height_reduction = blink_factor * self.eye1_radius * 2

        # Gestion du clin d'oeil (oeil droit)
        if self.is_winking:
            progress_wink = self.wink_step / self.total_wink_steps
            wink_factor = math.sin(progress_wink * math.pi)
        else:
            wink_factor = 0
        
        wink_height_reduction = wink_factor * self.eye2_radius * 2
        
        if self.is_happy:
            painter.setBrush(eye_color)
            painter.setPen(Qt.NoPen)

            # Dessiner le demi-cercle pour l'oeil gauche (avec clignement)
            rect1 = QRect(
                int(self.eye1_x),
                int(self.eye1_y + height_reduction / 2),
                int(self.eye1_radius * 2),
                max(0, int(self.eye1_radius * 2 - height_reduction))
            )
            painter.drawPie(
                    rect1,
                    0 * 16,
                    180 * 16
                )

            # Dessiner le demi-cercle pour l'oeil droit (avec clignement ou clin d'oeil)
            rect2 = QRect(
                int(self.eye2_x),
                int(self.eye2_y +  (height_reduction / 2 if not self.is_winking else wink_height_reduction / 2)),
                int(self.eye2_radius * 2),
                max(0, int(self.eye2_radius * 2 - (height_reduction if not self.is_winking else wink_height_reduction)))
                )
            painter.drawPie(
                rect2,
                0 * 16,
                 180 * 16
                )
        elif self.is_sad:
            painter.setBrush(eye_color)
            painter.setPen(Qt.NoPen)
            
            # Rotation de 45 degrés vers l'extérieur pour l'oeil gauche
            transform1 = QTransform()
            transform1.translate(self.eye1_x + self.eye1_radius, self.eye1_y + self.eye1_radius)
            transform1.rotate(-45)
            transform1.translate(-(self.eye1_x + self.eye1_radius), -(self.eye1_y + self.eye1_radius))
            painter.setTransform(transform1)
            # Dessiner le demi-cercle pour l'oeil gauche avec rotation et clignement inversé
            rect1 = QRect(
                int(self.eye1_x),
                int(self.eye1_y - height_reduction / 2),  # Inverser l'effet
                int(self.eye1_radius * 2),
                max(0, int(self.eye1_radius * 2 - height_reduction))
            )
            painter.drawPie(
                    rect1,
                    180 * 16,  # Inverser l'angle
                    180 * 16
                )

            painter.setTransform(QTransform()) # Réinitialiser la transformation pour l'oeil droit
            
            # Rotation de 45 degrés vers l'extérieur pour l'oeil droit
            transform2 = QTransform()
            transform2.translate(self.eye2_x + self.eye2_radius, self.eye2_y + self.eye2_radius)
            transform2.rotate(45) # 45 degrés dans le sens des aiguilles d'une montre 
            transform2.translate(-(self.eye2_x + self.eye2_radius), -(self.eye2_y + self.eye2_radius))
            painter.setTransform(transform2)

            # Dessiner le demi-cercle pour l'oeil droit avec rotation et clignement inversé
            rect2 = QRect(
                int(self.eye2_x),
                int(self.eye2_y - (height_reduction / 2 if not self.is_winking else wink_height_reduction / 2)), # Inverser l'effet
                int(self.eye2_radius * 2),
                max(0, int(self.eye2_radius * 2 - (height_reduction if not self.is_winking else wink_height_reduction)))
                )
            painter.drawPie(
                rect2,
                180 * 16,  # Inverser l'angle
                180 * 16
                )
            
            painter.setTransform(QTransform()) # Réinitialiser la transformation

        else:
            painter.setBrush(eye_color)
            # Dessiner l'oeil gauche (avec clignement)
            painter.drawEllipse(
                int(self.eye1_x),
                int(self.eye1_y + height_reduction / 2),
                int(self.eye1_radius * 2),
                int(max(0, self.eye1_radius * 2 - height_reduction))
            )
            # Dessiner l'oeil droit (avec clignement ou clin d'oeil)
            painter.drawEllipse(
                int(self.eye2_x),
                int(self.eye2_y + (height_reduction / 2 if not self.is_winking else wink_height_reduction / 2)),
                int(self.eye2_radius * 2),
                int(max(0, self.eye2_radius * 2 - (height_reduction if not self.is_winking else wink_height_reduction)))
            )

def create_image():
    image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((8, 8, 56, 56), fill=(0, 255, 255))
    return image


def show_message(window):
    print("Happy button clicked!")
    window.trigger_happy.emit()

def show_wink(window):
    print("Wink button clicked!")
    window.trigger_wink.emit()
    
def show_sad(window):
    print("Sad button clicked!")
    window.trigger_sad.emit()

looking_state = False
def show_looking(window):
    global looking_state
    looking_state = not looking_state
    print("Looking toggle changed")
    window.trigger_looking.emit()
    
move_state = False
def show_move(window):
    global move_state
    move_state = not move_state
    print("Move toggle changed")
    window.trigger_move.emit()

def get_looking_state(menu_item):
    global looking_state
    return looking_state

def get_move_state(menu_item):
    global move_state
    return move_state
def start_tray(app, window):
    menu = Menu(
        MenuItem("Happy", lambda: show_message(window)),
        MenuItem("Wink", lambda: show_wink(window)),
        MenuItem("Sad", lambda: show_sad(window)),
        MenuItem("Looking", lambda: show_looking(window),checked=get_looking_state),
        MenuItem("Move", lambda: show_move(window),checked=get_move_state),
        MenuItem("Quitter", lambda: quit_app(app))
    )
    icon = Icon("Eyes App", create_image(), menu=menu)
    icon.run()


def quit_app(app):
    app.quit()
    sys.exit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EyesWidget()
    window.show()

    tray_thread = threading.Thread(target=start_tray, args=(app, window), daemon=True)
    tray_thread.start()

    sys.exit(app.exec_())