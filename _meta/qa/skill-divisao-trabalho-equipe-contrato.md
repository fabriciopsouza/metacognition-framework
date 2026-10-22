# QA-evidence — skill-divisao-trabalho-equipe-contrato

- **Data:** 2026-10-22T13:30:32Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** inline: pedido literal do dono em 22/10/2026, implementacao de referencia no ssma-plataforma
- **RRC:** N/A: skill de metodo, sem fonte normativa
- **Metodo-senior:** N/A: sem fonte canonica nova

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| MEDIA | SKILL.md passo 6 | nomes localizados AGREGAR/MINIMOSES; trocados por _xlfn.AGGREGATE/_xlfn.MINIFS |
| MEDIA | agenda_equipe.py | sem validacao: dias vazios, horas invalidas, coringa sem aprendiz; _conferir() acrescentado |
| MEDIA | SKILL.md | limitacao do coringa Aprendiz (qualquer) declarada |
| BAIXA | capabilities.json | skill fora do capabilities.json, debito geral compartilhado com painel-status |

## Verificacoes executadas (anti-fabricacao)

- leitura SKILL.md e skills irmas
- diff contra a implementacao de referencia (so docstring)
- execucao isolada de planejar() com feriado, coringa, dependencia e apos_dependencias
- autor: guardas testados (dias_semana vazio e coringa sem aprendiz recusados)
- apos o QA: so o cabecalho de contrato (pass_criteria, confidence_required, enforcement, shared_refs) foi acrescentado, no molde do painel-status; test_skill_contract.py PASS
