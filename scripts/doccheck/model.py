from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Issue:
    path: str
    line: int | None
    category: str
    message: str
    level: str = "error"


@dataclass
class Document:
    path: Path
    kind: str
    metadata: dict[str, Any] = field(default_factory=dict)
    body: str = ""
    body_line: int = 1

    @property
    def identity(self) -> str | None:
        value = self.metadata.get("id")
        return value if isinstance(value, str) else None
