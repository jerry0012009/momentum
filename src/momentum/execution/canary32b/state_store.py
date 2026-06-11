from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class JsonStateStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self, default: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.path.exists():
            return default or {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, payload: dict[str, Any]) -> None:
        content = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
        tmp_path = self.path.with_name(f".{self.path.name}.tmp")
        tmp_path.write_text(content, encoding="utf-8")
        os.replace(tmp_path, self.path)
