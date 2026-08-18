# QA-evidence — release-1.88.0-nenhuma-capacidade-declara-bloquear-sem-prova

- **Data:** 2026-08-17T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar
- **Fecha release:** v1.88.0

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** o passivo foi MEDIDO antes de ser atacado, e a medicao mudou o plano: descobriu-se que ele nao era homogeneo (9 triviais x 8 estruturalmente improvaveis), o que separou o trabalho em dois lotes com solucoes diferentes
- **RRC:** PASSA - o critico nao perguntou se os canarios passam (passam por construcao), perguntou se o auto-teste exercita a MESMA funcao que roda em producao, que e a unica coisa que faz a fixture significar algo; e conferiu as duas direcoes de cada uma
- **Metodo-senior:** file-first antes de afirmar (o PR #118 dado como pendente ja estava na main; a memoria sobre o GHA morto estava desatualizada); sabotagem manual com restauracao verificada por hash em vez de confiar no relatorio do proprio auditor

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| medio | tools/test_audit_enforcement.py (caso i-l) | CORRIGIDO na R1. Trava por AST exigia so a existencia do keyword encoding, nunca o valor; encoding=None reintroduziria o bug original e passaria. Passou a exigir ast.Constant utf-8, provado contra os dois cenarios. |
| medio | docs/adr/106-prova-de-mutacao-para-capacidade-fail-closed.md | CORRIGIDO na R1. Codigo nomeava EMENDA 5 sem que o ADR a registrasse, quebrando o padrao das emendas 1-4. |
| baixo | tools/audit_enforcement.py | ACEITO COMO DIVIDA. O auditor detecta trecho-de que SUMIU (mutacao obsoleta) mas nunca trecho-de que DUPLICOU: se um commit adicionar uma 2a ocorrencia, o replace com count=1 sabota o trecho errado em silencio. Registrado como proximo passo no trabalhos.py. |

## Verificacoes executadas (anti-fabricacao)

- 29/29 provas de mutacao formais apos o commit (audit_enforcement --provar sem --id): todos os canarios ficaram vermelhos pelo motivo declarado
- R2 aplicou as 8 mutacoes do lote 3 manualmente e restaurou com verificacao de sha256 antes/depois
- confirmado que main() e autoteste() chamam a MESMA funcao extraida nos 8 canarios refatorados
- confirmado que os 8 autotestes cobrem as duas direcoes (pega o sujo E nao acusa o limpo)
- ambiguidade de trecho-de conferida nas 29 capacidades com mutacao: todas count==1
- test_consistency_closing.py: as 5 checagens originais seguem executando apos o refactor de main()
- vitrine recalculada do zero: 29+0+27+34=90; 29/90=0,322 confirma 'menos de um terco'
- run_canaries.py: 77 PASS / 1 SKIP / 0 FAIL (78)
