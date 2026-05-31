# requirements.md — Especificação Atômica de uma Feature/Caso

> Clonar esta pasta para cada feature/caso: `docs/specs/<nome>/`.
> Fonte do método: pesquisa A2 (camada atômica do SDD). Esta é a **intenção**,
> não a implementação — não ditar classes/libs aqui.

## Identificação
- **Caso/feature:** <nome>
- **Indicador/objeto:** <o que se analisa ou constrói>
- **Recorte:** <ano | regional | total | n/a>
- **Confiança da tarefa:** ALTA | MÉDIA | BAIXA  → governa o roteamento (ver `rules/04`)

## Escopo declarado pelo discovery (ADR-010 — obrigatório quando há sinal de contexto especializado)

> Lote temático do passo 6 do `discovery/SKILL.md`. **Modo A (Transcribe-mode determinístico):** se briefing tem declaração nominal+ubíqua+stakeholder+sem-contradição → transcrever do briefing (citar trechos). **Modo B (Interview-mode, default):** preencher abaixo via elicitação com dono.

### (a) Regulado?
Este projeto opera sob alguma norma/convenção externa? Quais? Vigência?
- `[CONFIRMADO|INFERIDO|DESCONHECIDO]` <norma> — <vigência> · fonte: <doc/dono>
- **Origem:** [via briefing — citar trecho] | [via interview]

### (b) Alto-risco?
Decisão downstream irreversível, financeira material ou auditável?
- Sim/Não + justificativa.

### (c) Regras com semântica?
Regra de negócio onde o "como" importa tanto quanto o "quê" (anti-fraude, audit trail, fairness, etc.)?
- Sim/Não + lista concreta.

### (d) Gaps não-bloqueantes?
Dimensões/dados sabidos ausentes mas não impedem entrega?
- <gap> · impacto se não tratado · decisão dono: manter gap / tratar follow-up.

**Sem declaração afirmativa em (a)/(b)/(c) → defaults agnósticos.** Gates downstream (`high-stakes-gate`, reforço sênior `metodo-senior.md`, roteamento reflexivo) carregam SOB DECLARAÇÃO, não por sinal semântico (ADR-010 §Princípio 12).

## Dimensões de elicitação (banco agnóstico — ADR-033)

> Obrigatório para **produto recorrente** (software/dado/pipeline/relatório-ferramenta). Para cada
> dimensão, registrar a **decisão** (não a pergunta). O discovery recomenda um default sênior com o
> trade-off; aqui fica a decisão confirmada/alterada. `tools/check_spec_depth.py` **barra J1**
> (discovery→architect) se alguma dimensão obrigatória ficar sem decisão. Banco e aliases:
> `_shared/discovery/elicitation-dimensions.md` (aliases permitem usar o vocabulário do domínio).

- operador: <quem opera — técnico/leigo → consequência na interface>
- interface: <CLI | GUI | web | planilha — proporcional ao operador>
- entrada-validacao: <como entram os dados; lista/valida/orienta a fonte?>
- escopo-temporal: <ponto único | intervalo | total | realizado+acumulado>
- recortes-saida: <por quais cortes a saída é vista; "todos"?>
- persistencia: <memória entre execuções? histórico? reprocesso?>
- auditoria-log: <registra quem rodou/quando/insumos/versão da regra?>
- ambiente-execucao: <instala/roda em máquina limpa? entry-point não-interativo?>
- formato-saida: <relatório/export; faixas/metas visíveis; rastreável à fonte?>

## Mapeamento de campo-fonte (ADR-035 — obrigatório quando há colunas-irmãs ambíguas)

> Quando um termo do pedido pode casar com mais de um campo/coluna de nome parecido (um componente vs.
> o total, "interna" vs. "manual" vs. soma), o mapeamento termo→coluna é **decisão registrada do dono**,
> não inferência. `tools/check_field_mapping.py` exige, por linha: **confirmação do dono** +
> **justificativa (`porque:`)**. Remover esta seção se não houver ambiguidade de campo-fonte.

- <termo> -> <coluna escolhida> | confirmação: [CONFIRMADO] pelo dono | porque: <justificativa, idealmente com prova numérica> | irmãs descartadas: <colunas candidatas e por que não>

## Cobertura exigida pelo pedido (ADR-034)

> Liste cada **quantificador de escopo** do pedido ("cada X", "por X", "mês a mês"/mensal, "acumulado",
> "ano inteiro"/anual, "intervalo", "todos"). `tools/check_completeness.py` cruza cada um com um critério
> binário do `validation.md` — quantificador do pedido sem critério = FAIL antes do PASS (J4). Remover
> esta seção se o pedido não tem quantificadores de escopo.

- <quantificador 1 — ex.: por unidade / cada entidade>
- <quantificador 2 — ex.: mês a mês ao longo do intervalo>
- <quantificador 3 — ex.: acumulado além do realizado>

## Escopo funcional (EARS — opcional, mas recomendado)
- **Ubíquo:** "O sistema DEVE <comportamento>."
- **WHEN:** "QUANDO <evento>, o sistema DEVE <resposta>."
- **IF/THEN:** "SE <condição de exceção>, ENTÃO o sistema DEVE <tratamento>."
- **WHERE:** "ONDE <contexto específico>, o sistema DEVE <variação>."

## Fluxos de exceção e lógicas limítrofes (explícitos)
- <NULL / zero / negativo / extremo / string vazia — como tratar>
- <divergência de fonte / dados ausentes>

## Fora de escopo (anti-spec gigante)
- <o que este caso NÃO cobre>

## Fontes de dados
- <tabela/dataset/arquivo + como acessar — file-first antes de assumir colunas>

## Glossário relevante
- <termos deste caso; remeter a 00-glossario.md>
