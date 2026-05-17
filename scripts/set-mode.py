#!/usr/bin/env python3
"""tsumugi-modes: setea un modo en el state file y muestra el resultado.

Uso:
    python set-mode.py auto-commit on|off
    python set-mode.py compile-mode manual|auto
    python set-mode.py test-mode manual|auto
    python set-mode.py safe-mode block|allow
    python set-mode.py push-mode manual|auto
    python set-mode.py status
"""

import json
import sys
from pathlib import Path

STATE_FILE = Path.home() / ".claude" / "state" / "tsumugi-modes.json"

DEFAULT_STATE = {
    "auto_commit": False,
    "compile_mode": "manual",
    "test_mode": "manual",
    "safe_mode": "block",
    "push_mode": "manual",
}

VALID_VALUES = {
    "auto-commit": {"on": True, "off": False},
    "compile-mode": {"manual": "manual", "auto": "auto"},
    "test-mode": {"manual": "manual", "auto": "auto"},
    "safe-mode": {"block": "block", "allow": "allow"},
    "push-mode": {"manual": "manual", "auto": "auto"},
}


def load_state() -> dict:
    if not STATE_FILE.exists():
        return DEFAULT_STATE.copy()
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return {**DEFAULT_STATE, **json.load(f)}
    except (json.JSONDecodeError, OSError):
        return DEFAULT_STATE.copy()


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def usage() -> None:
    print("uso: set-mode.py <mode> <value>", file=sys.stderr)
    print("     set-mode.py status", file=sys.stderr)
    print("", file=sys.stderr)
    print("modos disponibles:", file=sys.stderr)
    for mode, values in VALID_VALUES.items():
        print(f"  {mode} {'|'.join(values.keys())}", file=sys.stderr)
    sys.exit(2)


def main() -> None:
    if len(sys.argv) < 2:
        usage()

    cmd = sys.argv[1]

    if cmd == "status":
        state = load_state()
        print("tsumugi-modes — estado actual:")
        print(f"  state file:   {STATE_FILE}")
        print(f"  auto_commit:  {state['auto_commit']}")
        print(f"  compile_mode: {state['compile_mode']}")
        print(f"  test_mode:    {state['test_mode']}")
        print(f"  safe_mode:    {state['safe_mode']}")
        print(f"  push_mode:    {state['push_mode']}")
        return

    if len(sys.argv) != 3:
        usage()

    if cmd not in VALID_VALUES:
        print(f"modo desconocido: {cmd}", file=sys.stderr)
        usage()

    value_str = sys.argv[2]
    if value_str not in VALID_VALUES[cmd]:
        print(f"valor inválido para {cmd}: {value_str}", file=sys.stderr)
        usage()

    state_key = cmd.replace("-", "_")
    state = load_state()
    state[state_key] = VALID_VALUES[cmd][value_str]
    save_state(state)

    print(f"tsumugi-modes — modo actualizado:")
    print(f"  {state_key} = {state[state_key]}")
    print(f"  state file: {STATE_FILE}")
    print(f"  el nuevo modo aplica desde el próximo tool call.")


if __name__ == "__main__":
    main()
