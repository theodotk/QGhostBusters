import pygame
from pygame import Vector2

from src.Levels.base_level import BaseLevel
from src.Menus.menu import MenusManager
from src.SoundEffects.sound_manager import ScreenSoundManager


class GameState:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        pygame.mixer_music.set_volume(0.1)
        pygame.mixer.set_num_channels(4)
        self.window_channel = pygame.mixer.Channel(0)
        self.extra_level_channel = pygame.mixer.Channel(1)
        self.player_channel = pygame.mixer.Channel(2)
        self.enemies_channel = pygame.mixer.Channel(3)

        self.running = True
        self.clock = pygame.time.Clock()

        # window variables
        self.cellSize: Vector2 = Vector2(32, 32)
        self.worldSize: Vector2 = Vector2(40, 20)
        self.window = None
        self.window_title = "QhostBusters - Menu"
        self.setup_game_window()

        # level variables
        self.level: BaseLevel = None

        self.menu = MenusManager(window=self.window, channel=self.window_channel)
        self.setup_game_music(self.menu.music)
        self.last_game_status = None

    def load_level(self, level: BaseLevel):
        self.level = level(
            cellSize=self.cellSize,
            worldSize=self.worldSize,
            window=self.window,
            level_channel=self.window_channel,
            extra_level_channel=self.extra_level_channel,
            player_channel=self.player_channel,
            enemies_channel=self.enemies_channel,
        )
        self.level.load_level()

    def unload_level(self):
        self.level = None
        self.setup_game_window()
        self.setup_game_music(self.menu.music)

    def setup_game_window(self):
        windowSize = self.cellSize.elementwise() * self.worldSize
        self.window = pygame.display.set_mode((int(windowSize.x), int(windowSize.y)))
        pygame.display.set_caption(self.window_title)

    @staticmethod
    def setup_game_music(music: ScreenSoundManager):
        music.play_music()

    def update(
        self,
    ):
        if self.level:
            self.level.update()
            if not self.level.keep_running:
                self.last_game_status = self.level.game_status
                self.unload_level()
        else:
            if self.last_game_status is not None:
                if self.last_game_status == "won":
                    self.menu.current_menu = "win_message"
                elif self.last_game_status == "lost":
                    self.menu.current_menu = "lose_message"
                # in the game was paused, neither is chosen, and the level selection menu should appear
            level = self.menu.update()
            if level:
                self.load_level(level)
            self.running = self.menu.keep_running
            self.last_game_status = None

    def render(self):
        self.window.fill((0, 0, 0))
        if self.level:
            self.level.render()
        else:
            self.menu.render()
        pygame.display.update()

    def run(self):
        while self.running:
            self.update()
            self.render()
            self.clock.tick(60)
