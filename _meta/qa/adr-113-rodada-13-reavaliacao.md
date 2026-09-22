# QA-evidence — adr-113-rodada-13-reavaliacao

- **Data:** 2026-08-29T00:00:00Z
- **Veredito (passou):** False
- **Recomendacao:** reprovar

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** —
- **RRC:** —
- **Metodo-senior:** —

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | docs/adr/113-politica-de-lancamento-de-projeto-como-pacote-resolvido.md (cabecalho) + tools/test_numeros_controle.py (familia de mutacao) | numero estale no resumo executivo, escapando do detector pelo SINONIMO ('correcoes' onde o padrao exigia 'defeito'). Corrigido nas duas metades: prosa passa a dizer 34 e a referenciar a rodada certa; a familia passa a cobrir defeitos\|correcoes com concordancia provad\w+, mais seis auto-testes. |
| ALTA | tools/verify_qa_attestation.py — mecanismo de procedencia do ADR-108 | achado do AUTOR durante o registro deste veredito, nao do critico. Subagente lancado em background deixa no transcript o AVISO DE LANCAMENTO (1099 chars), nao o relatorio; um prova_transcript calculado sobre ele casaria e ficaria verde provando nada. Medido: 57 execucoes, 21 stubs; 24 vereditos com agentId+prova, 16 lastreados no relatorio real e 8 no stub (releases 1.80.1 x2, 1.81.0, 1.83.0, 1.84.0, 1.85.0, 1.86.0, 1.87.0). NAO corrigido neste bloco — aguarda decisao do dono. |
| MEDIA | docs/adr/113-politica-de-lancamento-de-projeto-como-pacote-resolvido.md (byte 11695) | achado do AUTOR antes de chamar o critico: um byte NUL literal gravado no markdown fazia o grep tratar o ADR inteiro como binario, escondendo todas as suas linhas de qualquer busca. git diff o mostrava como texto normal, entao seria commitado assim. Corrigido para a sequencia de escape literal; grep volta a ler o arquivo. |

## Verificacoes executadas (anti-fabricacao)

- len(MUTACOES) em test_mutacao_controle.py = 34, contra o numero da prosa — divergencia confirmada por comando
- test_mutacao_controle.py rodado sob python 3.12.10 E python3 3.14.4: as 34 mutacoes detectadas nos dois
- suite dos 5 canarios do pacote sob codepage 850 com PYTHONIOENCODING nao definida: PASS
- grep por comparacao de data fora de _data() em controle_projeto.py e controle_sharepoint.py: zero
- grep por read_text/write_text/open(/.resolve()/mkdir( cru fora de controle_base.py: zero valor externo
- recontagem independente de 164/141+11/68 via grep -cE na saida real dos canarios: bate
- autor, com o padrao ampliado e a prosa ainda errada: test_numeros_controle.py exit 1 com 'a prosa diz 9 (mutacoes (medido: 34))'
- autor, apos corrigir a prosa: test_numeros_controle.py exit 0, e run_canaries 85 PASS, 1 SKIP, 0 FAIL
