import pygame

from player import Player

from Map import MapManager
from src.dialog import DialogBox


class Game:

    def __init__(self):

        # definir si notre jeux a commencer

        # Démarrage
        self.running = True
        self.maps = "world"

        # Affichage de la fenêtre
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Pygamon - Adventure")

        # Générer le joeur
        self.player = Player()
        self.map_manager = MapManager(self.screen, self.player)
        self.dialog_box = DialogBox()

        img = pygame.image.load('map/logo.jpg')
        pygame.display.set_icon(img)

    def handle_input(self):
        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_ESCAPE]:
            self.running = False
        elif pressed[pygame.K_UP]:
            self.player.move_up()
        elif pressed[pygame.K_DOWN]:
            self.player.move_down()
        elif pressed[pygame.K_RIGHT]:
            self.player.move_right()

        elif pressed[pygame.K_LEFT]:
            self.player.move_left()

    def update(self):
        self.map_manager.update()

    def run(self):
        clock = pygame.time.Clock()

        # Clock
        while self.running:

            self.player.save_location()
            self.handle_input()
            self.update()
            self.map_manager.draw()
            self.dialog_box.render(self.screen)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.map_manager.check_npc_collisions(self.dialog_box)

            clock.tick(60)

        pygame.quit()
