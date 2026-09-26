# ADR-117 — Especificação em arquivo único, sem quebrar gate nem perder informação

- **Status:** Aceito
- **Data:** 2026-09-25
- **Decisores:** dono (Fabricio) — *"se um arquivo não quebrar os mecanismos e se não houver perda de
  especificação/informação, etc. necessários, então UM. Se for provocar perda, então 3 + espelho"*;
  plano do B2 aprovado com D1–D4 e D6 (*"sim todos"*). Autoria: Opus 5.5.
- **Crítica adversarial:** Sonnet isolado, um degrau abaixo do padrão. Ver a seção Estado do QA.
- **Relação:** EMENDA o `/feature-plan` (grau completo) e o `readiness-gate` (R1). Não revoga o
  formato antigo: ele continua aceito por todos os gates.

## Contexto

Uma especificação de feature ocupava até 5 arquivos (`requirements.md`, `validation.md`,
`context-brief.md`, `mission.md`, `data-dictionary.md`). O dono pediu documentação mais simples e um
plano que se acompanha num lugar só. Medido em 25/09/2026: esses nomes são lidos por **5 scripts**
(`check_spec_depth`, `check_completeness`, `check_field_mapping`, `check_context_brief`,
`qa_evidence`) e citados como obrigatórios em workflows e skills (`feature-plan`, `readiness-gate` —
que **bloqueava** sem `requirements.md` —, `discovery`, `developer`, `qa-critic`, `implement`,
`handoff`, regra 04). Existem **11** especificações no formato antigo.

## Decisão

1. **Formato único** `spec.md`, com a marca `<!-- spec-unico:v1 -->` e partes em título de nível 1:
   `Parte A — Requisitos`, `B — Aceite`, `C — Contexto e âncoras`, `D — Missão`,
   `E — Dicionário de dados`. Antes das partes: painel, resumo executivo, "quem precisa / o quê /
   para quê", crítica do pedido. Depois: decisões, tarefas com checklist, mapa de impacto,
   replanejamento, revisões. Modelo: `docs/specs/_template-spec-unico/spec.md`, gerado do modelo
   antigo pelo conversor (nada do modelo antigo ficou de fora).
2. **Leitor único** `tools/spec_fonte.py`: é o único lugar que sabe onde cada parte mora. Os gates
   pedem a parte e recebem o mesmo texto que antes liam do arquivo antigo; a lógica de verificação de
   cada gate não mudou. Um `#` dentro de bloco de código não encerra parte.
3. **Formato antigo continua aceito**, sem migração forçada. `tools/spec_unificar.py` converte uma
   pasta sob demanda, sem apagar os arquivos antigos, e recusa a forma que perderia a separação.
4. **Anti-autoaprovação preservada** (achado da revisão do plano): no arquivo único, requisito e
   aceite ficam em partes separadas e em momentos separados — a Parte B é escrita **depois** da
   aprovação da Parte A e ratificada pelo revisor isolado (carimbo de datas na Parte B). A J3 do
   `qa_evidence` recusa um `spec.md` único **sem** Parte B.
5. **Forma que faria uma parte engolir outra é RECUSADA, não aceita:** bloco de código aberto e nunca
   fechado, ou a mesma parte duas vezes → `SpecInvalida` (um `OSError`, então todo gate reprova com a
   mensagem). A cerca fecha só com o mesmo caractere que abriu; título com até 3 espaços de recuo é
   título, como no Markdown.
6. **Uma fonte por especificação:** pasta com o arquivo único E os arquivos antigos (o conversor não
   apaga nada) → na varredura sem argumento, o arquivo único é a fonte e os antigos daquela pasta saem
   da varredura (continuam lidos se passados explicitamente). No arquivo único, havendo Parte C, **ela**
   é o context-brief; um `context-brief.md` ao lado não a substitui, e o gate diz isso na mensagem.
7. **Grau `--quick` não muda**: continua com o `spec.md` de 3 seções **sem a marca**, que os gates não
   leem — exatamente como antes. Arquivo único (com marca) é o grau completo.

## A condição do dono, virando prova

- **Nenhum mecanismo quebra:** fotografia dos 4 gates nas 11 especificações antigas antes e depois
  da mudança — **0 diferenças**, comparando a saída inteira, não só o código de saída. Os canários
  existentes dos gates (`test_spec_depth`, `test_completeness`, `test_context_brief`,
  `test_qa_evidence`) continuam verdes. `readiness-gate` passou a aceitar o arquivo único em R1.
- **Nenhuma informação se perde:** `tools/test_spec_unico.py` converte cada uma das 11 e exige
  (a) o mesmo veredito dos 4 gates, achado por achado; (b) o mesmo em casos sintéticos feitos para
  **reprovar** em cada gate; (c) **igualdade exata, parte por parte**: cada parte é o arquivo de
  origem inteiro, linha a linha (só o título vira comentário) — e (c2) a própria prova pega linha
  perdida que exista igual em outra parte; (d) partes isoladas, cerca respeitada, parte ausente
  reprovando; (d2) cerca aberta, parte repetida e título com recuo; (e) recusa do conversor;
  (f) J3 recusando `spec.md` sem aceite; (g) coexistência contando uma vez; (h) Parte C × arquivo ao lado.
- **Provado por sabotagem:** 6 sabotagens (partes não isoladas, cerca aberta aceita, parte repetida
  aceita, recuo não reconhecido, conversor que perde uma linha, varredura em dobro) — cada uma deixa
  o canário vermelho com o achado certo, sem travar.
- **Se a prova tivesse falhado**, a decisão do dono já apontava a saída: 3 arquivos + espelho.

## Régua §0 — ganho líquido

Entram 2 ferramentas (`spec_fonte.py`, `spec_unificar.py`), 1 modelo e 1 canário. Sai, para toda
especificação nova, a obrigação de manter 5 arquivos (2 obrigatórios + 3 condicionais) — vira 1, com
os condicionais como partes opcionais. Os gates não ganharam lógica nova de verificação: ganharam um
ponto único de leitura.

## Consequências

- Painel, tarefas e mapa de impacto passam a ter lugar fixo na especificação. O **verificador** desses
  campos (decisão sem dono, "feito" sem prova, % que não bate, aceite datado antes da aprovação) é o
  bloco **B2b**, ainda não entregue.
- Quem mantiver especificação antiga não precisa fazer nada.
- Limite declarado: o conversor recusa arquivo antigo com mais de um título de nível 1 fora de código.
  Hoje nenhum dos 11 tem; se aparecer, a conversão daquela pasta pede ajuste manual.

## Estado do QA

| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| 3 | Sonnet isolado, primeiro plano, sobre o índice | PASS | correção da J3 reproduzida pela linha de comando numa cópia isolada: `RECUSADO` com o motivo, saída 1, nenhum ledger gravado; única rota do `qa_evidence` que chama o leitor, já tratada; os 4 gates tratam `OSError` | aprovado |
| 2 | Sonnet isolado, primeiro plano, sobre o índice | PASS-COM-RESSALVAS | os 7 da rodada 1 confirmados por reprodução própria (sabotagem registrada: PASS → FAIL(11); as 11 antigas sem diferença); 1 ALTO novo: na J3, `spec.md` malformado derrubava o `qa_evidence` com erro não tratado em vez da recusa limpa prometida (fail-closed, mas sem mensagem) | corrigido: `SpecInvalida` vira recusa `ValueError` com motivo; caso (f2) no canário, provado por sabotagem |
| 1 | Sonnet isolado, primeiro plano, sobre o índice | FAIL | 1 CRÍTICO (a prova de "perda zero" buscava a linha no arquivo inteiro: perda na Parte A escondida por linha igual na Parte D — reproduzido), 3 ALTO (cerca não fechada engolia a Parte B; título com recuo não reconhecido; pasta com os dois formatos contada duas vezes na varredura), 2 MÉDIO (Parte C incompleta calava o brief ao lado; parte repetida descartada em silêncio), 1 BAIXO (skill `architect` sem ajuste) | os 7 corrigidos; prova de perda virou igualdade exata; 6 sabotagens |
