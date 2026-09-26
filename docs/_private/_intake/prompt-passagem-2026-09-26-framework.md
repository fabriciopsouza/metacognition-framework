# Prompt de passagem — sessão do framework, 26/09/2026

Colar na próxima sessão, aberta em `C:\Users\fabriciosouza\metacognition-framework`:

```
iniciar

Contexto: sessão anterior (26/09) entregou na main o kit regulado (ADR-119), a biblioteca de conhecimento
(ADR-120), a dimensão escopo-e-prazo (emenda 2 do ADR-033) e o método único de projeto com desenho do processo
e manifesto de evidência (ADR-121). Checkpoint: topo do history.md. Relatório:
docs\_private\_intake\execution-report-2026-09-26-framework-b3.md.

Trabalhe só no que é agnóstico (método do framework); projetos de domínio (MRP, OPEX, pesagem) são de outras
sessões.

Próximo bloco, pela ordem do dono (B3d ✅ → B3a → B3c → B2b → B3b ANVISA por último):
B3a-2 — planilhas de confirmação (13 colunas, abas REGRAS/LEIA/VALORES POR TIPO) e de verificação
(15 colunas de base + 12 por rodada, abas COMO USAR/ANTES DE COMEÇAR/ACHADOS DO AMBIENTE/CORREÇÕES DA BASE/
CONTROLE DE VERSÃO), geradas do arquivo único, com ida e volta (REQ-05, REQ-06, critérios 3a e 3b do plano
docs\specs\b3-documentacao-regulada\spec.md).
ANTES de codificar, pergunte ao dono as decisões ainda abertas (recomendação entre parênteses):
 1. linhas da planilha de confirmação vêm de uma Parte nova "Definições a confirmar" com as 13 colunas (sim);
 2. linhas da planilha de verificação vêm de uma Parte nova "Roteiro de verificação", separada dos testes E2E
    da Parte G; cada rodada da área volta como subseção datada (sim);
 3. em projeto com impacto regulado, o gerador acrescenta as categorias obrigatórias do perfil que faltarem (sim);
 e os pontos do desenho do processo (Parte H) viram linhas da planilha de confirmação (decisão do dono de 26/09).
Modelos reais só para leitura: C:\Users\fabriciosouza\Downloads\2026-09-11-MRP\Checklist_Validacao_Cadastros_MRP_v1_1_TREPLICA-v3.xlsx
e DEFINICOES-PCP-para-confirmacao.xlsx (conferir colunas com openpyxl read_only).

Depois: B3a-3 (ERU gerada da Parte A, relatório de validação, mudança e versão), B3c (skill project-docs enxuta),
B2b (verificador do plano), B3b (perfil ANVISA + mapa peça→artigo + leitura primária da IN 134).

Pendências em tools\trabalhos.py: regra-global-instalar-apos-merge (instalar ~/.claude/CLAUDE.md após merge que
muda a regra global), subagente-revisor-so-leitura.

Regras que o dono cobrou nesta sessão: responder às perguntas antes de executar; criticar antes de fazer;
"status" = tabela com % por bloco + 3 linhas; revisão isolada (Sonnet) em todo bloco; rodar a suíte completa de
canários antes do PR.
```
