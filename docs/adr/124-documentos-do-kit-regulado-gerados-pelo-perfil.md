# ADR-124 — Documentos do kit regulado gerados com o modelo do perfil; mudança e versão geradas

- **Status:** Aceito
- **Data:** 2026-09-28
- **Decisores:** dono (Fabricio):
  - 27/09/2026, escopo: "ERU específico farma/alimento; skill enxuta geral; verificador do plano geral; perfil ANVISA
    somente farma/alimento, nunca citar empresa, é perfil de aplicação; teremos também perfil ANP";
  - 28/09/2026, decisões D1–D3 do bloco: "todas a".

  Autoria: Opus 5.5.
- **Relação:** executa o B3a-3 do plano `docs/specs/b3-documentacao-regulada/spec.md`:
  - REQ-09 a REQ-12;
  - critérios 10 a 13;
  - tarefas T5 e T5b.

  Reusa `regulado.py` (ADR-119), `spec_fonte` (ADR-117) e `gen_exec_doc.export` (docx).

## Contexto
1. A spec B3 pedia ERU, relatório de validação e checklist de prontidão gerados, mais registro de mudança e versão.
2. ERU, relatório de validação e prontidão são documentos de um tipo de ambiente regulado, não de todo projeto. O
   núcleo precisa continuar neutro (ADR-020, ADR-119).

## Decisão
1. **D1 — motor neutro, modelo no perfil.**
   - Comando: `python tools/regulado.py documento <tipo> <spec.md> --out-dir <pasta> [--rascunho]`, que delega a
     `tools/documento_regulado.py`.
   - O perfil declara em `"documentos"` o título, as seções e os rótulos de cada documento. O motor monta as seções:
     `identificacao`, `documento_controlado`, `requisitos`, `riscos`, `testes`, `desvios`, `prontidao`, `aprovacao`.
   - Perfil sem o documento recusa. O perfil farma/ANVISA traz `eru`, `relatorio-de-validacao` e
     `checklist-de-prontidao`; outros perfis trazem os seus.
2. **D2 — desvios:** `### Desvios` na Parte G (desvio, teste, descrição, tratamento, nome e data). Teste reprovado
   sem desvio é achado.
3. **D3 — código do documento:** tabela `### Documentos controlados` na Parte A (documento, código, versão). Código
   vazio sai como "a preencher pela Qualidade"; nunca é inventado.
4. **Atributos dos requisitos:** `### Atributos dos requisitos` na Parte A, com as colunas definidas no perfil (no
   farma: criticidade em BPF e origem).
5. **Prontidão:** `### Prontidão para operação` na Parte G. Os itens obrigatórios vêm do perfil.
6. **Lacuna reprova e nada é gravado.** O `--rascunho` grava com "RASCUNHO" no título e PENDENTE nas lacunas. O
   relatório inclui a verificação estrita do kit (`regulado.verificar`).
7. **Mudança e versão (geral):** `python tools/mudancas_spec.py <spec.md> --out-dir <pasta>` gera:
   - controle de versão pelo `git log --follow` do `spec.md`;
   - "o que mudou" pela seção Replanejamento;
   - correções da base pela Parte J.

   Versão sem data ou autor e mudança sem data ou sem quem aprovou reprovam.

## Alternativas descartadas
- **Ferramenta própria só para farma:** duplicaria o motor a cada perfil (ANP e outros).
- **"Teste reprovado" como desvio:** sem o registro do tratamento, o relatório não mostra o que foi feito.
- **Código do documento espalhado por documento:** uma tabela só é mais fácil de a Qualidade preencher e de conferir.

## Régua §0
Critério (c): quatro peças, antes escritas à mão, passam a ser geradas e verificadas, estendendo `regulado.py` e o
perfil. Adiciona 2 motores e 1 canário.

## Prova
- `tools/test_documento_regulado.py` (perfil sintético):
  - documento gerado em md e docx;
  - atributos, código vazio e aprovação;
  - 6 lacunas reprovam sem gravar;
  - rascunho;
  - recusas: perfil sem o documento e projeto sem impacto;
  - mudança e versão a partir de um repositório git temporário;
  - neutralidade dos motores.

## Limites
- **Formato do documento controlado:** o da empresa pode exigir outro layout. O docx sai no formato de seções do
  `gen_exec_doc`, não no modelo oficial da Qualidade.
- **Controle de versão:** um commit é uma versão. Commits pequenos geram linhas pequenas; a versão formal do documento
  é a da tabela de documentos controlados.
- **Resultado:** no relatório, o Resultado da Parte G só aceita `aprovado` ou `reprovado` (enum fechado). Qualquer
  outro texto reprova, e o reprovado exige desvio.

## Estado do QA
| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| 1 | Sonnet isolado (ab2076577416856cd) | FAIL | 1 CRÍTICA: REQ com descrição vazia fazia o seguinte sumir da ERU (regex própria atravessava linha). 1 MÉDIA: "não aprovado"/"rejeitado" escapavam do desvio. 1 BAIXA: traceback na gravação | lista de REQs do motor (fonte única); descrição linha a linha; Resultado em enum aprovado/reprovado; casos novos |
| 2 | Sonnet isolado (a1e9d873a50c85156) | PASS-COM-RESSALVAS | CRÍTICA e enum fechados, mutações mortas. 1 MÉDIA: REQ repetido em silêncio em documento sem seção de testes. 1 BAIXA: gravação sem tratamento | checagem de repetido; falha de gravação vira recusa |
| 3 | Sonnet isolado (a4e1e3c6b8d6d9ded) | PASS-COM-RESSALVAS | correções confirmadas, mutação morta. 1 MÉDIA: regra de repetido duplicada. 1 BAIXA: gravação sem caso de teste | `regulado.duplicados_reqs` único; caso de falha de gravação no canário |
