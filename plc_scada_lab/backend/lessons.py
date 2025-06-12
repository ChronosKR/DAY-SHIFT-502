
import pathlib
DOCS = pathlib.Path(__file__).parent.parent / "docs"
def list_lessons():
    return sorted(p.stem for p in DOCS.glob("*.md"))
def load_md(name: str) -> str:
    path = DOCS / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(name)
    return path.read_text(encoding="utf-8")
