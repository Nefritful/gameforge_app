"""Миграции формата DSL.

Идея: Runtime и Editor встречаются ТОЛЬКО здесь.
Если format_version вырос — Editor сохраняет новую версию,
а Runtime умеет мигрировать старые входные данные в актуальную модель.
"""

from typing import Any, Dict

CURRENT_VERSION = 1

def migrate_project(data: Dict[str, Any]) -> Dict[str, Any]:
    v = int(data.get("format_version") or 1)
    if v == CURRENT_VERSION:
        return data
    # пример: v0 -> v1
    if v == 0:
        data["format_version"] = 1
        return data
    # если неизвестно — пусть падает выше валидатором
    return data
