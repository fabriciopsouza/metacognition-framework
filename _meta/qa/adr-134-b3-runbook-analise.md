# QA-evidence — adr-134-b3-runbook-analise

- **Data:** 2026-11-24
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | tools/runbook_analise.py _r7_status | Codex r1: 'Feito ' com espaco passava; lido sem normalizar. |
| ALTA | tools/runbook_analise.py _r9_painel | Codex r1: formula comparada sem espacos; comparacao exata. |
| MEDIA | tools/runbook_analise.py _r3_passos | Codex r1: linhas ordenadas; R3 nomeia a causa e o molde manda filtrar, nao ordenar. |
| MEDIA | tools/runbook_analise.py _r11_colar | Codex r1: formula fora do Painel excedia a regra; retirada; campos a marcar nascem como texto. |
| MEDIA | tools/runbook_analise.py ler_conteudo | Codex r1, Sonnet r2, Codex r3: caractere invalido em XML (textos, chaves e nomes de aba), roteiro vazio e aninhamento profundo dao exit 2. |
| MEDIA | tools/runbook_analise.py _r8_visual | Codex r1: regra sem cor; confere a cor do molde. |
| MEDIA | tools/runbook_analise.py _r4_faca | Codex r1: '2.' depois de 'Deu certo'. |
| MEDIA | tools/templates/runbook-analise.json | Codex r1 e Sonnet r2: 8 campos da ficha, termos, --sep no dedup, marcas no 5.2. |
| MEDIA | .agent/skills/analise-dados/pacote-documental.md | Codex r1: analise do existente em N3 = se. Sonnet r2: comandos com pasta e caminho completo. |
| BAIXA | tools/runbook_analise.py _r14_massa | Sonnet r2: em massa Feito exige os tres Feitos; Substituido nunca conta. |
| MEDIA | tools/test_runbook_analise.py | Sonnet r4: canario cego ao texto do modelo e ao achado 9; conferencias e sabotagens novas. |

## Verificacoes executadas (anti-fabricacao)

- tools/test_runbook_analise.py PASS; sabotagem do plano (Roteiro sem a coluna Status) reprova pela linha de comando
- mutacoes do autor em copia: 74 no conjunto (71 reprovadas, 3 eram codigo redundante removido), 19 no delta (todas reprovadas), 8 no texto do modelo (todas reprovadas)
- Excel desta maquina: abriu, recalculou o Painel (1.1 Feito, 1.2 Pulado, 1.3 Erro: onde parei 1.3, erros 1, fase 33%, Substituido desconta o total), salvou; conferir PASSA no arquivo salvo; resposta '=1+1' ficou texto (alertas do Excel desligados: aviso de reparo nao observavel)
- regressoes: test_analise_dados, test_skill_contract, validate_skills, test_capabilities, test_web_export, test_marketing_claims, test_core_no_vendor, test_core_agnostic, test_planilhas_projeto, test_adr_changelog_sync PASS
- handoff identico ao do commit c1fd22d, sem dado de empresa (r2)
