---
description: Setea compile mode en AUTO. Claude podrá ejecutar comandos de build (UnrealBuildTool, msbuild, etc.) por su cuenta.
---

# /tsumugi-modes:compile-auto

Seteá el modo de compilación a AUTO corriendo el script `set-mode.py` con el tool Bash:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/set-mode.py" compile-mode auto
```

Mostrale al usuario la salida del script.

Recordale que:
- Desde el próximo tool call, Claude podrá ejecutar comandos de build de UE sin intervención.
- Si tenés el editor de UE abierto, **cerralo antes** o vas a tener conflictos de file lock durante el build.
- Para volver a manual: `/tsumugi-modes:compile-manual`.
