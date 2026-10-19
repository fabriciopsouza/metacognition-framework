---
name: painel-status
description: "Ativar quando o dono pedir status, status report, painel, situação, onde estamos, ou ao fechar um bloco de trabalho que mude o plano. No chat: tabela de blocos (Bloco · O que é · Situação ✅/⏳/☐ · % · Onde está · O que falta), 3 linhas (onde estamos · o que falta · próximo passo), caminho do painel e link — sem narrativa. No arquivo (painel HTML): além disso, 4 números de resumo, entregas por grupo, o que está com o dono e as fontes conferidas; salvo em pasta de recuperação fácil e, se o ambiente publicar páginas, republicado no mesmo endereço. NÃO ativar para resposta pontual sem relação com o plano."
version: 1.1.0
source: "pedido do dono, 19/10/2026: 'manter o status report como Painel, como skill para você e para o framework; respostas neste formato sempre que possível, salvas em pasta de fácil recuperação'"
last_review: 2026-10-19
role_order: null
consumes:
  - "plano ativo do projeto (documento de plano, controle de histórias/tarefas, PRs ou entregas)"
produces:
  - "resposta de status no chat (tabela + 3 linhas + caminho + link)"
  - "painel HTML datado, ULTIMO.html, status.md e link.txt na pasta de status do projeto"
pass_criteria: "PASS sse: (1) a tabela no chat tem as 6 colunas na ordem Bloco · O que é · Situação · % · Onde está · O que falta, todo bloco do plano (inclusive não iniciado) e nenhuma frase fora da tabela, das 3 linhas, do caminho e do link; (2) o status.md lista as fontes conferidas com data e hora, e todo número sem fonte aparece com a marca INFERIDO; (3) foram salvos AAAA-MM-DD_HHMMSS_status.html, ULTIMO.html e status.md na pasta de status do projeto escolhida pela regra de isolamento; (4) a resposta termina com o caminho absoluto do ULTIMO.html em link file:/// e, se houver, o link publicado."
confidence_required: true
enforcement:
  ide: "self-declared: prosa, sem gancho nem canário próprio (débito de mecanização declarado: um verificador do status.md pode conferir colunas, fontes e marca INFERIDO)"
  chat: "self-declared: o agente segue o fluxo e a ordem da resposta"
shared_refs:
  - _shared/output-format
  - _shared/confidence-classification
---

# painel-status — relatório de status no formato painel

## Definições

- **Bloco**: unidade do plano ativo com entrega própria (fase, épico, frente).
- **Slug do projeto**: nome em minúsculas, sem acento, espaços trocados por hífen (ex.: "Cockpit Financeiro" →
  `cockpit-financeiro`).
- **Pasta de status** (regra de isolamento): projeto **sem empresa cliente** → `%USERPROFILE%\status\<slug>\` (Windows) ou
  `~/status/<slug>/`; projeto **de empresa cliente** → `<repositório privado do projeto>\status\`, nunca a pasta central,
  porque nomes de blocos e pendências já são dado da empresa.
- **Empresa indeterminada**: se não der para saber se o projeto é de empresa cliente, perguntar ao dono antes de salvar.
- **Colisão de slug**: se a pasta do slug já existir para outro projeto, acrescentar o nome curto da empresa ou do
  repositório (ex.: `relatorio-vendas-loja-x`); na dúvida, perguntar ao dono.
- **Painel**: página HTML autocontida gerada de `painel-template.html` desta skill (abre do disco, sem rede).

## Fluxo

1. **Coletar dados conferidos agora.** Ler o plano, o controle de tarefas/histórias e o estado dos PRs ou entregas;
   anotar cada fonte lida com data e hora. Número sem fonte conferida recebe a marca INFERIDO no texto.
2. **Montar o objeto de dados** (formato no modelo): título, data e hora, 4 números de resumo, blocos, grupos de
   entregas, as 3 linhas, a lista "com o dono" e as fontes.
3. **Gerar o painel**: copiar `painel-template.html` e trocar o conteúdo do bloco
   `<script type="application/json" id="dados">` pelo objeto serializado em JSON **com todo `<` escrito como `\u003c`**, conferindo antes que o objeto tem o formato do modelo (listas de listas)
   (impede que texto do plano feche o script). Salvar como `AAAA-MM-DD_HHMMSS_status.html` na pasta de status e copiar
   para `ULTIMO.html`.
4. **Salvar a versão texto**: `status.md` com a tabela, as 3 linhas e a seção "Fontes conferidas" (sobrescreve; o
   histórico fica nos HTML datados).
5. **Publicar, se o ambiente oferecer página publicada**: republicar sempre no mesmo endereço do projeto, guardado em
   `link.txt` na pasta de status.
6. **Responder no chat**, nesta ordem e sem narrativa:
   1. a tabela de blocos (6 colunas, na ordem);
   2. três linhas: **Onde estamos** · **O que falta** · **Próximo passo**;
   3. o caminho absoluto do `ULTIMO.html` como link `file:///` e o link publicado.

## Regras

- Situação só com ✅ concluído, ⏳ em andamento, ☐ não iniciado; % é estimativa declarada (0 a 100), coerente com a
  situação.
- Bloco não iniciado aparece na tabela, com "o que é" preenchido.
- O painel não traz credencial nem dado pessoal de cliente; nomes de pessoas só se o plano já os usa.
- Comando permanente `status` do dono: responder ANTES de continuar o trabalho, só com o item 6.
- Sempre que possível, outras respostas de acompanhamento usam a mesma estrutura (tabela + 3 linhas).
- O tema do painel segue o tema do sistema operacional (claro ou escuro), decisão declarada.
