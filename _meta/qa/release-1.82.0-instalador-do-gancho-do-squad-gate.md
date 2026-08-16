# QA-evidence — release-1.82.0-instalador-do-gancho-do-squad-gate

- **Data:** 2026-08-16T12:40:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas
- **Fecha release:** v1.82.0

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** medicao do que ja existia do ADR-092 antes de escrever qualquer linha — 3 das 4 pecas ja estavam prontas desde junho
- **RRC:** PASSA — o critico foi ler o codigo do squad_gate para descobrir o que ele devolve, em vez de aceitar a premissa do gancho; foi exatamente isso que revelou o defeito. E descartou duas suspeitas proprias por falta de cenario reproduzivel.
- **Metodo-senior:** N/A: fecha peca faltante de ADR ja desenhado.

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| alto | tools/install_git_hooks.py (constante CORPO) | CORRIGIDO. O gancho tratava qualquer codigo 1 como 'falta evidencia'. O squad_gate devolve 1 tambem quando quebra, entao ferramenta com defeito barraria todo commit com mensagem errada — o oposto da decisao de desenho declarada no proprio arquivo. |
| baixo | tools/install_git_hooks.py (deteccao por linha-marca) | NAO corrigido, declarado. Um pre-commit alheio que por acaso contenha a linha-marca seria tratado como nosso. O critico levantou e descartou por nao construir cenario concreto; fica como limite conhecido. |

## Verificacoes executadas (anti-fabricacao)

- R1 reproduziu o achado ALTO: `python -c "import squad_gate; squad_gate.load_manifest('inexistente')"` -> returncode 1 com traceback nao tratado, indistinguivel do bloqueio legitimo
- R1 confirmou que `estado()` ja e' defensivo contra symlink e arquivo ilegivel (OSError -> 'alheio', impede sobrescrita)
- R1 confirmou o tratamento de core.hooksPath absoluto, relativo e vazio
- R1 provou a falsificabilidade do canario por conta propria: sabotando `estado()` para devolver sempre 'ausente', 6 das 15 verificacoes caem; restaurado, volta a 15/15 com `git diff --stat` sem diferenca contra o indice
- correcao: o gancho passa a exigir a marca '[squad-gate] BLOQUEADO' na saida; codigo 1 sem a marca = gate quebrado -> commit LIBERADO com aviso
- autor: prova de mutacao da guarda nova — sabotando o `case` que exige a mensagem, o caso novo vira [FALHA] e o canario sai com 1; restaurado, 16/16
- dogfooding: o gancho foi instalado neste repo e BLOQUEOU o commit deste proprio trabalho por falta de veredito — o que obrigou a rodar o critico antes de commitar, invertendo a ordem para a correta
- suite antes do veredito: 72 PASS / 1 SKIP / 0 FAIL de 73 canarios
