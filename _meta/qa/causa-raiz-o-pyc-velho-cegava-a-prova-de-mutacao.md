# QA-evidence — causa-raiz-o-pyc-velho-cegava-a-prova-de-mutacao

- **Data:** 2026-09-23T18:03:25Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | tools/test_mutacao_squad_gate.py (execucao das mutacoes) | O Python invalida __pycache__ por mtime + TAMANHO. A mutacao all->any tem o mesmo tamanho e e' escrita milissegundos depois da restauracao anterior: colidindo o mtime, o .pyc do baseline e' reaproveitado e a mutacao NUNCA e' executada. O canario reportava SOBREVIVEU (0->0) para algo que nao foi testado. |
| MEDIA | CHANGELOG.md (bloco da prova de mutacao) | A hipotese ORIGINAL (cobertura de src/a.py caindo por ambiente) ficou no arquivo logo abaixo da retratacao, sem ponte: lido de cima para baixo, o texto parecia apresentar duas explicacoes convivendo, quando uma refuta a outra. |
| BAIXA | tools/test_mutacao_squad_gate.py (_prova_que_o_cache_nao_cega) | No caminho feliz, com a env var valendo, o primeiro roda() nao escreve __pycache__ — entao o utime e o rmtree nao tem com o que colidir, e a funcao devolve True porque o fonte novo e' lido direto. O docstring prometia testar a colisao de mtime, que naquele caminho nao acontece. |
| BAIXA | diagnostico anterior deste mesmo bloco | A explicacao anterior (as quatro provas negativas passando por vacuidade quando a cobertura de src/a.py cai) NAO foi a causa deste incidente. Ela estava registrada como INFERIDA, e foi isso que impediu que virasse fato. |

## Verificacoes executadas (anti-fabricacao)

- o critico REPRODUZIU a causa por conta propria, fora do repo, sem partir da explicacao do autor: modulo com all -> .pyc -> reescrita com any do mesmo tamanho + os.utime -> processo seguinte executa all; com PYTHONDONTWRITEBYTECODE=1 e cache limpo executa any
- suite completa rodada DUAS vezes na rodada: test_squad_gate.py 96/96 e test_mutacao_squad_gate.py 37/37, exit 0, em 2m50s (dentro do intervalo das rodadas anteriores: sem overhead)
- grep confirmando que nenhum teste inspeciona __pycache__/.pyc ou lista tools/ — desligar bytecode nao muda comportamento de teste nenhum
- as 37 entradas de MUTACOES iteradas comparando `de` e `para` por caracteres E por bytes UTF-8
- instrumentacao de _prova_que_o_cache_nao_cega com o env de producao para observar se o .pyc chega a existir
