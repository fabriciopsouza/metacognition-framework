# .claude/skills/ — espelho opcional (auto-descoberta nativa)

O Claude Code auto-descobre skills aqui. Nossa FONTE ÚNICA das skills é `_shared/`
e `.agent/skills/` (cross-tool). Duas opções:

- **Quick:** deixe vazio. O CLAUDE.md aponta para `_shared/`/`.agent/skills/`; o
  Claude lê o SKILL.md quando instruído (não auto-dispara, mas funciona).
- **Native (auto-trigger):** copie/symlink as pastas de skill para cá. Mantenha
  `_shared/` como verdade; este diretório é só o ponto de descoberta.
  (Evite editar nos dois lugares — isso quebra o single source of truth.)
