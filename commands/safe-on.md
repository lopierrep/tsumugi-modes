---
description: Activa safe-mode (BLOCK). Bloquea comandos destructivos comunes (rm -rf, git push --force, git reset --hard, git clean -fd, git branch -D, git checkout --force).
---

# /tsumugi-modes:safe-on

Activá safe-mode (BLOCK) corriendo el script `set-mode.py` con el tool Bash:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/set-mode.py" safe-mode block
```

Mostrale al usuario la salida del script.

Recordale qué bloquea safe-mode cuando está ON:

| Comando bloqueado | Por qué |
|---|---|
| `rm -rf <path>` | Imposible de revertir si pegás mal el path |
| `git push --force` / `-f` | Reescribe historia remota; pisa trabajo de otros |
| `git reset --hard` | Pierde cambios uncomitted |
| `git clean -fd` | Borra archivos untracked sin confirmación |
| `git branch -D <name>` | Force-delete un branch (puede tener commits no merged) |
| `git checkout --force` | Pisa cambios locales |

Notas:
- `git push --force-with-lease` se permite — es la alternativa segura a `--force`.
- Para volver a permitir destructive temporalmente: `/tsumugi-modes:safe-off`.
- Para ver el estado actual: `/tsumugi-modes:status`.

Este es el default. Recomendado mantenerlo ON salvo que sepas que vas a necesitar destructive (e.g., rebase con force push intencional).
