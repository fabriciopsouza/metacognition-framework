# ADR-109 — Recuperar as premissas antes de decidir

- **Status:** Aceito
- **Data:** 2026-08-24
- **Decisores:** dono (gap de campo + decisão) · agente (proposta e mecanismo)
- **Relacionadas:** ADR-019 (sync com origin) · ADR-029 (não queimar contexto) · ADR-093 (premissa
  de ambiente é inferência) · ADR-094 (canônico-prevalece) · ADR-102 (`_shared/project-docs`)

## Contexto

Numa sessão real (2026-08-23) o agente cometeu três erros encadeados, todos com a mesma raiz:

1. **Afirmou `[CONFIRMADO]` uma premissa que contrariava definição já tomada pelo dono.** Não achou
   registro da origem de um indicador nos artefatos do repo e concluiu, como fato, a direção oposta.
   Era *ausência de evidência* tratada como *evidência de ausência*.
2. **Reprocessou trabalho já fechado mudando uma regra acordada** — normalizou um campo do modelo
   por julgar tecnicamente melhor, sem confirmar, sobre entrega que o dono considerava concluída.
3. **Leu como vigente o código de uma branch órfã**, 80 commits atrás de `main` e com a ADR nunca
   mergeada. Concluiu sobre o estado do framework a partir de arqueologia.

Diagnóstico do dono, textual: *"este comportamento de recuperar premissas, ver git, ler tudo e ter
certeza para não reinventar a roda DEVE ser comportamento padrão do framework."*

**A regra já existia como intenção.** `traceability` Regra 1 (file-first) manda ler antes de assumir;
a Regra 6 fixa canônico-prevalece. O que faltou não foi doutrina — foi **alcance do inventário** e
**mecanismo**. Duas lacunas medidas:

- **Nenhum inventário do framework olhava a memória.** Na sessão, a memória do próprio projeto
  estava vazia *e a premissa vivia na memória de um projeto irmão*. O agente concluiu "não há
  registro" de uma busca que nunca cobriu o lugar certo.
- **Nenhum inventário declarava a procedência do código lido.** `check_repo_sync` (ADR-019) gateia
  *sincronia*, mas não diz "você está numa branch cuja decisão nunca entrou em main".

> **EMENDA (2026-08-26, ao fechar o bloco).** A segunda lacuna acima estava **medida errada**. Ao
> implementar, a leitura de `check_repo_sync.py::baseline_staleness` (ADR-084) mostrou que ela já
> mede exatamente isto — `HEAD..origin/main` para branch com upstream próprio em dia — persiste
> `.claude/.stale-vs-main` e faz o route-gate repetir por turno até resolver ou reconhecer. Ou seja:
> a camada 2 **tinha dono**, e o dono era mais forte que a reimplementação proposta aqui (que seria
> um aviso de boot sem persistência nem repetição). Manter as duas seria duplicação mais fraca,
> rejeitada pela régua de ganho líquido (ADR-007). Ver §Decisão 1 emendada.

Havia ainda um precedente instrutivo: `boot_brief.py`, escrito na linha ADR-101 para um gap
irmão ("o modelo não lê a documentação antes de iniciar"), **nunca foi mergeado** — vive só na
branch órfã. Ou seja, o próprio remédio anterior é vítima do problema que esta ADR ataca.

## Decisão

**1. O inventário de premissas cobre três camadas, não uma.** Memória (própria **e dos irmãos**) ·
procedência do trabalho (branch, divergência, últimos commits, árvore suja) · artefatos de decisão
do repo (mission, requirements, ADRs, glossário, provas).

> **EMENDA (2026-08-26).** Três camadas continuam **obrigatórias no boot**; muda **quem entrega a
> camada 2**. `premises_brief.py` implementa as camadas 1 e 3 e **delega a 2** ao `check-repo-sync`
> (ADR-019/084), citando-o nominalmente no texto injetado — o agente é instruído a ler o aviso dele,
> nunca a presumir estar em dia. A cobertura do dono não diminui: ela passa a vir de um mecanismo
> que **persiste e repete**, em vez de um aviso de boot que se perde na primeira compactação.
>
> **Delegação sem canário é buraco silencioso**, e este era o risco real: se alguém removesse o
> `baseline_staleness`, a camada 2 sumiria e ninguém notaria, porque este hook nunca a mediu. Por
> isso `test_lacuna_2_delega_procedencia_e_o_delegado_existe` checa os dois lados — que o ponteiro
> está no texto **e** que o delegado existe e ainda expõe a função. Contraprova junto: se este hook
> voltar a medir divergência por conta própria, o canário reprova, porque aí a delegação virou
> duplicação.

**2. Vira mecanismo no boot:** `tools/hooks/premises_brief.py` (SessionStart). Emite **ponteiros,
nunca conteúdo** (ADR-029): a existência e o caminho, para não queimar contexto. Fail-open — o boot
nunca quebra por causa dele.

**3. Três invariantes viram texto injetado, não subentendido:**
- ausência de evidência não é evidência de ausência → `[A-DEFINIR]`, nunca `[CONFIRMADO]`;
- *"não encontrei X em A, B e C — onde está?"* é resposta legítima; presumir no lugar do dono não é;
- regra já acordada não muda sem confirmação, ainda que o agente a julgue melhor.

**4. Doutrina em `_shared/traceability` Regra 9**, ao lado de file-first e canônico-prevalece, que é
onde alguém procura.

**5. Cross-IA:** entra no `PROMPT-CHAT-WEB` e no `AGENT-FRAMEWORK`, porque o defeito é do
comportamento do agente, não da ferramenta — uma IA sem hooks precisa da regra em prosa.

## Alternativas consideradas

- **Só reforçar a prosa no CLAUDE.md.** Rejeitada: é exatamente o que já existia e perdeu para o
  viés de progredir na tarefa. `feedback-prosa-vira-mecanismo` é a memória que registra esse padrão.
- **Ressuscitar o `boot_brief.py` da branch ADR-101.** Rejeitada como caminho único: aquele hook
  cobre só a camada 3 (artefatos do repo) — não olha memória nem git, que são justamente as duas
  lacunas medidas. O que sobrevive dele está absorvido aqui.
- **Gate bloqueante que exige declarar as fontes consultadas antes de todo tool call de domínio.**
  Rejeitada por ora: o custo de falso-positivo é alto (toda tarefa trivial pagaria pedágio) e não há
  como verificar deterministicamente que *ler* aconteceu. Fica como débito, se o inventário provar
  ser insuficiente.
- **Listar todas as memórias irmãs com conteúdo.** Rejeitada: queima contexto e viola ADR-029.
  Lista nome + contagem, e o agente abre o que for pertinente.

## Consequências

**Positivas:** a premissa que se perdeu naquela sessão apareceria no boot — o inventário aponta as
memórias irmãs e a divergência de branch. O canário exercita as três lacunas **e a contraprova**
(projeto virgem não fabrica inventário), atendendo à exigência de `project-docs §3.1` de que gate
nunca exercitado é decoração.

**Negativas / dívidas:**
- **O inventário informa; não prova leitura.** Um agente pode ignorá-lo. A mitigação é social
  (ignorar passa a ser erro visível, não esquecimento), não técnica. Débito registrado.
- Custo fixo de boot: uma varredura de diretório e três chamadas `git` com timeout de 8s.
- A derivação do slug de memória (`:` e separador → `-`) espelha convenção do harness. Se ela mudar,
  a camada 1 degrada para "memória própria ausente" — que é fail-soft na direção segura, mas
  silencioso. Coberto por canário.
