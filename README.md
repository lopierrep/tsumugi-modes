# tsumugi-modes

Plugin de la familia [tsumugi](https://github.com/lopierrep/tsumugi) que provee **modos operacionales togglables** durante sesiones de Claude Code.

El problema que resuelve: Claude se acuerda de cosas que dijiste hace 20 turns atrás y se queda pegado a esa decisión aunque las condiciones cambien ("antes me dijiste que vos compilás, así que no compilo"). Este plugin elimina ese problema poniendo el estado **afuera** del contexto de la conversación: un archivo JSON + un hook PreToolUse que enforcement la decisión actual antes de cada tool call. La memoria de Claude se vuelve irrelevante.

## Modos incluidos

| Modo | Valores | Slash commands |
|---|---|---|
| `auto_commit` | `true` / `false` | `/tsumugi-modes:auto-commit-on`, `/tsumugi-modes:auto-commit-off` |
| `compile_mode` | `"manual"` / `"auto"` | `/tsumugi-modes:compile-manual`, `/tsumugi-modes:compile-auto` |

Plus `/tsumugi-modes:status` para ver el estado actual.

### Auto-commit

- `auto-commit-on`: Claude puede ejecutar `git commit` solo cuando lo justifique la tarea.
- `auto-commit-off` (default): si Claude intenta `git commit`, el hook lo bloquea e inyecta "mostrale el diff al usuario y proponé el mensaje, NO commitees".

### Compile mode

- `compile-auto`: Claude puede ejecutar comandos de build (UnrealBuildTool, msbuild, RunUAT BuildCookRun, etc.) por su cuenta.
- `compile-manual` (default): si Claude intenta compilar, el hook lo bloquea e inyecta "pedile al usuario que compile él (cerrar editor de UE primero)".

## Cómo funciona

```
Conversación → Claude decide ejecutar Bash → PreToolUse hook lee state file
                                              ↓
                                              ├─ permite si el comando matchea el modo actual
                                              └─ bloquea + inyecta mensaje si no
```

**Estado** en `~/.claude/state/tsumugi-modes.json`:
```json
{
  "auto_commit": false,
  "compile_mode": "manual"
}
```

Los slash commands escriben este archivo. El hook lo lee antes de cada Bash. Cambiar de modo es instantáneo desde el próximo tool call — Claude no necesita "acordarse" porque la regla viene de afuera.

## Instalación

```shell
# Vía el orquestador tsumugi
/tsumugi:skills-install tsumugi-modes

# O directo
/plugin marketplace add lopierrep/tsumugi
/plugin install tsumugi-modes@tsumugi
```

Tras instalar, los modos default son los más conservadores: `auto_commit=false`, `compile_mode=manual`. Cambialos con los slash commands cuando los necesites.

## Detección de comandos

El hook detecta:

**Git commit** (regex case-insensitive):
- `git commit ...`
- `git -c X.Y=Z commit ...`
- NO bloquea `git commit --amend` (asumido que es intencional)

**UE build commands** (regex case-insensitive, cualquiera matchea):
- `UnrealBuildTool[.exe]`
- `RunUAT[.bat|.sh|.cmd] BuildCookRun ...`
- `Build.bat`, `BuildScript.bat` (variantes)
- `msbuild ... .sln` / `msbuild ... .uproject`
- `cl.exe`
- `dotnet ... UnrealBuildTool`

Si encontrás un comando de build que NO se detecta, agregalo a `scripts/mode-gate.py` (lista `UE_BUILD_PATTERNS`) y abrí PR.

## Cómo extender con modos nuevos

1. Agregá la entrada al state JSON con un default.
2. Editá `scripts/set-mode.py` para aceptar el nuevo mode + value validation.
3. Editá `scripts/mode-gate.py` con la detección de comandos a bloquear.
4. Creá los slash commands en `commands/`.
5. Documentá en este README.

## Licencia

MIT.
