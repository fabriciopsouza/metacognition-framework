# Handoff — sessão nova, OUTRA conta, MESMA pasta (2026-08-18)

> Complementa o P14 determinístico (`python tools/handoff.py`). Aqui está só o que o
> gerador **não tem como saber**: o que muda por a próxima sessão rodar sob outra conta
> de usuário na mesma pasta.

## Estado

- `main` @ `b895643`, limpa, em dia com `origin`. Tag **v1.90.0** publicada.
- Suíte: **79 PASS · 1 SKIP · 0 FAIL** (de 80).
- Capacidades: **91 · 0 no passivo · 53 com sabotagem provada**.
- Nada pendente de commit ou push. Nenhum PR aberto.

## O que esta sessão entregou

| release | o quê |
|---|---|
| v1.88.0 | classe "declara fail-closed e nunca foi provada" → **0** (as 8 de `mechanism == test`) |
| v1.89.0 | as 34 sem campo `enforcement` classificadas → **passivo do registro = 0** |
| v1.90.0 | **ADR-108**: o registro do QA deixa de ser escrito só pelo avaliado |

O v1.90.0 levou **6 rodadas adversariais, 5 REPROVAR**. A leitura da conclusão do crítico
abandonou heurística de posição e virou **contrato**: sentinela único (`rule #13` do
qa-critic), com ambiguidade resolvida por **contagem**.

## ATENÇÃO — o que muda ao trocar de conta (medido, não suposto)

Quatro coisas do framework moram em `~/.claude/`, ou seja, **na conta**, não na pasta:

1. **Transcripts** (`~/.claude/projects/<slug>/`) — 16 arquivos, nesta conta.
   `verify_qa_attestation.py` os lê para provar procedência. Na outra conta eles **não
   existem**, então os 19 vereditos hoje provados vão aparecer como **`legado`**, com a
   mensagem *"transcripts indisponíveis nesta máquina — não verificado (declarado)"*.
   **Isso NÃO é regressão** — é o fail-safe correto, já verificado por simulação. Não
   tente "consertar": a procedência é local por design (ADR-108, limite declarado).

2. **Registro de trabalhos** (`~/.claude/trabalhos/`) — 12 registros, nesta conta.
   Na outra conta o boot **não vai oferecer** nenhum trabalho aberto. O relevante desta
   sessão está resumido abaixo, então nada se perde; mas não conclua "não há trabalho
   aberto" só porque a lista veio vazia.

3. **Auto-boot do squad** (`~/.claude/squad-owners.txt`) — se ausente na outra conta, o
   PMO não acorda sozinho. Basta dizer **"iniciar"** ou rodar `/start-session`.

4. **Modo de execução** (`~/.claude/framework-mode.json`) — hoje `autosuficiente`. Na
   outra conta volta ao default até ser reconfigurado.

Além disso: `git config user.name/email` é global por conta. Confira antes de commitar,
senão os commits saem com outro autor.

## Próximo passo de maior valor

**Amarrar `verify_qa_attestation.py` ao `squad_gate` como BLOQUEIO.** Hoje ele roda,
mede e reporta — mas não impede commit. É a diferença entre **medir** e **barrar**, que é
exatamente a distinção que este trabalho inteiro perseguiu.

Critério de aceite: um veredito com `agentId` que não existe no log de transcripts deve
**bloquear** o commit, e o canário deve provar que bloqueia (sabotagem + vermelho).
Cuidado: preservar o fail-safe do item 1 acima — máquina sem transcripts não pode virar
bloqueio, senão o gate trava qualquer clone.

Outras pendências, em ordem de valor: validar `escopo_paths` contra o que o crítico de
fato leu; mecanizar a exigência 3 do ADR-106 (coerência entre o adjetivo do índice e o
campo `enforcement`).

## Limites declarados — NÃO perseguir

Estão escritos no ADR-108 e no código. Em especial, um foi **explicitamente desaconselhado
pelo crítico**: um relatório que nunca escreve o próprio sentinela e cita um exemplo tem
exatamente um sentinela e ele é o último — as duas propriedades verificadas. Nenhuma regra
de forma distingue exemplo de conclusão. Persegui-lo com mais regex **repete o erro das
rodadas 1-5**. É julgamento irredutível, não regra faltando.

Critério de monitoramento (também do crítico): se `sem_leitura` continuar sendo maioria
**depois** de a norma ter tido tempo de pegar em relatórios novos, isso é evasão, não
legado.

## Validar em 3 comandos

```
python -X utf8 tools/run_canaries.py            # espera 79 PASS / 1 SKIP / 0 FAIL
python -X utf8 tools/audit_enforcement.py --passivo   # espera 91 conformes, 0 no passivo
python -X utf8 tools/verify_qa_attestation.py   # na outra conta: tudo legado (esperado)
```

Rode Python sempre com `-X utf8`: o console é cp1252 e quebra nos acentos das mensagens.
