# Contexto do projeto — o que só uma pessoa pode declarar

> Os outros três arquivos desta pasta (`backlog.csv`, `cronograma.csv`, `STATUS-REPORT.md`) são
> **gerados** por `python tools/projeto_docs.py` a partir do estado real do repositório. Este aqui
> é o oposto: contém o que nenhum dado revela — propósito, quem é afetado, o que está em jogo.
> **É o único desta pasta que se escreve à mão**, e por isso é curto: coisa longa escrita à mão
> não é relida.

## Objetivo

Fazer com que um agente de IA execute trabalho técnico com **garantia verificável**, não com boa
vontade. O critério é binário: toda regra do framework ou tem mecanismo que a força, ou está
declarada como dívida. Não existe terceira categoria.

## Visão

Um framework onde **"verde" significa alguma coisa**. Hoje, num repositório qualquer, um teste
verde pode significar "está correto", "não testa nada" ou "testa o que já era verdade antes". A
diferença é invisível. Aqui ela é medida: uma capacidade só conta como protegida depois que alguém
sabotou o mecanismo de propósito e viu o teste apitar.

O mesmo princípio vale para o resto — decisão que não virou ADR não vale, processo que não deixou
rastro no ledger não aconteceu, e documento que promete mais do que o mecanismo entrega é tratado
como defeito, não como estilo.

## Quem é afetado

| quem | o que ganha | o que arrisca |
|---|---|---|
| **Dono** (Fabricio) | trabalho técnico que não precisa de revisão linha a linha para ser confiável | gate mal calibrado que atrapalha em vez de proteger; tempo gasto em mecanismo que não paga |
| **Agente de IA** (esta sessão e as próximas) | contexto que sobrevive à troca de sessão; regra que não depende de lembrar | falso senso de garantia — mecanismo que parece proteger e não protege |
| **IA-par** (repo Gemini, via hub cross-IA) | lições transferíveis sobre defeitos em mecanismos de garantia | receber prática que não se aplica à arquitetura dela |
| **Quem clonar o framework** | instalação que se verifica e diz o que falta | achar que o framework garante mais do que garante |

## O que está em jogo

**O risco central não é o framework falhar — é ele parecer funcionar.** Um gate que aprova tudo é
pior que gate nenhum: produz confiança sem base. Foi o que a sessão de 15–16/08 mediu: de nove
rodadas de crítica adversarial, cinco reprovaram, e em quatro delas o defeito estava **dentro do
mecanismo criado para impedir aquele mesmo tipo de defeito**.

Daí a regra que organiza tudo: **nada entra sem prova de que sabe falhar.**

## Limites declarados

Três, ditos aqui para não precisarem ser descobertos:

1. **O agente escreve o registro que os verificadores leem.** Isso é auditabilidade — um terceiro
   re-roda e chega ao mesmo número —, não constrangimento externo. Rigor de verdade exigiria um
   árbitro neutro escrevendo o log.
2. **Qualidade de raciocínio não se mecaniza.** Ordem e presença de etapa, sim. Se o crítico foi
   de fato cético, não. Isso continua sob postura adversarial, não sob gate.
3. **O padrão documental deste projeto ainda não foi validado em um segundo projeto.** Está marcado
   como pendente no registro de capacidades e a marca só sai depois do segundo uso real.

## Como manter isto vivo

Este arquivo muda quando o **propósito** muda — o que deve ser raro. Se o que mudou foi o trabalho,
não mexa aqui: rode `python tools/projeto_docs.py` e os outros três se atualizam sozinhos. O gate
de fechamento avisa quando estão para trás.
