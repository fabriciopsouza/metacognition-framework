# QA-evidence — prova-de-mutacao-que-passava-pelo-motivo-errado

- **Data:** 2026-09-23T17:23:46Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| MEDIA | tools/test_mutacao_squad_gate.py + tools/test_squad_gate.py (provas da uniao) | A causa-raiz da variancia de ambiente no ubuntu NAO foi identificada, apenas contornada: medido em 9 runs, windows e macos nunca falham a mutacao e o ubuntu falhou em 5 de 7 runs de 22/09. A correcao conserta a PROVA, nao a variancia. |
| MEDIA | tools/test_squad_gate.py (controle positivo) | O controle positivo aumenta o raio: quando a cobertura cair, o baseline fica vermelho e as 37 mutacoes sao abortadas sem nenhuma ser testada, em vez de uma unica sobreviver em silencio. Trade-off defensavel, mas nao estava declarado em lugar nenhum do diff. |
| MEDIA | tools/test_mutacao_squad_gate.py (dump de sobrevivencia) | O dump das ultimas 6 linhas erra nos dois sentidos: no caso 0->0 falhas so mostra a linha RESULTADO, e no caso em que haveria o que mostrar um unico traceback empurra a linha 'FAIL <nome>' para fora da janela. |
| BAIXA | tools/test_mutacao_squad_gate.py:259-263 | _nomes_que_falharam aceitava qualquer linha iniciada por 'FAIL ', inclusive 'FAIL filtro pede teste(s)...' e 'FAIL barreira-de-completude: ...', que nao sao nomes de teste. |
| BAIXA | tools/test_squad_gate.py:551-567 | test_git_que_FALHA_nao_e_o_mesmo_que_nada_staged monkeypatcha sg.subprocess.run diretamente em vez de usar o helper do proprio arquivo. Seguro hoje (try/finally), pre-existente a esta mudanca. |
| BAIXA | diagnostico do autor | A explicacao de que a cobertura de src/a.py e o pivo permanece INFERIDO: o critico nao roda ubuntu e nao conseguiu observar a queda de cobertura ao vivo. |

## Verificacoes executadas (anti-fabricacao)

- python tools/test_squad_gate.py -> 96 PASS / 0 FAIL
- python tools/test_mutacao_squad_gate.py -> 37/37 mutacoes mortas (~2m52s)
- mutacao all->any reproduzida MANUALMENTE em copia isolada fora do repo (git init fresco em scratchpad)
- logs reais de 9 runs do GitHub Actions (gh run view --log), 21 a 23/09/2026, nas tres plataformas
- parse de _nomes_que_falharam confrontado com o formato real impresso por _rodar_sem_pytest
