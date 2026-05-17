---
description: Setea compile mode en MANUAL. Claude NO compilará — pedirá al usuario que compile él (típico cuando tenés el editor de UE abierto y querés evitar conflictos de file lock).
---

# /tsumugi-modes:compile-manual

Seteá el modo de compilación a MANUAL corriendo el script `set-mode.py` con el tool Bash:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/set-mode.py" compile-mode manual
```

Mostrale al usuario la salida del script.

Recordale que:
- Desde el próximo tool call, si Claude intenta correr `UnrealBuildTool`, `RunUAT BuildCookRun`, `msbuild *.sln/*.uproject`, `Build.bat`, `cl.exe` o similar, el hook lo bloqueará e inyectará "pedile al usuario que compile él (cerrar editor primero)".
- Para que Claude vuelva a poder compilar: `/tsumugi-modes:compile-auto`.
- Para ver el estado actual: `/tsumugi-modes:status`.

Útil cuando:
- Tenés el editor de UE abierto y necesitás evitar que Claude rompa el build por file locks.
- Estás iterando rápido en BP y no querés que cada cambio de código dispare un rebuild.
