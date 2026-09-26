# ADR-121 — Método único de projeto, desenho do processo gerado e manifesto de evidência

- **Status:** Aceito
- **Data:** 2026-09-26
- **Decisores:** dono (Fabricio). Plano B3 com as decisões D7 e D8 (26/09); prioridade dada em 26/09 ("antes da
  ANVISA, priorize B3d, B3a, B3c, B2b"); respostas do mesmo dia sobre o desenho:
  - raias por papel com teto de 15 passos; acima disso, agrupar em macroações e detalhar cada uma, ou confirmar com
    o dono;
  - quadro de aprovação e perguntas em aberto no HTML, respondidos na planilha de confirmação (Excel).
  Autoria: Opus 5.5.
- **Relação:** executa o B3d do plano `docs/specs/b3-documentacao-regulada/spec.md` (REQ-13, REQ-14, REQ-15;
  critérios 14, 15, 16; tarefas T8–T11). Reusa `spec_fonte` (ADR-117), `gen_exec_doc.py` (docx) e `doc_intake.py`
  (sha256).

## Contexto

1. O método de projeto estava espalhado em vários guias e skills; nenhum arquivo de entrada apontava para um fluxo
   único.
2. O mapeamento de processo existia só em texto; nenhuma ferramenta o lia.
3. O dono prefere desenho em SVG legível a layout automático (memória `diagrama-svg-a-mao-melhor-que-mermaid`), e o
   desenho precisa servir de documento controlado (docx).
4. Evidência de desenvolvimento (consultas, extrações, runbooks) não tinha rastro: caminho, hash, origem e o
   requisito que embasa.

## Decisão

1. **`guia/METODO-DE-PROJETO.md`:** fluxo de 8 etapas (abertura, elicitação, confirmação da área, especificação,
   desenho do processo, testes e evidências, liberação, operação e fechamento). Para cada etapa: o que sai, onde
   mora e o comando que verifica. É apontado pelo `CLAUDE.md` e pelo início de sessão. Os guias existentes são
   ligados, não substituídos.
2. **Parte H — Processo** no arquivo único: tabela de passos (passo, macroação, descrição, papel, gatilho, saída,
   próximo, regra, controle), pontos para aprovação e perguntas em aberto.
3. **`tools/desenho_processo.py`:**
   - **HTML autônomo:** uma raia vertical por papel, passos de cima para baixo, decisão em losango, retorno
     tracejado, papéis, gatilhos, regras, controles, pontos para aprovação e perguntas, com carimbo de versão
     (sha256 da especificação). A área responde na planilha de confirmação.
   - **docx** pelo `gen_exec_doc.export`, regravado a cada geração.
   - **Reprova:** passo sem descrição ou papel; destino inexistente; passo repetido; mais de 15 passos sem
     macroação (a menos que haja aceite do dono com data); macroação com mais de 15 passos; largura calculada pelos
     papéis maior que a tela (1536 px).
   - **Macroações:** com elas preenchidas, o desenho sai em dois níveis, visão geral e um desenho por macroação.
     Passo que segue em outra macroação é indicado.
4. **Manifesto de evidência** em `tools/doc_intake.py evidencia registrar | verificar`:
   - **Registro:** caminho absoluto, sha256, data, origem e ligação (requisito ou teste).
   - **Recusa:** mesmo caminho com conteúdo novo (nome novo, anterior em `_obsoleto/`); origem ou ligação vazias;
     data impossível.
   - **O `verificar` acusa:** arquivo apagado; conteúdo mudado; sensível rastreado pelo git; caminho relativo;
     entrada incompleta.

## Alternativas descartadas

- Mermaid no HTML: layout automático ilegível em fluxo com vários papéis (preferência registrada do dono).
- Raias horizontais: a largura cresceria com o número de passos e não caberia na tela.
- Ferramenta nova de manifesto: o `doc_intake.py` já calcula o sha256; foi estendido com um subcomando.
- Reescrever os guias no método único: duplicaria conteúdo; o método liga a eles.

## Régua §0

Critério (a): o método espalhado passa a ter uma entrada. Critério (c): processo e evidência, que eram prosa, passam
a ser gerados e verificados, estendendo `spec_fonte`, `gen_exec_doc` e `doc_intake`. Adiciona 1 gerador, 1 guia e
2 canários.

## Prova

- `tools/test_desenho_processo.py`:
  - geração de HTML, md e docx; HTML autônomo;
  - alterar um passo e gerar de novo muda o HTML e o docx, sem cópia `-1` (critério 15);
  - 6 sabotagens reprovam com a mensagem esperada e nada é gerado;
  - macroações em dois níveis; aceite com data libera e aceite sem data não libera;
  - o método tem as 8 etapas na ordem, e o `CLAUDE.md` e o início de sessão apontam para ele (critério 14).
- `tools/test_evidencia.py`: registro e verificação; 9 sabotagens (inclui manifesto corrompido); o uso antigo do `doc_intake` intacto
  (critério 16).
- Mutação (script de sessão, não versionado): 20 mutações, 20 mortas. As 3 que sobreviveram na primeira passada
  mostraram um caso de teste que reprovava pelo motivo errado, um limite duplicado (fundido na medição da largura) e
  a legenda mascarando o retorno.
- Renderização no Edge (1536 e 1100 px): legível, sem sobreposição, depois de corrigir os rótulos da decisão.

## Limites

- O layout é fixo (raias verticais), não posicionamento livre como o desenho feito à mão; é o preço de ser gerado.
- A docx segue o formato de seções do `gen_exec_doc`, sem o desenho gráfico; o desenho de revisão é o HTML.
- O código do documento controlado vem da Qualidade da empresa (B3a-3).

## Estado do QA

| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| 3 | Sonnet isolado, primeiro plano (a0137d1c08f2408b9) | PASS | nenhum: falha na escrita, primeira geração com falha e docx não gerado voltam limpos; correções das rodadas 1 e 2 de pé | — |
| 2 | Sonnet isolado, primeiro plano (aff590f529ac52cce) | FAIL | correções 1, 3 e 4 confirmadas. 1 ALTA nova: falha DURANTE a escrita dos novos (ex.: erro no exportador) deixava o HTML novo e o md/docx anteriores presos como `.anterior`, com traceback | a escrita virou tudo ou nada: qualquer falha apaga o que foi escrito e devolve os três anteriores; a presença dos três é conferida no fim; caso novo com exportador que falha |
| 1 | Sonnet isolado, primeiro plano (a49653d3ca8d24d01) | FAIL | 1 CRÍTICA: manifesto corrompido derrubava o `registrar`. 1 ALTA: docx aberto no Word derrubava a regravação e deixava html/md/docx inconsistentes. 1 MÉDIA: mesmo papel com caixa/acento diferente virava raias separadas. 1 BAIXA: acento corrompido no console | leitura do manifesto com recusa controlada; gerados antigos afastados antes de escrever, com volta ao estado anterior se algum estiver em uso; papel agrupado sem caixa e acento; saída em UTF-8. 3 casos novos |
