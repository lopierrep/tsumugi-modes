# tsumugi-modes

Plugin de la familia [tsumugi](https://github.com/lopierrep/tsumugi) que provee **modos operacionales togglables** durante sesiones de Claude Code.

El problema que resuelve: Claude se acuerda de cosas que dijiste hace 20 turns atrás y se queda pegado a esa decisión aunque las condiciones cambien ("antes me dijiste que vos compilás, así que no compilo"). Este plugin elimina ese problema poniendo el estado **afuera** del contexto de la conversación: un archivo JSON + un hook PreToolUse que enforcement la decisión actual antes de cada tool call. La memoria de Claude se vuelve irrelevante.

## Modos incluidos

| Modo | Valores | Default | Slash commands |
|---|---|---|---|
| `auto_commit` | `true` / `false` | `false` | `/tsumugi-modes:auto-commit-on`, `/tsumugi-modes:auto-commit-off` |
| `compile_mode` | `"manual"` / `"auto"` | `"manual"` | `/tsumugi-modes:compile-manual`, `/tsumugi-modes:compile-auto` |
| `test_mode` | `"manual"` / `"auto"` | `"manual"` | `/tsumugi-modes:test-manual`, `/tsumugi-modes:test-auto` |
| `safe_mode` | `"block"` / `"allow"` | `"block"` | `/tsumugi-modes:safe-on`, `/tsumugi-modes:safe-off` |
| `push_mode` | `"manual"` / `"auto"` | `"manual"` | `/tsumugi-modes:push-manual`, `/tsumugi-modes:push-auto` |

Plus `/tsumugi-modes:status` para ver el estado actual de todos los modos.

### Detalle por modo

**auto-commit** (`auto_commit: bool`)
- ON: Claude puede ejecutar `git commit` por su cuenta cuando lo justifique la tarea.
- OFF (default): bloquea `git commit`, Claude propone el mensaje y deja que vos commitees.
- `git commit --amend` se permite siempre.

**compile-mode** (`compile_mode: manual|auto`)
- AUTO: Claude puede ejecutar comandos de build de UE.
- MANUAL (default): bloquea `UnrealBuildTool`, `RunUAT BuildCookRun`, `msbuild *.sln/*.uproject`, `Build.bat`, `BuildScript.bat`, `cl.exe`, `dotnet ... UnrealBuildTool`. Pide al usuario que compile él.

**test-mode** (`test_mode: manual|auto`)
- AUTO: Claude puede correr test runners.
- MANUAL (default): bloquea `pytest`, `vitest`, `jest`, `phpunit`, `rspec`, `mocha`, `playwright test`, `cypress run`, `npm/pnpm/yarn/bun (run) test`, `cargo (nextest) test`, `dotnet test`, `go test`, `mvn test`, `gradle test`, `swift test`, `python -m unittest`.

**safe-mode** (`safe_mode: block|allow`)
- BLOCK (default): bloquea comandos destructivos comunes — `rm -rf`, `git push --force/-f` (no `--force-with-lease`), `git reset --hard`, `git clean -fd`, `git branch -D`, `git checkout --force`.
- ALLOW: deja pasar todo. Útil para operaciones destructivas intencionales.

**push-mode** (`push_mode: manual|auto`)
- AUTO: Claude puede ejecutar `git push`.
- MANUAL (default): bloquea `git push`, propone el comando. `git push --dry-run` se permite siempre.
- Ortogonal a safe-mode: `--force` lo bloquea safe-mode aunque push-mode esté en auto.

## Cómo funciona

```
Conversación → Claude decide ejecutar Bash → PreToolUse hook lee state file
                                              ↓
                                              ├─ permite si el comando es OK según los modos actuales
                                              └─ bloquea + inyecta mensaje si no
```

**Estado** en `~/.claude/state/tsumugi-modes.json`:
```json
{
  "auto_commit": false,
  "compile_mode": "manual",
  "test_mode": "manual",
  "safe_mode": "block",
  "push_mode": "manual"
}
```

Los slash commands escriben este archivo. El hook lo lee antes de cada Bash. Cambiar de modo es instantáneo desde el próximo tool call — Claude no necesita "acordarse" porque la regla viene de afuera.

## Orden de evaluación del hook

Si un comando matchea múltiples modos, el hook evalúa en este orden y bloquea con el **primer** modo que se opone:

1. `safe_mode` (destructive check) — se evalúa primero porque es el más severo.
2. `auto_commit` (git commit detection)
3. `push_mode` (git push detection)
4. `compile_mode` (UE build detection)
5. `test_mode` (test runner detection)

Ejemplo: si corrés `git push --force` con `safe_mode=block` Y `push_mode=manual`, el hook bloquea por safe-mode (más específico al peligro). Si lo corrés con `safe_mode=allow` y `push_mode=manual`, bloquea por push-mode.

## Instalación

```shell
# Vía el orquestador tsumugi
/tsumugi:skills-install tsumugi-modes

# O directo
/plugin marketplace add lopierrep/tsumugi
/plugin install tsumugi-modes@tsumugi
```

Tras instalar, los modos default son los más conservadores. Cambialos con los slash commands cuando los necesites.

## Cómo extender con modos nuevos

1. Agregá la entrada al state JSON con un default en `DEFAULT_STATE` (set-mode.py + mode-gate.py).
2. Agregá la entrada al diccionario `VALID_VALUES` en `set-mode.py`.
3. Agregá la detección + logic de bloqueo en `mode-gate.py`.
4. Agregá los slash commands en `commands/` (uno por valor).
5. Documentá en este README + actualizá la tabla de la `status.md`.

## Licencia

MIT.
