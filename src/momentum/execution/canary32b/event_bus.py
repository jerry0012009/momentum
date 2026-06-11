from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from momentum.domain.canary32b_models import EventRecord


class JsonlEventBus:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: EventRecord) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")

    def append_many(self, events: Iterable[EventRecord]) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            for event in events:
                f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
