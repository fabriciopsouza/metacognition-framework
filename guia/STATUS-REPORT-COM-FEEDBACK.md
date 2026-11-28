# POP: status report com construção do feedback

Versão 1.0 · 28/11/2026 · Origem: diretriz do mantenedor, válida para todas as sessões, repositórios e IAs: a construção do feedback passa a ser método, além do acompanhamento de ações, e é espelhada nos frameworks e repositórios.

## 1. Objetivo

Transformar o acompanhamento de ações em feedback acionável. Cada bloqueio vira um pedido com evidência, impacto, destinatário, prazo e consequência. O status report só fecha quando cada pedido tem resposta ou foi escalado.

## 2. Definições

| Termo | Definição |
|---|---|
| Acompanhamento de ações | Lista de ações com dono, prazo e situação. Mostra **o que** está parado. |
| Construção do feedback | Texto escrito para um destinatário que diz **por que** importa e **o que se pede**: fato com evidência, impacto no objetivo, pedido específico, prazo e consequência de não atender. |
| Bloqueio | Ação parada por dependência externa: acesso, dado, decisão, recurso. |
| Escada de escalonamento | Ordem dos destinatários quando o anterior não responde no prazo: equipe ou sessão dona → suporte de TI (chamado) → liderança técnica → gestão → dono. Cada projeto registra os nomes da sua escada. |
| Ciclo | Intervalo entre status reports. Padrão: semanal; bloqueio crítico: a cada 2 dias úteis. |

## 3. Fluxo

1. **Coletar fatos.** Rodar sincronizações e canários do repositório. Ler os chamados e os pedidos dos contratos. Usar o assistente corporativo (ex.: Copilot do Microsoft 365) para buscar conversas e e-mails, com um prompt que cite termos, sistemas e IDs. Fato sem evidência entra como INFERIDO.
2. **Atualizar o quadro de ações:** ID · ação · dono · prazo · situação (✅/⏳/☐/⛔) · evidência.
3. **Classificar os bloqueios** pelo impacto no objetivo: crítico (impede a entrega ao público), alto (degrada a entrega), médio (atrasa a expansão). Separar a contagem por tipo (acesso, dado ausente, recarga, decisão, duplicado) para não superestimar nem subestimar o problema.
4. **Construir o feedback** de cada bloqueio crítico ou alto com o molde da seção 4, um texto por destinatário.
5. **Escolher o degrau** pela duração do bloqueio e pela resposta anterior. Pedido sem resposta no prazo sobe um degrau no ciclo seguinte.
6. **Enviar e registrar** data, canal e destinatário. O envio para fora (e-mail, chat corporativo, chamado) é do dono ou exige ordem dele.
7. **Fechar o ciclo.** Registrar a resposta, atualizar o cronograma e reabrir o que voltou. Lição reutilizável vai para a biblioteca de conhecimento da empresa do projeto.

## 4. Molde do feedback

| Campo | Conteúdo |
|---|---|
| Destinatário e degrau | Quem recebe e por quê |
| Fato | O que está parado, desde quando, com ID do chamado ou evidência; inferência marcada como tal |
| Impacto | O que deixa de ser entregue, para quem, e o número afetado |
| Pedido | Uma ação específica por item, com o objeto exato (tabela, papel, conta) |
| Prazo | Data pedida, motivo e data de envio coerente com o prazo |
| Consequência | O que acontece sem atendimento (contorno, atraso, risco) |
| Próximo checkpoint | Data da próxima verificação |

## 5. Checklist do status report

- [ ] Sincronizações e canários do ciclo rodados e anexados
- [ ] Quadro de ações atualizado com evidência
- [ ] Contagem de bloqueios separada por tipo
- [ ] Todo bloqueio crítico ou alto com feedback construído
- [ ] Pedido sem resposta escalado um degrau
- [ ] Cronograma atualizado com o efeito dos bloqueios, com checkpoint no ciclo de bloqueio crítico
- [ ] Envio registrado (data, canal, destinatário) ou pendente de ordem do dono
- [ ] Biblioteca de conhecimento: registrado ou "nada a registrar"

## 6. Rotina semanal (toda segunda-feira)

Padrão para todos os projetos (regra global 12). O report tem duas partes: a página publicada, sempre no mesmo link, e o PDF,
com o link da página no rodapé.

| # | Quem | Ação |
|---|---|---|
| 1 | Tarefa agendada (segunda, 08:00, usuário conectado) | Sincroniza, se o projeto tiver sincronização; abre a página; grava um arquivo de lembrete; mostra o lembrete |
| 2 | Dono | Abre a sessão no repositório e diz "status report semanal" |
| 3 | Agente | Cria a pasta do ciclo e atualiza o quadro de ações, os bloqueios, o feedback e o cronograma |
| 4 | Agente | Republica a página no mesmo link |
| 5 | Agente | Gera e abre o PDF, com o link da página no rodapé |
| 6 | Agente | Revisão adversarial, commit e PR |
| 7 | Dono | Confere, envia e registra o envio |

Cuidados: um lembrete deixado aberto bloqueia a tarefa e pode pular a semana seguinte; projeto sem sincronização desliga essa
etapa. Implementação de referência (scripts de registro da tarefa, lembrete e PDF) fica no repositório do projeto que a criou,
não aqui.

## 7. Relação com o resto do framework

- O status report derivado (`docs/projeto/STATUS-REPORT.md`, gerado por `tools/projeto_docs.py`) mostra o estado. Este POP acrescenta o feedback que destrava o estado.
- Pesquisa de domínio pode ir primeiro à IA consultora com os recursos da empresa (RAG corporativo por API), que economiza a varredura de arquivos. A resposta é conferida na fonte antes de virar CONFIRMADO e não substitui a revisão adversarial.
- Isolamento entre empresas: o quadro, os nomes da escada e os IDs de chamado ficam no repositório do projeto, nunca aqui.
