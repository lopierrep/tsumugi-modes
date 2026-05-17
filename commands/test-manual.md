---
description: Setea test-mode en MANUAL. Claude NO correrá tests — los corre el usuario y le pega el output.
---

# /tsumugi-modes:test-manual

Seteá test-mode a MANUAL corriendo el script `set-mode.py` con el tool Bash:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/set-mode.py" test-mode manual
```

Mostrale al usuario la salida del script.

Recordale que:
- Desde el próximo tool call, si Claude intenta `pytest`, `npm test`, `cargo test`, `dotnet test`, `go test`, `vitest`, `jest`, etc., el hook bloquea e inyecta "pedile al usuario que corra los tests él y te pegue el output".
- Para que Claude vuelva a correr tests: `/tsumugi-modes:test-auto`.

Útil cuando:
- El test suite es lento (>30s) y no querés que cada cambio dispare un run.
- Tenés el test runner corriendo en watch mode aparte (vitest --watch, pytest-watch, etc.) y querés evitar conflictos.
- Estás iterando rápido y los tests son ruido temporalmente.
