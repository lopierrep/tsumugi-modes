---
description: Setea push-mode en MANUAL. Claude NO ejecutará `git push` — propondrá el comando para que el usuario lo corra.
---

# /tsumugi-modes:push-manual

Seteá push-mode a MANUAL corriendo el script `set-mode.py` con el tool Bash:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/set-mode.py" push-mode manual
```

Mostrale al usuario la salida del script.

Recordale que:
- Desde el próximo tool call, si Claude intenta `git push`, el hook lo bloquea e inyecta "mostrale al usuario lo que ibas a pushear y dejá que decida él".
- `git push --dry-run` sí se permite (es informativo, no muta nada remoto).
- Para que Claude vuelva a poder pushear: `/tsumugi-modes:push-auto`.

Útil cuando:
- Querés revisar manualmente cada commit antes de que llegue al remote.
- Estás trabajando en un branch shared y no querés race conditions.
- Estás en la fase de "ya commiteé pero todavía estoy iterando, no quiero pushear todavía".
