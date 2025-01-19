from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import sys

# Couleur par défaut
current_color = 'blue'

def create_image(color):
    """Créer une icône circulaire avec la couleur spécifiée."""
    width = 64
    height = 64
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((8, 8, width - 8, height - 8), fill=color, outline='white')
    return image

def on_quit(icon, item):
    """Fermer l'application."""
    icon.stop()
    sys.exit()

def on_hello(icon, item):
    """Exemple d'action dans le menu."""
    print("Bonjour depuis la barre des tâches !")

def change_color(icon, item, color):
    """Changer la couleur de l'icône."""
    global current_color
    current_color = color
    icon.icon = create_image(color)  # Met à jour l'icône
    icon.update_menu()  # Met à jour le menu contextuel si nécessaire

# Menu contextuel
menu = Menu(
    MenuItem("Dire Bonjour", on_hello),
    MenuItem("Changer Couleur", Menu(
        MenuItem("Bleu", lambda icon, item: change_color(icon, item, 'blue')),
        MenuItem("Rouge", lambda icon, item: change_color(icon, item, 'red')),
        MenuItem("Vert", lambda icon, item: change_color(icon, item, 'green'))
    )),
    MenuItem("Quitter", on_quit)
)

# Initialiser l'icône
icon = Icon("MonApplication", create_image(current_color), "Assistant Looi", menu)

# Lancer l'application
icon.run()
