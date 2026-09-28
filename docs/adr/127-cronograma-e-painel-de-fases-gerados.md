# ADR-127 — Cronograma e painel de fases gerados do arquivo único

- **Status:** Aceito
- **Data:** 2026-09-28
- **Decisores:** dono (Fabricio), 28/09/2026:
  - D5 "a": um bloco único, com cronograma e painel por fase gerados do `spec.md` e verificador;
  - D6 "a": este bloco antes do perfil ANP.

  Autoria: Opus 5.5.
- **Relação:**
  - fecha o REQ-07 e o critério 9 do plano B3 (`docs/specs/b3-documentacao-regulada/spec.md`, T16);
  - fecha o trabalho `painel-de-fase-gerado`;
  - estende o verificador do plano (ADR-125) e segue o arquivo único (ADR-117).

## Contexto
Quatro pendências de acompanhamento de projeto estavam abertas:
1. cronograma gerado (REQ-07);
2. painel por fase verificável;
3. status curto por resposta (B2.6);
4. página visual do painel (B2.7).

O painel por fase era escrito à mão. Numa medição de 23/09/2026, dois percentuais mentiam por 10 e 11 pontos, com a barra coerente com o percentual errado.

Ao gerar o painel do plano B3, o REQ-07 apareceu como 100% concluído. Ele não tinha tarefa, então não entrava na contagem.

## Decisão
1. **`python tools/plano.py painel <spec.md> [--escrever]`** gera, a partir das Tarefas, uma tabela por fase (`### ` das Tarefas). Cada linha traz:
   - feitas/total;
   - barra de 12 blocos;
   - percentual;
   - a marca "◀ onde estamos" na primeira fase aberta.

   `--escrever` grava a tabela entre `<!-- painel:inicio -->` e `<!-- painel:fim -->`, logo abaixo de `## Painel`.
2. **`python tools/plano.py cronograma <spec.md> [--csv <arquivo>]`** lista as tarefas por prazo, deixando as sem prazo por último. Tarefa aberta com prazo vencido sai ATRASADA, e o CSV (separador `;`) abre direto no Excel. A sintaxe na linha da tarefa é `prazo: dd/mm/aaaa` e, se houver dependência, `depende: T1, T2`.
3. **`plano.py verificar` passa a reprovar:**
   - painel entre os marcadores diferente do que as tarefas geram, seja % editado à mão ou tarefa marcada sem regenerar;
   - prazo ilegível;
   - dependência inexistente;
   - prazo anterior ao da dependência.

   O verificador não depende da data de hoje: o atraso aparece só na saída do cronograma.
4. **O critério 9 muda de fonte:** o cronograma sai da linha da tarefa no `spec.md`, não do `estado.json`. Esse arquivo é do lançamento no portal (`controle_projeto.py`).
5. **O plano B3 ganhou a tarefa que faltava (T16)** e o painel gerado.

## Régua §0
Critério (c): painel e cronograma deixam de ser prosa mantida à mão e passam a ser derivados e verificados. O bloco estende `plano.py`, sem ferramenta nem capacidade nova.

## Fora deste bloco
- **B2.6:** status curto com link do painel em toda resposta. Continua parcial, pelo hook de resposta executiva do ADR-123.
- **B2.7:** página visual do painel. Depende da decisão D6 do plano modo planejado.
- **Ciclo de dependências:** não é detectado. T1 → T2 → T1 com prazos iguais passa.
- **Painéis antigos sem marcadores** (fora de `docs/specs`) não são auditados até serem regenerados.
- **Fase com todas as tarefas `[~]` (replanejadas) não aparece no painel.** Ela está registrada no Replanejamento,
  que o verificador já cobra.

## Prova
- `tools/test_plano.py`:
  - (f) painel:
    - gerado e intacto passa;
    - % editado reprova;
    - tarefa marcada sem regenerar reprova;
    - `--escrever` insere sem duplicar;
    - marcadores duplicados ou invertidos reprovam;
    - tarefa dentro de bloco de código não conta;
  - (g) cronograma:
    - ordena por prazo e marca atraso;
    - mudança de data muda o cronograma (critério 9);
    - ponto final depois do id não gera falso achado;
    - prazo ilegível, dependência inexistente e prazo fora de ordem reprovam;
  - (e) as specs reais passam.

## Estado do QA
| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| 1 | Sonnet isolado (acf6de8e52082714f) | FAIL | ALTA: `depende: T1.` capturava o ponto e acusava dependência inexistente. MÉDIA: tarefa dentro de bloco de código contava. BAIXA: marcadores invertidos ou duplicados passavam calados. BAIXA: fase só com `[~]` somia sem registro. 6 de 6 mutações mortas. | pontuação removida do id; `_blocos` ignora código (causa, vale para todas as seções); marcador inválido vira achado e `--escrever` recusa; limite declarado; 4 testes novos |
| 2 | Sonnet isolado (a4e62c12c7ca1ba26) | PASS | nenhum; correções generalizadas (`T1;`, `T1-`, `T1, T3.`); sem regressão em `_blocos`; 4 de 4 mutações mortas | — |
