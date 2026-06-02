# ADR 053 — Teste binário de handoff alargado: entregabilidade ao HUMANO (não só à próxima sessão)

- Status: **Aceito** · Data: 2026-06-02 · Decisores: dono + squad (architect)
- Onda: retroalimentação do framework (v1.39.0) · Tipo: **EMENDA** — alarga o Princípio 14 (ADR-012). Net-gain régua §0: cláusula (a) **funde** com princípio existente (não cria princípio novo) + cláusula (c) **destrava** uma verificação hoje inexistente (nada no framework checa entregabilidade ao humano destinatário).
- Política: **EMENDA** o ADR-012 (§Consequências/escopo do teste binário). Relaciona: ADR-012 (handoff cross-sessão), incidente 2026-05-31 (de-hardcode de ambiente), ADR-005 (execution-modes).

## Contexto

O Princípio 14 (ADR-012) tem um teste binário de handoff: *"a outra sessão consegue começar sem perguntar nada de volta?"* — mas só num eixo: o próximo **agente/sessão**. Um caso de campo (sessão paralela, 2026-06-02) expôs o eixo que faltava, destilado em princípio agnóstico (os termos de domínio foram descartados):

1. **Hardcode de ambiente é defeito, não escolha.** Acoplar a solução a um path/máquina/dono do autor a faz quebrar no instante em que muda de mãos ou de pasta.
2. **Dependência de tooling é oculta.** Uma entrega que pressupõe o destinatário abrir um terminal, instalar algo ou editar um caminho não foi *entregue* — é uma **barreira**. Para um destinatário não-técnico, "o script funciona aqui" não é solução.
3. **O teste de portabilidade é uma pergunta só:** *"se eu mandar isto a um colega, ele usa sem editar nada nem aprender uma ferramenta nova?"* Se a resposta não é "sim", não está pronto.

Esse é o **mesmo teste binário** do Princípio 14, aplicado ao **humano destinatário** em vez da próxima sessão.

## Decisão (1 frase ativa)

Alargar o teste binário do Princípio 14 para **dois destinatários**: a próxima *sessão/agente* (começa sem perguntar de volta — já existia) **e** o *humano que recebe o artefato* (usa sem depender de **capacidade oculta**: terminal, instalação, edição de path/ambiente). **Hardcode de ambiente e dependência de tooling oculto REPROVAM o handoff.** Proporcional ao destinatário declarado: artefato para usuário não-técnico exige entrega sem terminal; artefato para outro agente/dev mantém o teste original.

## Alternativas consideradas (≥3)

1. **Não fazer.** Entregas seguem quebrando ao mudar de mãos; o framework não tem gate de entregabilidade. **Rejeitada — é o gap provado.**
2. **Criar um princípio novo (15) "entregabilidade".** Duplica o teste binário que já existe no 14. Viola régua §0 (adição pura). **Rejeitada.**
3. **Alargar o Princípio 14 com uma cláusula de destinatário-humano (ESCOLHIDA).** Funde no princípio existente; reusa o teste binário; adiciona só o eixo que faltava. Net-gain.

## Consequências

**Positivas:** o teste binário passa a pegar hardcode de ambiente e dependência de terminal/instalação como **reprovação de handoff** — não só falta de contexto para o próximo agente. Discovery/architect passam a perguntar "quem recebe e com que capacidade?" quando o entregável é para humano. **Limite/proporcionalidade:** não exige GUI para tudo — é proporcional ao **destinatário declarado** (ADR-005/discovery 6(e)/6(f)); artefato dev-para-dev mantém o teste original. Sem declaração → defaults agnósticos.

## Implementação (ponteiro)

- Edição cirúrgica do **Princípio 14** no `AGENT-FRAMEWORK.md` §6 (cláusula de destinatário-humano). Ponteiro no `/handoff` workflow se necessário. Sem código novo (é princípio + gate de prosa no discovery/handoff). DONE quando: Princípio 14 cita os dois destinatários e o teste de capacidade-oculta.
