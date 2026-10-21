# QA-evidence — skill-painel-status-cronograma

- **Data:** 2026-10-21T12:15:26Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Steelman
dado invalido nao quebra, secao some sem o campo (provado por pixels), CSS sem biblioteca; um canario versionado protegeria contra regressao futura

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| MEDIA | SKILL.md | r1 (agentId a992e9d4b2bf52845): citava cronograma-painel.json, inexistente no repo |
| BAIXA | painel-template.html per() | r1: texto do leitor de tela 'a em aberto' |
| BAIXA | painel-template.html eixo e rotulos | r1: ano omitido em periodo que cruza o ano |
| BAIXA | painel-template.html .cr-ml | r1: list-style:none sem role=list |
| BAIXA | SKILL.md | r1: 'vai ate hoje' sem hoje |
| BAIXA | processo | r1/r2: teste Playwright fora do repositorio; sem canario da secao |
| BAIXA | teste | r2: sem caso dirigido a periodo maior que 2 anos ou hoje em ano diferente; a logica cobre |

## Verificacoes executadas (anti-fabricacao)

- autor: testar.py (Playwright, 11 casos x 390/1366 x claro/escuro) FALHAS 0; sem rolagem horizontal; contraste minimo 6,29 claro e 6,08 escuro; sem o campo, DOM e pixels iguais ao template de origin/main
- autor: validate_skills.py PASS, test_skill_contract.py PASS, test_core_no_vendor.py PASS, test_core_agnostic.py PASS, test_adr_changelog_sync.py PASS
- critico r1 e r2: leitura dos 3 arquivos, reexecucao de testar.py (FALHAS 0), validate_skills e test_skill_contract PASS
