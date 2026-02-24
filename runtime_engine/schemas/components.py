from __future__ import annotations
from typing import Literal, Optional, Dict, Any, List
from pydantic import BaseModel, Field

class Transform(BaseModel):
    x: float = 0
    y: float = 0
    rotation: float = 0
    scale: float = 1

class Velocity(BaseModel):
    vx: float = 0
    vy: float = 0

ColliderShape = Literal["box", "circle", "poly"]

class Collider(BaseModel):
    shape: ColliderShape = "box"
    w: float = 64
    h: float = 64
    r: float = 32

BodyType = Literal["dynamic", "static", "kinematic", "none"]

class Physics(BaseModel):
    body: BodyType = "dynamic"
    mass: float = 1.0
    friction: float = 0.2
    restitution: float = 0.0
    collider: Optional[Collider] = None

class Sprite(BaseModel):
    texture_id: str = ""
    width: float = 64
    height: float = 64
    layer: int = 1

class PlayerController(BaseModel):
    enabled: bool = True
    speed: float = 260
    scheme: Literal["wasd", "arrows"] = "wasd"

class CameraFollow(BaseModel):
    enabled: bool = True
    target: str = "self"
    lerp: float = 0.12

class AreaTrigger(BaseModel):
    on_enter: List[Dict[str, Any]] = Field(default_factory=list)
    on_exit: List[Dict[str, Any]] = Field(default_factory=list)

class AreaLight(BaseModel):
    enabled: bool = False
    radius: float = 220
    intensity: float = 1.0

class AreaComponent(BaseModel):
    kind: Literal["trigger", "light", "zone"] = "trigger"
    trigger: AreaTrigger = Field(default_factory=AreaTrigger)
    light: AreaLight = Field(default_factory=AreaLight)

class UiRect(BaseModel):
    x: float = 20
    y: float = 20
    w: float = 220
    h: float = 90

class UiText(BaseModel):
    value: str = "UI"
    size: int = 16

class UiComponent(BaseModel):
    widget: Literal["panel", "button", "label", "image"] = "panel"
    anchor: Literal["top_left","top_right","bottom_left","bottom_right","center"] = "top_left"
    rect: UiRect = Field(default_factory=UiRect)
    text: UiText = Field(default_factory=UiText)
    on_click: List[Dict[str, Any]] = Field(default_factory=list)

class EntityFile(BaseModel):
    id: str
    base: Literal["Pawn","Object","Area","Ui"]
    name: str = ""
    type: str = ""
    transform: Transform = Field(default_factory=Transform)
    velocity: Velocity = Field(default_factory=Velocity)
    physics: Optional[Physics] = None
    sprite: Optional[Sprite] = None
    tags: List[str] = Field(default_factory=list)
    components: Dict[str, Any] = Field(default_factory=dict)

    # Pawn-specific
    player_controller: Optional[PlayerController] = None
    camera_follow: Optional[CameraFollow] = None

    # Area-specific
    area: Optional[AreaComponent] = None

    # Ui-specific
    ui: Optional[UiComponent] = None
