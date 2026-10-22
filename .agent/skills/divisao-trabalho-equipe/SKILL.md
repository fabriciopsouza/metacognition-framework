---
name: divisao-trabalho-equipe
description: "Ativar quando o dono pedir para dividir o trabalho de um projeto entre pessoas (aprendizes, estagiários, equipe), em paralelo ou em sequência, com agenda por pessoa, checklist de execução, runbook em planilha, passagem de bastão ou capacidade (horas por dia, dias por semana, turnos). Produz: tarefas de até um turno com executante, dependências, passos e aceite; datas calculadas pela capacidade; agenda por pessoa; checklist de execução por gate (Painel 'onde parou', Quem, Turno, Espere antes); e alimenta o painel técnico (painel-status) e o dash das áreas (dash-projeto-online). NÃO ativar para status do projeto sem redistribuir trabalho (isso é painel-status) nem para estimar custo ou preço (isso é service-valuation)."
version: 1.0.0
source: "pedido do dono, 22/10/2026: 'preciso utilizar a mão de obra dos aprendizes, são 3, 2 pela manhã e 1 pela tarde, e cada um tem 4 h/dia, 4 dias/semana. A ideia é poder dividir trabalho paralelo, ou sequencial entre pessoas diferentes, de forma clara, objetiva, direta, e explicativa quando necessário. Pedi a criação desta habilidade ou skill na documentação de projeto ágil ou em paralelo a esta'"
last_review: 2026-10-22
role_order: null
consumes:
  - "plano do projeto com tarefas, dependências e aceite (ex.: estado.json)"
  - "equipe: papel, turno, horas por dia, dias da semana; feriados"
produces:
  - "tarefas por executante com datas calculadas pela capacidade"
  - "agenda por pessoa (planilha e Markdown)"
  - "checklist de execução por gate, nunca sobrescrito em uso"
pass_criteria: "PASS sse: (1) toda tarefa de pessoa da equipe tem executante, horas positivas, passos, aceite e dependências, e cabe num turno ou declara a continuação; (2) as datas vêm de agenda_equipe.planejar com a capacidade declarada (horas por dia, dias da semana, feriados, folga) e estão marcadas como previsão, nunca prazo combinado; (3) nenhuma conferência é feita por quem criou o que confere; (4) dado real e permissão ampla ficam só com a coordenação, e a permissão de construção é retirada antes de dado real; (5) o checklist de execução por gate tem Painel por pessoa (feitos, total, %, erros, próximo passo, passo com erro), Roteiro com Quem, Turno e Espere antes, Leia antes e Histórico, e nunca sobrescreve versão em uso; (6) as fórmulas do Painel foram abertas no Excel real e não mostram #NOME?."
confidence_required: true
enforcement:
  ide: "self-declared: prosa mais o guarda de entrada em agenda_equipe.py (_conferir); débito de mecanização declarado: um verificador do plano pode conferir os itens 1 a 3"
  chat: "self-declared: o agente segue o fluxo e as regras de quebra do trabalho"
shared_refs:
  - _shared/output-format
  - _shared/confidence-classification
---

# divisao-trabalho-equipe — dividir o trabalho entre pessoas, pela capacidade de cada uma

## Definições

- **Executante:** papel que faz a tarefa (ex.: "Aprendiz manhã 1"). No dash das áreas aparece só o papel ou a área.
- **Capacidade:** horas por dia × dias por semana de cada executante, menos feriados.
- **Turno:** bloco de trabalho de uma pessoa num dia (ex.: 4 h); a menor unidade de tarefa.
- **Espere antes:** tarefas ou passos que precisam estar feitos antes de começar — a passagem de bastão.
- **Gate:** ponto de controle com revisão da coordenação, revisão adversarial, PR e merge.
- **Folga:** percentual somado às horas estimadas no cálculo das datas (padrão 20% para quem está aprendendo).

## Regras para quebrar o trabalho

1. **Tarefa cabe num turno** sempre que possível; acima de 16 h, quebrar em tarefas.
2. **Cada tarefa tem:** verbo + objeto, passos (uma tela por passo), onde está o detalhe, aceite verdadeiro ou falso,
   de quem espera e para quem entrega.
3. **Paralelo por frente:** tarefas sem dependência entre si vão para pessoas diferentes no mesmo dia.
4. **Sequencial com passagem de bastão:** o primeiro passo da tarefa seguinte cita o número do último passo da anterior.
5. **Quem cria não confere:** toda criação tem conferência feita por outra pessoa.
6. **Decisão, acesso, dado real e aprovação ficam com a coordenação** (dono). Aprendiz trabalha com dado fictício e com a
   menor permissão que a tarefa exige, retirada antes de qualquer dado real.
7. **Porta fechada não é erro de quem executa:** falta de acesso vira observação e aviso; a pessoa segue para o próximo
   passo que não depende daquele.
8. **Nunca apagar linha:** passo que não serviu vira Substituído, com linha nova e registro no Histórico.
9. **Datas são previsão,** marcadas como calculadas pela capacidade; prazo combinado só com o dono.

## Fluxo

1. **Levantar a equipe:** papel, turno, horas por dia, dias da semana, início, feriados. O que não foi dito pelo dono vira
   suposição declarada (ex.: "segunda a quinta, a confirmar").
2. **Quebrar as tarefas** pelas regras acima, gravando no plano do projeto os campos: `id`, `fase`, `o_que`, `horas`,
   `executante` (ou "Aprendiz (qualquer)"), `depende_de`, `como` (passos), `aceite`, `onde`, `entrega_para`. Tarefa da
   coordenação que só depende de outras: `apos_dependencias: true`. Formato da equipe: `equipe` = lista de
   `{papel, turno, horas_dia, dias_semana}` (0 = segunda … 6 = domingo), `equipe_inicio` e `equipe_feriados` em
   AAAA-MM-DD, `equipe_folga` (0.2 = 20%). O coringa "Aprendiz (qualquer)" só escolhe entre papéis que começam
   por "Aprendiz".
3. **Calcular as datas** com `agenda_equipe.py` desta skill (`planejar(estado, inicio)`): começa quando as dependências
   terminaram e o executante está livre; ocupa as horas do turno dele, nos dias de trabalho dele; aplica `equipe_folga`.
4. **Validar antes de gerar:** `planejar` recusa equipe sem dias, horas não positivas e coringa sem aprendiz; o projeto
   ainda valida executante existente (equipe ou lista de externos) e dependência circular (referência: `checklist_excel.py`, `validar`).
5. **Gerar as saídas** (molde completo no projeto de referência abaixo):
   - planilha geral com abas Agenda (dia a dia por pessoa, só consulta) e Equipe (carga de cada um);
   - checklist de execução **por gate**: Painel (por pessoa: feitos, total, %, erros, próximo passo, passo com erro),
     Leia antes, Roteiro (Nº, Quem, Turno, Data prevista, Tarefa, Faça, Onde, Espere antes, Status, Data/hora,
     Observação, Resposta da coordenação), Histórico. Nunca sobrescrever versão em uso; versão nova herda as marcações;
   - painel técnico (skill painel-status, com cronograma) e dash das áreas (skill dash-projeto-online) do mesmo plano.
6. **Testar o Painel no Excel real** antes de entregar: no arquivo, fórmulas novas do Excel se gravam com o nome em inglês e o
   prefixo `_xlfn.` (ex.: `_xlfn.AGGREGATE`, `_xlfn.MINIFS`), senão aparecem como `#NOME?` (referência:
   `execucao_gate.py`, Painel).
7. **Revisão adversarial** (qa-critic) do plano e das planilhas; corrigir; PR e merge por gate.
8. **Uso diário:** a planilha de execução fica numa pasta compartilhada para coedição; a coordenação responde a última
   coluna, atualiza o plano e regera; ausência de alguém = recalcular (as datas andam).

## Arquivos e referência

- `agenda_equipe.py` — planejador genérico (sem dependência externa).
- Projeto de referência (implementação completa, 22/10/2026): `C:\Users\fabriciosouza\ssma-plataforma\tools\`
  (`checklist_excel.py`, `execucao_gate.py`, `painel_status.py`, `dash_area.py`), método em
  `C:\Users\fabriciosouza\ssma-plataforma\docs\agil\METODO-DIVISAO-TRABALHO.md` e rotina em
  `C:\Users\fabriciosouza\ssma-plataforma\runbooks\RB-04-EQUIPE-APRENDIZES.md`.
- Moldes de origem: checklist SIPAT v5 (Quem, Turno, Espere antes, Painel "onde parou"), checklist do Master Plan
  (nunca sobrescrever em uso), método de runbook do CAPA (M-1 a M-10), cronograma da Migração SAC (Gantt e 5W2H).
