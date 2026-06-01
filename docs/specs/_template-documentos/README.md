# Templates de documentos premium — REFERÊNCIA, não estrutura fixa (ADR-050)

> **Modelos de REFERÊNCIA, não-determinísticos.** Estes templates são **pontos de partida** — a estrutura
> REAL de cada documento é **objetivada pelo briefing + spec do cenário/domínio concreto**, definido pelo
> **discovery / explorer / briefing + PMO** (regra deles, inalterada). Não são gabaritos rígidos: ao atender
> um caso, o discovery **adapta** (adiciona/remove/renomeia seções, ajusta o `<!-- required: ... -->`) e o
> `tools/gen_exec_doc.py` **renderiza o que a spec declarar** (md/docx/pptx/pdf).
>
> **Inspiração:** padrões observados em entregáveis premium reais de vários domínios (recálculo de
> indicadores, reconciliação, análise de capacidade, analytics). Extraímos a **FORMA agnóstica** (seções,
> sequência, "o que um deck/relatório/POP precisa ter") — **nunca** o conteúdo, números ou nomes de domínio.

## Piso de validação + domínio regulado (não-negociável)
A geração é **flexível** por público (executivo, operador, técnico) e objetivo do projeto — mas com **piso**:
- **Runbook de validação SEMPRE** (`runbook-validacao.md`) — toda entrega premium prova *que funciona*
  (passos → resultado esperado → aceite → evidência). **Default-obrigatório**, não rígido: só dispensável por
  **decisão consciente do dono** em caso trivial (mesma flexibilidade do retrospective gate — escolha registrada,
  não default silencioso). Em regulado, deixa de ser dispensável.
- **Domínio regulado → docs adicionais.** Quando o **discovery declara** o domínio/normas (ex.: saúde,
  alimentos, farmacêutico, financeiro — passo 6, ADR-010/012) e o `high-stakes-gate` ativa, o conjunto
  obrigatório **expande** (validação/qualificação, rastreabilidade, controle de mudança) conforme a norma
  declarada. **O framework não decide "é regulado" sozinho** — o discovery declara; aí o piso sobe. Docs
  regulados não são pré-fixados aqui: clone/crie o template conforme a norma que o discovery levantar.

## Como usar (o discovery/PMO conduz)
1. O discovery/PMO **escolhe** o(s) tipo(s) de documento que a situação exige (mínimo: o runbook de validação).
2. **Clona** o template mais próximo, **adapta** as seções ao cenário (o `<!-- required -->` é o *default* do
   modelo — ajuste-o ao que o caso realmente precisa).
3. Preenche com o conteúdo do projeto; campos vazios saem como **NÃO PREENCHIDO** (anti-fabricação — nunca
   inventar custo/número).
4. Gera: `python tools/gen_exec_doc.py <doc.md> --out-dir saida --formats md,docx,pptx,pdf`.

## Modelos de partida (adapte por cenário)
| Template | Para quê (referência) |
|---|---|
| `runbook-validacao.md` | **PISO — sempre.** prova que funciona: passos → resultado esperado → aceite → evidência → rollback |
| `decisao-executiva.md` | proposta + orçamento (custo + trade-offs + alternativas) + pedido de aprovação |
| `apresentacao-executiva.md` | deck de decisão: contexto → faixas/metas → cenários → comparação → resultado×meta → recomendação |
| `pop-sop.md` | procedimento operacional padrão (operação repetível) |
| `manual-operacao.md` | manual do usuário (como operar, telas, troubleshooting) |
| `guia-configuracao.md` | instalação/configuração/validação |
| `plano-manutencao.md` | manutenção/sustentação (periodicidade, tarefas, indicadores) |

> Faltou um tipo? **Crie um novo** (mesmo formato: título `#`, seções `##`, `<!-- required: ... -->`
> opcional). O gerador é doc-type-agnóstico — serve qualquer documento que o cenário pedir. Premium-only (ADR-049).
