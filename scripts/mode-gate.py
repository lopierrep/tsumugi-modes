#!/usr/bin/env python3
"""tsumugi-modes: PreToolUse hook que enforcement los modos sobre tool calls Bash.

Recibe el payload del tool call por stdin (JSON). Decide allow/block según el
estado en ~/.claude/state/tsumugi-modes.json. Imprime resultado a stdout en
formato JSON si bloquea, exits clean si permite.

Formato del payload (PreToolUse hook):
{
  "tool_name": "Bash",
  "tool_input": {"command": "git commit -m '...'"}
}

Formato de respuesta para bloquear:
{
  "decision": "block",
  "reason": "explicación que se le inyecta al modelo"
}
"""

import json
import re
import sys
from pathlib import Path

STATE_FILE = Path.home() / ".claude" / "state" / "tsumugi-modes.json"

DEFAULT_STATE = {
    "auto_commit": False,
    "compile_mode": "manual",
}

# Detecta `git commit` (no `git commit --amend`, no `git log` que tenga "commit" en output)
GIT_COMMIT_RE = re.compile(
    r"\bgit\s+(?:-c\s+\S+\s+)*commit\b",
    re.IGNORECASE,
)

# Detecta comandos de build de UE5 (cualquiera de estos patterns matchea = es build)
UE_BUILD_PATTERNS = [
    r"\bUnrealBuildTool(?:\.exe)?\b",
    r"\bRunUAT(?:\.bat|\.sh|\.cmd)?\b.*\bBuildCookRun\b",
    r"\bBuild\.(?:bat|sh|cmd)\b",
    r"\bBuildScript\.(?:bat|sh|cmd)\b",
    r"\bmsbuild\b.*\.(?:sln|uproject)",
    r"\bcl\.exe\b",
    r"\bdotnet\s+.*UnrealBuildTool",
]


def load_state() -> dict:
    if not STATE_FILE.exists():
        return DEFAULT_STATE.copy()
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return {**DEFAULT_STATE, **json.load(f)}
    except (json.JSONDecodeError, OSError):
        return DEFAULT_STATE.copy()


def is_git_commit(cmd: str) -> bool:
    if not GIT_COMMIT_RE.search(cmd):
        return False
    # --amend se permite (asumido intencional)
    if re.search(r"--amend\b", cmd):
        return False
    return True


def is_ue_build(cmd: str) -> bool:
    return any(re.search(p, cmd, re.IGNORECASE) for p in UE_BUILD_PATTERNS)


def block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        # input malformado, dejá pasar
        sys.exit(0)

    if payload.get("tool_name") != "Bash":
        sys.exit(0)

    cmd = payload.get("tool_input", {}).get("command", "")
    if not cmd:
        sys.exit(0)

    state = load_state()

    if is_git_commit(cmd) and not state.get("auto_commit", False):
        block(
            "tsumugi-modes: auto-commit está OFF. "
            "NO commitees ahora. Mostrale al usuario el diff con `git diff --staged` "
            "y proponé un mensaje de commit, pero dejá que el usuario commitee. "
            "Si querés que Claude pueda commitear solo, el usuario debe correr "
            "/tsumugi-modes:auto-commit-on."
        )

    if is_ue_build(cmd) and state.get("compile_mode", "manual") == "manual":
        block(
            "tsumugi-modes: compile_mode está en MANUAL. "
            "NO compiles ahora. Pedile al usuario que compile él "
            "(asegurate de que cerró el editor de UE antes para evitar conflictos de lock). "
            "Si querés que Claude pueda compilar, el usuario debe correr "
            "/tsumugi-modes:compile-auto."
        )

    # permitido
    sys.exit(0)


if __name__ == "__main__":
    main()
