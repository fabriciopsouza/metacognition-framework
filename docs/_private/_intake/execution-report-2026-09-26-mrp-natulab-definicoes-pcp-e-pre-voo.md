# Execution report — MRP Natulab: regras do PCP, programa de faixa de lote e pré-voo

**Sessão de 25 e 26/09/2026** (continuação da de 24/09) · projeto de domínio em
`C:\Users\fabriciosouza\Downloads\2026-09-11-MRP` (sem git; framework aplicado por sessão, não instalado) ·
nenhuma escrita no núcleo do framework

- **Tokens:** NÃO MEDIDO por sessão (o `--from-transcripts` soma o diretório inteiro).
- **Tempo (wall-clock):** NÃO MEDIDO
- **Turnos:** cerca de 40 mensagens do dono (contagem aproximada na conversa)
- **Arquivos tocados:** documento de definições do PCP (gerador + xlsx), checklist v3 (gerador + xlsx), 9 runbooks
  de cadastro, pacote do programa 1 (pesquisa, especificação, plano de validação, 4 runbooks, comece-aqui, prompt,
  respostas do pré-voo, consultas), 4 pesquisas, plano, fila, glossário, premissas, mapa de fontes, 6 memórias.
- **Testes:** travas dos geradores provadas por sabotagem (recusa sobrescrever respostas; aba "o que mudou" infiel
  aborta).
- **Rodadas de retrabalho:** cerca de 20 rodadas de QA isolado; mais da metade reprovou na primeira.

## O que foi entregue
- **Documento de regras do PCP** (24 regras, com "é possível? como? em massa?" e links) enviado ao PCP em 25/09.
- **Checklist v3** (v2 das áreas intacta + parecer, valor, onde, quem, ação, situação) — aguarda o PCP.
- **Runbooks de cadastro** RB-10 a RB-18.
- **Programa 1 (faixa de lote nas versões de produção)**: pesquisa, especificação, plano IQ/OQ/PQ, runbooks de
  instalação/transporte/execução/validação, "comece aqui" e prompt para IDE. A IDE (Kiro) **parou corretamente**
  por falta do pré-voo.
- **Pré-voo**: respostas de dicionário já obtidas pelo Datasphere (MKAL-MKSP é o bloqueio, `SPERR` não existe;
  PLKO-CHRULE regra de modificação; faixas em PLKO/MAST) e 8 consultas DBACOCKPIT prontas.

## Placar gate × achado
| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| Afirmei "ME11 e ME21N concluídos nos 7 cenários" contando a palavra, não o status (real: 6/7 e 3/7) | QA isolado do handoff | Autor: contar o status |
| Afirmei que o MRP de hoje "não pede nada" no exemplo de validade (pede 40 kg) | QA isolado | Autor: simular o saldo em ordem de data |
| Aba "o que mudou" omitia a mudança na LEIA, e a mensagem dizia "exatamente" | QA isolado | Agora: conferidor no gerador compara com a versão enviada e aborta |
| Gerador sobrescreveu o xlsx num `import` (sem guarda `__main__`) | QA isolado, por acidente | Agora: guarda `__main__` + recusa sobrescrever respostas (provado) |
| QA afirmou que MKAL não tem BSTMI/BSTMA e propôs LOSVN/LOSBS | Autor, medindo no DD03L | Medição antes de aplicar achado de QA |
| Consultas com `TRIM(x)=''` quebram com NULL; sem exclusão de obsoletos | Inventário das consultas da casa (Mapeamento v14) | Ler o que já existe antes de escrever |
| Placeholder `'???'` rodou em produção e voltou 0 linhas | Dono | Consulta sai pronta |
| Arquivo em revisão na mesma pasta dos prontos; dono não sabia se tinha enviado | Dono | Agora: pasta `_EM-REVISAO` |
| Mensagem ao Teams foi para fora sem QA isolado | Autor, depois | Texto para fora também passa QA |
| Caminho com `\_` sumia ao copiar do chat renderizado | IDE do dono | Prompt entregue em bloco de código e em arquivo |

## Detecção: framework × humano
O dono pegou 5 falhas de processo (placeholder, "não parta do zero", pasta de revisão, "arquivo único", prompt por
padrão). O QA isolado pegou a maioria das falhas de conteúdo. A medição (DD03L via Datasphere) derrubou 1 achado
errado do QA.

## Gaps
- Pasta do projeto sem git: sem histórico nem gate (BLOCO 0 nunca aprovado).
- Regras do framework que o dono pediu como padrão ainda só na memória do agente (T31).
- `MEMORY.md` acima de 20 KB, perto do limite de leitura.

## Melhorias (propostas ao framework, régua §0)
- **Entrega para desenvolvimento sai com `00-COMECE-AQUI` + prompt pronto, sem perguntar** (pedido explícito do
  dono como padrão).
- **Artefato em revisão fica fora da pasta de envio** (`_EM-REVISAO`).
- **Gerador de documento para fora: guarda `__main__`, recusa sobrescrever respostas, e conferidor de
  "o que mudou" contra a versão enviada** — os três provados por sabotagem nesta sessão.
Todas fundem ou substituem comportamento em prosa por mecanismo (régua §0 b/c).

## Boas práticas
- Conferir campo SAP no dicionário (DD03L) pelo Datasphere antes de entregar SQL; usar a descrição do campo
  (FIELDDESCRIPTION) para achar o campo certo (achou CHRULE, LOSVN/LOSBS, MKSP).
- Inventariar consultas e lições da casa antes de escrever consulta nova.
- Fila de pendências com IDs fixos; toda resposta termina com a fila.

## Lições por skill
- dev: SQL para humano rodar é código de produção: sem placeholder, com COALESCE, mandante e exclusões da casa.
- qa-critic: achado que afirma fato verificável se mede antes de aplicar; o revisor erra com a mesma confiança.
- docops: documento para fora tem um arquivo e um texto; versão anterior não aparece para quem recebe.
- discovery: quem define a regra é o dono do processo; guia técnico é referência, não regra.
