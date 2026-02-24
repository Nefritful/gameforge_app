from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field
from .components import EntityFile

class SceneFile(BaseModel):
    scene_id: str
    entities: List[EntityFile] = Field(default_factory=list)
