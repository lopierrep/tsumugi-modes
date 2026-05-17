---
description: Activa push-mode AUTO. Claude podrá ejecutar `git push` por su cuenta cuando lo justifique.
---

# /tsumugi-modes:push-auto

Activá push-mode (AUTO) corriendo el script `set-mode.py` con el tool Bash:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/set-mode.py" push-mode auto
```

Mostrale al usuario la salida del script.

Recordale que:
- Desde el próximo tool call, Claude podrá ejecutar `git push`, `git push origin <branch>`, etc.
- `git push --force` sigue bloqueado por **safe-mode** (independiente del push-mode). Si querés force-push, usá `--force-with-lease` o desactivá safe-mode temporalmente.
- Para volver a manual: `/tsumugi-modes:push-manual`.
- Para ver el estado actual: `/tsumugi-modes:status`.

Útil cuando:
- Estás en un loop CI/CD que quiere autocommits + autopushes.
- Tenés un branch personal donde no importa pushear seguido.
- Combinás con `auto-commit-on` para flow autónomo total.
