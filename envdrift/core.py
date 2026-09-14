from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import re
from typing import Iterable


KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class ParsedEnv:
    values: dict[str, str]
    duplicates: list[str]
    invalid_lines: list[int]


@dataclass(frozen=True)
class DriftReport:
    missing: list[str]
    unexpected: list[str]
    empty_required: list[str]
    duplicate_keys: list[str]
    invalid_lines: list[int]

    @property
    def ok(self) -> bool:
        return not any(
            (
                self.missing,
                self.empty_required,
                self.duplicate_keys,
                self.invalid_lines,
            )
        )

    def to_dict(self) -> dict:
        data = asdict(self)
        data["ok"] = self.ok
        return data


def _strip_optional_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_env_lines(lines: Iterable[str]) -> ParsedEnv:
    values: dict[str, str] = {}
    duplicates: list[str] = []
    invalid_lines: list[int] = []

    for number, raw in enumerate(lines, start=1):
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[7:].lstrip()

        if "=" not in line:
            invalid_lines.append(number)
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not KEY_RE.fullmatch(key):
            invalid_lines.append(number)
            continue

        if key in values and key not in duplicates:
            duplicates.append(key)

        values[key] = _strip_optional_quotes(value)

    return ParsedEnv(
        values=values,
        duplicates=sorted(duplicates),
        invalid_lines=invalid_lines,
    )


def parse_env_file(path: str | Path) -> ParsedEnv:
    path = Path(path)
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Environment file not found: {path}") from exc
    except OSError as exc:
        raise OSError(f"Could not read environment file: {path}") from exc

    return parse_env_lines(content.splitlines())


def compare_envs(
    reference: ParsedEnv,
    target: ParsedEnv,
    *,
    allow_unexpected: bool = False,
) -> DriftReport:
    reference_keys = set(reference.values)
    target_keys = set(target.values)

    missing = sorted(reference_keys - target_keys)
    unexpected = sorted(target_keys - reference_keys)

    empty_required = sorted(
        key
        for key in (reference_keys & target_keys)
        if reference.values[key] != "" and target.values[key] == ""
    )

    duplicate_keys = sorted(set(reference.duplicates) | set(target.duplicates))
    invalid_lines = sorted(set(reference.invalid_lines) | set(target.invalid_lines))

    if allow_unexpected:
        unexpected = []

    return DriftReport(
        missing=missing,
        unexpected=unexpected,
        empty_required=empty_required,
        duplicate_keys=duplicate_keys,
        invalid_lines=invalid_lines,
    )
