from __future__ import annotations
import arcade
from typing import List

from .loader import load_project_dir
from .world import World
from .systems import InputSystem, PhysicsSystem, RenderSystem, UiSystem, System

class GameApp(arcade.Window):
    def __init__(self, project_dir: str):
        self.project, self.world, self.textures = load_project_dir(project_dir)
        super().__init__(self.project.window.width, self.project.window.height, self.project.title)
        arcade.set_background_color(arcade.color.from_hex_string("#0b1220"))

        self.input = InputSystem()
        self.systems_fixed: List[System] = [
            self.input,
            PhysicsSystem(),
        ]
        self.systems_draw: List[System] = [
            RenderSystem(self.textures),
            UiSystem(),
        ]

        self._fixed_dt = 1/60.0
        self._acc = 0.0

    def on_key_press(self, key: int, modifiers: int):
        self.input.on_key_press(self.world, key)

    def on_key_release(self, key: int, modifiers: int):
        self.input.on_key_release(self.world, key)

    def on_update(self, delta_time: float):
        # fixed-step
        self._acc += delta_time
        while self._acc >= self._fixed_dt:
            for s in self.systems_fixed:
                s.update_fixed(self.world, self._fixed_dt)
            self._acc -= self._fixed_dt

        for s in self.systems_fixed:
            s.update(self.world, delta_time)

    def on_draw(self):
        self.clear()
        for s in self.systems_draw:
            s.draw(self.world)

def run(project_dir: str):
    app = GameApp(project_dir)
    arcade.run()
