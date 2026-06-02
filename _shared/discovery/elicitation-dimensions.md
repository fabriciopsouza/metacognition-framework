# Banco agnóstico de dimensões de elicitação (ADR-033)

> **O que é:** a lista das **dimensões universais** que toda elicitação de **produto recorrente**
> (software, dado, pipeline, relatório que vira ferramenta) deve **endereçar com uma decisão
> registrada** antes de codar. É a SSoT consumida por `tools/check_spec_depth.py`, que **barra o
> avanço para J2** (discovery→architect) se o `requirements.md` não decidir cada dimensão obrigatória.
>
> **O que NÃO é:** um catálogo de perguntas de domínio. Há dois tipos de pergunta e só um vive aqui:
> - **Meta-pergunta de elicitação** ("quem opera?", "qual escopo temporal?", "precisa persistência?")
>   — **agnóstica, universal** → vive aqui.
> - **Pergunta de domínio** ("descartar tais centros de custo?", "a referência é a variação X ou Y?")
>   — específica do projeto → **NUNCA entra aqui**; é *gerada* pelo discovery ao ler o material.
>   `check_core_agnostic.py` barra qualquer termo de domínio que vaze para este arquivo.
>
> **Limite declarado (→ `LIMITS.md`):** o linter garante **cobertura de dimensão** (a dimensão foi
> endereçada), **não a qualidade da decisão** (que a recomendação default seja sênior depende do
> agente). Mecanizado: cobertura. Não-mecanizado: acerto do default.

## Como o discovery usa (consultoria, não coletor de requisitos)

Para CADA dimensão, o discovery **não pergunta em aberto** — **recomenda um default sênior com o
trade-off** e pede confirmação. Ex.: em vez de *"qual interface?"*, diz *"isto vai a decisão de
gente não-técnica e é auditável → recomendo GUI + log de auditoria; confirma, ou prefere outro
caminho?"*. A decisão (confirmada ou alterada) é **registrada** na seção de dimensões do
`requirements.md`. É o que teria impedido o incidente de campo de pular "quem opera / interface /
escopo acumulado".

## Dimensões (contrato — lidas pelo linter)

A tabela abaixo é **machine-readable**: `check_spec_depth.py` extrai a 1ª coluna (chave canônica) e a
2ª (aliases, separados por vírgula) e exige, no `requirements.md`, uma **decisão registrada** para
cada chave obrigatória (`obr=sim`). Aliases permitem que a spec use o vocabulário do seu domínio.

| chave | aliases | obr | pergunta-guia (agnóstica) | default sênior sugerido (a confirmar) |
|---|---|---|---|---|
| operador | usuario, quem-opera, persona, ator | sim | Quem executa/consome no dia a dia — técnico ou leigo? | leigo → interface guiada; técnico → CLI aceitável |
| interface | ui, cli, gui, web, planilha, front | sim | Como se interage — linha de comando, app, web, planilha? | proporcional ao operador; leigo → GUI/app |
| entrada-validacao | entrada, input, upload, validacao, schema | sim | Como entram os dados — o produto lista/valida/orienta a fonte? | listar + validar schema + orientar origem antes de processar |
| escopo-temporal | periodo, intervalo, mes, ano, acumulado, realizado | sim | Janela: ponto único, intervalo, total, realizado e acumulado? | cobrir intervalo + acumulado quando o pedido implica série |
| recortes-saida | recorte, granularidade, dimensoes, agrupamento, drill | sim | Por quais cortes a saída é vista — por entidade, por grupo, todos? | oferecer todos os cortes que o pedido nomeia + "todos" |
| persistencia | memoria, historico, estado, reprocesso, armazenamento | sim | Há memória entre execuções — histórico, reprocessar fechado? | persistir resultados + permitir reprocesso idempotente |
| auditoria-log | log, trilha, auditoria, accountability, quem-rodou | sim | Registra quem rodou, quando, com quais insumos e versão da regra? | log de auditoria sempre que a saída alimenta decisão |
| ambiente-execucao | instalacao, deploy, ambiente, requisitos, maquina-limpa | sim | Instala/roda em máquina limpa — dependências resolvem do zero? | testar instalação limpa + entry-point não-interativo |
| formato-saida | saida, relatorio, export, entrega, artefato | sim | Formato final — relatório formatado, exportável, faixas/metas visíveis? | export legível + números rastreáveis à fonte |
| contexto-entidade | contexto, entidade, cliente, perfil-entidade, pesquisa-de-contexto | nao | Quem é a entidade/cliente (setor, porte, modelo, escopo, posição) e o domínio foi PESQUISADO além do artefato dado? | quando há stake → pesquisar perfil+domínio e registrar em context-brief |
| verificacao-ancora | ancora, vigencia, pertinencia, fonte-aplicavel | nao | Cada norma/benchmark citado é VIGENTE e PERTINENTE a ESTE tipo de entidade (acusar mesmo se deliberado)? | verificar vigência+pertinência de toda âncora; registrar no context-brief |

> **Editável:** novas dimensões universais podem entrar (régua §0: só se universais e não-domínio).
> Marcar `obr=nao` cria dimensão **recomendada** (linter avisa, não barra). A coluna `aliases` é o que
> permite ao banco ser agnóstico e a spec falar a língua do seu próprio domínio.
>
> **`contexto-entidade` e `verificacao-ancora` (ADR-051):** recomendadas aqui (advisory no
> `check_spec_depth`), mas com **enforcement DURO quando há sinal de stake** via
> `tools/check_context_brief.py` (exige `context-brief.md` antes de J2). Aqui ficam `obr=nao` para
> não duplicar a barra nem quebrar o canário de cobertura; o gate de contexto é quem barra de fato.
