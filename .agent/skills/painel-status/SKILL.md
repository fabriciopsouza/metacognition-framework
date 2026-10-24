---
name: painel-status
description: "Ativar quando o dono pedir status, status report, painel, situação, onde estamos, ou ao fechar um bloco de trabalho que mude o plano. No chat: tabela de blocos (Bloco · O que é · Situação ✅/⏳/☐ · % · Onde está · O que falta), 3 linhas (onde estamos · o que falta · próximo passo), caminho do painel e link — sem narrativa. No arquivo (painel HTML): além disso, 4 números de resumo, entregas por grupo, o que está com o dono e as fontes conferidas; salvo em pasta de recuperação fácil e, se o ambiente publicar páginas, republicado no mesmo endereço. NÃO ativar para resposta pontual sem relação com o plano."
version: 1.2.2
source: "pedido do dono, 19/10/2026: 'manter o status report como Painel, como skill para você e para o framework; respostas neste formato sempre que possível, salvas em pasta de fácil recuperação'; 21/10/2026 (A44): seção Cronograma no painel; 21/10/2026: endereços https do painel devem ser links, no mesmo local do texto; 24/10/2026: 'qd peço status report quero O DASH DO PROJETO': abrir o painel na tela do dono"
last_review: 2026-10-24
role_order: null
consumes:
  - "plano ativo do projeto (documento de plano, controle de histórias/tarefas, PRs ou entregas)"
produces:
  - "resposta de status no chat (tabela + 3 linhas + caminho + link)"
  - "painel HTML datado, ULTIMO.html, status.md e link.txt na pasta de status do projeto"
pass_criteria: "PASS sse: (1) a tabela no chat tem as 6 colunas na ordem Bloco · O que é · Situação · % · Onde está · O que falta, todo bloco do plano (inclusive não iniciado) e nenhuma frase fora da tabela, das 3 linhas, do caminho e do link; (2) o status.md lista as fontes conferidas com data e hora, e todo número sem fonte aparece com a marca INFERIDO; (3) foram salvos AAAA-MM-DD_HHMMSS_status.html, ULTIMO.html e status.md na pasta de status do projeto escolhida pela regra de isolamento; (4) a resposta termina com o caminho absoluto do ULTIMO.html em link file:/// e, se houver, o link publicado; (5) se o objeto de dados traz `cronograma` com ao menos uma etapa ou marco, o painel mostra a seção Cronograma entre os cartões e a tabela; sem o campo, nenhuma seção nova aparece; (6) todo endereço https nos campos meta, onde, falta, próximo, comDono, fontes e nas colunas Onde está e O que falta aparece como link clicável no mesmo lugar do texto, e nenhum outro texto vira link ou HTML; (7) depois de salvar e republicar, o painel foi aberto na tela do dono (Artifact `open` do endereço publicado ou o `ULTIMO.html` local)."
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
   entregas, as 3 linhas, a lista "com o dono" e as fontes. Se o projeto tiver datas de etapas e marcos, acrescentar o
   campo opcional `cronograma` (seção "Cronograma (opcional)" abaixo).
3. **Gerar o painel**: copiar `painel-template.html` e trocar o conteúdo do bloco
   `<script type="application/json" id="dados">` pelo objeto serializado em JSON **com todo `<` escrito como `\u003c`**, conferindo antes que o objeto tem o formato do modelo (listas de listas)
   (impede que texto do plano feche o script). Salvar como `AAAA-MM-DD_HHMMSS_status.html` na pasta de status e copiar
   para `ULTIMO.html`.
4. **Salvar a versão texto**: `status.md` com a tabela, as 3 linhas e a seção "Fontes conferidas" (sobrescreve; o
   histórico fica nos HTML datados).
5. **Publicar, se o ambiente oferecer página publicada**: republicar sempre no mesmo endereço do projeto, guardado em
   `link.txt` na pasta de status, e **abrir o painel na tela do dono** (no Claude Code: Artifact `action: "open"` com o
   endereço do `link.txt`; republicar um artifact de outra conversa não abre a página sozinho). Sem página publicada,
   abrir o `ULTIMO.html` local (Windows: `start "" "<caminho absoluto do ULTIMO.html>"`).
6. **Responder no chat**, nesta ordem e sem narrativa:
   1. a tabela de blocos (6 colunas, na ordem);
   2. três linhas: **Onde estamos** · **O que falta** · **Próximo passo**;
   3. o caminho absoluto do `ULTIMO.html` como link `file:///` e o link publicado.

## Cronograma (opcional)

Campo `cronograma` do objeto de dados. Presente, o painel ganha a seção **Cronograma** entre os cartões de resumo e a
tabela de blocos; ausente (ou sem nenhuma etapa nem marco), nada muda no painel.

Formato:

```json
"cronograma": {
  "marcos": [{"id": "M1", "nome": "Marco 1 vendável", "data_prevista": null, "data_real": null, "situacao": "todo"}],
  "etapas": [{"nome": "Sprint 0", "inicio": "2026-10-18", "fim": "2026-10-19", "situacao": "ok", "pct": 100, "horas_ativas": 7.5}],
  "hoje": "2026-10-22"
}
```

| Campo | Regra |
|---|---|
| datas (`inicio`, `fim`, `data_prevista`, `data_real`, `hoje`) | `AAAA-MM-DD`; `fim`, `data_prevista` e `data_real` podem ser `null` |
| `situacao` | `ok` · `wip` · `todo` (fora disso, o painel mostra `todo`) |
| `pct` | 0 a 100, estimativa declarada como na tabela de blocos |
| `horas_ativas` | número ou `null`; só com fonte medida, senão `null` |
| data prevista de marco | só se medida (velocidade) ou combinada com o dono; senão `null` |

O que a seção mostra:

1. Eixo de tempo do menor ao maior dia informado (etapas, marcos e hoje), com datas nas pontas e no meio.
2. Uma barra por etapa, na posição do período: a faixa inferior da barra é o % concluído e o número aparece na barra
   (ou ao lado, se a barra for curta); borda tracejada = etapa sem `fim` (em aberto: vai até `hoje` ou, sem `hoje`, até o fim do eixo).
3. Marcos com data como losango (cheio = data real, vazado = só prevista) e a lista de marcos com previsto, real e
   situação; marco sem data aparece só na lista.
4. Linha vertical "hoje".
5. Texto para leitor de tela: lista oculta com cada etapa (período, situação, %, horas); a parte gráfica fica fora da
   leitura (`aria-hidden`). Datas do eixo e das etapas em dd/mm; com dd/mm/aa quando o período cruza o ano.

Dado inválido não quebra o painel: data fora do formato ou inexistente vira "sem data"; `fim` antes do `inicio` vira o
próprio início; etapa só com `fim` usa o `fim` como início; `pct` fora de 0–100 é limitado e não numérico vira "—";
`horas_ativas` negativa ou não numérica é omitida; item que não é objeto é ignorado. Data muito distante comprime o
eixo, sem quebrar: conferir as datas antes de gerar.

Visual: CSS sem biblioteca, tema claro e escuro, sem rolagem horizontal a 390 px, contraste de texto ≥ 4,5:1 (medido em
21/10/2026: mínimo 6,29 no claro e 6,08 no escuro).

## Regras

- Situação só com ✅ concluído, ⏳ em andamento, ☐ não iniciado; % é estimativa declarada (0 a 100), coerente com a
  situação.
- Bloco não iniciado aparece na tabela, com "o que é" preenchido.
- O painel não traz credencial nem dado pessoal de cliente; nomes de pessoas só se o plano já os usa.
- Comando permanente `status` do dono: responder ANTES de continuar o trabalho, só com o item 6; abrir o painel (passo 5)
  faz parte da resposta, não é texto extra.
- Sempre que possível, outras respostas de acompanhamento usam a mesma estrutura (tabela + 3 linhas).
- O tema do painel segue o tema do sistema operacional (claro ou escuro), decisão declarada.
- **Links (1.2.1):** endereços `https://` nos textos do painel viram links; o texto continua escapado. Vale para
  `meta`, `onde`, `falta`, `proximo`, `comDono`, `fontes` e as colunas Onde está e O que falta dos blocos; o link
  fica no mesmo lugar do texto e abre em nova aba. `http:`, `javascript:` e outros esquemas continuam texto; título,
  números, "O que é" e grupos nunca viram link. Pontuação final (`.`, `,`, `;`, `:`, `!`, `?`) e `)` sem `(`
  correspondente ficam fora do link; `&` no fim fica dentro. `https` colado a letra, dígito ou `_` antes (ex.:
  `xhttps://`) não vira link. Limite declarado: reticências (`…`), aspas tipográficas (`’`, `»`) e espaço de largura
  zero (U+200B) colados ao fim entram no link; separar o endereço com espaço. Escrever o endereço completo, com `https://`.
