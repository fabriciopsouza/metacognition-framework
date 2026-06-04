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

A geração do **OWNER local** é sempre obrigatória (é o seu aprendizado, fica com você). A publicação **PÚBLICA** é **opt-in explícito, 1× na adoção**:

```
# registrar consentimento (cria ~/.claude/exec-report-consent.json)
# conteúdo: {"consent": true, "date": "<AAAA-MM-DD>", "scope": "learnings-public-anonimizado", "adr": "062"}
```

- **Sem esse arquivo → o learnings-public NÃO é publicado** (só o OWNER local existe).
- **Opt-out a qualquer momento:** delete o arquivo, OU `FRAMEWORK_NO_TELEMETRY=1`, OU `.claude/no-telemetry.lock` (mata a telemetria EXTERNAL também — ADR-052).
- O dono (`metacognition-framework`) é colaborador dos repos privados de relatório; isso é parte do opt-in (visibilidade do mantenedor para agregar aprendizado).

## 5. Fluxo (mecanizado — não prosa)

Fim de bloco/sessão → `docops` gera o OWNER enriquecido → `consistency-gate` declara se faltou (7ª dimensão, fail-soft) → **se opt-in:** `execution_report.py --learnings-public` (anonimiza + gate denylist) → revisão → push ao repo público + ao privado do colaborador.
