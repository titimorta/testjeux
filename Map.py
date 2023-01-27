from dataclasses import dataclass

import pygame
import pyscroll
import pytmx
from pytmx import TiledMap

from src.player import NPC


@dataclass
class Portal:
    from_world: str
    origin_point: str
    target_world: str
    teleport_point: str


@dataclass
class Map:
    name: str
    walls: list[pygame.Rect]
    group: pyscroll.PyscrollGroup
    tmx_data: pytmx.TiledMap
    portals: list[Portal]
    npcs: list[NPC]


class MapManager:

    def __init__(self, screen, player):
        self.maps = dict()  # "house" -> Map("house", walls, group, tmx_data, panel, portals, npcs)
        self.screen = screen
        self.player = player
        self.current_map = "villeDepart"

        self.register_map("villeDepart", portals=[
            Portal(from_world="villeDepart", origin_point="ville", target_world="world", teleport_point="spawn_player"),
            Portal(from_world="villeDepart", origin_point="PN's_house", target_world="PN'shouse", teleport_point="spawn_pns")
        ])
        self.register_map("PN'shouse", portals=[
            Portal(from_world="PN'shouse", origin_point="exit_pn's", target_world="villeDepart", teleport_point="exit_PN's"),
            Portal(from_world="PN'shouse", origin_point="secondpn's", target_world="secondpn's", teleport_point="spawn_seconde")
        ])
        self.register_map("secondpn's", portals=[
            Portal(from_world="secondpn's", origin_point="exit_seconde", target_world="PN'shouse", teleport_point="exit_second")
        ])
        self.register_map("world", portals=[
            Portal(from_world="world", origin_point="enter_house", target_world="house", teleport_point="spawn_house"),
            Portal(from_world="world", origin_point="enter_dungeon", target_world="dungeon",
                   teleport_point="spawn_dungeon"),
            Portal(from_world="world", origin_point="enter_second_zone", target_world="zone2",
                   teleport_point="spawn_level1"),
            Portal(from_world="world", origin_point="premiervillage", target_world="villeDepart", teleport_point="exit_ville")
        ], npcs=[
            NPC("paul", nb_points=4, dialog=["Ici il y a un centre pokémon", "viens les faire soignier à l'occasion "]),
            NPC("test", nb_points=1, dialog=["Attention dongeons cacher"])
        ])
        self.register_map("house", portals=[
            Portal(from_world="house", origin_point="exit_house", target_world="world",
                   teleport_point="enter_house_exit"),
            Portal(from_world="house", origin_point="second_floor", target_world="house2", teleport_point="enter_floor")
        ], npcs=[
            NPC("mom", nb_points=1, dialog=["Bienvenue chez toi !"])
        ])
        self.register_map("house2", portals=[
            Portal(from_world="house2", origin_point="exit_floor", target_world="house", teleport_point="spawn_house")
        ])
        self.register_map("dungeon", portals=[
            Portal(from_world="dungeon", origin_point="exit_dungeon", target_world="world",
                   teleport_point="sortie_dungeon")
        ], npcs=[
            NPC("boss", nb_points=4, dialog=["Ne pense même pas pouvoir prendre mon trésor >:("])
        ])
        self.register_map("zone2", portals=[
            Portal(from_world="zone2", origin_point="exit_zone2", target_world="world",
                   teleport_point="exit_world_zone2"),
            Portal(from_world="zone2", origin_point="enter_house_champ", target_world="house_zone2",
                   teleport_point="spawn_house")
        ], npcs=[
            NPC("test", nb_points=1, dialog=["Maison de maitre d'arène"]),
            NPC("test2", nb_points=1, dialog=["Arène pokemon"]),
            NPC("test3", nb_points=1, dialog=["Centre pokemon"]),
        ])

        self.register_map("house_zone2", portals=[
            Portal(from_world="house_zone2", origin_point="exit_house", target_world="zone2",
                   teleport_point="sortie_house")
        ], npcs=[
            NPC("champion1", nb_points=1,
                dialog=["Reviens a l'arène plus tard je suis fatiguer", "et en plus tu est chez moi vas t'en !!!"])
        ])

        self.teleport_player('spawn_player')
        self.teleport_npcs()

    def check_npc_collisions(self, dialog_box):
        for sprite in self.get_group().sprites():
            if sprite.feet.colliderect(self.player.rect) and type(sprite) is NPC:
                dialog_box.execute(sprite.dialog)

    def check_collision(self):
        # portal
        for portal in self.get_map().portals:
            if portal.from_world == self.current_map:
                point = self.get_object(portal.origin_point)
                rect = pygame.Rect(point.x, point.y, point.width, point.height)

                if self.player.feet.colliderect(rect):
                    copy_portal = portal
                    self.current_map = portal.target_world
                    self.teleport_player(copy_portal.teleport_point)
        # collision
        for sprite in self.get_group().sprites():

            if type(sprite) is NPC:
                if sprite.feet.colliderect(self.player.rect):
                    sprite.speed = 0
                else:
                    sprite.speed = 1

            if sprite.feet.collidelist(self.get_walls()) > -1:
                sprite.move_back()

    def teleport_player(self, name):
        point = self.get_object(name)
        self.player.position[0] = point.x
        self.player.position[1] = point.y
        self.player.save_location()

    def register_map(self, name, portals=[], npcs=[]):
        # charger la carte (tmx)
        tmx_data: TiledMap = pytmx.util_pygame.load_pygame(f"map/{name}.tmx")
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 2

        # definir une liste qui va stocker les rectangle de collision
        walls = []

        for object in tmx_data.objects:
            if object.type == "collision":
                walls.append(pygame.Rect(object.x, object.y, object.width, object.height))

        # dessiner le groupe de calques
        group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=5)
        group.add(self.player)

        # récuperer les NPC
        for npc in npcs:
            group.add(npc)

        # creer un objet Map
        self.maps[name] = Map(name, walls, group, tmx_data, portals, npcs)

    def get_map(self):
        return self.maps[self.current_map]

    def get_group(self):
        return self.get_map().group

    def get_walls(self):
        return self.get_map().walls

    def get_panel(self):
        return self.get_map().panel

    def get_object(self, name):
        return self.get_map().tmx_data.get_object_by_name(name)

    def teleport_npcs(self):
        for map in self.maps:
            map_data = self.maps[map]
            npcs = map_data.npcs

            for npc in npcs:
                npc.load_points(map_data.tmx_data)
                npc.teleport_spawn()

    def draw(self):
        self.get_group().draw(self.screen)
        self.get_group().center(self.player.rect.center)

    def update(self):
        self.get_group().update()
        self.check_collision()

        for npc in self.get_map().npcs:
            npc.move()
