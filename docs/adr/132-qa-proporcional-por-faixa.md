# ADR-132 — QA proporcional por faixa, cinco princípios de execução e sessão por fase

- **Status:** Aceito
- **Data:** 2026-10-26
- **Decisores:** dono (Fabricio), 26/10/2026, nas palavras dele:
  - "será que precisava de revisao adversarial em tudo? uma tarefa simples dessa? confirmado, inferido, nao sei nao bastava?";
  - "Objetivo é: dá pra simplificar? Dá pra cortar? Entao ok!" e "NAO SIGNIFICA economia a qualquer custo, nem baixar a qualidade atual!";
  - "eventualmente temos TANTO qa que gasta mais que se tivesse rodado a tarefa toda e feito qa ai";
  - "garantir que a especificação seja bem feita e de forma critica, que o executor siga o projeto, que o qa pegue realmente se este todo foi bem feito";
  - "Nao podemos seguir por aqui por enquanto? usando opus como autor e sonnet como revisor qa? Siga sempre pelo recomendado!".

  Autoria: Opus 5.5.
- **Relação:**
  - emenda a regra global seção 1 (revisão em todo bloco) e a skill `qa-critic` (disparo condicional);
  - mantém o ADR-011 (todo QA de F1 e F2 é adversarial), o ADR-110 (autor no padrão, 1º QA um degrau abaixo, 2º só com autorização) e o ADR-118 (limite de rodadas);
  - reafirma, para esta linha de trabalho, autor Opus e revisor Sonnet; a decisão de papéis registrada e não aplicada no ADR-131 continua com o dono;
  - pesquisa: `C:\Users\fabriciosouza\pesquisas\2026-10-26_qa-proporcional-orquestracao-multi-ia\relatorio.md` (32 fontes, QA Sonnet com ressalvas aplicadas).

## Contexto
1. A regra global mandava revisão em subagente para **toda** alteração. Em 26/10 um ajuste de duas linhas em `settings.json`, reversível e com cópia, gastou ~44 mil tokens de revisão para nenhuma mudança de resultado.
2. Medição sobre 130 vereditos em `_meta/qa/` (103 blocos):
   - o desperdício se concentra em laço: 25 das 28 reprovações vêm de uma série (ADR-115, até a rodada 39), metade dos vereditos dela cita "irmão" ou "mesmo defeito";
   - fora dela, 3 reprovações em 100; o QA achou defeito relevante em ~51% dos vereditos;
   - nenhum veredito registra tokens ou duração.
3. Evidência externa (fontes no relatório): revisão sem informação nova tem ganho ~0; revisor instruído a achar falha sempre acha algo; rigor cedo e verificação executável custam menos que revisão tardia; contexto longo piora a resposta; o BMAD v7 dimensiona o método pelo tamanho da intenção.

## Decisão
1. **Três faixas**, declaradas pelo autor antes de executar; na dúvida, a mais alta; o dono pode subir a faixa. **Gatilhos de F2** (basta um), definidos uma vez: regulado; irreversível; número para decisão; dado de empresa saindo da máquina; permissão, segurança ou credencial; várias sessões, sistemas ou pessoas; regra do framework, release ou ADR.

   | Faixa | Critério | Revisão |
   |---|---|---|
   | F2 complexo/alto risco | Qualquer gatilho de F2 | Revisão da spec antes, script nas junções do meio, process-critic no fim; ADR-118 |
   | F1 padrão | Nenhum gatilho de F2 | Process-critic único no fim; máx. 2 rodadas |
   | F0 simples | Nenhum gatilho de F2 + reversível, cópia do original, conferível por script | Classificação de confiança + conferência executada, declaradas na resposta final; sem subagente |

   A pesquisa propunha também "diff descritível em uma frase" e "efeito E1–E2 da `action-safety`" para a F0: o primeiro foi descartado por ser subjetivo (a fonte trata de dispensar plano, não QA); o segundo está contido em "reversível" e "nenhum gatilho de F2".

2. **Escopo do revisor:** critério de aceite e o que mudou, não a conversa. Achado fora do critério vira nota. Rodada nova só com correção feita ou fato novo. Quem acha não valida.
3. **Cinco princípios de execução** na regra global seção 3: pensar antes; simplicidade primeiro; mudança cirúrgica; guiado por meta; não simplificar demais o que precisa de método.
4. **Sessão por fase** na regra global seção 6: com o desenho aprovado, bloco em sessão limpa a partir do `tools/handoff.py`, salvo pedido do dono para seguir na mesma sessão.
5. Revisar abaixo da faixa exige ordem explícita do dono, como antes "não rodar"; declarar F0 ou F1 para fugir da revisão é revisar abaixo da faixa.
6. **Mandato do process-critic** ("final de cada bloco aprovado") passa a valer nas faixas F1 e F2. Ressalva aplicada em `.agent/skills/qa-critic/SKILL.md`, `.agent/workflows/handoff.md`, `.agent/workflows/checkpoint.md`, `.agent/workflows/feature-plan.md`, `_shared/traceability/SKILL.md`, `CLAUDE.md`, `AGENT-FRAMEWORK.md`, `guia/METODO-DE-PROJETO.md`, `guia/COMO-FOI-CONSTRUIDO.md` e `guia/GUIA-EQUIPE.md`. Release e ADR são sempre F2, então a evidência fail-closed por release (ADR-074) não muda. O ADR-116 (regras permanentes) fica como registro histórico; a regra vigente é a seção 1 emendada.

## Régua §0
Porta (b): reduz tokens e latência em F0 e corta laço em F1, editando regra e skill existentes (nenhuma seção nova na skill; o parágrafo de disparo condicional foi substituído).

## Limites
- **A faixa é declarada pelo próprio autor, e a F0 não tem revisor.** A defesa até haver classificador por script é parcial: critério verificável, F0 declarada na resposta final com o que foi conferido (o dono vê), e o process-critic do bloco seguinte que a encontrar trata F0 indevida como achado. Não há freio para F0 indevida isolada que ninguém revisite.
- **"69% dos blocos em 1 ou 2 rodadas" é subestimado** (relatório, D5: blocos sem o campo `rodada` contam como 1). O bloco B2 (26/10/2026) entregou os três mecanismos: classificador de faixa em `tools/risk_score.py` (`--gatilho`, `--nenhum-gatilho`, `--f0`; nomes na constante `GATILHOS_F2`), busca do mesmo texto em outros arquivos antes do revisor em `tools/varrer_irmaos.py`, e `tokens`/`duracao_s` por rodada em `tools/qa_evidence.py`. O classificador confere a regra, não a declaração: gatilho que o autor omite continua sendo F0 indevida.
- **"Máx. 2 rodadas" em F1 é proposta**, sem estudo de revisão de código por LLM que a fixe; recalibrar quando houver tokens por rodada.
- A heterogeneidade (revisor de outra família) continua pelo ADR-131 e pela escada; este ADR não muda o revisor.

## Prova
- Conferência por script: `python tools/check_rules_parity.py` e os canários de consistência rodados no fechamento.
- QA do bloco (F2, muda regra de todos os projetos): `qa-critic` Sonnet isolado; veredito em `_meta/qa/adr-132-qa-proporcional.json`.
