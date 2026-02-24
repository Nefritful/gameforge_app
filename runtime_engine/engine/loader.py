from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

import arcade

from ..schemas.project import ProjectFile
from ..schemas.scene import SceneFile
from ..schemas.migrations import migrate_project
from .world import World, Scene
from .entities import Object, Pawn, Area, Ui, Transform, Velocity, Renderable, PhysicsBody

def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def build_entity(e: Dict[str, Any]) -> Object:
    base = e.get("base") or "Object"
    cls = {"Object": Object, "Pawn": Pawn, "Area": Area, "Ui": Ui}.get(base, Object)

    t = e.get("transform") or {}
    v = e.get("velocity") or {}
    s = e.get("sprite") or {}

    obj = cls(
        id=e.get("id",""),
        name=e.get("name",""),
        type=e.get("type",""),
    )
    obj.transform = Transform(
        x=float(t.get("x",0)),
        y=float(t.get("y",0)),
        rotation=float(t.get("rotation",0)),
        scale=float(t.get("scale",1)),
    )
    obj.velocity = Velocity(
        vx=float(v.get("vx",0)),
        vy=float(v.get("vy",0)),
    )

    # physics
    phys = e.get("physics") or {}
    if phys and phys.get("body","dynamic") != "none":
        obj.physics = PhysicsBody(
            body=str(phys.get("body","dynamic")),
            mass=float(phys.get("mass",1.0)),
            friction=float(phys.get("friction",0.2)),
            restitution=float(phys.get("restitution",0.0)),
            collider=phys.get("collider"),
        )
    else:
        obj.physics = PhysicsBody(body="none")

    obj.render = Renderable(
        texture_id=str(s.get("texture_id","")),
        width=float(s.get("width",64) or 64),
        height=float(s.get("height",64) or 64),
        layer=int(s.get("layer",1) or 1),
    )
    obj.tags = list(e.get("tags") or [])
    obj.components = dict(e.get("components") or {})

    # pawn extras
    if base == "Pawn":
        obj.controller = dict(e.get("player_controller") or e.get("controller") or {"enabled":True,"speed":260,"scheme":"wasd"})
        obj.camera_follow = dict(e.get("camera_follow") or {"enabled":True,"target":"self","lerp":0.12})
    if base == "Area":
        obj.area = dict(e.get("area") or {})
    if base == "Ui":
        obj.ui = dict(e.get("ui") or {})
    return obj

def load_project_dir(project_dir: str | Path) -> tuple[ProjectFile, World, dict[str, arcade.Texture]]:
    project_dir = Path(project_dir)
    project_data = migrate_project(load_json(project_dir / "project.json"))
    project = ProjectFile.model_validate(project_data)

    world = World()
    textures: dict[str, arcade.Texture] = {}

    # assets/textures: ожидаем файлы в assets/textures/<id>.<ext>
    tex_dir = project_dir / "assets" / "textures"
    if tex_dir.exists():
        for p in tex_dir.glob("*.*"):
            tex_id = p.stem
            try:
                textures[tex_id] = arcade.load_texture(str(p))
            except Exception:
                pass

    # scenes: files scene_<id>.json
    for sp in project_dir.glob("scene_*.json"):
        scene_data = load_json(sp)
        scene = SceneFile.model_validate(scene_data)
        sc = Scene(scene_id=scene.scene_id)
        for ent in scene.entities:
            # pydantic -> dict
            sc.entities.append(build_entity(ent.model_dump()))
        world.scenes[scene.scene_id] = sc

    if project.start_scene in world.scenes:
        world.set_active(project.start_scene)
    elif world.scenes:
        world.set_active(next(iter(world.scenes.keys())))
    return project, world, textures
