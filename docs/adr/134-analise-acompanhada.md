# ADR 134 — Análise acompanhada humano-IA: modo padrão, painel por fase e decisão registrada

- Status: **Aceito** (19/11/2026) · Decisores: dono + squad
- Origem: pesquisa e plano aprovados pelo dono em 19/11/2026, repositório central de pesquisas, `2026-11-19_analise-acompanhada-humano-ia/relatorio.md` (seções 4, 6 e 7; bloco B1 da seção 7.8)
- Relaciona: ADR-089 (ficha de insumo; recebe a emenda 1), ADR-122 (Parte I/Parte J), ADR-132 (faixas de QA), ADR-003 (companion files), ADR-070 (cada repositório escreve só em si)

## Contexto

O dono pediu que toda tarefa com dado seja conduzida com ele acompanhando: ver as etapas, questionar as decisões na hora,
documentar sempre, e só deixar a IA seguir sozinha quando mandar. A pesquisa (seção 3 do relatório) mostra que o nível de
automação desejado varia por etapa, que o analista quer ver dado e procedimento juntos, e que decisão analítica não
registrada some. O framework já tinha a ficha de insumo (ADR-089), o registro D-nn praticado nos projetos e a Parte I/J
(ADR-122), mas nenhum condutor de fases com modo, painel e pausa por classe de decisão.

## Decisão

1. **Modo padrão = acompanhado** em toda sessão. Decisões literais do dono de 19/11/2026: "o modo acompanhado é padrão até
   primeira ordem para seguir autônomo dali em diante na sessão"; "siga recomendado para demais" (tensões T1 a T9 na opção
   recomendada; T10, escopo da autonomia, pela frase literal anterior; seção 8 do relatório).
2. **Skill condutora `analise-dados`** (`.agent/skills/analise-dados/SKILL.md`): gatilho = tarefa que toque dado, indicador,
   métrica ou modelo; conduz fases CRISP-DM com negócio e dados juntos (fase 1+2); traz o catálogo de etapas, o painel
   mínimo, as 7 classes de decisão que param o acompanhado, a invariante por operação, o diário (só acréscimo, com a linha
   de modo) e o registro D-nn.
3. **Regras de sessão:** ordem de autônomo vale dali em diante na sessão; o modo mora no diário, não na memória; análise
   nova herda o modo e o declara na primeira linha do painel; gatilhos F2 (efeito irreversível, dado saindo da máquina,
   permissão ou credencial) param mesmo em autônomo; em autônomo, decisão aberta recebe a opção padrão, D-nn PRELIMINAR e
   revisão obrigatória no fim. **Opção padrão** (lacuna da seção 7.4 do plano, fechada com a sessão autora em 19/11/2026,
   mesma regra do `prompt-uso-imediato.md`): (1) regra já decidida em documento do projeto; (2) regra que reproduz o número
   oficial; (3) a mais conservadora (marcar em vez de excluir, não imputar, linha de base antes de modelo complexo,
   partição temporal). Nenhuma se aplica: para e pergunta, mesmo em autônomo.
4. **Sub-modo `produto-de-dados` do discovery** (`.agent/skills/discovery/produto-de-dados.md`): banco de perguntas por tema e
   procedimento de seis passos, recuperados de quatro produtos de dados do dono (só o método; isolamento entre empresas).
5. **Emenda 1 do ADR-089:** ficha de insumo de 6 para 8 campos (alvo e métrica de sucesso; premissas editáveis) e disparo
   também no início da fase 1+2 de toda análise da skill, em qualquer risco.
6. **Disparo no Claude Code:** `description` da skill (espelhada em `~/.claude/skills` por `bootstrap.py`) + regra de uma
   linha na fonte global `.claude/global/CLAUDE-global.md`, seção 6.
7. **Delegação:** pedido a outra IA dentro da sessão leva o modo vigente. Pacote para sessão nova:
   `tools/handoff.py --modo acompanhado|autonomo [--modo-origem "<literal, hora>"]` sempre traz a seção do modo, com
   "modo vigente na próxima sessão: acompanhado"; o autônomo da origem fica só como histórico, sem autorização (a ordem
   vale só na sessão em que foi dada). Autônomo sem origem é recusado (`ValueError` no `build()`, exit 2 na CLI).
8. **Pacote web:** a skill entra no tier premium como papel lateral (`tools/web_export.py`, lista `LATERAL`); o README gerado
   passa a calcular a contagem de skills.

## Mecanismo e prova

| Peça | Prova |
|---|---|
| Ficha com 8 campos e disparo ampliado | `tools/test_elicitation_gate.py` (rótulos 7 e 8 e menção à skill) |
| Fiação da skill, regra global, sub-modo, classes e painel | `tools/test_analise_dados.py` (com autoteste sabotado) |
| Campo "modo" no handoff | `tools/test_handoff.py` |
| Ativação da skill pelo modelo | teste de comportamento 3/3 com sinal e 0/3 sem; não determinístico, débito de prova por prosa, repetido no piloto (B4) |

## Fora deste ADR

B2 (ferramenta de conferência por invariante e lista da QA de análise), B3 (modelo de runbook), B4 (piloto), B5
(retrospectiva e emenda com a medição) e o apêndice A do plano (sinal de análise no orquestrador, painel, AGENTS.md e
GEMINI.md). No chat, a skill gerada traz só gatilho e critério de conclusão (formato enxuto do tier); o protocolo completo
para colar fica no `prompt-uso-imediato.md` da pasta da pesquisa.

## Consequências

- (+) O dono acompanha por padrão e troca de modo com uma frase; nada de decisão analítica fica sem registro.
- (+) Reusa ficha, D-nn, Parte I/J e molde Parte C; o único código novo é o campo do handoff e o canário.
- (−) Pausa por fase custa toque; mitigado pelo lote por fase e pela troca barata de modo. Medir no piloto (critério 4 da
  seção 7.9 do relatório).
- (−) A ativação depende do modelo ler a `description`; prova por comportamento, não por script.
- **Régua §0:** cláusula (c), destrava a análise acompanhada pedida pelo dono editando gates existentes (ficha, handoff,
  regra global); a skill e o companion são as únicas peças novas de conteúdo.
