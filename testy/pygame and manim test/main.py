from manim import *

class CircleAnimation(Scene):
    def construct(self):
        # Créer les deux cercles bleus
        circle1 = Circle(color=BLUE, fill_opacity=1).scale(2).shift(LEFT * 3)
        circle2 = Circle(color=BLUE, fill_opacity=1).scale(2).shift(RIGHT * 3)
        
        # Afficher les cercles avec une animation
        self.play(Create(circle1), Create(circle2))
        
        # Attendre 2 secondes
        self.wait(2)
        
        # Diviser le premier cercle en deux depuis le bas (utiliser un arc pour une animation fluide)
        half_1 = Arc(
            angle=PI, radius=circle1.radius, arc_center=circle1.get_center(), color=BLUE, fill_opacity=1
        )
        
        half_2 = Arc(
            angle=PI, radius=circle2.radius, arc_center=circle2.get_center(), color=BLUE, fill_opacity=1
        )
        
        # Créer l'animation de "coup de moitié" pour le cercle1
        self.play(
            circle1.animate.scale(0.5),  # Réduire le cercle
            Transform(circle1, half_1),
            Transform(circle2, half_2)  # Transformer en arc
        )
        
        self.wait(1)  # Attendre 1 seconde avant de finir
