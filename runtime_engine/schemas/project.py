from __future__ import annotations
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class WindowConfig(BaseModel):
    width: int = 1280
    height: int = 720
    title: str = "GameForge"

class ProjectFile(BaseModel):
    format_version: int = 1
    title: str = "Untitled"
    window: WindowConfig = Field(default_factory=WindowConfig)
    plugins: List[str] = Field(default_factory=list)
    assets: Dict[str, Any] = Field(default_factory=dict)
    start_scene: str = "level1"
