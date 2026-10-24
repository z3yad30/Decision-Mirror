from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".venv", ".git", "__pycache__", ".pytest_cache"}
PURPOSES = {
    ".vscode": "Workspace editor settings",
    "data": "Gold, raw, and processed datasets",
    "docs": "Project documentation and source archives",
    "evaluation": "Evaluation outputs and results",
    "experiments": "Experimental and legacy implementations",
    "prompts": "Versioned model prompts",
    "schemas": "Data contracts and validation schemas",
    "scripts": "Project maintenance utilities",
    "src": "Decision Mirror application source",
    "tests": "Automated test suite",
}


def render_tree(path: Path, prefix: str = "") -> list[str]:
    entries = sorted(
        (
            entry
            for entry in path.iterdir()
            if entry.name not in EXCLUDED and not entry.name.endswith(".egg-info")
        ),
        key=lambda entry: (not entry.is_dir(), entry.name.casefold()),
    )
    lines = []
    for index, entry in enumerate(entries):
        is_last = index == len(entries) - 1
        connector = "`-- " if is_last else "|-- "
        name = entry.name + ("/" if entry.is_dir() else "")
        if path == ROOT and entry.is_dir():
            purpose = PURPOSES.get(entry.name)
            if purpose:
                name += f"  # {purpose}"
        lines.append(prefix + connector + name)
        if entry.is_dir():
            child_prefix = prefix + ("    " if is_last else "|   ")
            lines.extend(render_tree(entry, child_prefix))
    return lines


def main() -> None:
    output = "Decision-Mirror/\n" + "\n".join(render_tree(ROOT)) + "\n"
    (ROOT / "file_structure.txt").write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
