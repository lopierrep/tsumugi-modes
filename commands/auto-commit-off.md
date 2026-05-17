---
description: Desactiva auto-commit. Claude propondrá mensajes de commit pero no ejecutará `git commit`.
---

# /tsumugi-modes:auto-commit-off

Desactivá el modo auto-commit corriendo el script `set-mode.py` con el tool Bash:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/set-mode.py" auto-commit off
```

Mostrale al usuario la salida del script.

Recordale que:
- Desde el próximo tool call, si Claude intenta `git commit ...`, el hook PreToolUse lo bloqueará e inyectará "mostrá el diff y proponé el mensaje, pero NO commitees".
- `git commit --amend` se permite igual (asumido intencional).
- Para reactivar: `/tsumugi-modes:auto-commit-on`.
