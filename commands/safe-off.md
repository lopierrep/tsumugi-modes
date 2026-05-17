---
description: Desactiva safe-mode (ALLOW). Claude podrá ejecutar comandos destructivos sin gate (rm -rf, git push --force, git reset --hard, etc.). Úsalo solo cuando lo necesites — el default es safe-on.
---

# /tsumugi-modes:safe-off

Desactivá safe-mode (ALLOW) corriendo el script `set-mode.py` con el tool Bash:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/set-mode.py" safe-mode allow
```

Mostrale al usuario la salida del script.

**Advertencia**: con safe-mode OFF, Claude puede ejecutar:
- `rm -rf <path>`
- `git push --force`
- `git reset --hard`
- `git clean -fd`
- `git branch -D`
- `git checkout --force`

Recordale al usuario:
- Después de la operación destructiva, **volvé a activar safe-mode**: `/tsumugi-modes:safe-on`.
- Si solo necesitás force-push, considerá usar `git push --force-with-lease` que NO requiere safe-off (es la alternativa segura).
- Para ver el estado actual: `/tsumugi-modes:status`.

Casos legítimos donde safe-off está justificado:
- Limpiar un working directory que está hecho pelota (`git clean -fd` después de bisección).
- Rebase intencional + force push a un branch propio sin colaboradores.
- Reset hard a un commit anterior cuando los cambios están perdidos pero no importan.
