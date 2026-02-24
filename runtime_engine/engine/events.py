from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, List, Type, Any

@dataclass(frozen=True)
class Event: ...

@dataclass(frozen=True)
class KeyDown(Event):
    key: int

@dataclass(frozen=True)
class KeyUp(Event):
    key: int

@dataclass(frozen=True)
class SceneLoaded(Event):
    scene_id: str

class EventBus:
    def __init__(self) -> None:
        self._subs: Dict[Type[Event], List[Callable[[Event], None]]] = {}

    def on(self, event_type: Type[Event], fn: Callable[[Event], None]) -> None:
        self._subs.setdefault(event_type, []).append(fn)

    def emit(self, ev: Event) -> None:
        for fn in self._subs.get(type(ev), []):
            fn(ev)
