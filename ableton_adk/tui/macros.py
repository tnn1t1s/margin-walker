"""Macro system — capture LLM tool sequences as replayable slash commands."""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from ..tools import GROUPS


MACRO_DIR = Path.home() / ".margin-walker"
MACRO_FILE = MACRO_DIR / "macros.json"


def _build_func_lookup() -> dict[str, callable]:
    return {func.__name__: func for funcs in GROUPS.values() for func in funcs}


@dataclass
class MacroStep:
    function_name: str
    args: dict = field(default_factory=dict)


@dataclass
class Macro:
    name: str
    steps: list[MacroStep]
    created_from: str = ""


class MacroStore:
    def __init__(self, reserved_names: set[str]):
        self._reserved = reserved_names
        self._func_lookup = _build_func_lookup()
        self._macros: dict[str, Macro] = {}
        self._load()

    def _load(self):
        if not MACRO_FILE.exists():
            return
        try:
            data = json.loads(MACRO_FILE.read_text())
            for name, entry in data.items():
                steps = [MacroStep(**s) for s in entry["steps"]]
                self._macros[name] = Macro(name=name, steps=steps, created_from=entry.get("created_from", ""))
        except (json.JSONDecodeError, KeyError):
            pass

    def _save(self):
        MACRO_DIR.mkdir(parents=True, exist_ok=True)
        data = {}
        for name, macro in self._macros.items():
            data[name] = {
                "steps": [asdict(s) for s in macro.steps],
                "created_from": macro.created_from,
            }
        MACRO_FILE.write_text(json.dumps(data, indent=2))

    def save(self, name: str, prompt: str, steps: list[dict]) -> str:
        if name in self._reserved:
            return f"'{name}' conflicts with a built-in command"
        macro_steps = [MacroStep(function_name=s["function_name"], args=s.get("args", {})) for s in steps]
        for step in macro_steps:
            if step.function_name not in self._func_lookup:
                return f"Unknown function: {step.function_name}"
        self._macros[name] = Macro(name=name, steps=macro_steps, created_from=prompt)
        self._save()
        return ""

    def delete(self, name: str) -> bool:
        if name in self._macros:
            del self._macros[name]
            self._save()
            return True
        return False

    def list(self) -> list[Macro]:
        return list(self._macros.values())

    def get(self, name: str) -> Macro | None:
        return self._macros.get(name)

    def has(self, name: str) -> bool:
        return name in self._macros

    def execute(self, name: str) -> list[dict]:
        macro = self._macros[name]
        results = []
        for step in macro.steps:
            func = self._func_lookup[step.function_name]
            try:
                result = func(**step.args)
                results.append({"function": step.function_name, "result": result, "ok": True})
            except Exception as e:
                results.append({"function": step.function_name, "error": str(e), "ok": False})
        return results
