# ADR 058 — Pacote web em DOIS repos: público (`-web`) × premium privado (`-web-premium`)

- Status: **Aceito** · Data: 2026-06-02 · Decisores: dono + squad (architect)
- Onda: encarnação web (v1.41.0) · Tipo: **EMENDA** do ADR-054 (§repo dedicado). Atende: decisão do dono "tier premium web = privado".
- Política: **EMENDA** ADR-054 (de um repo `-web` com dois tiers → dois repos). Relaciona: ADR-049 (split `-public` × `-premium` pago), ADR-057 (profile web), ADR-054 (keystone).

## Contexto

O ADR-054 colocou os dois tiers web (público + premium) num único repo público `-web`. O dono decidiu que o **tier premium é pago → deve ser privado**, espelhando o split não-web já existente (`-public` público × `-premium` pago, ADR-049). Premium num repo público é vazamento de monetização.

## Decisão (1 frase ativa)

Separar o pacote web em **dois repos**: `metacognition-framework-web` (**PÚBLICO** — só o tier público `prompt-web-publico.md`) e `metacognition-framework-web-premium` (**PRIVADO/pago** — orquestrador + 15 skills). O `web_export` gera `publico/` e `premium/` como **repo-roots independentes** (README próprio em cada); o `publish-clean` publica cada subdir no seu repo, com **deploy keys separadas** (`PUBLISH_DEPLOY_KEY_WEB` público, `PUBLISH_DEPLOY_KEY_WEB_PREMIUM` privado).

## Alternativas consideradas

1. **Manter tudo no `-web` público.** Vaza a camada paga. **Rejeitada (decisão do dono).**
2. **Premium num branch privado do mesmo repo.** GitHub não faz branch privado num repo público; inviável. **Rejeitada.**
3. **Dois repos, espelhando ADR-049 (ESCOLHIDA).** Consistente com o split não-web; deploy key por repo; sentido único main→cada um. Custo: +1 repo + +1 deploy key (padrão conhecido, barato).

## Consequências

**Positivas:** monetização preservada (premium privado); consistência com `-public`/`-premium`; o tier público segue grátis e autocontido. **Negativas/limite:** +1 repo e +1 secret para manter; o `-web` público teve o `premium/` removido (republicado só com `publico/`). **Sentido único:** ambos gerados do main; nunca editar à mão. O conteúdo premium **não é segredo de dados** (são skills geradas de descrições agnósticas) — a privacidade é **fronteira de produto/pago**, não contenção de PII.

## Implementação (ponteiro)

- `tools/web_export.py`: README por tier (cada dir = repo-root). `publish-clean.yml`: estágio WEB vira **dois pushes** (publico→`-web`; premium→`-web-premium`), gated em deploy keys separadas. Repo privado criado; deploy key + secret configurados. DONE quando: workflow publica público no `-web` (sem `premium/`) e premium no `-web-premium` privado. [CONFIRMADO após run]
