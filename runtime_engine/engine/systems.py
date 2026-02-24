from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
import arcade

from .world import World
from .events import KeyDown, KeyUp

class System(ABC):
    @abstractmethod
    def update_fixed(self, world: World, dt: float) -> None: ...
    def update(self, world: World, dt: float) -> None: ...
    def draw(self, world: World) -> None: ...

class InputSystem(System):
    def __init__(self):
        self.keys_down: set[int] = set()

    def on_key_press(self, world: World, key: int):
        self.keys_down.add(key)
        world.bus.emit(KeyDown(key))

    def on_key_release(self, world: World, key: int):
        self.keys_down.discard(key)
        world.bus.emit(KeyUp(key))

    def update_fixed(self, world: World, dt: float) -> None:
        # Pawn controller: WASD/Arrows
        for e in world.scene.entities:
            if getattr(e, "base", "") != "Pawn":
                continue
            ctrl = getattr(e, "controller", {}) or {}
            if not ctrl.get("enabled", True):
                continue
            speed = float(ctrl.get("speed", 260))
            vx = vy = 0.0
            scheme = ctrl.get("scheme","wasd")
            if scheme == "wasd":
                if arcade.key.W in self.keys_down: vy += speed
                if arcade.key.S in self.keys_down: vy -= speed
                if arcade.key.A in self.keys_down: vx -= speed
                if arcade.key.D in self.keys_down: vx += speed
            else:
                if arcade.key.UP in self.keys_down: vy += speed
                if arcade.key.DOWN in self.keys_down: vy -= speed
                if arcade.key.LEFT in self.keys_down: vx -= speed
                if arcade.key.RIGHT in self.keys_down: vx += speed
            e.velocity.vx = vx
            e.velocity.vy = vy

class PhysicsSystem(System):
    def update_fixed(self, world: World, dt: float) -> None:
        # минимальная кинематика без столкновений
        for e in world.scene.entities:
            if getattr(e, "physics", None) and getattr(e.physics, "body", "dynamic") == "none":
                continue
            e.transform.x += e.velocity.vx * dt
            e.transform.y += e.velocity.vy * dt

class RenderSystem(System):
    def __init__(self, textures: dict[str, arcade.Texture]):
        self.textures = textures

    def update_fixed(self, world: World, dt: float) -> None:
        pass

    def draw(self, world: World) -> None:
        # sort by layer
        ents = sorted(world.scene.entities, key=lambda e: getattr(e, "render", None).layer if getattr(e, "render", None) else 0)
        for e in ents:
            r = getattr(e, "render", None)
            if not r:
                continue
            tex = self.textures.get(r.texture_id)
            if tex:
                arcade.draw_texture_rectangle(e.transform.x, e.transform.y, r.width, r.height, tex)
            else:
                # placeholder
                arcade.draw_rectangle_outline(e.transform.x, e.transform.y, max(r.width, 24), max(r.height, 24), arcade.color.WHITE, 2)

class UiSystem(System):
    def update_fixed(self, world: World, dt: float) -> None:
        pass

    def draw(self, world: World) -> None:
        for e in world.scene.entities:
            if getattr(e, "base", "") != "Ui":
                continue
            ui = getattr(e, "ui", {}) or {}
            rect = ui.get("rect", {})
            x = float(rect.get("x", 20))
            y = float(rect.get("y", 20))
            w = float(rect.get("w", 220))
            h = float(rect.get("h", 90))
            arcade.draw_lrtb_rectangle_filled(x, x+w, y+h, y, (255,255,255,30))
            txt = (ui.get("text", {}) or {}).get("value", "UI")
            arcade.draw_text(txt, x+10, y+h-28, arcade.color.WHITE, 14)
