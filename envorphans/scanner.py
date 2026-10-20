"""Core scanning logic for envorphans."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Set

DEFAULT_IGNORE = {
    ".git", "node_modules", ".venv", "venv", "__pycache__",
    "dist", "build", ".next", "target", ".tox",
}
DEFAULT_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".rb",
    ".java", ".sh", ".yaml", ".yml", ".json", ".toml", ".md",
    ".html", ".css", ".env",
}

REFERENCED_PATTERNS = [
    re.compile(r"process\.env\.([A-Za-z_][A-Za-z0-9_]*)"),
    re.compile(r"process\.env\[['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\]"),
    re.compile(r"os\.environ\[['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\]"),
    re.compile(r"os\.environ\.get\(['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"),
    re.compile(r"os\.getenv\(['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"),
    re.compile(r"getenv\(['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"),
    re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}"),
    re.compile(r"\benv\.([A-Z_][A-Z0-9_]*)\b"),
    re.compile(r"\bDeno\.env\.get\(['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"),
]


def parse_env_file(path: Path) -> Set[str]:
    names: Set[str] = set()
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return names
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key = line.split("=", 1)[0].strip()
        if key.startswith("export "):
            key = key[len("export "):].strip()
        key = key.strip("\"'")
        if key and re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
            names.add(key)
    return names


def _is_excluded_env_name(name: str) -> bool:
    low = name.lower()
    return any(tok in low for tok in ("example", "sample", "template"))


def discover_env_files(root: Path) -> list[Path]:
    result: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        name = p.name
        if name == ".env" or name.startswith(".env."):
            if _is_excluded_env_name(name):
                continue
            result.append(p)
    return sorted(result)


def discover_source_files(root: Path, extensions: Set[str], ignore: Set[str]) -> list[Path]:
    result: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        try:
            rel_parts = p.relative_to(root).parts
        except ValueError:
            continue
        if any(part in ignore for part in rel_parts[:-1]):
            continue
        if p.suffix.lower() in extensions or p.name in (".env",):
            result.append(p)
    return result


def find_referenced_vars(files: Iterable[Path]) -> Set[str]:
    found: Set[str] = set()
    for p in files:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat in REFERENCED_PATTERNS:
            for m in pat.finditer(text):
                for g in m.groups():
                    if g:
                        found.add(g)
    return found


def find_orphans(root, extensions=None, ignore=None):
    root_path = Path(root).resolve()
    exts = set(extensions) if extensions else set(DEFAULT_EXTS)
    ign = set(ignore) if ignore else set(DEFAULT_IGNORE)
    env_files = discover_env_files(root_path)
    defined: Set[str] = set()
    for f in env_files:
        defined |= parse_env_file(f)
    src_files = discover_source_files(root_path, exts, ign)
    referenced = find_referenced_vars(src_files)
    orphans = sorted(defined - referenced)
    return {
        "root": str(root_path),
        "env_files": [str(f) for f in env_files],
        "defined": sorted(defined),
        "referenced_count": len(referenced),
        "orphans": orphans,
    }
