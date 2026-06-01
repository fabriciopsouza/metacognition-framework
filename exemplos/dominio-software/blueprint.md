# Blueprint de produto — domínio Software/Dados (ADR-046)

> **O que é:** o *formato premium de "pronto"* para um produto de software/dado, em **padrão agnóstico**
> (não em domínio). O `discovery` carrega este blueprint quando o `product_type` é de software/dado e
> **PROPÕE proativamente** a forma completa do produto (default sênior + trade-off) — para o dono
> **confirmar/ajustar numa batelada**, em vez de empurrar requisito a requisito. É a memória de "como é
> um entregável premium", carregada **sob demanda** (progressive disclosure — não infla o núcleo).
>
> **NÃO é hardcode:** descreve a FORMA (ter launcher, ter dicionário-contrato, ter suíte de saída), não
> o CONTEÚDO (quais módulos, quais colunas) — isso vem do dicionário do projeto + discovery.

## Proposta assertiva (o discovery põe isto na mesa de uma vez)

Para `product_type ∈ {gui-app, executable, data-pipeline, data-notebook}`, propor como default sênior:

1. **Ponto de entrada único — "fácil OU CLI".** Um `EXECUTAR.py`/launcher que: abre **GUI por default**
   (leigo) E aceita **subcomandos CLI** (`python EXECUTAR.py <modulo>` para automação/poweruser). Nunca
   `input()` bloqueante como única via (gate `check_entrypoint_tty`, ADR-036).
2. **Launcher de módulos (se >1 função).** Tela inicial com **cards** claros (1 por módulo), cada um com
   título + descrição curta + 2-3 bullets do que faz + botão "Abrir". Padrão observado em produto premium real.
3. **Entrada por dicionário-contrato.** O produto **auto-detecta** os arquivos na pasta selecionada e
   **valida** schema antes de processar (`docs/specs/<caso>/data-dictionary.md` + `check_input_contract`,
   ADR-046). Orienta o usuário sobre qual arquivo falta. Resolve "sem validação de arquivos".
4. **Suíte de saída (não só um número).** Conforme o público: planilha (dados), **documento** (relatório),
   **apresentação executiva** (decisão), gráficos. Cada saída rastreável à fonte (ADR-034/038).
   **Elaboração de documentos (ADR-050):** `tools/gen_exec_doc.py` gera md/docx/pptx/pdf de qualquer tipo —
   decisão/orçamento (custo + trade-offs + aprovação), apresentação executiva, **POP/SOP**, **manual de
   operação**, **guia de configuração**, **plano de manutenção** (templates de REFERÊNCIA em
   `docs/specs/_template-documentos/` — não-determinísticos: o briefing/spec do cenário adapta). **Qual
   documento cada situação exige é definido pelo discovery/explorer/briefing+PMO** (regra deles, inalterada);
   o gerador só renderiza. **Piso não-negociável: runbook de validação SEMPRE** (prova que funciona); em
   domínio **regulado declarado pelo discovery** (ADR-010/012 + `high-stakes-gate`) o conjunto obrigatório
   expande (validação/qualificação, rastreabilidade). Campo vazio → `NÃO PREENCHIDO` (nunca fabrica custo).
5. **Persistência + auditoria.** Histórico entre execuções (reprocesso idempotente) + trilha (quem/quando/
   insumos/versão-da-regra). Para `product_type=regulated`, ver `exemplos/dominio-regulado/`.
6. **Definição de pronto = gates.** `check_spec_depth` (dimensões) · `check_completeness` (cobertura do
   pedido) · `check_entrypoint_tty` + `check_clean_env` (porta do usuário) · `check_input_contract`
   (arquivos) · **ux-gate premium** (`ux-designer` §Definição de pronto). Verde em todos = pronto.

## Ativação (product-types → papéis)
Ver `product-types.txt` desta pasta. `gui-app`/`dashboard` ativam `ux-designer` (que aplica o ux-gate
premium). `data-pipeline`/`data-notebook` ativam `evals-engineer`. Sem aplicação → defaults flexíveis.

## Limite declarado (→ LIMITS.md)
O blueprint torna o discovery **assertivo** (propõe a forma) e mecaniza a **presença** dos elementos
(entry-point, dicionário, suíte). A **qualidade estética** ("premium" de verdade) é parcialmente
julgamento — o ux-gate verifica o checklist (launcher, leigo-rodável, estados), não "beleza".
