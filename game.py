from distutils.command.config import config

import pygame

from player import Player

from Map import MapManager
from src.dialog import DialogBox


class CurrentGameState:
    pass


class Game:

    def __init__(self):

        self.battle = None
        self.player = None
        self.event = None

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

    def determine_pokemon_found(self, map_tile):
        if map_tile not in config.MONSTER_TYPES:
            return

        random_number = utilities.generate_random_number(1, 10)

        # 20 percent chance of hitting pokemon
        if random_number <= 2:
            found_monster = self.monster_factory.create_monster(map_tile)
            print("you found a monster!")
            print("Monster Type: " + found_monster.type)
            print("Attack: " + str(found_monster.attack))
            print("Health: " + str(found_monster.health))

            self.battle = Battle(self.screen, found_monster, self.player)
            self.current_game_state = CurrentGameState.BATTLE

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

        if self.current_game_state == CurrentGameState.MAP:
            self.player.move = False
            self.screen.fill(config.BLACK)
            # print("update")
            self.handle_events()

            if self.player_has_moved:
                self.determine_game_events()

            self.map.render(self.screen, self.player)

        elif self.current_game_state == CurrentGameState.BATTLE:
            self.battle.update()
            self.battle.render()

            if self.battle.monster.health <= 0:
                self.current_game_state = CurrentGameState.MAP

        if self.event is not None:
            self.event.render()
            self.event.update()

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
