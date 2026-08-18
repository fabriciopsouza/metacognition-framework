# QA-evidence — adr-108-procedencia-do-veredito

- **Data:** 2026-08-18T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** —
- **RRC:** PASSA - o critico nao perguntou se o mecanismo funciona, perguntou se ele e teatro, e reprovou cinco vezes seguidas ate a resposta parar de ser uma regex melhor. Na 6a, recomendou explicitamente NAO perseguir o residual — que e' o oposto de inflar achado para parecer util
- **Metodo-senior:** —

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| alto | tools/verify_qa_attestation.py (veredito_do_relatorio) | CORRIGIDO ao longo de 5 rodadas. A leitura da conclusao por heuristica de posicao foi abandonada; a conclusao passou a ser um sentinela UNICO, com ambiguidade resolvida por contagem. |
| alto | tools/verify_qa_attestation.py (agentId, dedup, autor, rollup) | CORRIGIDOS. agentId ancorado no trailer; dedup de provas; autor por sessao; rollup com N provas e categorias nao-limpas concatenadas. |
| medio | tools/verify_qa_attestation.py (limite declarado) | ACEITO COMO LIMITE, por recomendacao explicita do critico. Um relatorio que NUNCA escreve o proprio sentinela e cita um exemplo ('o formato e assim: <<<...>>>') tem exatamente um sentinela e ele e o ultimo — as duas propriedades verificadas. Nenhuma regra de posicao ou contagem distingue exemplo de conclusao quando tem forma identica. Persegui-lo com mais regex repetiria o erro das rodadas 1-5. Declarado no ADR. |
| medio | tools/verify_qa_attestation.py (custo de sem_leitura) | ACEITO COMO DIVIDA com criterio de monitoramento dado pelo critico: sem_leitura e ressalva saem com o mesmo exit 3 e a mesma linha. Se sem_leitura continuar sendo maioria DEPOIS de a norma ter tido tempo de pegar em relatorios novos, e sinal de evasao, nao de legado. |

## Verificacoes executadas (anti-fabricacao)

- 6 rodadas com reproducao em codigo de cada vetor, sempre em copias fora do repo
- os 5 vetores derrubados foram convertidos em casos de canario e provados por reversao
- regex do sentinela atacada em 8 eixos (case, espacos, >>> extra, negacao dentro, quebra de linha, colagem sem boundary)
- rollup com sem_leitura + ressalva + verificado juntos: precedencia conferida
- run_canaries: 77 PASS / 1 SKIP / 2 FAIL esperadas; canario do bloco 34/34
