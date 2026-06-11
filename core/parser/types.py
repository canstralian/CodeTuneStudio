from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Language(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    BASH = "bash"
    UNKNOWN = "unknown"


@dataclass
class ParseError:
    message: str
    line: int
    column: int
    source: str


@dataclass
class ParseResult:
    language: Language
    ast_data: dict[str, Any]
    errors: list[ParseError] = field(default_factory=list)
    success: bool = True
