# ADR-129 — Resposta executiva: medir sem bloquear, achados antes da resposta seguinte

- **Status:** Aceito
- **Data:** 2026-09-28
- **Decisores:** dono (Fabricio), 28/09/2026:
  - sobre um fechamento real de projeto: "esse status está uma bagunça! IMPOSSÍVEL COMPREENDER. [...] e os espaços? e as eventuais contextualizações de o que é cada um? é pra ser conciso, objetivo, etc, mas não omisso";
  - "passei o sac para você avaliar e ver como foi o fechamento e corrigir o método no framework";
  - "número de palavras não deve ser escrito em pedra. deve ser conciso, mas claro, objetivo, mas compreensível".

  Autoria: Opus 5.5.
- **Relação:**
  - suplanta em parte o ADR-123 (bloqueio e limite fixo);
  - regra global, seção 4;
  - responde ao débito `avaliar-resposta-executiva` com evidência.

## Contexto
O fechamento avaliado tinha quatro defeitos, e três eram de método:
1. **Conteúdo duplicado.** O hook de Stop (ADR-123) reprovou a resposta com exit 2 depois que ela já estava na tela. A reescrita saiu embaixo, e o dono leu tudo duas vezes. O próprio autor deste ADR reproduziu o defeito na mesma sessão.
2. **Tabelas coladas, sem título.** Não se via onde terminava o resultado e começava a pendência.
3. **Termos do projeto sem definição.**
4. **Seis perguntas sem recomendação.** Uma era uma data impossível, que devia ser corrigida e avisada, não perguntada.

O limite fixo de 150 palavras empurrava para cortar contexto, ou seja, para ser omisso.

## Decisão
1. **O Stop só mede e nunca bloqueia (sempre exit 0).** A mensagem final vem de `last_assistant_message`, porque, pela documentação oficial, o transcript pode ainda não tê-la no Stop. Os achados ficam no estado da sessão (`~/.claude/estado/resposta_executiva/<sessão>.json`). A mensagem que já está no transcript é reconhecida mesmo com CRLF ou espaços diferentes, para não ser contada duas vezes. O histórico vai para `historico.jsonl` por acréscimo; ao passar de 1.000 linhas, é podado às últimas 500. Sem id de sessão, nada é gravado.
2. **Retorno antes da próxima resposta.** O `UserPromptSubmit` (`resposta_executiva.py --lembrete`) injeta os achados da resposta anterior uma única vez e os consome. Sem achado, não injeta nada. O molde é estático, fica só na regra global (CLAUDE.md) e carrega uma vez por sessão; a documentação oficial dos hooks manda instrução que nunca muda para o CLAUDE.md. Não há duplicação na tela.
3. **Mede estrutura, não número de palavras:**
   - pedido ao dono no meio do processamento;
   - bloco "★ Insight";
   - tabela de decisão (cabeçalho com "Decisão") sem coluna de recomendação;
   - tabelas coladas sem título entre elas;
   - prosa longa, como **sinal** e não como limite: 300 palavras fora de tabela e código, sem pedido de detalhe ou de artefato.
4. **Molde na regra global, seção 4:**
   - seções com título curto e linha em branco: resultado, arquivos, pendências, decisões, sua ação;
   - cada item diz o que é, e termo novo ganha meia frase de definição;
   - o conteúdo aparece uma vez só;
   - decisão tem opções e recomendação;
   - o que dá para decidir sozinho é corrigido e avisado;
   - os ritos de fechamento são feitos, não só declarados.
5. **Instalação global:** `ensure-global-wiring.ps1` liga os dois eventos.

## Régua §0
Critério (a): remove o bloqueio que causava a duplicação e o limite fixo. Acrescenta um evento de hook que reaproveita o mesmo arquivo. Só há custo por mensagem quando existe achado.

## Limites
- **Sem bloqueio, a correção depende de o modelo seguir o molde.** A medida está no histórico, e a avaliação do débito `avaliar-resposta-executiva` passa a ter dados.
- **"Termo sem definição" e "ritos feitos" não são medidos automaticamente.** Ficam no molde e na revisão.
- **Histórico sem trava de arquivo.** Se duas sessões podarem ao mesmo tempo, perde-se no máximo uma linha de diagnóstico. A poda é rara (a cada 500 medições), e o estado de cada sessão, que é o que volta ao modelo, fica em arquivo próprio.

## Prova
`tools/test_resposta_executiva.py`:
- 200 palavras passam, e prosa muito longa vira sinal;
- decisão sem recomendação e tabelas coladas viram achado;
- o Stop sai com 0 mesmo com vários achados;
- o lembrete traz o achado uma vez só e fica vazio sem achado, isolado por sessão;
- a mensagem final vem do evento quando o transcript ainda não a tem;
- tabela de referência com "Opções" não é tratada como decisão;
- o histórico cresce por acréscimo, não é podado abaixo de 1.000 linhas e, acima disso, fica nas últimas 500;
- a regra global e a instalação cobrem os dois eventos.

## Estado do QA
| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| 1 | Sonnet isolado (ac264f3ba8dff2464) | PASS-COM-RESSALVAS | contrato dos hooks conferido na documentação oficial. ALTA: o Stop lia só o transcript, que pode não ter a mensagem final. MÉDIA: "Opções" isolado virava tabela de decisão. MÉDIA: molde estático injetado em toda mensagem, duplicando o CLAUDE.md. MÉDIA: histórico sem limite. BAIXA: sessão sem id compartilhava estado. 7 de 8 mutações mortas. | `last_assistant_message`; decisão só com "Decisão" no cabeçalho; lembrete só com achado; histórico de 500; sem id não grava; 7 testes novos |
| 2 | Sonnet isolado (a4c45131e46d349df) | FAIL | ALTA: a comparação com a final só aparava as pontas; com CRLF ou espaço interno, a final era contada duas vezes e gerava falso "pedido no meio". MÉDIA: o histórico era reescrito inteiro a cada resposta, com corrida entre sessões, e o limite não estava declarado. BAIXA: teste "sem sessão" fraco. 4 de 6 mutações mortas. | comparação normaliza o branco; histórico por acréscimo com poda rara e limite declarado; 5 testes novos |
| 3 | Sonnet isolado (afa98307504953277) | PASS-COM-RESSALVAS | normalização sem falso positivo perigoso; números coerentes. MÉDIA: o teste não distinguia poda rara de poda em toda chamada (mutação sobreviveu). BAIXA: texto da Prova impreciso. 3 de 4 mutações mortas. | teste "abaixo do dobro não poda"; a mutação sobrevivente agora morre (conferido pelo autor em cópia); texto da Prova corrigido |
