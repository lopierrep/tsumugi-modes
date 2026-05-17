---
description: Activa auto-commit. Claude podrá ejecutar git commit por su cuenta cuando la tarea lo justifique.
---

# /tsumugi-modes:auto-commit-on

Activá el modo auto-commit corriendo el script `set-mode.py` con el tool Bash:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/set-mode.py" auto-commit on
```

Mostrale al usuario la salida del script.

Recordale que:
- El nuevo modo aplica **desde el próximo tool call** (la regla la enforcement el hook PreToolUse leyendo el state file).
- Para volver atrás: `/tsumugi-modes:auto-commit-off`.
- Para ver el estado actual de todos los modos: `/tsumugi-modes:status`.
