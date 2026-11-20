# QA-evidence — adr-134-analise-acompanhada-b1

- **Data:** 2026-11-20T02:23:54Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | tools/handoff.py | Codex r1: pacote transportava autonomo como vigente para sessao nova. Agora 'Modo vigente na proxima sessao: acompanhado'; autonomo da origem so historico, sem autorizacao. |
| MEDIA | tools/handoff.py build() | Codex r1: API aceitava autonomo sem origem. ValueError no build(); exit 2 na CLI; testes de API e CLI. |
| MEDIA | .agent/skills/analise-dados/SKILL.md | Codex r1: description excluia validacao contra referencia, contra o gatilho global. Skill conduz e usa validation-reporting como metodo. |
| MEDIA | tools/test_analise_dados.py | Codex r1: canario da regra global aceitava padrao invertido e falta de gatilho. 4 padroes + lookbehind; sabotagens novas. |
| MEDIA | tools/web_export.py | Codex r1: pacote web fora do B1 (desvio do plano). Skill em LATERAL; contagem do README calculada; canario confere. |
| BAIXA | docs/adr/134-analise-acompanhada.md | Codex r1: T1 a T10 -> T1 a T9 + T10 pela frase literal. |
| BAIXA | tools/web_export.py | Sonnet r2: skill gerada so tinha a linha do explorer; linha propria para analise-dados (nao read-only). |
| BAIXA | tools/test_analise_dados.py | Sonnet r2: verificacao LATERAL sem sabotagem no autoteste; acrescentada. |
| BAIXA | tools/test_elicitation_gate.py; tools/test_web_export.py | Sonnet r2: residuos SEIS_CAMPOS e 'esperado 15'; renomeado e mensagem calculada. |
| MEDIA | capabilities.json analise-acompanhada.mutacao | bateria completa (test_audit_enforcement): mutacao apontava a regra global, nao o mecanismo declarado (a skill). Mutacao movida para a tabela de classes da skill; 37/37. |
| MEDIA | guia/web/index.html secao #provas | bateria completa (test_marketing_claims): numeros da vitrine defasados com a capacidade nova. 77 de 118 provadas, 103 canarios, conta fecha em 118. |
| INFORMATIVO | E10 do b1-spec | bootstrap e teste de ativacao 3/3 e 0/3 sao operacao pos-merge (fora do diff), nao prova por script. |

## Verificacoes executadas (anti-fabricacao)

- 14 canarios de aceite exit 0: test_elicitation_gate, test_handoff, test_rules_parity, test_elicitation_catalog, test_adr_changelog_sync, test_skill_contract, validate_skills, test_capabilities, test_web_export, test_premium_tier, test_discovery_eval, test_core_no_vendor, test_analise_dados, check_core_agnostic
- 10 sabotagens em copia da worktree, todas reprovaram pelo motivo certo: S1a/S1b/S1c (ficha sem campo 7, sem campo 8, sem paragrafo do disparo), S2a/S2b/S2c (handoff sem secao modo, autonomo sem origem aceito, autonomo transportado como vigente), S3a/S3b/S3c (regra global sem a skill, skill sem classe, discovery sem linha do sub-modo), S4 (pacote web sem a skill)
- autoteste de test_analise_dados com 13 sabotagens internas
- web_export gerado: 16 skills, SKILL.md de analise-dados presente
- bateria completa run_canaries.py no estado final: 102 PASS, 1 SKIP (test_parity, igual a base), 0 FAIL de 103; base antes do B1: 101 PASS, 1 SKIP, 0 FAIL de 102
