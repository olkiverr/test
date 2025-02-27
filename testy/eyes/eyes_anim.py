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


class NewWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("New Window")
        self.setGeometry(300, 300, 200, 150)
        self.setStyleSheet("background-color: white;")
        self.show()


class EyesWidget(QWidget):
    trigger_happy = pyqtSignal()
    trigger_wink = pyqtSignal()
    trigger_sad = pyqtSignal()
    trigger_looking = pyqtSignal()
    trigger_move = pyqtSignal()
    trigger_border = pyqtSignal()
    trigger_random_move = pyqtSignal()
    trigger_random_look = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clignement synchronisé")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: black;")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.MSWindowsFixedSizeDialogHint)
        

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
        self.trigger_move.connect(self.move_window)
        
        # New variable for "border" mode
        self.is_borderless = True
        self.trigger_border.connect(self.border)
        
        #New variable for "random move"
        self.trigger_random_move.connect(self.random_move)
        
        #New variable for "random look"
        self.trigger_random_look.connect(self.random_look)

        
        # Timer to track the mouse position
        self.mouse_timer = QTimer(self)
        self.mouse_timer.timeout.connect(self.update_eye_positions)
        self.mouse_timer.start(30)  # Update every 30 milliseconds
        
        self.last_mouse_x, self.last_mouse_y = win32api.GetCursorPos()
        self.default_window_pos = self.frameGeometry().topLeft()
        self.target_window_pos = self.default_window_pos

        # list to store the new windows
        self.new_windows = []
        
        # Random Move animation variables
        self.random_move_timer = QTimer(self)
        self.random_move_timer.timeout.connect(self.animate_random_move)
        self.target_random_move_pos = None
        self.current_random_move_pos = None
        self.move_duration = 300  # Time to move (in ms)
        self.move_step = 0
        
        # Random look animation variables
        self.random_look_timer = QTimer(self)
        self.random_look_timer.timeout.connect(self.animate_random_look)
        self.target_random_look_angle = None
        self.look_duration = 2000
        self.look_step = 0
        self.original_eye1_x = self.eye1_x
        self.original_eye1_y = self.eye1_y
        self.original_eye2_x = self.eye2_x
        self.original_eye2_y = self.eye2_y

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
    
    def move_window(self):
        self.is_moving = not self.is_moving
        self.repaint()
        
    def border(self):
        self.is_borderless = not self.is_borderless
        if self.is_borderless:
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.FramelessWindowHint)
        self.show()  #Refresh flags
        self.repaint()
    
    def random_move(self):
        screen = QApplication.desktop().screenGeometry()
        new_x = random.randint(screen.x(), screen.right() - self.width())
        new_y = random.randint(screen.y(), screen.bottom() - self.height())
        self.target_random_move_pos = QPoint(new_x, new_y)
        self.current_random_move_pos = self.frameGeometry().topLeft()
        self.move_step = 0
        self.random_move_timer.start(30)  # Update animation every 30ms
        

    def animate_random_move(self):
        self.move_step += 1
        if self.move_step * 30 >= self.move_duration:
            self.random_move_timer.stop()
            super().move(self.target_random_move_pos)
            self.default_window_pos = self.frameGeometry().topLeft()
            self.target_window_pos = self.default_window_pos
            return
    
        progress = self.move_step * 30 / self.move_duration
        
        # Quadratic ease-out function
        progress = 1 - (1 - progress) ** 2
        
        current_x = self.current_random_move_pos.x()
        current_y = self.current_random_move_pos.y()
        
        target_x = self.target_random_move_pos.x()
        target_y = self.target_random_move_pos.y()

        new_x = current_x + (target_x - current_x) * progress
        new_y = current_y + (target_y - current_y) * progress
        
        super().move(QPoint(int(new_x),int(new_y)))
        
    def random_look(self):
        # Generate a random angle between 0 and 360 degrees
        random_angle = random.uniform(0, 360)
        self.target_random_look_angle = random_angle
        self.look_step = 0
        self.random_look_timer.start(30)
    
    def animate_random_look(self):
        self.look_step += 1
        if self.look_step * 30 >= self.look_duration:
            self.random_look_timer.stop()
            self.eye1_x = self.original_eye1_x
            self.eye1_y = self.original_eye1_y
            self.eye2_x = self.original_eye2_x
            self.eye2_y = self.original_eye2_y
            self.update()
            return
        
        progress = self.look_step * 30 / self.look_duration
        
        #Ease in out function
        progress = (math.sin(progress * math.pi - math.pi / 2) + 1) / 2

        angle_rad = math.radians(self.target_random_look_angle)
        
        # Calculate the displacement of the eyes from their original position
        move_x1 = math.cos(angle_rad) * self.eye1_radius/2 * progress
        move_y1 = math.sin(angle_rad) * self.eye1_radius/2 * progress
        
        move_x2 = math.cos(angle_rad) * self.eye2_radius/2 * progress
        move_y2 = math.sin(angle_rad) * self.eye2_radius/2 * progress

        self.eye1_x = self.original_eye1_x + move_x1
        self.eye1_y = self.original_eye1_y + move_y1
        
        self.eye2_x = self.original_eye2_x + move_x2
        self.eye2_y = self.original_eye2_y + move_y2
        
        self.update()


    
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
            self.target_window_pos = QPoint(int(window_center_x - self.width()/2 + normalized_x * distance),
                                          int(window_center_y - self.height() / 2 + normalized_y * distance))
                                        
            current_pos = self.frameGeometry().topLeft()
            
            # Smooth the movement
            new_x = current_pos.x() + (self.target_window_pos.x() - current_pos.x()) * 0.1
            new_y = current_pos.y() + (self.target_window_pos.y() - current_pos.y()) * 0.1
            
            super().move(QPoint(int(new_x), int(new_y)))

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
        if not self.random_look_timer.isActive():
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
        if self.is_borderless:
            painter.setBrush(Qt.transparent)
        else:
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

border_state = True
def show_border(window):
    global border_state
    border_state = not border_state
    print("Border toggle changed")
    window.trigger_border.emit()

def show_random_move(window):
    print("Random Move button clicked!")
    window.trigger_random_move.emit()
    
def show_random_look(window):
    print("Random Look button clicked")
    window.trigger_random_look.emit()


def get_looking_state(menu_item):
    global looking_state
    return looking_state

def get_move_state(menu_item):
    global move_state
    return move_state
    
def get_border_state(menu_item):
    global border_state
    return border_state

def show_new_window(app, window):
    new_window = NewWindow()
    window.new_windows.append(new_window)
    print("Open new window")

def start_tray(app, window):
    menu = Menu(
        MenuItem("Eyes", Menu(
            MenuItem("Happy", lambda: show_message(window)),
            MenuItem("Wink", lambda: show_wink(window)),
            MenuItem("Sad", lambda: show_sad(window)),
            MenuItem("Looking", lambda: show_looking(window),checked=get_looking_state),
            MenuItem("Move", lambda: show_move(window),checked=get_move_state),
        )),
        MenuItem("test", Menu(
            MenuItem("Border", lambda: show_border(window), checked=get_border_state),
            MenuItem("Window", lambda: show_new_window(app, window)),
            MenuItem("Random Move", lambda: show_random_move(window)),
            MenuItem("Random Look", lambda: show_random_look(window)),
        )),
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