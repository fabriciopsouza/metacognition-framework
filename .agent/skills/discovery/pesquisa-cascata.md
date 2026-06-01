# Discovery — Sub-modo Pesquisa em Cascata (G1)

> Companion file do `discovery` (v1.7.0+). Progressive disclosure (ADR-003):
> carregado SOB DEMANDA quando o trabalho exige pesquisa antes da spec.
> Fonte: ADR-007 (G1). NÃO carregar em sessão pontual sem demanda explícita.

## Filtro de entrada (passo 1 — obrigatório antes de qualquer pesquisa)

Ativar este sub-modo apenas quando **todos** os critérios se verificam:

1. **Há pergunta de fundo** que precisa ser respondida ANTES de a spec ser viável (ex.: "qual o estado-da-arte de SDD em 2026?", "como esta norma/padrão declarado pelo discovery trata componente X?" — exemplos flexíveis; o domínio específico vem do projeto declarado pelo discovery, ADR-010).
2. **Não há fonte canônica disponível** no contexto da sessão (briefing/glossário/ADR existente não cobrem).
3. **A resposta destrava decisão** — não é curiosidade lateral.

Se qualquer critério falha → NÃO carregar este companion. Voltar ao método universal do `SKILL.md` ou ao sub-modo apropriado.

## Princípio

Pesquisa em cascata é **monólito single-thread** que segue o pipeline da pesquisa A0+A2 (intake §2): decompor → buscar → refletir → ramificar → sintetizar → atacar → fechar. Multi-agente paralelo só na fase de busca (sub-perguntas independentes via `explorer` em contexto isolado); síntese e escrita são single-writer para preservar coerência de decisões implícitas.

## Algoritmo canônico (9 passos)

```
1. Filtro de entrada: confirmar que e pesquisa antes da spec (sec acima)
2. Decompor: pergunta principal → 3-5 sub-perguntas multi-hop concretas
3. Buscar: delegar CADA sub-pergunta ao `explorer` em contexto isolado
   (subagente read-only; output em achados estruturados + fontes)
4. Refletir: sintetizar achados; classificar cada um como
   CONFIRMADO | INFERIDO | DESCONHECIDO (via _shared/confidence-classification)
5. Ramificar: lacunas viraram novas sub-perguntas → volta ao passo 3
   (LIMITE HARD: N=2 rodadas no maximo; alem disso, lacuna fica DESCONHECIDO)
6. Sintetizar: monolito single-thread em `research-brief.md`
   (clonar o diretorio `docs/specs/_template-research/` para
   `docs/specs/<nome-do-tema>/` e preencher o research-brief.md;
   manter o diretorio como container caso o template ganhe arquivos auxiliares)
7. **ATAQUE ANTI-RASO (obrigatorio, R3 do intake)**: persona read-only ataca
   os achados antes de fechar. Perguntas tipicas: lacuna nao declarada?
   vies de confirmacao? fonte fraca? alternativa rejeitada sem registro?
8. Refinar: incorporar achados do ataque; fechar QUANDO (criterio binario):
   lacunas que BLOQUEIAM decisao de spec ou que invalidam a hipotese
   principal estao todas marcadas DESCONHECIDO com sugestao de validacao.
   Lacunas perifericas NAO bloqueiam o fechamento.
9. Falha do explorer: se retornar vazio em todas as sub-perguntas de uma
   rodada, registrar a sub-pergunta como [DESCONHECIDO] com sugestao de
   fonte alternativa; NAO repetir a mesma sub-pergunta na rodada N+1.
```

## Output obrigatório

Entrega `research-brief.md` (clonar template) preenchido com:

- **Pergunta principal** + **decomposição** (3-5 sub-perguntas).
- **Fontes consultadas** (com link/path; classificadas por relevância).
- **Achados** (cada um classificado `CONFIRMADO|INFERIDO|DESCONHECIDO`).
- **Gaps críticos** (com sugestão de validação).
- **Ataque anti-raso** (perguntas que persona adversarial levantou + respostas).
- **Recomendação ao orquestrador** (continuar para spec via discovery, ou enviar direto ao architect, ou mais elicitação).
- **Antecipações + Backlog de elicitação** — quando o reforço transversal sênior está ativo em paralelo (`metodo-senior.md`, ADR-009; gatilho: há fonte canônica/normativa citada), preencher também **§7 Antecipações** e **§8 Backlog de elicitação** do template `research-brief.md` (obrigatórias). Sobreposição cascata + sênior produz brief de 10 seções (vs 8 da cascata pura).

Resumo YAML ao orquestrador:
```yaml
papel: discovery
sub_modo: pesquisa-cascata
pergunta_principal: "<o que estava em aberto>"
rodadas: <1 ou 2>
sub_perguntas: <3-5>
achados_classificados:
  confirmado: <N>
  inferido: <N>
  desconhecido: <N>
gaps_criticos: ["<lacuna>", ...]
ataque_anti_raso: ["<pergunta-ataque>", ...]
output: docs/specs/<nome>/research-brief.md
recomendacao_ao_orquestrador: "<continuar-spec|architect|mais-elicitacao>"
```

## Fronteiras

- **NÃO é discovery completo.** Este sub-modo termina com `research-brief.md`. A elicitação que vira `requirements.md` é o método universal do SKILL.md — pode usar o brief como input.
- **NÃO é replacement do explorer.** Pesquisa-cascata orquestra; o explorer executa cada busca em contexto isolado.
- **NÃO é multi-agente paralelo na escrita.** Apenas a fase de busca (passo 3) é paralela; síntese (passo 6) e ataque (passo 7) são single-thread.
- **NÃO carregar em sessão pontual sem demanda explícita** — fere a régua §0 (ADR-007).
