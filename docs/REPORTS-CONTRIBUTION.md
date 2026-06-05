# Relatórios de execução — contribuição, privacidade e LGPD (ADR-062)

> **O preço de usar e melhorar o framework é contribuir com aprendizado — de forma honesta, anônima e auditável.**
> Este documento é o aviso de transparência (LGPD) e o contrato de contribuição. Ao optar por contribuir
> (opt-in registrado, abaixo), você concorda com o que segue. Sem opt-in → nada é publicado.

## 1. O que é gerado (ADR-038/052/062)

Ao fim de cada **bloco aprovado** e ao fim de **sessão**, o framework gera um relatório de execução em até 3 formas:

| Forma | Onde | Conteúdo | Visibilidade |
|---|---|---|---|
| **OWNER (full)** | `docs/_private/_intake/execution-report.md` (deste repo; `export-clean` o remove de toda distribuição) | TUDO: erros, acertos, **detecção framework × humano**, gaps, melhorias, boas práticas, **lições por skill** (dev/discovery/architect/qa/docops/research/ux) | **privado, local** — nunca sai daqui |
| **Learnings PÚBLICO (anonimizado)** | repo público compartilhado `metacognition-exec-reports` | o OWNER passado por `anonymize.py` + **gate `sensitive-denylist`** (recusa publicar se token de cliente/PII sobrevive) — só lições **agnósticas de domínio** | **público** — só com **opt-in** |
| **Telemetria EXTERNAL (estruturada)** | repo privado do colaborador `metacognition-exec-reports-<user>` | só sinais de PROCESSO codificados (gates, pontos de falha mecanismo×junção, eventos de correção, rota, modo) — **whitelist de schema, zero texto livre** (ADR-052) | **privado por colaborador** |

## 2. Modelo de acesso (decisão do dono — ADR-062)

GitHub **não isola por-arquivo** dentro de um repo. Para "o dono vê todos, cada colaborador só o seu":

- **1 repo PRIVADO por colaborador** — `metacognition-exec-reports-<user>` (cada um vê só o seu). O **dono é adicionado como colaborador** em cada → o dono vê **todos**.
- **1 repo PÚBLICO compartilhado** — `metacognition-exec-reports` — corpus de melhoria **anonimizado** que qualquer um lê e do qual qualquer projeto pode aprender.

> Criar os repos é ação do dono (`gh`); o framework **gera o conteúdo + valida + prepara o push**, não cria conta/repo.

## 3. Privacidade / LGPD (Lei 13.709/2018)

- **Finalidade declarada:** melhorar o framework (qualidade de método, detecção de gaps, lições reutilizáveis). Nada de marketing, perfilamento ou venda.
- **Minimização:** o público carrega **só o agnóstico** (lições de método por skill). Cliente, caso, número de negócio, PII → **removidos por `anonymize.py` + barrados pelo gate `sensitive-denylist`** (fail-closed: se um token sensível sobrevive, **não publica**).
- **Base legal:** o conteúdo público é **anonimizado de fato** → fora do escopo da LGPD (Art. 12). Ainda assim, exigimos **consentimento informado (opt-in)** por transparência.
- **Limite honesto (ADR-044/020):** anonimização por regex **não é exaustiva**. O gate de denylist é o backstop; revise o `learnings-public.md` antes do push. Não prometemos detecção perfeita de PII parafraseada.
- **Titular do dado privado é o colaborador:** o OWNER full e a telemetria por-colaborador são **seus**; você controla.

## 4. Opt-in (como contribuir)

A geração do **OWNER local** é sempre obrigatória (é o seu aprendizado, fica com você). A publicação **PÚBLICA** é **opt-in explícito, 1× na adoção** — o ato de rodar o comando É o consentimento informado (ADR-063):

```
python tools/execution_report.py --init-consent
# cria ~/.claude/exec-report-consent.json = {consent:true, pseudonym:<aleatório>, adr:"062/063"}
```

- Gera um **pseudônimo ALEATÓRIO** (não derivado de e-mail/username — anti-rainbow). Seus relatórios públicos ficam em `reports/<pseudônimo>/…` no repo central — **ordenados por você sem te identificar** (atribuição real é opt-in separado).
- **Sem esse arquivo → o learnings-public NÃO é publicado** (só o OWNER local existe).
- **Opt-out a qualquer momento:** delete o arquivo, OU `FRAMEWORK_NO_TELEMETRY=1`, OU `.claude/no-telemetry.lock` (mata a telemetria EXTERNAL também — ADR-052).
- O dono (`metacognition-framework`) é colaborador dos repos privados de relatório; isso é parte do opt-in (visibilidade do mantenedor para agregar aprendizado).

## 5. Fluxo (mecanizado — não prosa)

Fim de bloco → `docops` gera o **OWNER local** + `consistency-gate` (7ª dim). A **PUBLICAÇÃO é POR SOLUÇÃO, no merge** (ADR-065, ver §8) — **não** automática por sessão. Quando você confirma a conclusão no popup: `execution_report.py --publish` (anonimiza + **gate `sensitive-denylist` fail-closed, client-side**) → abre **PR** ao repo central `metacognition-exec-reports` em `reports/<pseudônimo>/<timestamp>__<exec>.md` (**contribuidor limitado** — só PR; ADR-063).

## 6. Repo central, "contribuidor limitado" e auto-merge (ADR-063)

- **Como viro contribuidor:** não há pré-cadastro. O **ato de abrir o PR** é tornar-se contribuidor limitado (GitHub não tem write-isolado por-usuário; PR é o "limitado" nativo).
- **Receber de todos COM segurança:** o **CI do repo central RE-VALIDA** cada PR com varredura **anti-PII genérica** (`tools/templates/central-reports-ci.yml`) — defesa-em-profundidade sobre a anonimização client-side. PR com PII = check vermelho = **não entra**. A `sensitive-denylist` privada NÃO roda no central (publicá-la vazaria os nomes; roda só client-side).
- **Auto-merge:** CI verde → **auto-merge** (o gate é a validação, não revisão humana). O dono ativa em Settings (branch protection exigindo o check + "Allow auto-merge").
- **Irreversibilidade:** PR público entra no histórico git mesmo se fechado → por isso o fail-closed é **antes** do PR (client-side) e o CI central é a 2ª barreira.

## 7. Adoção — zero atrito recorrente (ADR-064)

**Cada passo manual por relatório mataria a adesão.** Por isso a contribuição é **automática** após dois passos ÚNICOS:

| Quem | Passo ÚNICO | Depois disso |
|---|---|---|
| **Contribuidor** | responde 1 pergunta no `bootstrap` (ou `python tools/execution_report.py --init-consent`) — opt-in, default **Não** | ao **concluir cada solução** (popup no merge, você confirma — §8/ADR-065) o relatório anonimizado vai sozinho; fail-soft |
| **Dono** | **1 comando guiado**: `python tools/setup_central_reports.py` (cria o repo + CI + auto-merge + grava o destino; orienta em cada passo, falha-soft com instrução) | nada — os relatórios chegam e auto-mergeiam |

- **Fail-soft:** sem `gh` autenticado → gera local em `telemetry/learnings-public/…` e **não publica** (nunca trava).
- **Privacy-by-default:** opt-in (não opt-out), pergunta clara — mais confiável e LGPD-correto.
- **Não-interativo** (CI/cron) não pergunta → sem opt-in → não publica (default seguro).

## 8. Oferta POR SOLUÇÃO, no merge (ADR-065)

Cada **solução** (ex.: um projeto de BI/dados) gera **1 relatório-resumo de aprendizado ao concluir** — não por sessão. A oferta aparece **no merge de um PR da solução**, num **popup**, e **quem decide se concluiu é você**:

| Opção no popup | O que faz |
|---|---|
| ✅ **Gerar e contribuir** | anonimiza (fail-closed) → PR ao repo central → auto-merge; marca a solução `done` |
| 📄 **Só gerar local** | gera o anonimizado local, **não** publica; marca `done` |
| ⏳ **Ainda não** | este merge **não** é a conclusão → não gera agora; **pergunta de novo no próximo merge** (`deferred`) |
| 🚫 **Não, para esta solução** | **nunca** ofereça para esta solução (`declined`) — sem nag |

- **1× por solução** (estado em `.claude/.report-offers/<solução>`). O popup mostra **o que vai / o que NÃO vai** (§1) — é a disclosure + consentimento por-solução, além do opt-in global do §4. **"Ainda não" ≠ "Não":** o primeiro adia (re-oferta), o segundo silencia de vez.
