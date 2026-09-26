# QA-evidence — b2a-spec-arquivo-unico

- **Data:** 2026-09-26T02:27:27Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** inline: condicao do dono (um arquivo so se nenhum mecanismo quebrar e nenhuma informacao se perder) transformada em prova executavel antes do codigo; fotografia dos gates antes da mudanca
- **RRC:** PASSA
- **Metodo-senior:** N/A: mecanismo do proprio framework, sem fonte canonica regulada

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| CRITICO | tools/test_spec_unico.py perda_de_linhas | r1: a prova de perda zero buscava cada linha no arquivo inteiro; perda na Parte A escondida por linha igual na Parte D. Agora igualdade exata parte a parte, com caso (c2) que reproduz a mutacao da revisora. |
| ALTA | tools/spec_fonte.py | r1: cerca de codigo nao fechada engolia a Parte B; agora SpecInvalida (recusa). |
| ALTA | tools/spec_fonte.py | r1: titulo de parte com recuo de ate 3 espacos nao era reconhecido; regex corrigida. |
| ALTA | 4 gates + check_completeness._resolve | r1: pasta com os dois formatos contada duas vezes na varredura; sombreado_por_unico. |
| MEDIA | tools/check_context_brief.py | r1: Parte C incompleta calava o context-brief.md ao lado; regra de fonte unica declarada e mensagem explicita. |
| MEDIA | tools/spec_fonte.py | r1: parte repetida descartada em silencio; agora SpecInvalida. |
| BAIXA | .agent/skills/architect/SKILL.md | r1: consumes sem o arquivo unico. |
| ALTA | tools/qa_evidence.py append_junction | r2: spec.md malformado na J3 subia SpecInvalida sem tratamento; agora recusa ValueError com motivo, caso (f2). |

## Verificacoes executadas (anti-fabricacao)

- fotografia dos 4 gates nas 11 specs antigas antes/depois (autor) -> 0 diferencas na saida inteira, repetida apos as correcoes
- python tools/test_spec_unico.py -> PASS (autor e revisora, rodadas 1-3)
- sabotagens do autor: partes nao isoladas, cerca aberta aceita, parte repetida aceita, recuo nao reconhecido, conversor perde linha, varredura em dobro, J3 sem tratamento -> 7 de 7 vermelhas com o achado certo
- revisora r2: mutacao registrada em capabilities.json aplicada numa copia -> PASS vira FAIL(11)
- revisora r3: CLI qa_evidence --junction J3 com spec malformado numa copia isolada -> RECUSADO com motivo, exit 1, nenhum ledger
- test_spec_depth, test_completeness, test_context_brief, test_qa_evidence, test_capabilities, test_consistency_closing, test_marketing_claims -> PASS
