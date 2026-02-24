from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, Literal

BaseKind = Literal["Pawn","Object","Area","Ui"]

@dataclass
class Transform:
    x: float = 0
    y: float = 0
    rotation: float = 0
    scale: float = 1

@dataclass
class Velocity:
    vx: float = 0
    vy: float = 0

@dataclass
class Renderable:
    texture_id: str = ""
    width: float = 64
    height: float = 64
    layer: int = 1

@dataclass
class PhysicsBody:
    body: str = "dynamic"  # dynamic/static/kinematic/none
    mass: float = 1.0
    friction: float = 0.2
    restitution: float = 0.0
    collider: Optional[Dict[str, Any]] = None

# ---- 4 базовых класса ----

@dataclass
class Object:
    id: str
    base: BaseKind = "Object"
    name: str = ""
    type: str = ""
    transform: Transform = field(default_factory=Transform)
    velocity: Velocity = field(default_factory=Velocity)
    physics: PhysicsBody = field(default_factory=PhysicsBody)
    render: Renderable = field(default_factory=Renderable)
    tags: list[str] = field(default_factory=list)
    components: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Pawn(Object):
    base: BaseKind = "Pawn"
    controller: Dict[str, Any] = field(default_factory=lambda: {"enabled": True, "speed": 260, "scheme":"wasd"})
    camera_follow: Dict[str, Any] = field(default_factory=lambda: {"enabled": True, "target":"self", "lerp":0.12})

@dataclass
class Area(Object):
    base: BaseKind = "Area"
    # прозрачная сущность: триггеры, зоны, свет, коллизии и т.п.
    area: Dict[str, Any] = field(default_factory=lambda: {
        "kind":"trigger",
        "trigger": {"on_enter": [], "on_exit": []},
        "light": {"enabled": False, "radius": 220, "intensity": 1.0},
    })

@dataclass
class Ui(Object):
    base: BaseKind = "Ui"
    # UI сущность: виджеты, якоря, события клика, текст/спрайт
    ui: Dict[str, Any] = field(default_factory=lambda: {
        "widget":"panel",
        "anchor":"top_left",
        "rect":{"x":20,"y":20,"w":220,"h":90},
        "text":{"value":"UI","size":16},
        "on_click": [],
    })
