# QA-evidence — skill-painel-status-links

- **Data:** 2026-10-21T20:17:05Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Steelman
texto continua escapado antes do link; so https vira link; correcoes A1/A2 cobertas por casos dirigidos

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| MEDIA | painel-template.html lk() | A1: endereco terminando em & ganhava ';' no texto visivel (o laco de pontuacao final tirava o ';' de '&amp;') |
| BAIXA | painel-template.html lk() | A2: regex sem ancora; 'xhttps://x.com' virava link |
| BAIXA | SKILL.md | A3: reticencias, aspas tipograficas e U+200B colados ao fim entram no link |
| BAIXA | processo | teste Playwright fora do repositorio; sem canario proprio da skill |

## Verificacoes executadas (anti-fabricacao)

- critico r1 (a7c141ca6dc7886bd): revisao read-only dos 3 arquivos; nenhuma injecao; achados A1-A3
- autor apos r1: painel-links-teste.py (Playwright, 390/1366 x claro/escuro, inclui a&, a&;, a&&, xhttps://, 1https://) FALHAS 0 no template do framework e na copia local; controle contra o template anterior falha
- autor apos r1: tools/run_canaries.py 98 PASS 1 SKIP 0 FAIL (de 99)
- autor: validate_skills, test_skill_contract, test_core_no_vendor, test_core_agnostic, test_adr_changelog_sync PASS (antes da r1; mudanca da r1 restrita a lk() e prosa)
- blobs_revisados omitido: as correcoes A1/A2/A3 foram aplicadas depois da r1 e nao foram revisadas pelo critico
