import re
import requests
from pathlib import Path
from config import logger

KROKI_BASE = "https://kroki.io"

DIAGRAM_TYPE_MAP = {
    "mermaid": "mermaid",
    "plantuml": "plantuml",
    "puml": "plantuml",
}

FENCE_PATTERN = re.compile(
    r"```(mermaid|plantuml|puml)\s*\n(.*?)\n```",
    re.DOTALL,
)


def _render_diagram(code: str, diagram_type: str) -> bytes | None:
    try:
        r = requests.post(
            f"{KROKI_BASE}/{diagram_type}/svg",
            data=code.encode("utf-8"),
            headers={"Content-Type": "text/plain"},
            timeout=30,
        )
        r.raise_for_status()
        return r.content
    except requests.RequestException as e:
        logger.warning(f"Kroki render failed for {diagram_type}: {e}")
        return None


def render_diagrams(content: str, work_dir: Path) -> str:
    svg_files: list[Path] = []
    counter = 0

    def _replace(m: re.Match) -> str:
        nonlocal counter
        diagram_type = DIAGRAM_TYPE_MAP.get(m.group(1).lower())
        if not diagram_type:
            return m.group(0)

        svg_bytes = _render_diagram(m.group(2), diagram_type)
        if not svg_bytes:
            return m.group(0)

        counter += 1
        svg_path = work_dir / f"kroki_{counter}.svg"
        svg_path.write_bytes(svg_bytes)
        svg_files.append(svg_path)
        return f"![Diagram {counter}]({svg_path.name})"

    result = FENCE_PATTERN.sub(_replace, content)

    if counter > 0:
        logger.info(f"Rendered {counter} diagram(s) via Kroki")

    return result
