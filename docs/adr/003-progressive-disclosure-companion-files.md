# ADR 003 — Progressive Disclosure: companion files para skills longas

- **Status:** Aceito (2026-05-25 — pelo mantenedor; aplicado imediatamente à skill `discovery`)
- **Data:** 2026-05-25 · **Decisores:** Fabricio (mantenedor) + Claude (papel `architect`)
- **Relaciona-se a:** ADR-002 (não substitui — complementa: aplica-se à estrutura física da skill `discovery` v1.6.0 já decidida)
- **Substitui:** nenhum · **Substituído por:** nenhum

## Contexto

A skill `discovery` cresceu de 90 linhas (v1.5.0) para 190 linhas (v1.6.0) após
absorver o sub-modo "mapeamento de processo" + saneamentos adjacentes
(ADR-002). Comparada às outras 14 skills do framework (média 37 linhas, 2ª
maior = `output-format` com 61 linhas), `discovery` virou **5x a 2ª maior e
6.7x a média**.

O usuário levantou pergunta de design: skill monolítica está coerente com o
próprio framework, que dedica o Bloco 2.5 do `AGENT-FRAMEWORK.md` a Context
Engineering como **princípio central** ("tratar contexto como recurso finito ·
attention budget")? A análise honesta é: **não está**. Carregar 190 linhas
toda vez que `discovery` ativa, mesmo em modo universal puro (caso mais
comum), viola o princípio que o próprio framework prega.

Padrão mainstream: **Progressive Disclosure** — SKILL.md leve como entry point
+ arquivos companion carregados sob demanda quando o caso específico aparece.
É a recomendação oficial da Anthropic para Claude Skills e converge com Cursor
rules, Aider conventions, GitHub Copilot, OpenAI Custom GPTs.

## Decisão (1 frase ativa)

Skills longas do framework DEVEM adotar **progressive disclosure**: SKILL.md
permanece como entry point curto (princípio + método universal + apontadores)
e cada sub-modo/extensão vive em **companion file** no mesmo diretório,
carregado sob demanda quando seu filtro de entrada ativar.

## Aplicação imediata a `discovery` v1.6.0

Estrutura final:

```
.agent/skills/discovery/
├── SKILL.md                              # ~100 linhas — entry point + apontadores
├── revisar-projeto-existente.md          # ~20 linhas — sub-modo v1.5.0 extraído
└── mapeamento-de-processo.md             # ~97 linhas — sub-modo v1.6.0 completo
```

A SKILL.md mantém **tabela de apontadores explícita** mapeando sub-modo →
companion file → quando carregar. Cada companion contém: filtro de entrada,
fluxo do sub-modo, output esperado, e qualquer EARS/regra específica.

## Alternativas consideradas

| # | Alternativa | Prós | Contras |
|---|---|---|---|
| 1 | **Progressive disclosure via companion files (escolhida)** | Padrão mainstream (Anthropic Skills, Cursor, Aider). Reduz context budget em caso comum (modo universal puro carrega só ~100 linhas em vez de 190 — economia de 47%). Manutenção isolada por sub-modo. Coerente com Bloco 2.5 do framework | Múltiplos arquivos a manter. Operador precisa entender o conceito de companion file. Padrão novo NO REPO (apesar de mainstream no ecossistema) |
| 2 | **Compactar redação da SKILL.md monolítica** | Sem padrão novo. Esforço só de redação | Reduz só visual (de 190 para ~140 linhas). Carrega tudo toda vez. Não resolve a doença (context budget), só o sintoma (tamanho aparente) |
| 3 | **Skill irmã (`process-mapping/SKILL.md`)** | Boundary máxima entre skills | Cria padrão de **delegação inter-skills** que não existe no framework (alto custo). Rejeitada já no ADR-002 D1. Não faz sentido reverter |
| 4 | **Manter monolítica** ("é proporcional ao escopo") | Zero esforço | Contradiz o Bloco 2.5 do próprio framework. Próximas skills que crescerem repetem o anti-padrão. Não escala |
| 5 | **Subdir `references/` (variante de #1)** | Convenção Anthropic Skills mais formal | Adiciona uma indireção a mais sem ganho proporcional para o escopo atual (2 companions). Vale considerar quando crescer para 4+ companions |

## Justificativa

A alternativa #2 (compactar) era a recomendação inicial do `architect` — mas
caía no anti-padrão "tratar sintoma em vez de doença". O problema NÃO era
tamanho visual: era **carregar contexto irrelevante** em maioria das chamadas
(método universal puro nem usa o sub-modo BPM). Compactar não muda isso.

A alternativa #4 (manter) só é honesta se admitirmos que o Bloco 2.5 do
framework é decorativo. Não é — é princípio operacional. Recusar applicar é
incoerência interna.

A alternativa #3 (skill irmã) já foi rejeitada no ADR-002 D1 por criar padrão
de delegação inter-skills inexistente.

Sobra a #1 (companion files): mainstream, coerente, custo baixo. Auto-sync
hook já suportava porque usa `Copy-Item -Recurse` (descoberta na implementação
— linhas 38, 50 de `.claude/hooks/sync-global.ps1`). Nenhum custo de hook;
apenas documentação do comportamento já existente.

## Consequências

### Positivas
1. **Context budget reduzido em caso mais comum** (modo universal puro): 190 → 100 linhas = -47%.
2. **Manutenção isolada por sub-modo:** alterar matriz de 13 dimensões BPM não toca a SKILL.md core. Diff git mais limpo, blast radius menor.
3. **Padrão escalável:** quando outras skills crescerem (`developer` ganhar sub-modos por linguagem? `qa-critic` por tipo de revisão?), o padrão já existe — clonar, não reinventar.
4. **Coerência arquitetural:** o framework agora **pratica** o que prega no Bloco 2.5.
5. **Convergência com ecossistema:** novos contribuidores vindos do Claude Skills/Cursor/Aider reconhecem o padrão imediatamente.
6. **Auto-sync funciona automaticamente:** hook já usava `-Recurse`. Zero custo de infra.

### Negativas
1. **Pasta de skill com múltiplos arquivos:** quem está acostumado com "1 skill = 1 arquivo" precisa ajustar mental model. Mitigação: tabela de apontadores em SKILL.md torna explícito.
2. **Outro arquivo na lista de referências cruzadas:** AGENT-FRAMEWORK.md, validation.md, ADR-002 ganham mais 2 paths para referenciar. Mitigação: paths nomeados (`mapeamento-de-processo.md`) são autoexplicativos.
3. **qa-critic precisa re-rodar** (round 3) — pequeno custo no ciclo desta sessão.

### Riscos
1. **Fragmentação excessiva** se o padrão for aplicado liberalmente. Mitigação: regra — aplicar **só quando SKILL.md > 80 linhas E tem sub-modos identificáveis**. Skills curtas (`pmo`, `architect`, `developer` com 23-31 linhas) NÃO precisam.
2. **Companion file órfão** (referenciado em SKILL.md mas removido por engano). Mitigação: `qa-critic` valida apontadores via grep cruzado.
3. **Auto-sync arrasta arquivos não-skill por engano** (ex.: alguém colocar um README.md na pasta). Mitigação: o filtro `Test-Path (Join-Path $_.FullName 'SKILL.md')` continua sendo o gate de "é skill válida"; arquivos sem essa condição não entram. Companion files entram automaticamente porque a pasta inteira é copiada quando a pasta É skill válida.

## Implementação (ponteiro após aceito)

- **Ponteiro:**
  - Branch: `feat/discovery-process-mapping-v160` (a criar pelo developer; aplica em conjunto com ADR-002)
  - Data: 2026-05-25 (este ADR foi escrito e aplicado na mesma sessão que ADR-002)
  - Grep para localizar implementação: `git log --all --grep "v1.6.0" --grep "progressive disclosure" --grep "companion file"`
- **Hash de commit:** opcional como complemento — NUNCA único.
- **Aplicação imediata em `discovery` v1.6.0:**
  1. ✅ Criado `.agent/skills/discovery/mapeamento-de-processo.md` (sub-modo BPM extraído).
  2. ✅ Criado `.agent/skills/discovery/revisar-projeto-existente.md` (sub-modo v1.5.0 extraído).
  3. ✅ SKILL.md reduzida de 190 → 100 linhas, com tabela de apontadores.
  4. ✅ Header do hook `sync-global.ps1` atualizado para documentar suporte automático a companion files.
  5. ✅ `validation.md` itens 1 e 11 atualizados para grep nos companion files corretos.
- **Validação:** `qa-critic` roda o gabarito atualizado de `validation.md` em round 3.

## Regra de aplicação futura

Skills do framework DEVEM adotar progressive disclosure quando:
1. SKILL.md ultrapassar **80 linhas**, OU
2. Skill ganhar **2+ sub-modos identificáveis** com filtros de entrada distintos.

Skills curtas (atuais: `pmo`, `architect`, `developer`, `qa-critic`, `docops`,
`explorer`, `_template`, `_shared/*`) **não** precisam ser refatoradas
preemptivamente. Adotar quando atingirem o gatilho acima.

## Referências

- Aplicação imediata: `.agent/skills/discovery/` (3 arquivos)
- ADR irmão: [docs/adr/002-discovery-process-mapping-v160.md](002-discovery-process-mapping-v160.md) (decisões D1-D7 sobre a feature)
- Bloco 2.5 do framework: [`AGENT-FRAMEWORK.md`](../../AGENT-FRAMEWORK.md) — Context Engineering
- Hook auto-sync (já suporta companion files via `-Recurse`): [`.claude/hooks/sync-global.ps1`](../../.claude/hooks/sync-global.ps1)
- Padrão mainstream:
  - Anthropic Claude Skills (oficial): SKILL.md + `references/` + `helpers/` sob demanda
  - Cursor rules: `.cursor/rules/*.mdc` múltiplos por escopo
  - Aider: `CONVENTIONS.md` + arquivos adicionais
  - GitHub Copilot: `.github/copilot-instructions.md` + complementos
