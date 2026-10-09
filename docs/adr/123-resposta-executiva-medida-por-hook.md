# ADR-123 — Resposta executiva medida por hook de Stop

- **Status:** Aceito, **suplantado em parte pelo ADR-129** (28/09/2026): o hook não bloqueia mais, e o limite
  fixo de 150 palavras saiu.
- **Data:** 2026-09-27
- **Decisores:** dono (Fabricio), 27/09/2026:
  - "CONCISÃO, CLAREZA, informação simples e direta, overview, checklist, ações e ideias encadeadas. NÃO uma
    redação verborrágica. A explicação detalhada pode e deve ser feita SE SOLICITADA."
  - "Reportou e a tarefa precisa de algo, tem que parar e esperar. Ou terminar o que está fazendo e pedir ao final."
  - "siga".

  Autoria: Opus 5.5.
- **Relação:** regra global, seção 4 (ADR-116); wiring global (ADR-027); regra "nada de fiar as capacidades somente
  em prosa" (27/09/2026).

## Contexto
1. O formato executivo já era regra em prosa (seção 4 da regra global e memória) e foi violado em várias sessões.
2. Dois plugins de estilo de saída (explicativo e de aprendizagem) estavam ligados e injetavam, em toda sessão, a
   ordem contrária.
3. Pedido feito ao dono no meio do processamento some quando a tela sobe.

## Decisão
1. **`tools/hooks/resposta_executiva.py`, hook de Stop.** Mede o turno encerrado e devolve a resposta para reescrita
   uma vez (exit 2) quando:
   - a mensagem final passa de 150 palavras de prosa, fora de tabela, código e título, salvo se o dono pediu
     detalhe ou um artefato ("escreva o ADR", "gere o relatório");
   - há pedido ao dono em texto intermediário do turno;
   - há bloco "★ Insight".

   Com `stop_hook_active` não devolve de novo. Transcript ilegível não trava a sessão.

   **Turno:** começa no último pedido do dono ou aviso do sistema, porque o turno anterior já foi medido no Stop
   dele. A isenção de detalhe e de artefato vem do último pedido escrito pelo dono; aviso do sistema não conta.

   **Contrato**, conferido nos docs oficiais de hooks em 27/09/2026:
   - exit 2 no Stop impede a parada e o stderr volta ao modelo;
   - outro código não bloqueia.

   **Comando:** `python "<hook>" --hook`, sem `|| true`, que engoliria o exit 2. Sem python no PATH, o shell sai
   com 127, que não bloqueia: a sessão segue.
2. **Instalação em toda pasta:** o `sync-global.ps1` espelha o hook para `~/.claude/hooks/` e o
   `ensure-global-wiring.ps1` o liga em `hooks.Stop` do `~/.claude/settings.json`, com auto-cura.
3. **Regra global, seção 4:** toda resposta é executiva; o pedido ao dono fica só no fim.
4. **Plugins desligados:** os dois de estilo de saída foram desligados no `~/.claude/settings.json` do dono em
   27/09/2026, com backup `settings.json.antes-plugins-estilo.bak`.

## Alternativas descartadas
- **Só regra em prosa:** já existia e falhou.
- **Bloquear sem limite de devoluções:** laço infinito; uma devolução por turno basta.
- **Limite de tamanho total:** puniria tabela e código, que são o formato pedido.

## Limites
- O limite de 150 palavras e a detecção de pedido ("?" no fim da linha, verbos de decisão) são heurísticos: pedido
  escrito sem esses sinais passa; pergunta retórica no meio é devolvida.
- Depois de uma devolução, a segunda resposta passa sem medição (`stop_hook_active`).
- Subagente não é medido: o dono lê a resposta do orquestrador.
- Em 24 turnos reais anteriores à regra (3 transcripts), 23 seriam devolvidos. É a magnitude esperada no início;
  cada turno é devolvido no máximo uma vez.

## Prova
- `tools/test_resposta_executiva.py`.

## Estado do QA
| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| 1 | Sonnet isolado (a542a5bd060858b40) | PASS-COM-RESSALVAS | 2 ALTA: aviso do sistema lido como pedido do dono (6 transcripts reais); artefato pedido devolvido por ser longo. 2 MÉDIA: `-RepoDir` não copiava o hook; sem proteção sem python. Contrato do Stop DESCONHECIDO. Mutações 4/4 mortas | turno começa em pedido ou aviso; isenção de artefato; cópia e log; contrato conferido nos docs (exit 2) |
| 2 | Sonnet isolado (ab12af5e903bc8916) | FAIL | 1 ALTA: mensagem de outra sessão (`cross-session-message`) ainda lida como pedido. 1 MÉDIA: artefato sem verbo de criação ("preciso de um prompt"). 1 MÉDIA: esta tabela vazia. Mutações 5/5 mortas; exit 2 propaga no Git Bash. Registrou 3 arquivos de depuração deixados pela rodada 1 em `~/.claude/projects/` | envelope de outra sessão e qualquer mensagem iniciada por tag fora; verbos "preciso", "mande", "envie", "quero", "faça", "prepare"; tabela preenchida; arquivos conferidos e apagados |
| 3 | Sonnet isolado (a1739d7a661b1f6ce) | PASS-COM-RESSALVAS | ALTA da rodada 2 fechada, provada no transcript real. 2 MÉDIA: tag sem hífen (HTML colado) lida como envelope; "quero"/"preciso" + documento isentava conversa sobre o artefato. 1 BAIXA: cobertura da tag por um caso só | só tag com hífen é envelope; "quero"/"preciso" só isentam prompt, texto, e-mail e mensagem; "faça" retirado; 7 casos novos |