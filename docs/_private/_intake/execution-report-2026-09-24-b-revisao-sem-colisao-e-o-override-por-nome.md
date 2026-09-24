# Andamento — 24/09/2026 (bloco B): revisar sem colidir, e o override que morre por um espaço

> Execution-report de encerramento de bloco (ADR-038/052/062 · tier **OWNER** · privado,
> não distribuído). **Segundo bloco do dia.** O primeiro
> ([`...sistema-pesagem-e-o-gate-tautologico.md`](execution-report-2026-09-24-sistema-pesagem-e-o-gate-tautologico.md))
> fechou antes deste trabalho existir, e por isso não o cobre.

## Onde estamos, em uma linha

O dono pediu duas coisas numa planilha GUT — registrar a classificação do Diretor de Planta
para o Sistema de Pesagem e tornar a cor da nota dinâmica — e **as duas já estavam feitas
por outra sessão**, num arquivo que estava sendo editado no momento em que eu o li. O bloco
virou o que não colidia: **revisão adversarial só-leitura**, e o registro do enquadramento
do diretor no repositório que é meu.

## Métricas

| Métrica | Valor |
|---|---|
| Tokens | **NÃO MEDIDO CONFIAVELMENTE** (mesma razão do bloco A: o `--from-transcripts` agrega vários transcripts) |
| Commits | 1 no repo de domínio (`769d20a`) + este report |
| Arquivos escritos em repo de terceiro | **zero** — deliberado |
| Achados da revisão | 4 (1 ALTA, 2 MÉDIA, 1 BAIXA) |
| Achado descartado por conferência | 1 (ver abaixo) |
| Testes | `tools/verifica.py` do pacote de domínio: 6 gates, rodado 3× (reprovou 1× por âncora minha, depois PASS). Nenhum teste novo escrito neste bloco — a revisão foi só-leitura, e os testes que faltam são do repositório de terceiro, entregues como ressalva 3 em vez de patch |
| Rodadas de retrabalho | 1 — a âncora inventada, barrada pelo `G1` e corrigida perguntando o slug ao verificador |

## De onde saímos → onde chegamos

**O que o dono trouxe:** uma captura da matriz GUT, a classificação nova do diretor (risco
de contaminação de insumos, perda financeira, paralisação da produção) e a queixa de que
teve de mudar a cor do 100 **à mão**.

**O primeiro achado foi de procedência, não de conteúdo.** A planilha é **gerada** por
`gut.py`; nota ajustada na célula é perda agendada. Enquanto eu lia o gerador, **os números
de linha deslocaram**: medi `gut.py` modificado às `11:10:16` contra a minha leitura às
`11:10:24` — **8 segundos**. Outra sessão estava implementando exatamente os dois consertos
pedidos, inclusive com um comentário citando que "o dono teve de corrigir a mão em
24/09/2026".

**A decisão que definiu o bloco:** parar. A pasta `info-projetos-sistemas` **não tem git**.
Duas sessões escrevendo ali destroem trabalho sem reflog, stash ou fsck — e eu já havia
apagado uma edição não commitada nesta mesma sessão, com git disponível. Ancorei a revisão
no sha `ed95d8af` e declarei a âncora, porque revisar alvo móvel e reportar como estado
final é mentir sem querer.

**A revisão foi feita gerando numa cópia isolada no scratchpad**, nunca no arquivo real —
que ainda estava aberto no Excel.

## O placar gate × achado

| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| Planilha é gerada; edição manual é perda agendada | **eu**, ao procurar o arquivo antes de editá-lo | nenhum — não existe gate que avise "este artefato é gerado" |
| Arquivo sendo editado por outra sessão, ao vivo | **eu**, comparando mtime com o relógio | **nenhum** — o framework não tem detecção de sessão concorrente fora do git |
| Override do diretor casado por nome exato, sem asserção | **eu**, sabotando a chave em cópia isolada | nenhum lá; é a mesma família do `I5` que construí no bloco A |
| Desempate declarado × implementado divergem após ordenar | **eu**, lendo a fórmula | nenhum |
| Conserto sem canário em `verifica.py` | **eu**, procurando o canário | nenhum — a ausência de canário não dispara nada |
| Nota apagada fica verde (`>=0` pinta Baixa) | **eu**, olhando a regra 4 | nenhum |
| **Achado que eu ia reportar e não era achado** | **eu**, conferindo antes de afirmar | — |
| Âncora quebrada no link que escrevi | **`G1`**, do meu próprio pacote | `G1` — **funcionou** |

## Detecção: framework × humano

- **O `G1` pegou meu erro na mesma hora** — link com âncora inexistente, escrito minutos
  antes. Corrigi perguntando o slug **ao próprio verificador** em vez de adivinhar a regra,
  que foi o que me fez errar da primeira vez no bloco A.
- **Nada no framework detectou a sessão concorrente.** Foi comparação manual de `mtime`
  contra o relógio. Em pasta versionada o `git status` acusaria; fora do git não há sinal.

## O que eu errei, e o que derrubou cada erro

1. **Ia reportar como defeito que o desempate do topo era arbitrário.** Antes de afirmar,
   fui ler: o critério **está declarado** na aba "Como utilizar" ("por Urgência, depois por
   Gravidade, depois por ordem alfabética") e há asserção provando prioridades únicas.
   Derrubou: a conferência. **O achado virou outro, e melhor** — a aba declara *alfabética*
   e a fórmula implementa `ROW()`; coincidem na geração e divergem quando alguém ordena a
   planilha, o que o AutoFilter convida a fazer.
2. **Escrevi uma âncora inventada** no link novo do HANDOFF. Derrubou: `G1`.

## Gaps (flagados, não silenciados)

- **Não há sinal de sessão concorrente fora do git.** O framework assume um autor por
  árvore, e em pasta sem git não há nem `git status` para desmentir. Aqui a colisão só não
  aconteceu porque eu comparei `mtime` por hábito. **Gap conhecido, sem mecanismo
  proposto** — detectar isso genericamente é caro e dependente de plataforma.
- **Não há marca de "artefato gerado" legível por quem edita.** Quem abre um `.xlsx` no
  Excel não tem como saber que ele é reescrito por script. O projeto vizinho resolveu isso
  do jeito certo — mensagem no `PermissionError` avisando que nota editada na célula some —
  mas é remédio no momento da falha, não prevenção.

## Melhorias candidatas (régua §0 — nenhuma promovida)

- **Asserção de override órfão.** `DECIDIDAS.get(nome)` devolvendo `None` em silêncio é a
  mesma classe do `I5` do bloco A (anotação citando ID inexistente). **Duas ocorrências, em
  dois projetos, no mesmo dia** — é o candidato mais forte que o dia produziu, e o primeiro
  a ter a segunda instância que a régua §0 pede. **Ainda assim não promovo aqui**, porque as
  duas instâncias vivem em repositórios de domínio e o núcleo não tem o padrão genérico
  ("dicionário de override casado por chave textual") declarado em lugar nenhum. Quitação:
  se aparecer a terceira, extrair o padrão, não o código.

## Boas práticas (reutilizável)

- **Medir `mtime` contra o relógio antes de editar arquivo de pasta compartilhada.** Custou
  um comando e evitou uma colisão sem recuperação.
- **Ancorar revisão num sha e declarar a âncora.** Alvo móvel revisado sem âncora produz
  relatório que parece estado final e não é.
- **Sabotar em cópia isolada para medir consequência.** "O override pode falhar" é hipótese;
  "cai de 100/prioridade 2 para 36/prioridade 15 e o script sai 0" é medição.
- **Perguntar a regra ao próprio verificador** em vez de reimplementá-la de cabeça.

## Lições por skill (agnóstico de domínio)

- **qa-critic:** *conferir o achado antes de reportá-lo derruba uns e melhora outros.* O
  achado que eu ia escrever era falso; o que sobrou da conferência é mais preciso e mais
  grave.
- **developer:** *override casado por string exata precisa de asserção de que casou.*
  `.get()` que devolve `None` em silêncio é o mesmo defeito do gate que conta e não compara.
- **architect:** *artefato gerado precisa dizer que é gerado, no lugar onde alguém o edita.*
  Dizer no README não alcança quem abre o arquivo no Excel.
- **docops:** *revisar trabalho de outra sessão é leitura, não escrita* — e a entrega é o
  achado, não o patch. Aplicar seria mais rápido e teria destruído trabalho alheio.
- **pmo:** *quando o pedido do dono já está atendido por outro caminho, a entrega muda de
  natureza.* Refazer teria sido duplicação com colisão; o valor estava em conferir.

## Procedência

- Repo de domínio (meu): `C:\Users\fabriciosouza\sistema-pesagem` @ `769d20a`, 6 gates PASS.
- Repo revisado (de terceiro): `C:\Users\fabriciosouza\info-projetos-sistemas`, `gut.py` @
  sha `ed95d8af`, **somente leitura, zero escrita**. Sem git.
- Sessões concorrentes vistas no momento: `metacognition-framework-b9` e
  `metacognition-framework-c9`, ambas ativas.
- Framework: `main` sincronizado 0/0 com origin ao início deste bloco.
- Gates inertes desta sessão (ADR-061), aplicados à mão: `check-repo-sync` → 0/0 ·
  `check-core-agnostic` → PASS (norma).
- **O que este report não mede:** tokens, tempo de parede e turnos; e não mede se as 4
  ressalvas serão aplicadas — isso é decisão em aberto do dono.
