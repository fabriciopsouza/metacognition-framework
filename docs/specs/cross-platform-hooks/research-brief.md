---
papel: discovery
sub_modo: pesquisa-cascata
pergunta_principal: "Qual a estratégia canônica para portar a cadeia de hooks do framework (hoje PowerShell/.ps1) para ambientes não-Windows (bash/.sh), e quais acoplamentos bloqueiam um porte direto?"
rodadas: 2
data: 2026-05-27
status: revisado
---

# Research Brief — Porte cross-platform da cadeia de hooks (D4)

> Output do sub-modo `pesquisa-cascata` (G1 / ADR-007). Gerado como **field-validation**
> do eval seção I (ver `_meta/eval-results-papeis.md` §I). Tema: backlog D4
> (`docs/_backlog/gaps-otimizacao.md:84-87`), **trigger-gated** — este brief de-risca
> a decisão ANTES do gatilho, mas NÃO autoriza o ADR (ver §7).

## 1. Pergunta principal

Qual a estratégia canônica para portar a cadeia de hooks do framework (hoje PowerShell/`.ps1`,
Windows-only) para ambientes não-Windows (bash/`.sh`), e quais acoplamentos bloqueiam um
porte direto?

## 2. Decomposição (sub-perguntas multi-hop)

1. **SQ1 — Inventário:** quais hooks existem versionados e qual a função de cada um no ciclo boot/sync/inject/exec-mode?
2. **SQ2 — Hazards de portabilidade:** quais construções PowerShell/Windows-específicas cada hook usa que não portam direto para bash?
3. **SQ3 — Wiring/instalação:** como os hooks são registrados (`settings.json`) e instalados (`bootstrap`)? O mecanismo é OS-aware ou hard-coded para `.ps1`?
4. **SQ4 — Blockers (síntese):** quais acoplamentos bloqueiam o porte direto? (derivado de SQ1-3 na reflexão)
5. **SQ5 — Ramificação (round 2):** o repo registra `pwsh` (PowerShell Core) como ponte cross-platform? E o comportamento do host quando o comando de hook falha em SO sem `powershell.exe`?

## 3. Fontes consultadas

| Fonte | Tipo | Autoridade | Relevância | Acessada via |
|---|---|---|---|---|
| `.claude/settings.json` | config (registro de hooks) | alta | direta | explorer (SQ1, SQ3) |
| `.claude/hooks/sync-global.ps1` | código (hook) | alta | direta | explorer (SQ1, SQ2) |
| `.claude/hooks/check-execution-mode.ps1` | código (hook) | alta | direta | explorer (SQ1, SQ2) |
| `.claude/hooks/inject-start-session.ps1` | código (hook) | alta | direta | explorer (SQ1, SQ2) |
| `.claude/hooks/inject-start-session-global.template.ps1` | código (template hook global) | alta | direta | explorer (SQ1, SQ2) |
| `bootstrap.ps1` | código (instalador Windows) | alta | direta | explorer (SQ1-3) |
| `bootstrap.sh` | código (instalador macOS/Linux, parcial) | alta | direta | explorer (SQ3, SQ5) |
| `docs/_backlog/gaps-otimizacao.md` (D4) | backlog | alta | direta | explorer (SQ3, SQ5) |
| `docs/adr/004,005,006` | ADR (constraints registrados) | alta | direta | explorer (SQ3, SQ5) |

> Todas as fontes são **internas ao repo** (autoridade alta para "o que o framework faz hoje").
> Nenhuma fonte externa foi consultada (explorer é repo/filesystem read-only) — ver §6 (fonte fraca).

## 4. Achados classificados

### CONFIRMADO (fonte direta no repo)

- **A cadeia tem 4 hooks versionados + 1 instalador**, todos no evento `SessionStart`, registrados em ordem: `sync-global.ps1` → `check-execution-mode.ps1` → `inject-start-session.ps1`; o `inject-start-session-global.template.ps1` é espelhado por `sync-global` e registrado pelo `bootstrap.ps1` no `~/.claude/settings.json`. — `settings.json:4-35`, `sync-global.ps1:101-119`, `bootstrap.ps1:147-206`.
- **O registro é hard-coded para PowerShell.** As 3 entradas de `settings.json` invocam `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".claude\hooks\*.ps1"` — sem condicional de SO, sem wrapper agnóstico, com separador `\` (Windows-only). — `settings.json:4-35`.
- **O lock-in já é dívida CONHECIDA e registrada.** ADR-004:84, ADR-005:122, ADR-006:155 declaram "PowerShell-only / só funciona no Windows hoje"; backlog **D4** rastreia o porte `.sh`, **trigger-gated** ("mantenedor usando Linux/macOS regularmente — hoje só Windows"). — `docs/_backlog/gaps-otimizacao.md:84-87`.
- **O esqueleto cross-platform já está parcialmente iniciado.** Existe `bootstrap.sh` cobrindo git/gh/clone/memória, mas o passo 6 é **subset deliberado**: cria `squad-owners.txt` e NÃO instala hook nenhum, com aviso explícito apontando para "ADR cross-platform futuro". — `bootstrap.sh:142`.
- **Todos os hooks forçam `exit 0` (soft-fail por design).** Num SO sem `powershell.exe`, o comando do hook simplesmente não roda — o host nunca vê "falha", os hooks só ficam inertes. — `inject-start-session.ps1:13`, `sync-global.ps1:13`, `check-execution-mode.ps1:11`, `template:19`; corroborado em ADR-004:82, ADR-005:128, ADR-006:146.
- **A superfície não-portável é ampla porém majoritariamente mecânica:** `$env:USERPROFILE`→`$HOME`, separador `\`→`/`, `Test-Path`→`[ -e ]`, `Get-Content -Raw`→`cat`, `Copy/Remove/New-Item`→`cp/rm/mkdir`, `Get-FileHash SHA256`→`sha256sum`/`shasum -a 256`, `Get-Date -Format`→`date +`. (~30 tipos de construção em 5 arquivos; maioria com equivalente bash de 1 linha.) — SQ2, file:line por construção.

### INFERIDO (cruzamento de fontes / raciocínio)

- **Os pontos PS-específicos NÃO-triviais são poucos e concentrados:** (i) manipulação de JSON do `settings.json` com chaves ordenadas via `[ordered]@{}` + `Add-Member` (`bootstrap.ps1:160-203`) → exige `jq` em bash (dependência externa nova); (ii) here-strings `@"..."@` com interpolação multilinha (`inject-*:65/105`) → here-doc bash com risco de escape de `$`/backtick; (iii) self-referência `$PSCommandPath`/`$MyInvocation` → `$0`/`readlink -f`. Os workarounds de encoding (`[Console]::OutputEncoding`, BOM, ASCII-safe) **não têm equivalente porque o problema não existe em bash** — superfície que *desaparece* no porte, não que precisa ser reescrita. — SQ2.
- **Risco multi-PC não-documentado:** o `~/.claude/settings.json` global inscreve caminho absoluto expandido via `$env:USERPROFILE` da máquina onde o bootstrap rodou (`bootstrap.ps1:147`) → frágil se copiado entre PCs com `USERPROFILE` diferente. Cruza com a memória `[[fabricio-multi-pc-workflow]]`. Nenhum ADR registra isso. — SQ3.
- **Existe uma bifurcação estratégica de custo** que o repo nunca avaliou: completar `.sh` (reescrever 4 hooks + install no `bootstrap.sh` + dependência `jq`) **vs.** trocar `powershell.exe`→`pwsh` no registro e corrigir só os breakers (`$env:USERPROFILE`, CP-1252). A segunda seria drasticamente mais barata SE os cmdlets atuais rodarem sob PowerShell Core. — síntese SQ2+SQ3+SQ5.

### DESCONHECIDO (lacuna explícita — sem fonte no repo)

- **Viabilidade de `pwsh` como ponte.** O repo não menciona PowerShell Core como estratégia; a direção registrada é sempre `.sh` (D4, ADRs). Não há evidência de que alguém *rejeitou* `pwsh` — provavelmente nunca foi *considerado*. — **Sugestão de validação:** spike de 1h — instalar `pwsh` num macOS/Linux, rodar os 4 hooks atuais sob ele e listar o que quebra (hipótese: só `$env:USERPROFILE` e o encoding-workaround). — SQ5.
- **Comportamento do host Claude Code** quando o comando de hook falha ou o interpretador não existe (soft-fail silencioso vs. bloquear sessão). O repo só documenta a política dos *scripts* (`exit 0`), não a do *host*. — **Sugestão de validação:** doc oficial de hooks do Claude Code + 1 run real em SO sem `powershell.exe`. — SQ5.
- **Disponibilidade de `jq`** no ambiente-alvo (dependência se a rota `.sh` for escolhida para os hooks que manipulam JSON). — **Sugestão de validação:** decidir na ADR se `jq` é pré-req do `bootstrap.sh` ou se a manipulação de `settings.json` é feita sem ele. — SQ2.

## 5. Gaps críticos (bloqueiam a decisão de ADR)

- **GAP-1 (bloqueante): a bifurcação `pwsh` vs `.sh` está DESCONHECIDA e decide o custo do porte.** Se `pwsh` rodar os hooks atuais com poucos ajustes, o porte é "trocar o registro + 2 fixes" (barato, sem `jq`, sem reescrever lógica). Se não, é reescrever 4 hooks + install em bash + dependência `jq` (caro). **Nenhuma ADR pode fechar sem resolver isto primeiro.** Mitigação: o spike de validação acima (1h) resolve o gap antes de qualquer linha de código.
- **GAP-2 (não-bloqueante, mas registrar): risco multi-PC do caminho absoluto** no `settings.json` global é um bug latente independente do porte. Deve entrar como achado próprio (candidato a fix pequeno ou nota em ADR), não se perder dentro do tema cross-platform.

## 6. Ataque anti-raso (R3 do intake — obrigatório)

Persona read-only adversarial atacou os achados antes do fechamento:

| Pergunta adversarial | Resposta / Mitigação |
|---|---|
| **Há lacuna não declarada?** | Sim, a decisiva: eu nunca *validei* que `pwsh` roda estes hooks — só confirmei que o repo não o menciona. Essa é a bifurcação que decide o custo e está **não-provada**. Promovida a GAP-1 bloqueante + spike de validação. |
| **Viés de confirmação?** | Sim, detectado: o enquadramento "completar o stub `.sh`" herda a âncora dos próprios ADRs (004/005/006 dizem ".sh"). Mas eles dizem `.sh` sem **avaliar** `pwsh` — provável omissão, não rejeição informada. Corrigido: a recomendação força a comparação `pwsh` vs `.sh`, não assume `.sh`. |
| **Fonte fraca?** | Sim, assimetria honesta: as fontes mais fortes (o próprio repo) cobrem "o que o framework faz" — mas as duas perguntas que **decidem** o porte (viabilidade `pwsh`, comportamento do host) **não têm fonte no repo**. Os achados mais bem-fundamentados são os menos decisivos. Registrado em §4 DESCONHECIDO com caminho de validação externo. |
| **Alternativa rejeitada sem registro?** | `pwsh` nunca foi registrado como avaliado-e-rejeitado; a ausência nos ADRs é silêncio, não decisão. A recomendação trata `pwsh` como alternativa **viva**, não descartada. |
| **A pergunta vale ser destravada agora?** | Não ainda: D4 é **trigger-gated** (só escala quando o mantenedor usar Linux/macOS regularmente; hoje é Windows-only). Pela régua §0 / disciplina de backlog, esta pesquisa é **pré-gatilho** — de-risca, mas não autoriza o ADR. Explicitado em §7 para impedir que um exercício de eval contrabandeie um gap não-autorizado. |

## 7. Recomendação ao orquestrador

**Enviar ao `architect` — porém GATED, não imediato.** Justificativa:

1. Os achados (inventário + hazards + esqueleto `.sh` já stubado + soft-fail por design) são suficientes para uma decisão arquitetural — é material de ADR, não de mais elicitação de requisitos. Logo, **não** é "continuar spec via discovery".
2. **MAS** a decisão está **duplamente travada**: (a) por **GAP-1** (a bifurcação `pwsh` vs `.sh` precisa do spike de 1h antes de qualquer ADR), e (b) pelo **gatilho de D4** (não disparado — mantenedor segue Windows-only). Pela régua §0, abrir o ADR agora seria adição pré-gatilho.
3. **Próximo passo concreto quando o gatilho disparar:** (i) rodar o spike `pwsh`; (ii) com o resultado, o `architect` abre o ADR cross-platform escolhendo a rota de menor custo; (iii) tratar GAP-2 (caminho absoluto multi-PC) como achado próprio, em paralelo.

> **Decisão de escopo (régua §0):** este brief NÃO foi seguido de uma ADR nem de implementação — fazê-lo violaria o gatilho de D4. O valor entregue é o de-risking antecipado + a correção do viés `.sh`-only dos ADRs anteriores.

## 8. Metadados

- **Rodadas executadas:** 2 (limite hard N=2 do passo 5 do algoritmo — atingido; round 3 NÃO executado).
- **Falhas do explorer:** nenhuma busca retornou vazio. SQ5 (round 2) confirmou *ausência de fonte* para as 2 perguntas externas → marcadas DESCONHECIDO sem re-perguntar (guard do passo 9 aplicado por *natureza external-knowledge*, não por falha técnica).
- **Custo de busca (datum do eval):** ~104K tokens nas 4 chamadas explorer (SQ1 24.8K · SQ2 29.0K · SQ3 30.8K · SQ5 19.4K) — confirma empiricamente o aviso do intake §2 sobre o custo do padrão multi-agente; aceitável aqui por ser field-validation.
- **Próximo papel:** `architect` (gated — ver §7).
