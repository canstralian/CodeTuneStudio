from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


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
    ast_data: Dict[str, Any]
    errors: List[ParseError] = field(default_factory=list)
    success: bool = True
