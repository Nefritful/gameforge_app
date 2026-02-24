from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .events import EventBus
from .entities import Object

@dataclass
class Scene:
    scene_id: str
    entities: List[Object] = field(default_factory=list)

@dataclass
class World:
    bus: EventBus = field(default_factory=EventBus)
    scenes: Dict[str, Scene] = field(default_factory=dict)
    active_scene_id: Optional[str] = None

    def set_active(self, scene_id: str) -> None:
        if scene_id not in self.scenes:
            raise KeyError(f"scene not found: {scene_id}")
        self.active_scene_id = scene_id
        self.bus.emit(__import__("runtime_engine.engine.events", fromlist=["SceneLoaded"]).SceneLoaded(scene_id))

    @property
    def scene(self) -> Scene:
        if not self.active_scene_id:
            raise RuntimeError("active_scene_id is not set")
        return self.scenes[self.active_scene_id]
