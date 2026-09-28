# ADR-125 — Verificador do plano no arquivo único

- **Status:** Aceito
- **Data:** 2026-09-28
- **Decisores:** dono (Fabricio):
  - 25/09/2026, plano modo planejado, B2b: "sim todos";
  - 27/09/2026: verificador do plano geral para todos.

  Autoria: Opus 5.5.
- **Relação:** executa o B2b do plano `docs/specs/plano-modo-planejado/PLANO.md` (B2.2 e B2.3b). Lê o arquivo único
  (ADR-117) com `spec_fonte`.

## Contexto
O painel e as tarefas da especificação são o que o dono lê para decidir. Nenhuma ferramenta conferia se o que
estava escrito ali era coerente. Rodando o verificador pela primeira vez, as duas especificações reais do repositório
tinham 18 achados:
- tarefas marcadas como feitas sem a prova citada;
- itens do mapa de impacto que mudavam e estavam sem situação.

## Decisão
1. **`python tools/plano.py verificar [<spec.md> ...] [--avisar]`** reprova:
   - seção obrigatória ausente;
   - decisão pendente no Painel sem "Quem age";
   - tarefa `[x]` sem prova (a palavra "prova", um PR ou um arquivo entre crases);
   - tarefa `[~]` sem linha no Replanejamento;
   - % do Avanço diferente da contagem das tarefas do bloco em mais de 5 pontos;
   - mapa de impacto sem linhas, ou item que muda sem situação;
   - aceite datado antes da aprovação dos requisitos.
2. **Neste repositório barra:** o canário `test_plano` roda o verificador sobre todas as especificações reais, e o
   plano enganoso derruba a suíte. **Nos outros repositórios avisa:** `--avisar` (decisão D1 do plano, 25/09).
3. **Regra 06:** o plano vive no Painel do arquivo único, verificado por esta ferramenta.
4. As duas especificações reais foram corrigidas: provas citadas e situação do mapa de impacto preenchida.

## Fora deste bloco
- **B2.6:** status curto com link para o painel em toda resposta. Parcialmente coberto pelo ADR-123 (resposta
  executiva).
- **B2.7:** página visual do painel; depende da decisão D6 do plano.

## Régua §0
Critério (c): regra que era prosa (painel coerente) vira verificação. Adiciona 1 ferramenta e 1 canário.

## Limites
- **"Prova" é verificada pela forma**, não pelo conteúdo: a palavra, um PR ou um arquivo citado. Uma prova falsa com
  a forma certa passa; a revisão adversarial continua sendo quem a confere.
- **O % só é comparado quando o nome do bloco no Avanço bate com um `### <bloco>` das Tarefas.**

## Prova
- `tools/test_plano.py`:
  - plano coerente passa;
  - 8 sabotagens reprovam;
  - 2 exceções legítimas passam;
  - `--avisar` não bloqueia;
  - todas as especificações reais passam.

## Estado do QA
| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| 1 | Sonnet isolado (a154afe401cad9da1) | PASS | nenhum novo; os 2 falsos negativos achados (prova pela forma; % só com nome de bloco igual) já estão em Limites; provas das specs reais conferidas; 3 mutações mortas | — |
