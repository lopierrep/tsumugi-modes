#!/usr/bin/env python3
"""tsumugi-modes: PreToolUse hook que enforcement los modos sobre tool calls Bash.

Recibe el payload del tool call por stdin (JSON). Decide allow/block según el
estado en ~/.claude/state/tsumugi-modes.json. Imprime resultado a stdout en
formato JSON si bloquea, exits clean si permite.

Modos soportados:
- auto_commit (bool): off → bloquea `git commit` (deja pasar `git commit --amend`)
- compile_mode (manual/auto): manual → bloquea comandos de build de UE5
- test_mode (manual/auto): manual → bloquea test runners (pytest, npm test, cargo test, ...)
- safe_mode (block/allow): block → bloquea comandos destructivos (rm -rf, git push --force,
  git reset --hard, git clean -fd, git branch -D)
- push_mode (manual/auto): manual → bloquea `git push` (--dry-run permitido)
"""

import json
import re
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

# ---------- regex patterns ----------

GIT_COMMIT_RE = re.compile(
    r"\bgit\s+(?:-c\s+\S+\s+)*commit\b",
    re.IGNORECASE,
)

GIT_PUSH_RE = re.compile(
    r"\bgit\s+(?:-c\s+\S+\s+)*push\b",
    re.IGNORECASE,
)

UE_BUILD_PATTERNS = [
    r"\bUnrealBuildTool(?:\.exe)?\b",
    r"\bRunUAT(?:\.bat|\.sh|\.cmd)?\b.*\bBuildCookRun\b",
    r"\bBuild\.(?:bat|sh|cmd)\b",
    r"\bBuildScript\.(?:bat|sh|cmd)\b",
    r"\bmsbuild\b.*\.(?:sln|uproject)",
    r"\bcl\.exe\b",
    r"\bdotnet\s+.*UnrealBuildTool",
]

TEST_RUNNER_PATTERNS = [
    # Generic test runners called directly
    r"\bpytest\b",
    r"\bvitest\b",
    r"\bjest\b",
    r"\bphpunit\b",
    r"\brspec\b",
    r"\bmocha\b",
    r"\bplaywright\s+test\b",
    r"\bcypress\s+(?:run|open)\b",
    # Package-manager test scripts
    r"\b(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?test\b",
    # Language-specific test runners
    r"\bcargo\s+(?:nextest\s+)?test\b",
    r"\bdotnet\s+test\b",
    r"\bgo\s+test\b",
    r"\bmvn\s+test\b",
    r"\bgradle(?:w)?\s+test\b",
    r"\bswift\s+test\b",
    # Python unittest
    r"\bpython\s+-m\s+unittest\b",
]

# Destructive command patterns (safe-mode = block)
RM_RF_RE = re.compile(
    r"\brm\s+(?:-[a-zA-Z]*[rRfF][a-zA-Z]*\s+|--force\s+|--recursive\s+)",
)
# git push --force or -f (but NOT --force-with-lease which is safer)
GIT_PUSH_FORCE_RE = re.compile(
    r"\bgit\s+(?:[\w\-]+\s+)*push\s+(?:.*?\s)?(?:--force(?!-with-lease)|-f(?!-)|--force\b)",
    re.IGNORECASE,
)
GIT_RESET_HARD_RE = re.compile(r"\bgit\s+reset\s+--hard\b", re.IGNORECASE)
GIT_CLEAN_FORCE_RE = re.compile(r"\bgit\s+clean\s+-[a-zA-Z]*f", re.IGNORECASE)
GIT_BRANCH_FORCE_DEL_RE = re.compile(r"\bgit\s+branch\s+-D\b")
GIT_CHECKOUT_FORCE_RE = re.compile(r"\bgit\s+checkout\s+.*--force\b", re.IGNORECASE)

# ---------- helpers ----------


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


def is_git_push(cmd: str) -> bool:
    if not GIT_PUSH_RE.search(cmd):
        return False
    # --dry-run se permite (no-op informativo)
    if re.search(r"--dry-run\b", cmd):
        return False
    return True


def is_ue_build(cmd: str) -> bool:
    return any(re.search(p, cmd, re.IGNORECASE) for p in UE_BUILD_PATTERNS)


def is_test_runner(cmd: str) -> bool:
    return any(re.search(p, cmd, re.IGNORECASE) for p in TEST_RUNNER_PATTERNS)


def detect_destructive(cmd: str) -> str | None:
    """Return a description of the destructive pattern matched, or None."""
    if RM_RF_RE.search(cmd):
        return "rm con flags recursive+force"
    if GIT_PUSH_FORCE_RE.search(cmd):
        return "git push --force (no force-with-lease)"
    if GIT_RESET_HARD_RE.search(cmd):
        return "git reset --hard"
    if GIT_CLEAN_FORCE_RE.search(cmd):
        return "git clean con -f"
    if GIT_BRANCH_FORCE_DEL_RE.search(cmd):
        return "git branch -D (force delete)"
    if GIT_CHECKOUT_FORCE_RE.search(cmd):
        return "git checkout --force"
    return None


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

    # --- safe_mode: bloquear destructive (chequear PRIMERO, antes que otros modos) ---
    if state.get("safe_mode", "block") == "block":
        destructive = detect_destructive(cmd)
        if destructive:
            block(
                f"tsumugi-modes: safe_mode está en BLOCK. Comando detectado como destructivo: "
                f"{destructive}. NO ejecutes. Si la intención es legítima, pedile al usuario "
                f"que corra /tsumugi-modes:safe-off para permitir destructive temporalmente. "
                f"Considerá alternativas más seguras (e.g., --force-with-lease en lugar de --force, "
                f"git stash en lugar de reset --hard, mover a un branch nuevo en lugar de force-delete)."
            )

    # --- auto_commit ---
    if is_git_commit(cmd) and not state.get("auto_commit", False):
        block(
            "tsumugi-modes: auto-commit está OFF. "
            "NO commitees ahora. Mostrale al usuario el diff con `git diff --staged` "
            "y proponé un mensaje de commit, pero dejá que el usuario commitee. "
            "Si querés que Claude pueda commitear solo, el usuario debe correr "
            "/tsumugi-modes:auto-commit-on."
        )

    # --- push_mode ---
    if is_git_push(cmd) and state.get("push_mode", "manual") == "manual":
        block(
            "tsumugi-modes: push_mode está en MANUAL. "
            "NO pushees ahora. Mostrale al usuario lo que ibas a pushear y dejá que decida él. "
            "Si querés que Claude pueda pushear, el usuario debe correr "
            "/tsumugi-modes:push-auto."
        )

    # --- compile_mode ---
    if is_ue_build(cmd) and state.get("compile_mode", "manual") == "manual":
        block(
            "tsumugi-modes: compile_mode está en MANUAL. "
            "NO compiles ahora. Pedile al usuario que compile él "
            "(asegurate de que cerró el editor de UE antes para evitar conflictos de lock). "
            "Si querés que Claude pueda compilar, el usuario debe correr "
            "/tsumugi-modes:compile-auto."
        )

    # --- test_mode ---
    if is_test_runner(cmd) and state.get("test_mode", "manual") == "manual":
        block(
            "tsumugi-modes: test_mode está en MANUAL. "
            "NO corras tests ahora. Si necesitás ver los resultados de un test, pedile al usuario "
            "que los corra él y te pegue el output. "
            "Si querés que Claude pueda correr tests autónomamente, el usuario debe correr "
            "/tsumugi-modes:test-auto."
        )

    # permitido
    sys.exit(0)


if __name__ == "__main__":
    main()
