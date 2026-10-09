---
name: project-docs
version: 2.0.0
source: "Padrão extraído de um conjunto documental real (projeto de domínio, 12-13/08/2026) submetido a 5 rodadas de revisão adversarial, REPROVADO 3 vezes antes de aprovar; entrada enxuta desde 28/09/2026 (B3c)"
last_review: 2026-09-28
description: Núcleo SSoT do CONJUNTO DOCUMENTAL DE PROJETO — como documentar um projeto para que ele sobreviva à troca de pessoa, de sessão e de IA. Carregar quando a tarefa for criar, reorganizar ou auditar a documentação de um projeto (não de um bloco). Define o teste de pronto, as 7 propriedades, o kit essencial (gerado do arquivo único), os gates e a revisão. NÃO carregar para fechar bloco (isso é docops) nem para validar dado contra referência (isso é validation-reporting).
---

# Documentação de projeto que sobrevive à troca de dono

Entrada enxuta. O detalhe de cada ponto mora num arquivo desta pasta, lido só quando o assunto aparece.

## §0 — Onde se encaixa
- **Fonte única:** o arquivo único `docs/specs/<projeto>/spec.md` (ADR-117). TAP, planilhas, documentos regulados e
  desenho do processo **saem dele**, gerados; nunca são escritos em paralelo.
- `confidence-classification` define as marcas; `traceability`, o rastro; `validation-reporting`, a validação de
  dado; `docops` fecha o bloco e chama esta skill quando o bloco mexe na documentação do projeto.
- Método do projeto, etapa a etapa: `guia/METODO-DE-PROJETO.md`. Origem e porte: `origem-e-porte.md`.

## §1 — Teste de pronto
> Uma pessoa nova — ou outra sessão de IA — retoma o projeto **sem perguntar nada a ninguém**.

Verifique: entregue a documentação a quem não participou e peça o próximo passo. Se perguntar, o documento falhou.

## §2 — As 7 propriedades (detalhe e casos reais: `propriedades.md`)
| # | Propriedade | Regra |
|---|---|---|
| 2.1 | Dono único por fato | cada afirmação tem **um** arquivo dono; os demais apontam, nunca copiam |
| 2.2 | Marca de confiança | CONFIRMADO (com prova) · INFERIDO (de onde) · DESCONHECIDO · REFUTADO; crença refutada **nunca** é apagada |
| 2.3 | Prova reproduzível | pergunta · **consulta exata** · resultado · conclusão com marca |
| 2.4 | Número com data | número sem data não é usado como valor atual |
| 2.5 | Ponto de retomada | onde estamos · próximo passo · travado **por quem** · decisão aberta **e quem decide** |
| 2.6 | Vocabulário | termo técnico explicado na 1ª vez; em domínio sensível, sinalizar, não julgar |
| 2.7 | Fronteira declarada | parte reutilizável × parte de domínio, verificada por comando |

## §3 — Kit essencial (vale para todo projeto)
| Peça | Responde | Onde mora / como sai |
|---|---|---|
| TAP | por quê, escopo, quem | portal de projetos; sem portal, a Parte D (Missão) do `spec.md` |
| Arquivo único | requisitos, aceite, riscos, testes, processo, definições, verificação | `docs/specs/<projeto>/spec.md` |
| HANDOFF | onde paramos, próximo passo | `python tools/handoff.py` |
| Glossário | nome oficial de cada coisa | `.agent/rules/00-glossario.md` |
| Cronograma | datas e dependências | gerado das Tarefas do `spec.md`: na linha da tarefa, `prazo: dd/mm/aaaa` e `depende: T1`. `python tools/plano.py cronograma <spec.md> [--csv <arquivo>]` (atraso na data de hoje); o painel de fases sai de `python tools/plano.py painel <spec.md> --escrever`. `plano.py verificar` reprova painel editado à mão, prazo ilegível e dependência inexistente ou fora de ordem (ADR-127) |
| Confirmação e verificação com a área | a área confirma as regras e confere o sistema | `python tools/planilhas_projeto.py gerar <spec.md> --out-dir <pasta>` (Partes I e J) |

**Condicionais:**
- Alguém vai operar com as mãos (tela, terminal, console, credencial) → **RUNBOOK**: `runbook.md`.
- Equipe com trabalho em paralelo → **quadro de estado** gerado: `quadro-de-estado.md`.
- Projeto muda ou cria processo → desenho do processo: `python tools/desenho_processo.py <spec.md> --out-dir <pasta>`.
- Mudança e versão → `python tools/mudancas_spec.py <spec.md> --out-dir <pasta>`.
- **Impacto regulado** → as peças vêm do **perfil regulado** declarado no projeto (um por tipo de regulação):
  `python tools/regulado.py kit <spec.md>` lista; `python tools/regulado.py documento <tipo> <spec.md> --out-dir
  <pasta>` gera. Procedimento interno da empresa entra pela camada privada: `**Empresa:** <e>` na Parte A soma
  `perfis/compliance-profile-<perfil>.json` da biblioteca da empresa (ADR-128).

Adote o menor conjunto que passa no §1: peça a mais é o mesmo defeito que esta skill combate. A tabela antiga por
porte está em `conjunto-graduado-anterior.md`.

## §4 — Gates (nenhum é opinião; detalhe em `gates-falhas-e-revisao.md`)
1. Link quebrado: 0.
2. Fronteira: a parte reutilizável não cita o domínio. 0.
3. Anti-duplicação: número-chave por extenso só no arquivo dono, conferido **contra a fonte viva**.
4. Verdade contra o mundo: consulta das invariantes contra a fonte viva. Tudo PASS.

Cada gate lista as próprias exceções e por quê.

## §5 — Modos de falha já observados
Duplicação que o mapa nega · glossário perdido na consolidação · nome sem procedência sob título que promete
verificação · junção que não dá erro e corrompe · corrigir só onde o revisor apontou · polimento que escapa da
revisão. Casos e antídotos: `gates-falhas-e-revisao.md`.

## §6 — Revisão
Revisor ≠ autor (modelo ou pessoa diferente), instruído a achar defeito, com veredito explícito. Três reprovações
seguidas = o problema é o desenho: pare e reabra a decisão.

## §7 — Prompt de partida
Para começar ou auditar o conjunto de um projeto: `prompt-de-partida.md`.

## §8 — Débito declarado
Esta skill é prosa, sem canário próprio (registro `project-docs-standard`). Débitos (verificador do RUNBOOK,
gerador de quadro, gates genéricos) e quitação: `debito.md`.
