# Validation — v1.16.0 Compaction por threshold + digest (gate binário)

| # | Critério | Como verificar | V/F |
|---|---|---|---|
| V1 | §2.5 alavanca 1 tem as 4 faixas (fronteiras sem sobreposição: <50/50–69/70–84/≥85) substituindo o gatilho qualitativo | leitura | — |
| V2 | §2.5 declara proxy `chars ÷ 3` no chat como alarme de fumaça | grep "÷3"/"chars÷3" | — |
| V3 | §2.5/ADR declaram cortes como escolha [INFERIDO] (não recomendação numérica de P2) | leitura | — |
| V4 | checkpoint.md: gatilho por faixa + aponta para o template (não relista campos) | leitura | — |
| V5 | digest.md tem os 5 headers canônicos do §Pacote como seções [P14] (Artefato consumível, Localização, Acesso, Prompt pronto-para-colar, Pendências e premissas) | `grep -c "\[P14\]"` = 5 + cada header presente | — |
| V6 | digest.md tem os 5 marcadores [P14] + carimbo (versão+timestamp+faixa) + 5 arquivos recentes | grep "[P14]" | — |
| V7 | ADR-016 cita P2 e é EMENDA ao Princípio 8 (não SUPLANTA) | leitura | — |
| V8 | Régua §0: nenhum módulo _shared novo; só §2.5 + checkpoint + 1 template | git diff --stat | — |
| V9 | Agnóstico de domínio (faixas/proxy/digest não hardcodam BI/farma/regulado) | leitura | — |
| V10 | ÷3 declarado dentro do intervalo ÷3–÷3,5 de P2 (default conservador), não inventado | leitura ADR | — |
| V11 | (regressão-check) Contrato Onda 0 segue 7/7 PASS (skills não tocadas nesta onda) | `python tools/validate_skills.py` | — |
| V12 | Fronteiras de faixa sem sobreposição em ADR + §2.5 + checkpoint (70∈🟠, 85∈🔴) | grep "50–69"/"70–84"/"≥85" nos 3 | — |
