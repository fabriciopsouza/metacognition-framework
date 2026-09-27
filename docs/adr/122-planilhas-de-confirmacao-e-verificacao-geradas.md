# ADR-122 — Planilhas de confirmação e de verificação geradas do arquivo único, com versão comparada

- **Status:** Aceito
- **Data:** 2026-09-27
- **Decisores:** dono (Fabricio), em 27/09/2026:
  - decisões D1 a D3 do plano, "recomendações de acordo":
    - D1: Parte I como origem da confirmação;
    - D2: Parte J como origem da verificação, separada da Parte G;
    - D3: categorias obrigatórias acrescentadas pelo gerador;
  - rodada: "faça com uma rodada e a instrução para adicionar rodada quando for necessário";
  - cabeçalhos: "não é só SAP, é requisitos de projeto, seja qual for";
  - valores por categoria: "ok, ajustar e a skill adapta";
  - versão: "ao regravar/responder, cria nova versão (v1, v2, etc.), move a antiga para obsoleta, cria a nova,
    compara ambas, somente então apaga a antiga".

  Autoria: Opus 5.5.
- **Relação:** executa o B3a-2 do plano `docs/specs/b3-documentacao-regulada/spec.md` (REQ-05, REQ-06; critérios 3a
  e 3b; tarefa T4). Reusa `spec_fonte` (ADR-117), `regulado.carregar` (perfil e impacto, ADR-119) e os pontos para
  aprovação da Parte H (ADR-121).

## Contexto

1. As duas planilhas-modelo do dono (confirmação de definições e checklist de verificação) já eram, na prática, os
   documentos de confirmação de requisitos e de roteiro de verificação; eram montadas à mão.
2. As 12 colunas "de rodada" do checklist-modelo são três rodadas diferentes empilhadas (5 + 6 + 1 colunas), não um
   formato repetível.
3. Os cabeçalhos do modelo citam um sistema específico; copiados literalmente, levariam termo de domínio ao núcleo.
4. Gerar de novo uma planilha que a área já preencheu apagou respostas em caso real (memória
   `planilha-gerada-que-o-dono-preenche`).

## Decisão

1. **Parte I — Definições a confirmar** no arquivo único:
   - tabela `DEF-nn` com as 13 colunas neutras, na ordem e no papel do modelo;
   - campos `**...:**` que formam a aba LEIA;
   - `### Valores por categoria` opcional, com as categorias como colunas;
   - `### Rótulos`, que troca o texto do cabeçalho por projeto. É por ele que a skill adapta a planilha ao domínio.
2. **Parte J — Roteiro de verificação:**
   - `### Bloco: <nome>` com linhas `VER-nn` nas 15 colunas de base;
   - uma `### Rodada N — dd/mm/aaaa` de formato fixo (Pergunta de volta · Resposta da área · O que fazer · Situação ·
     Nome e data), com a instrução, no modelo e na aba COMO USAR, de acrescentar a rodada seguinte;
   - `### Antes de começar`, `### Achados do ambiente`, `### Correções da base` e `### Controle de versão`.
3. **Pontos para aprovação da Parte H** entram na confirmação como linhas `H-n`. A resposta volta à própria tabela de
   pontos, que ganha as três colunas de resposta.
4. **`tools/planilhas_projeto.py`**, com cinco comandos. Passo que alguém executa é comando, não instrução em
   texto (regra do dono de 27/09: "nada de fiar as capacidades somente em prosa"):
   - `verificar`: estrutura;
   - `gerar`: `confirmacao_vN.xlsx` e `verificacao_vN.xlsx`;
   - `importar`: grava as respostas no arquivo único e gera a versão seguinte;
   - `situacao [--exigir]`: conta o que a área respondeu com nome e data válida. É a prova da etapa 2 do método
     ("Não" e "Com correção" contam como pendência a tratar);
   - `rodada --data --ids`: acrescenta a próxima rodada no formato fixo.

   Colunas de resposta saem em formato texto: o que começa com "=" não vira fórmula. Terminador de linha (CRLF ou LF)
   do arquivo único preservado.
5. **Versão comparada:**
   - cada gravação cria vN+1 e move a vN para `_obsoleto/`;
   - toda resposta não vazia da vN tem de estar, idêntica, na vN+1; só então a vN é apagada;
   - divergência apaga a vN+1, devolve a vN ao lugar e reprova;
   - planilha aberta (`~$`), versão superada, cabeçalho alterado pela área e planilha sem marca de versão são
     recusados sem alterar nada;
   - causas distintas têm recusas distintas:
     - resposta ainda não importada pede `importar`;
     - resposta em linha removida do arquivo único pede devolver a linha ou `--descartar "<frase do dono,
       dd/mm/aaaa>"`, que guarda a vN em `_obsoleto/` em vez de apagá-la;
   - a vN anterior é lida pela posição das colunas: rótulo mudado entre versões não perde resposta;
   - falha ao apagar a vN depois da comparação só avisa: a vN+1 vale e a vN fica em `_obsoleto/`.
6. **Categorias obrigatórias:**
   - com `**Impacto regulado:** sim`, as categorias `testes_obrigatorios_com_impacto` do perfil que faltarem como
     bloco são acrescentadas pelo `gerar`;
   - `verificar` reprova a falta.

## Alternativas descartadas

- Copiar as 12 colunas de rodada: cada volta criaria colunas de formato próprio e a importação não teria formato
  fixo.
- Cabeçalho literal do modelo no núcleo: termo de sistema no núcleo (princípio 12); os rótulos reproduzem o modelo
  sem isso.
- Manter a planilha como fonte: decisão D3 do plano (o repositório gera e importa).
- Apagar a versão anterior sem comparar: foi o que perdeu respostas no caso real.

## Régua §0

Critério (c): as duas planilhas, montadas à mão, passam a ser geradas e verificadas, estendendo `spec_fonte` e o
modelo de arquivo único. Adiciona 1 gerador e 1 canário.

## Prova

- `tools/test_planilhas_projeto.py`, com 68 verificações:
  - estrutura das abas e colunas;
  - com os rótulos do modelo real, o cabeçalho gerado é idêntico ao do modelo (critério 3a);
  - ida e volta com quebra de linha e barra;
  - pontos da Parte H ampliados e ainda lidos pelo `desenho_processo`;
  - v1 → v2 com a comparação;
  - recusas de versão, cada uma pelo motivo certo;
  - categoria obrigatória acrescentada e exigida;
  - 8 sabotagens de estrutura;
  - rodada 2 acrescentada depois de respostas importadas;
  - um caso por achado da revisão: "=" como texto, `<br>` literal, rótulo mudado, linha removida com e sem
    `--descartar`, falha ao apagar, CRLF, arquivo vazio;
  - `situacao` e `rodada`.

## Limites

- O `importar` não apaga resposta: célula esvaziada pela área não limpa o arquivo único.
- Rótulo mudado no arquivo único ENTRE gerar a vN e importá-la faz o `importar` recusar a vN (o cabeçalho não bate
  com o atual). A saída é gerar de novo antes de enviar, ou voltar o rótulo, importar e mudar depois.
- O texto literal `&lt;br&gt;` digitado pela área volta como `<br>`. É a única sequência ambígua do escape.
- Rótulos por projeto mudam só o texto; a ordem das colunas é fixa.
- Achados do ambiente, correções da base e controle de versão são mantidos no arquivo único pela equipe; a
  planilha só os mostra.

## Estado do QA

| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| 3 | Sonnet isolado, segundo plano (a8c92769abb3f04c3), escopo das correções da rodada 2 | PASS | mutação 4 morta pelo motivo certo; 3 casos novos com âncora única; `--ids` sem repetição antes do filtro de existência; 68 verificações. Nota BAIXA opcional: nenhum caso combina ID repetido e inexistente (a ordem do código garante) | — |
| 2 | Sonnet isolado, segundo plano (abdd541d0a8351a16); travou 600 s e foi retomado com o mesmo contexto | PASS-COM-RESSALVAS | as 5 correções da rodada 1 conferidas por cenário; mutações 4/5 mortas. 1 MÉDIA: nenhum caso com "Nome e data" inválido (mutação de `_nome_e_data` → `.strip()` sobreviveu). 1 BAIXA: `rodada` gravava ID repetido | 3 casos (nome sem data, data sem nome, 31/02) e `--ids` sem repetição, com caso |
| 1 | Sonnet isolado, segundo plano (a6acdb62011b4b5bb); a 1ª tentativa travou 600 s sem veredito e foi relançada | PASS-COM-RESSALVAS | 1 ALTA: resposta iniciada por "=" vira fórmula e some. 3 MÉDIA: CRLF regravado em LF; `<br>` literal corrompido; recusa igual para causas distintas e sem saída. 1 BAIXA: falha ao apagar a anterior sem tratamento. 1 de teste: caso do `~$` não isolava a regra. Mutações 5/5 mortas | colunas de resposta em texto e leitura sem `data_only`; terminador preservado; escape de `<br>`; recusas distintas, leitura por posição e `--descartar` com data; falha ao apagar vira aviso; caso do `~$` isolado. O autor achou mais um: `gerar_tipo` chamado direto não conferia a estrutura (arquivo vazio gerava planilha vazia). Casos novos para todos |
