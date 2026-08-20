# QA-evidence — procedencia-narrativa-na-prosa-publica

- **Data:** 2026-08-19T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** —
- **RRC:** —
- **Metodo-senior:** —

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | tools/test_marketing_claims.py TEM_FONTE | falso positivo em prosa honesta que citava fonte fora do formato previsto, ou no bloco seguinte. Quatro casos executados pelo critico. TEM_FONTE ampliado e vizinhanca de bloco aceita; os quatro viraram regressao no auto-teste. |
| MEDIA | tools/test_marketing_claims.py, laco do gate (i) | [achado na r2] o auto-teste provava a funcao e nao a fiacao: laco vazio fazia o gate reportar PASS sem varrer nada. Contador de arquivos varridos, com reprovacao em zero. |
| MEDIA | comentario do limite | limite declarado era vago. Passou a nomear as 4 fugas uma a uma, incluindo fonte decorativa (arquivo, URL, ADR, decisao) e o modelo de ameaca: o alvo e' o autor desatento, nao um adversario. |
| MEDIA | ABRE_CASO | ampliar para conjugacao singular ('pediu'). RECUSADO com motivo: casa com prosa legitima do repo ('o dono pediu que...'), e o falso positivo custa mais que a fuga. O critico da r2 validou a recusa buscando ocorrencias reais. |
| MEDIA | escopo do gate (i) | README fora do escopo. Mantido, agora DECLARADO com o motivo: nao tem trecho que dispare, e ampliar sem necessidade medida contraria a regua §0. |
| BAIXA | tools/test_marketing_claims.py | branch 'href=' apontado como morto na r1; a r2 verificou e nao o encontrou — a reescrita do TEM_FONTE ja o havia removido. Discrepancia reportada pelo proprio critico em vez de aceita. |

## Verificacoes executadas (anti-fabricacao)

- r1: executou 4 padroes de prosa honesta e provou falso positivo em todos
- r1: mapeou as classes de fuga e exigiu que o limite fosse nomeado, nao resumido
- r2: reexecutou os 4 FP e confirmou que fecharam
- r2: buscou FP NOVO criado pela ampliacao do regex — nao achou exploracao viva na vitrine real
- r2: validou a recusa da conjugacao singular contra prosa real do repo (ADR-065, ADR-094)
- r2: provou em copia fora do repo que o auto-teste nao cobria a fiacao
- autor: mutacao cegando o padrao inteiro -> auto-teste apita
- autor: mutacao reinserindo o caso fabricado na vitrine -> gate reprova
- autor: mutacao esvaziando o laco de arquivos (exploit da r2) -> gate reprova
- suite completa: 80 PASS, 1 SKIP, 0 FAIL
