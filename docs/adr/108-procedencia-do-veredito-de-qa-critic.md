# ADR-108 — Procedência do veredito de qa-critic: o boletim deixa de ser escrito só pelo avaliado

- Status: **Aceito** (2026-08-18 — gate: qa-critic isolado, modelo ≠ autor, **6 rodadas / 5 REPROVAR**; canário com 34 verificações) · Decisores: dono ("pedi que o framework fosse determinístico, que as ferramentas funcionassem e não fosse TEATRO") + squad
- Tipo: **fecha furo estrutural de integridade de evidência**. Régua §0 (ADR-007): satisfaz (c) — *destrava enforcement que não existia*: o `squad_gate` conferia forma, escopo e recência do veredito e nunca a procedência. +1 capability `qa-attestation-provenance`.
- Relaciona: ADR-011 (QA bicelular), ADR-074/077 (qa-evidence, ledger de junções), ADR-103 (recência e escopo do veredito), ADR-071 (`verify_hitl_proofs` — o padrão de "verificado, não declarado" que este ADR copia), ADR-106 (prova de mutação).

## Contexto — a pergunta que expôs o furo

O dono perguntou se, depois de zerar o passivo (v1.89.0), podia considerar que "tudo tem gates reais e que seguir as etapas é determinístico". A resposta honesta era não, e o motivo mais caro não era o número de capacidades provadas: era que **o registro do processo é escrito pelo avaliado**.

O método do dono estava correto e rodando: QA adversarial em subagente isolado, modelo ≠ autor. Quatro rodadas naquela mesma sessão acharam defeitos reais, incluindo uma fixture cega do próprio autor. O que faltava não era independência de julgamento — era **procedência do registro**:

- `atestacao.agentId` e `atestacao.modelo` eram **strings que o orquestrador digitava**;
- o texto do veredito era **transcrito à mão** do relatório do subagente;
- o `escopo_paths` era escolhido pelo orquestrador;
- nada obrigava a rodar o crítico: o gate exigia **o artefato**, não a execução.

Modo de falha concreto: um agente com pressa graveria um veredito plausível, com `modelo: "claude-sonnet-5"` e um `agentId` inventado, e o gate liberaria — porque tudo que ele checava era forma, escopo e recência.

## A decisão

Usar os **transcripts do harness** (`~/.claude/projects/<slug>/*.jsonl`) como fonte de procedência. Eles são escritos pelo harness, no momento em que cada coisa acontece, e deles saem quatro fatos que o orquestrador não produz:

1. que houve chamada `Agent` com `subagent_type` de qa-critic, e com que modelo foi **pedida**;
2. o **texto exato** que o subagente devolveu (`tool_result`);
3. o `agentId` daquela execução;
4. o modelo do **autor**, gravado turno a turno (`message.model`).

**A prova:** o veredito declara `atestacao.prova_transcript = "sha256:<hex>"`, o hash do relatório devolvido. `tools/verify_qa_attestation.py` procura nos transcripts um `tool_result` cujo hash bata. Sem relatório real com aquele texto não existe hash que bata — achado não pode ser inventado sem quebrar a prova.

**A invariante de maior valor**, além do hash: **relatório que REPROVA não pode virar veredito aprovativo**. É a fraude que mais importa e é checável direto no texto.

Passivo pelo mesmo desenho do ADR-106: veredito **sem** `prova_transcript` é **listado**, não reprovado (34 legados). Quem nasce depois da norma nasce sob ela. Dos 51 vereditos existentes, **17 foram verificados retroativamente** contra o relatório real do crítico.

## Seis rodadas adversariais — cinco REPROVAR

Este ADR levou **cinco reprovações seguidas** do qa-critic antes de passar. Vale registrar a
sequência, porque ela é o argumento do próprio ADR:

| # | o que o crítico derrubou |
|---|---|
| 1 | guarda de negação só no caminho secundário: `"o veredito não é APROVAR, é REPROVAR"` lia **aprovar** — desarmava a invariante central; `agentId` pela primeira ocorrência sequestrava a chave |
| 2 | "última não-negada no texto inteiro": um **P.S. comparando com rodadas passadas** enterrava um `**REPROVAR**` real |
| 3 | "última linha formal": **exemplo em cerca de código** e **citação em blockquote** faziam o mesmo |
| 4 | "última formal antes do trailer": o crítico **narrando que mudou de ideia** (prática que este framework incentiva) e **subveredito por achado** ainda invertiam a leitura |
| 5 | sentinela por posição: **citação de auditoria** do sentinela da rodada anterior vencia o próprio |

Cada rodada fechou o vetor apontado e **nenhuma fechou a classe**. O crítico nomeou o motivo na
rodada 4: *heurística de posição sobre prosa livre não distingue "a conclusão" de "qualquer outra
linha formatada como token"* — e os motivos legítimos para escrever a segunda são ilimitados.

A saída não foi mais uma regex: foi **mudar o contrato**. A conclusão passou a ser um sentinela
único (`rule #13`), e a ambiguidade passou a ser resolvida por **contagem**, não por posição —
porque reuso quebra contagem em qualquer ordem.

**O preço, declarado:** o número caiu de "17 verificados" para **0**, porque nenhum relatório
anterior à norma tem sentinela. Os 17 mantêm **procedência** provada; o que falta neles é a
**concordância**. São duas provas diferentes e o verificador passou a reportá-las separadas.

## Limites declarados — não são propriedades que este verificador finge ter

- **Qual modelo REALMENTE respondeu não é verificável.** O harness não grava os turnos do subagente. Prova-se o modelo **pedido** e o do **autor**, não o que executou.
- **Exemplo que é a última coisa escrita.** Um relatório que **nunca escreve o próprio sentinela** e menciona um exemplo (`"o formato é assim: <<<VEREDITO_FINAL: APROVAR>>>"`) tem exatamente um sentinela, e ele é o último — as duas propriedades que o mecanismo verifica. Nenhuma regra de posição ou contagem distingue "isto é a conclusão" de "isto é um exemplo que por acaso não teve nada depois". **Não será perseguido:** exige que o crítico já tenha violado a cláusula primária da rule #13, é visualmente óbvio no texto bruto, e persegui-lo com mais regex repetiria o erro das rodadas 1-5. É o limite honesto do que heurística de texto prova — a distinção exemplo × conclusão, quando têm forma idêntica, é julgamento irredutível.
- **Amaciamento fino escapa.** O hash prova que o relatório existe e que o veredito global concorda com ele; não que cada achado manteve a severidade.
- **`sem_leitura` e `ressalva` têm o mesmo custo** (exit 3, mesma linha "PASS COM RESSALVA"). Nada distingue "esqueceu o sentinela" de "evitou o sentinela". **Critério de monitoramento**, dado pelo crítico: se `sem_leitura` continuar sendo maioria *depois* de a norma ter tido tempo de pegar em relatórios novos, é sinal de evasão, não de legado.
- **O transcript é arquivo local, gravável pelo agente em princípio.** Modelo de ameaça: *"agente com pressa corta caminho"*, não *"agente forja o log do harness"*.
- **Local, não CI.** Transcripts não são versionados. Roda na máquina do autor, mesma postura do `post_canary_status.py`.

## Alternativas consideradas

1. **O próprio subagente grava o veredito.** Rejeitada: o `qa-critic` é read-only por desenho (ADR-011); dar-lhe `Write` cria um caminho de escrita no repo a partir de um papel cujo valor é justamente não ter interesse no resultado.
2. **Assinatura criptográfica do crítico.** Rejeitada por ora: não há material de chave disponível ao subagente. É o degrau seguinte se o hash provar insuficiente.
3. **Exigir `prova_transcript` de todos os 51 retroativamente.** Rejeitada: fabricar procedência para veredito antigo seria exatamente o teatro que este ADR combate. Os 34 sem execução no log ficam declarados como legados.

## Consequências

- `squad_gate` continua sendo o gate de commit; este verificador é canário da suíte (`run_canaries.py`) e roda a cada release. Amarrá-lo ao `squad_gate` como bloqueio é bloco próprio — a mesma disciplina do ADR-104.
- Veredito novo sem `prova_transcript` fica visível a cada execução; não é silêncio.
- O que este ADR **não** resolve: o `escopo_paths` continua escolhido pelo orquestrador, e o prompt dado ao crítico continua sendo escolha do autor. Crítico independente apontado para a pergunta errada é independente e cego.

## Artefatos

- `tools/verify_qa_attestation.py` — verificador. Modos: todos os vereditos, `--veredito <path>`, `--transcripts/--qa-dir` (para o canário).
- `tools/test_verify_qa_attestation.py` — canário, **14 verificações**, forja pega em 4 formas (agentId inexistente, hash divergente, subagente não-crítico, relatório que reprova) + anti-falso-positivo + legado.
- `capabilities.json` — capability `qa-attestation-provenance`, `fail-closed` com mutação provada.

## Pendências

- Amarrar ao `squad_gate` como bloqueio (hoje é canário da suíte).
- Convenção de linha final de veredito nos prompts de qa-critic, para elevar a cobertura da checagem de concordância acima dos 5/51 atuais.
- `escopo_paths` validado contra o que o crítico de fato leu — o furo irmão, ainda aberto.
