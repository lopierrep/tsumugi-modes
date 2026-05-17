---
description: Activa test-mode AUTO. Claude podrá correr test runners (pytest, npm test, cargo test, etc.) por su cuenta.
---

# /tsumugi-modes:test-auto

Seteá test-mode a AUTO corriendo el script `set-mode.py` con el tool Bash:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/set-mode.py" test-mode auto
```

Mostrale al usuario la salida del script.

Recordale que:
- Desde el próximo tool call, Claude podrá correr `pytest`, `npm test`, `pnpm test`, `yarn test`, `bun test`, `cargo test`, `dotnet test`, `go test`, `mvn test`, `gradle test`, `vitest`, `jest`, `phpunit`, `rspec`, `mocha`, `playwright test`, `cypress run`, `python -m unittest`, etc.
- Para volver a manual: `/tsumugi-modes:test-manual`.
- Para ver el estado actual: `/tsumugi-modes:status`.

Útil cuando:
- Estás haciendo TDD y querés que Claude valide cambios automáticamente con el test suite.
- El test suite es rápido y querés feedback inmediato.
