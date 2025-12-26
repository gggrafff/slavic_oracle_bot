from typing import Generator
from typing import Any
import logging


def prepare_logging() -> None:
    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    # set higher logging level for httpx to avoid all GET and POST requests being logged
    logging.getLogger("httpx").setLevel(logging.WARNING)


def isiterable(object_: Any) -> bool:
    return hasattr(type(object_), "__iter__")


def chunks(lst: list[Any], n: int) -> Generator[list[Any], Any, None]:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def unique(lst: list[Any]) -> list[Any]:
    seen: set[Any] = set()
    seen_add = seen.add
    return [x for x in lst if not (x in seen or seen_add(x))]


def format_dict(obj_dict: dict[Any, Any], indent: int = 0) -> str:
    output = []
    for key, value in obj_dict.items():
        output.append("  " * indent + f"- {key}")
        if isinstance(value, dict):
            output.append(format_dict(value, indent + 1))
    return "\n".join(output)
