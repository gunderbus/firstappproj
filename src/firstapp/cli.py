from __future__ import annotations

import argparse
import json
from pathlib import Path

from firstapp import __version__


DEFAULT_GITIGNORE = """__pycache__/
*.pyc
.venv/
dist/
build/
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="firstapp",
        description="Bootstrap a starter project directory.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init",
        help="Create a starter project structure.",
    )
    init_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Directory to initialize. Defaults to the current directory.",
    )

    subparsers.add_parser(
        "doctor",
        help="Check whether the current directory looks initialized.",
    )

    return parser


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.write_text(content, encoding="utf-8")
    return True


def cmd_init(target: Path) -> int:
    target.mkdir(parents=True, exist_ok=True)

    created = []
    for directory in ("src", "tests"):
        directory_path = target / directory
        directory_path.mkdir(exist_ok=True)
        created.append(f"dir:{directory}")

    if write_if_missing(target / ".gitignore", DEFAULT_GITIGNORE):
        created.append("file:.gitignore")

    if write_if_missing(
        target / "README.md",
        f"# {target.resolve().name}\n\nCreated with firstapp.\n",
    ):
        created.append("file:README.md")

    config = {
        "name": target.resolve().name,
        "version": "0.1.0",
        "generated_by": "firstapp",
    }
    config_path = target / "firstapp.json"
    if not config_path.exists():
        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        created.append("file:firstapp.json")

    print(f"Initialized project at {target.resolve()}")
    for item in created:
        print(f"created {item}")
    return 0


def cmd_doctor(target: Path) -> int:
    expected = ["src", "tests", ".gitignore", "README.md", "firstapp.json"]
    missing = [name for name in expected if not (target / name).exists()]

    if missing:
        print("Project is missing expected files:")
        for name in missing:
            print(f"- {name}")
        return 1

    print("Project looks healthy.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        return cmd_init(Path(args.path))
    if args.command == "doctor":
        return cmd_doctor(Path("."))

    parser.error("Unknown command")
    return 2
