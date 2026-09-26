# PLANO — Modo planejado, resposta executiva e documentação de projeto enxuta

> **Estado:** em aprovação · **Criado:** 25/09/2026 · **Autor:** sessão Opus 5.5 · **Última atualização:** 25/09/2026
> Este plano ainda é escrito à mão. Quando o B2 estiver pronto, ele passa a ser **gerado** a partir dos
> arquivos-fonte, como o próprio plano propõe.

---

## Painel — tudo o que foi pedido e decidido nesta frente

> Acumula as decisões de **todas** as respostas, inclusive as que já saíram da tela. A resposta no
> chat traz só um status curto e aponta para cá.

**Avanço:** B1 ✅ (PR #154; falta só a verificação manual B1.8) · B1.9 ✅ (PR #155) · S12 ✅ (PR #156) · B2a ✅ (PR #157) · B2b a fazer · B3 plano em 3ª revisão, aguarda D1–D8 · B4 em revisão

| # | Assunto | Situação | Quem age | Resultado / próximo |
|---|---|---|---|---|
| S1 | Relatório de 24/09 (bloco D) entrar no git | ✅ decidido (sim) · **concluído** | — | PR #153 mergeado em 25/09 (canários locais 88 PASS, 0 FAIL) |
| S2 | Branch `kiro-ide-adapter` ir para o GitHub | ✅ decidido (sim) · feito | — | enviada em 25/09 |
| S3 | Pasta aninhada `C:\Users\fabriciosouza\metacognition-framework\metacognition-framework\` pode ser apagada? | ✅ decidido (sim, 25/09) · **apagada** após conferência final (0 alterações, 0 commits sem push em `main` e `kiro-ide-adapter`, 0 stash) | — | É uma segunda cópia inteira do framework (22 MB), clonada por outra sessão de IA em 24/09 15:49 para criar a camada do Kiro IDE; última atividade 24/09 16:39. Sem nenhuma alteração pendente; o único commit dela já está no GitHub (branch `kiro-ide-adapter`). Apagar não perde nada. Recomendação: apagar |
| S4 | Débitos rápidos de "prova que não prova" | ⏸ adiado | dono | depois deste plano |
| S5 | Revisão em subagente "proibida" fora do repo | ✅ ordem do dono: resolver sempre, em todo lugar · **feito** | — | regra global instalada; ADR-116 |
| S6 | Link e caminho relativo | ✅ ordem do dono: sempre absoluto · **feito** | — | mesma regra global |
| S7 | Painel acumulado + status curto por resposta | ✅ pedido do dono · em uso | agente | vira item B2.6 |
| S8 | 1 arquivo × 3 de especificação + plano espelho | ✅ **decidido pelo dono (25/09), condicional:** "se um arquivo não quebrar os mecanismos e não houver perda de especificação/informação, então UM. Se provocar perda, 3 + espelho" | agente | B2 vai com **1 arquivo**, e a condição vira critério de aceite binário: prova antes = depois nos gates + nenhuma seção dos 2 modelos atuais sem destino. Falhou a prova → volta para 3 + espelho, sem nova consulta |
| S15 | Princípios sempre aplicados + circuit breaker padrão entre agentes + débitos declarados + comandos de sessão ("sem circuit breaker", "sem limite de rodadas de QA", "economia de tokens") + estilo corporativo direto sobrepondo o modo explicativo + fontes sempre em arquivo | ✅ aprovado (25/09, D1–D3) · 🔄 B4 em revisão (ADR-118) | agente | reaproveita ADR-073, `trabalhos.py`, ADR-087, ADR-028; novo: contador de rodadas no ledger + regra global de estilo e comandos |
| S14 | B3 em ambiente REGULADO: enxuto, ágil, mas completo e conforme — o que uma auditoria (ex.: ANVISA) exige? cronograma, E2E, checklists como os do MRP (`Checklist_Validacao_Cadastros_MRP_v1_1_TREPLICA-v3.xlsx`, `DEFINICOES-PCP-para-confirmacao_v2.xlsx`) | 🔄 discovery em andamento (25/09) · **admitido:** o "kit de 4" do B3 foi proposto SEM pesquisa regulatória, sem crítica e sem QA — não segue assim | agente → **dono** | pesquisa de fontes canônicas (ANVISA/GAMP, com link e data) em andamento; os 2 arquivos do MRP lidos e mapeados como modelos (confirmação de requisitos com assinatura; protocolo de verificação com evidência e versão); núcleo neutro + perfil farma/ANVISA como pacote de aplicação |
| S13 | Documentos que ficam na simplificação (B3) | ✅ **decidido pelo dono (25/09):** "os necessários são ERU (quando for sistema novo), Testes E2E, Evidências dos Testes" | agente | entram no kit do B3 ao lado de TAP, especificação, HANDOFF e glossário. Interpretação a confirmar: E2E e evidências valem para toda entrega testada; ERU só para sistema novo |
| S9 | Toda mudança considera hooks, scripts, gates, README, site, links | ✅ ordem do dono | agente | vira item B1.7 (regra global) e o "mapa de impacto" do B2 |
| S10 | Haiku como autor? | ✅ confirmado: nunca; só tarefa mecânica conferida por script | — | escrito na regra global |
| S11 | Estudar o repositório `DietrichGebert/ponytail`: trazer, criar parecido ou incorporar? Se o ganho for grande e rápido, sobe nas prioridades | ✅ estudado · **priorizado** pelo critério do dono (ganho plausível, 0,5–1 h) | agente | recurso próprio, sem o pacote (Node.js + cerca de 20 adaptadores, a maioria para ferramentas não usadas aqui): escada anti-excesso de 7 degraus na skill `developer` + checagem no `qa-critic`. Próximo item depois do B1 (item B1.9). Ganho do autor (−54% linhas) é INFERIDO (n=4) |
| S12 | A escada anti-excesso vale também na regra global (toda pasta)? | ✅ decidido (sim, 25/09) · feito | agente | seção 3 da regra global + 10ª cláusula do canário; marcador de dívida fica para depois |
| D1–D6 | Decisões de desenho do B2/B3 | ✅ decididas (25/09, "sim todos"): D1 barra aqui/avisa fora · D2 tarefas no arquivo (ou `estado.json` quando existir) · D3 tabela de decisões, ADR só para arquitetura · D4 mantém `/feature-plan` · D6 markdown agora | — | B2 aprovado e em execução |

---

## Resumo executivo

**Onde estamos.** A regra global está instalada e revisada uma vez (7 achados, todos corrigidos). A
partir dela, revisão adversarial em subagente e caminho absoluto valem em toda pasta. O modo planejado
e a documentação enxuta ainda estão em desenho.

**O que falta.** (1) Plano como espelho sempre sincronizado dos arquivos de especificação, com
checklist, % de avanço e painel de decisões, gerado e conferido por ferramenta. (2) O kit documental de
projeto encolher de 15 documentos obrigatórios para 4 essenciais, mais os condicionais de ambiente
regulado, com TAP e pptx.

**Próximos passos.** Fechar o B1 (2ª revisão, merge). Você responde as 6 decisões de desenho. Depois
vêm o B2 e o B3, cada um com registro de decisão (ADR), revisão adversarial automática e pull request.

---

## Quem precisa, o quê, para quê

| Quem | Precisa de | Para |
|---|---|---|
| Dono (gestor de sistemas) | resposta executiva: onde estamos, o que falta, próximos passos | decidir e repassar sem reescrever |
| Dono | o framework completo em qualquer projeto, com revisão adversarial sem pedir | não ter de cobrar a mesma coisa de novo |
| Dono e equipe | um plano que funcione como contrato do bloco, sempre em dia com a especificação | conferir o que foi combinado e o que foi feito |
| Quem retoma o projeto (pessoa ou IA) | poucos documentos, cada um com um dono | retomar sem perguntar nada |
| Ambiente regulado | rastro de elicitação, requisito, prova e aprovação | ser auditável |

---

## 1 arquivo ou 3 + espelho — avaliação (decisão do dono, S8)

**Medido em 25/09:** os nomes `requirements.md` / `validation.md` são lidos por **5 scripts**
(`check_spec_depth`, `check_completeness`, `check_field_mapping`, `check_context_brief`,
`qa_evidence`), **3 testes** e citados em **20 documentos** de skill e roteiro. Existem **16
especificações** em `docs/specs`. Os scripts localizam o arquivo **pelo nome** e leem **por título de
seção**. Hoje, sem argumento, 3 dos 4 gates saem com erro, porque especificações antigas são anteriores
às regras (ex.: `web-package` não tem as 9 dimensões). Não é defeito novo, e "funcionar como antes"
quer dizer **o mesmo resultado para a mesma entrada**.

| | **A — 3 arquivos + plano espelho gerado** | **B — 1 arquivo único (recomendado)** |
|---|---|---|
| O que o dono lê | o espelho | o próprio arquivo: painel e resumo no topo, profundidade abaixo |
| "Nunca descolar" | depende de gerar de novo a cada edição (hook + canário); entre uma edição e a regeneração, **descola** | **não há cópia**: impossível descolar |
| Onde se marca o checklist, se responde decisão, se registra replanejamento | **não pode ser no espelho** (seria sobrescrito) → precisa de uma 4ª fonte (tarefas/decisões) | no mesmo arquivo |
| Arquivos por especificação | 3 + espelho + fonte de tarefas = **5** | **1** (+ TAP e HANDOFF do projeto) |
| Mudança nos gates | nenhuma | os 5 scripts passam a ler **também** o arquivo único, por seção; o formato antigo continua aceito |
| Separação requisito × aceite (anti-autoaprovação) | por arquivo, mas **nada mecânico** garante a ordem no tempo | carimbo "requisitos aprovados em" + "aceite ratificado pelo revisor em", com data do aceite ≥ data dos requisitos: **o verificador passa a garantir** a ordem |
| Risco | baixo nos gates, alto de descolar e de confundir onde se edita | médio nos gates, coberto pela prova abaixo |

**Por que recomendo B:** o plano tem conteúdo **interativo** (checklist, respostas, replanejamento).
Espelho gerado não pode receber edição, então a opção A precisa de uma 4ª fonte e acaba com **mais**
arquivos, não menos. E "nunca descolar" só é garantido de forma absoluta quando não existe cópia.

**Condição de aceite da opção B, conforme sua regra "funcionar como antes, sem quebrar":**
1. **Prova antes = depois:** rodar os 4 gates de especificação nas 16 especificações existentes antes
   e depois da mudança → **resultado idêntico, arquivo a arquivo** (as que passam continuam passando e
   as que falham continuam falhando pelo mesmo motivo).
2. O formato antigo (`requirements.md` + `validation.md`) **continua aceito** pelos gates. Nada é
   migrado à força.
3. O formato novo passa pelos mesmos gates, e o teste de mutação prova que cada gate **reprova** o
   arquivo único quando a seção que ele confere é apagada.
4. Ganho medido: o modelo de hoje clona 5 arquivos por especificação, 2 deles obrigatórios
   (`requirements`, `validation`) e 3 condicionais (`context-brief`, `data-dictionary`, `mission`).
   Com B: 1 arquivo, com os condicionais virando seções que só aparecem quando o caso pede.
   `mission.md` na raiz do projeto continua existindo, porque um hook de boot o lê.

---

## Crítica do pedido, antes de agir

1. **Plano escrito à mão ao lado da especificação vira a segunda verdade.** Por isso o plano é gerado.
2. **"Obrigatório de ser seguido" tem limite técnico.** Nenhum mecanismo força o agente a seguir um
   plano. O que dá para mecanizar: o verificador recusa fechar o bloco com critério sem ☑ + prova, ou
   sem registro de replanejamento; e desvio só existe se estiver registrado. Prometer mais seria
   encenação.
3. **O "Plan mode" nativo do Claude não serve de fonte.** Guarda o plano fora do projeto e não existe
   em Gemini, Copilot ou Kiro. Pode ser usado como tela de aprovação, sem ser obrigatório.
4. **Épicos e histórias formais custam mais do que rendem** num time de 4. O entregável faz o papel de
   épico, e cada item diz "quem precisa · o quê · para quê".
5. **O backlog já tem dono** em projetos que usam o pacote de controle de projeto (`estado.json`).
   Decisão D3.
6. **O TAP existente pertence ao adaptador do portal da empresa**
   (`C:\Users\fabriciosouza\projetos-portal\ferramentas\termo.py`, 18 campos). O núcleo ganha um TAP
   neutro com os mesmos campos, sem nome de cliente.
7. **Já existe um nome em uso para o painel.** Hoje, em paralelo, a sessão do projeto MRP recebeu o
   mesmo pedido seu e criou `FILA-PENDENCIAS.md` (IDs fixos: D = decisão do dono, T = trabalho). Criar
   "painel" com outro nome daria duas palavras para a mesma coisa. **Proposta:** a fila do projeto
   segue com esse nome, e o painel de cada especificação usa os mesmos IDs e o mesmo formato.
8. **Mapa de impacto em toda mudança** (sua ordem): cada bloco declara o que mais tem de mudar junto
   (hooks, scripts, gates e canários, README, guia, site, CHANGELOG, índice de capacidades, links) e o
   estado de cada item. Sem isso, a mudança fica pela metade e ninguém percebe.

---

## Decisões em aberto

| # | Decisão | Alternativas | Recomendação | Resposta do dono |
|---|---|---|---|---|
| D1 | Força do verificador do plano | (a) só avisa · (b) barra o fechamento do bloco neste repo e avisa nos outros | **(b)**: verificação que não barra é só relatório | _pendente_ |
| D2 | Onde vivem as tarefas (backlog) | (a) seção de tarefas no `requirements.md` · (b) arquivo `tarefas` curto ao lado da especificação · (c) `estado.json` quando o projeto usa controle de projeto, senão (b) | **(c)**: um dono por fato; não cria um segundo quadro onde já existe um | _pendente_ |
| D3 | Onde vivem as decisões | (a) só ADR · (b) tabela de decisões na especificação, e ADR só para decisão de arquitetura | **(b)**: ADR para toda decisão pequena é cerimônia | _pendente_ |
| D4 | Nome do roteiro | (a) manter `/feature-plan` e ampliar · (b) criar `/plano` e aposentar o antigo por ADR | **(a)**: renomear custa ADR e quebra hábito sem ganho | _pendente_ |
| D5 | Quando a revisão automática roda fora do repo | já decidido na regra global: todo bloco que entrega ou altera algo; pergunta e leitura, não | — | ✅ aplicado |
| D6 | Visualização do painel | (a) tabela markdown com % · (b) além dela, página visual gerada do mesmo arquivo, sob demanda | **(a) agora, (b) depois do B2** | _pendente_ |

---

## Backlog e checklist

Legenda: `[ ]` a fazer · `[x]` feito, com prova · `[~]` replanejado, com motivo em "Replanejamento".

### B1 — Regras do dono em toda pasta

- [x] B1.1 Fonte versionada `C:\Users\fabriciosouza\metacognition-framework\.claude\global\CLAUDE-global.md`: revisão em subagente, escada de modelos, caminho absoluto. Prova: `check_rules_parity.py` PASS.
- [x] B1.2 `sync-global` instala em `C:\Users\fabriciosouza\.claude\CLAUDE.md` por marcadores, sem apagar texto do usuário. Prova: 2 execuções com o mesmo hash; marcador órfão sem escrita; somente-leitura relatado; BOM preservado.
- [x] B1.3 Canário que morde: 9 cláusulas apagadas uma a uma, 9 reprovadas; instalador só com comentário reprova. Prova: `test_rules_parity.py` PASS.
- [x] B1.4 ADR-116 + índice de capacidades + CHANGELOG. Prova: `test_capabilities.py` PASS.
- [x] B1.5 1ª revisão adversarial (Sonnet): FAIL, 7 achados, 7 corrigidos.
- [x] B1.6a Revisões 2 a 5 (a 3ª reprovou e levou ao redesenho: uma implementação só). Prova: ADR-116, tabela "Estado do QA".
- [x] B1.6b Suíte completa de canários · pull request · merge. Prova: PR #154 mergeado em 25/09, canários locais 88 PASS · 0 FAIL; `~/.claude/CLAUDE.md` reinstalado a partir da `main`.
- [ ] B1.7 Regra global ganha "mapa de impacto em toda mudança" (sua ordem de 25/09), com canário.
- [ ] B1.9 Escada anti-excesso de código (estudo do ponytail, S11): 7 degraus na skill `developer` (não precisa existir → já existe no repo → biblioteca padrão → recurso nativo → dependência já instalada → uma linha → código mínimo) e checagem de excesso no `qa-critic`. Texto próprio, sem copiar o pacote; atribuição à ideia original (MIT). Aceite: a skill `developer` tem a escada; a skill `qa-critic` e o subagente `.claude/agents/qa-critic.md` conferem contra ela; registro PARTIAL/prosa honesto; `test_capabilities`, `test_marketing_claims` e `test_audit_enforcement` verdes. Não há canário de conteúdo das skills: é prosa, cobrada em revisão.
- [ ] B1.8 Verificação comportamental numa pasta virgem: pedir uma mudança de código → o revisor roda sem pedido e os links saem absolutos.

### B2 — Modo planejado (opção decidida: arquivo único — S8)

**B2a — arquivo único + gates + prova** (em revisão)
- [x] B2.1 Modelo `docs/specs/_template-spec-unico/spec.md`: painel, resumo executivo, quem/o quê/para quê, crítica; Partes A–E com todo o conteúdo do modelo antigo (gerado pelo conversor); decisões, tarefas, mapa de impacto, replanejamento, revisões. Prova: o leitor resolve as 5 partes do modelo.
- [x] B2.2b Os gates leem o arquivo único pelo leitor `tools/spec_fonte.py`; formato antigo aceito. Prova: fotografia dos 4 gates nas **11** especificações antigas (eram "16 pastas"; 11 têm `requirements.md`) — 0 diferenças na saída inteira; `tools/test_spec_unico.py` PASS (mesmo veredito + perda zero) e 3 sabotagens pegas.
- [x] B2.3a `/feature-plan` (grau completo) cria o arquivo único; `readiness-gate`, `discovery`, `developer`, `qa-critic`, `implement`, `handoff` e regra 04 aceitam os dois formatos. `--quick` não muda.
- [x] B2.4 Ordem das etapas escrita no topo do modelo.
- [x] B2.5a ADR-117 + CHANGELOG + índice de capacidades (`spec-arquivo-unico`, fail-closed) + site (103).

**B2b — verificador do plano e painel** (depois do B2a)
- [ ] B2.2 `tools/plano.py verificar`: reprova seção obrigatória ausente, decisão pendente sem "quem age", item `[x]` sem prova, % que não bate com a contagem, mapa de impacto ausente, aceite datado antes da aprovação dos requisitos. Barra o fechamento neste repo; avisa nos outros (D1).
- [ ] B2.3b A regra de confirmação (regra 06) aponta para o painel do arquivo único.
- [ ] B2.6 Painel acumulado + status curto por resposta: toda resposta com a frente aberta termina com avanço, decisões pendentes pelo número e link absoluto para o painel.
- [ ] B2.7 (depende de D6) Página visual gerada do painel.

### B3 — Documentação de projeto enxuta

- [ ] B3.1 Kit essencial: **TAP** · **especificação** (arquivo único, conforme S8) · **HANDOFF** · **GLOSSÁRIO**.
- [ ] B3.1b Necessários por decisão do dono (S13): **Testes E2E** e **Evidências dos Testes** em toda entrega testada; **ERU** (especificação de requisitos do usuário) quando for **sistema novo**. O código de documento controlado (ex.: da garantia da qualidade) nunca é inventado: vem do dono.
- [ ] B3.2 Gerados, nunca à mão: pptx e one page a partir do TAP + especificação, via `tools/gen_exec_doc.py` (já gera pptx).
- [ ] B3.3 Condicionais: RUNBOOK (quando alguém opera com as próprias mãos) · em ambiente regulado, além dos de B3.1b: matriz requisito → prova e aprovação.
- [ ] B3.4 Modelo de TAP neutro no núcleo (campos do termo do adaptador, sem nome de cliente); `mission.md` e `context-brief.md` são absorvidos por ele, respeitando o hook que lê `mission.md`.
- [ ] B3.5 Reescrever a tabela de 15 documentos da skill `project-docs` para kit essencial + condicionais.
- [ ] B3.6 ADR-118 + CHANGELOG + índice de capacidades.

### Em todos os blocos (não negociável)

- [ ] Revisão adversarial automática em subagente isolado (um degrau abaixo do padrão) em cada etapa e no fechamento.
- [ ] Mapa de impacto preenchido: hooks, scripts, gates e canários, README, guia, site, CHANGELOG, capacidades, links.
- [ ] Veredito no ledger de evidências; pull request por bloco; canários e status antes do merge.

---

## Fora de escopo

- Plugin instalável. O pedido é comportamento.
- Regras equivalentes para Gemini, Copilot e Kiro (leem outros arquivos). Ficam para o bloco de paridade entre IAs.
- Repositórios de domínio (MDriver, portal de projetos). Do portal só se lê o TAP.
- Migrar projetos existentes para o kit novo: acontece em cada um, quando for retomado.
- Observado e não tratado: o `CLAUDE.md` do repo chama o ADR-070 de "isolamento de escrita", mas ele trata de identidade do repositório.

---

## Replanejamento

| Data | Item | O que mudou | Por quê | Quem aprovou |
|---|---|---|---|---|
| 25/09 | B2 inteiro | de "PLANO substitui 3 arquivos" para "3 arquivos são a fonte, PLANO é espelho gerado" | juntar desligaria 3 verificações automáticas existentes; o dono decidiu | dono |
| 25/09 | Ordem | B1 executado antes da aprovação do plano | ordem direta do dono: "resolva por padrão, sempre, em todo lugar" | dono |

---

## Revisões adversariais

| Rodada | Objeto | Revisor | Veredito | O que mudou |
|---|---|---|---|---|
| P1 | versão 1 deste plano | Sonnet isolado | FAIL, 9 achados | autoaprovação, régua de ganho líquido, ordem, custo, jargão: corrigidos na versão 2 |
| B1-1 | regra global (B1) | Sonnet isolado | FAIL, 7 achados (3 ALTA) | 7 corrigidos; ver ADR-116 |
| B1-2 | correções do B1 | Sonnet isolado | PASS-COM-RESSALVAS, 2 novos | `bootstrap.py` passa a instalar; caminho absoluto gerado por máquina |
| B1-3 | correções da rodada 2 | Sonnet isolado | FAIL (2 ALTA, 1 MÉDIA) | 3ª reprovação → **redesenho**: uma implementação só (Python), os outros pontos só chamam |
| B1-4 | o redesenho | Sonnet isolado (1ª tentativa travou sem veredito; relançada) | PASS-COM-RESSALVAS, 4 achados (1 ALTA) | somente-leitura sem exceção; regex ancorada; estilo dominante; provados por sabotagem |
| B1-5 | confirmação, em primeiro plano, sobre o índice do commit | Sonnet isolado | PASS-COM-RESSALVAS | aprovado; revisora violou só-leitura e declarou; conferido sem dano |
| P2 | esta versão do plano | — | **ainda não revisada** | revisa na aprovação |
