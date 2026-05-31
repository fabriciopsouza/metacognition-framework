# Incidente de vazamento de dados sensíveis — 2026-05-31 (PRIVADO · NÃO DISTRIBUIR)

> Registro **completo e com dados reais** para debug/estudo/auditoria do dono.
> A versão de distribuição é anonimizada; este arquivo é a chave para reverter.

## 1. Resumo executivo
O framework é, por princípio declarado (Princípio 12 / ADR-010 / ADR-020), **agnóstico de
domínio**. Porém, ao longo do dogfood em casos reais de cliente, identificadores de
**cliente / caso / repositório** vazaram para o núcleo agnóstico, ADRs, CHANGELOG, history e
hooks — num repositório que estava **PÚBLICO** (`github.com/fabriciopsouza/metacognition-framework`).

Total medido pelo linter estendido (tier sensível): **95 ocorrências em 17 arquivos**
(detalhe bruto: `_leak-scan-raw.txt`).

## 2. Contenção (feita em 2026-05-31)
- Repositório alterado de **PUBLIC → PRIVATE** via `gh repo edit ... --visibility private`.
  Verificado: `isPrivate: true`. `forkCount: 0`, `stars: 0` no momento (captação externa baixa).
- **Risco residual honesto:** o que esteve público pode ter sido cacheado/indexado
  (Google, archive.org, GH Archive). Privatizar impede acesso futuro, não desfaz o passado.
- **Ação recomendada de segurança:** rotacionar qualquer credencial que tenha encostado nestes
  dados. (Nenhum segredo/credencial foi encontrado nos arquivos varridos — só identificadores.)

## 3. Causa-raiz (confirmada por inspeção de código)
Já existia um linter de agnosticismo (`tools/check_core_agnostic.py`, ADR-020), mas ele
**não** pegou estes vazamentos por três defeitos compostos:
1. **Categoria errada na denylist.** `agnostic-denylist.txt` só listava *normas regulatórias*
   (ANVISA, GAMP, FDA…). "Vibra", "Natulab", "AIVI", `vibraenergia`, nomes de repo **não são
   normas** — o linter nunca os procurou.
2. **Escopo exclui `docs/`.** Justificativa válida p/ *normas como exemplo pedagógico*, mas
   **não** p/ identificadores de cliente. Resultado: ADRs/CHANGELOG/_intake nunca varridos.
3. **Falso negativo institucionalizado.** `AGENT-FRAMEWORK.md` afirmava "check_core_agnostic
   PASS" — verdadeiro, porque o linter não olhava para esses tokens.

**Causa-raiz sistêmica:** o loop de auto-melhoria (dogfood em caso real → ADR/CHANGELOG)
não tinha **disciplina de anonimização**. Cada ciclo de melhoria gravava o cliente no núcleo.

## 4. Correção aplicada
- **Tier SENSÍVEL** novo no linter: `tools/sensitive-denylist.txt` + escopo **repo inteiro**
  (exceto `.git/`, `docs/_private/`, denylists, binários). Sentinela `lint-sensitive:allow`.
- **Anonimização** da superfície de distribuição (mantendo a LIÇÃO; ver token-map §6).
- **De-hardcode** das seeds de allowlist (orgs de cliente saem do bootstrap versionado).
- **Wiring** do linter como gate de fechamento.
- **AUTOR ≠ CLIENTE:** nome do mantenedor permanece em LICENSE/NOTICE/git (atribuição legal).

## 5. Decisões do dono (2026-05-31)
1. **Profundidade:** "Tudo — anonimizar + remover scratch." (genericizar núcleo; anonimizar
   ADRs/CHANGELOG/history; mover `docs/_intake/` p/ cá.)
2. **Identidade autor:** "Manter autoria legal; de-hardcode allowlist." (preserva nome do autor
   em LICENSE/NOTICE; remove orgs-cliente vibraenergia/natulab das seeds versionadas.)
3. **Mecanismo:** "Limpar + estender linter + wirar gate" + criar este cofre privado;
   tornar repo privado AGORA; distribuir versão limpa depois. **Histórico não pode ser perdido.**

## 6. TOKEN-MAP (real → genérico) — chave de reversão
Use para ler qualquer doc anonimizado da distribuição e recuperar o referente real.

| Real (sensível) | Substituto na distribuição |
|---|---|
| AIVI (caso/indicador) | "incidente de roteamento" · "o caso real" · "caso regulado externo" |
| Vibra · "distribuição de combustíveis Vibra" | "cliente regulado" · "setor regulado externo" |
| Natulab | "outro cliente" (ou removido) |
| BABET · Betim | "uma base" (removido o nome próprio) |
| VIACOMP | (removido) |
| repo `LIMITES-BATENTES-RECALC` | "repo privado do mantenedor (caso real)" |
| repo `test-aivi-isolated` | "repo de teste isolado (caso real)" |
| branch `claude/discovery-aivi-metodo-2026-05-27` | (nome de branch removido) |
| commits `74bd613` `039fd6d` `10ecf0…` | (hashes removidos) |
| orgs allowlist `vibraenergia` `natulab` | placeholder `<seu-usuario-ou-org>` (de-hardcode) |
| `exemplos/aivi-indicator-analyst`, `roles/aivi-indicator-analyst`, `aivi-recalculo-limites`, `v1.13.0-aivi-method-fixes` | nomes de exemplo/spec genéricos ou removidos |
| memory slug `framework-gaps-from-aivi-case-2026-05-27` | `framework-gaps-from-case` (slug opaco) |
| "ANP 884" / "combustíveis" como dica setorial | "norma setorial" / "setor regulado" |

## 7. Inventário completo
Ver `_leak-scan-raw.txt` (95 linhas `LEAK [sensivel] <arquivo>:<linha>: '<token>' -> <snippet>`).
Distribuição por arquivo: CHANGELOG.md (31), ADR-009 (16), history.md (13), ADR-010 (10),
ADR-012 (7), ADR-006 (5), bootstrap.ps1/sh (2+2), route-gate.ps1 (1), ensure-global-wiring.ps1 (1),
guia/SETUP.md (1), ADR-027 (1), ADR-028 (1), metacognition-core (1), CLAUDE.md (1), AGENTS.md (1),
AGENT-FRAMEWORK.md (1).

## 8. Verificação de fechamento
`python tools/check_core_agnostic.py` deve retornar **PASS** após a limpeza (tier sensível =
zero vazamento na árvore distribuível; `docs/_private/` é excluído por escopo).
