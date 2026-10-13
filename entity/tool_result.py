"""
    统一的 ToolResult
"""
from dataclasses import dataclass
from typing import Any

import orjson


@dataclass
class ToolResult:
    ok: bool
    tool_name: str
    data: Any = None
    error_type: str | None = None
    error_message: str | None = None
    elapsed_ms: int = 0

    def to_model_content(self) -> str:
        payload = {
            "ok": self.ok,
            "tool": self.tool_name,
            "data": self.data,
            "error": None if self.ok else {
                "type": self.error_type,
                "message": self.error_message,
            },
        }
        return orjson.dumps(payload).decode("utf-8")