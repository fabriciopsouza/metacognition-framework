# ADR 065 — Oferta do relatório POR SOLUÇÃO: popup no merge, decidido pelo humano, 1× por solução

- Status: **Aceito** (2026-06-05 — CI verde 3 SOs + qa-critic; state-machine de oferta testada) · Data: 2026-06-05 · Decisores: dono + squad (architect)
- Onda: telemetria/aprendizado (alvo v1.43.0) · Tipo: **EMENDA do gatilho do ADR-064** (de "fim de sessão" → "por solução, no merge"). Atende: "cada solução produz 1 relatório ao concluir; oferecido no merge; 1×; fácil; legal/LGPD".
- Relaciona/herda: ADR-064 (auto-publish — BASE), ADR-022 (`mission.md` = identidade/escopo da solução), ADR-062/063 (anonimização, pseudônimo, consent).

## Contexto

O ADR-064 dispara no FIM DE SESSÃO. O dono refinou: o relatório é **por SOLUÇÃO** (ex.: um projeto de BI/dados), gerado **ao concluí-la**, oferecido **no merge** e **1×**. Tensão: uma solução tem VÁRIOS merges (cada bloco) → "merge" sozinho ofereceria toda hora; "1× ao concluir" exige saber QUAL merge é o final — julgamento que o framework não deve adivinhar.

## Decisão (1 frase ativa)

**A oferta é SURFACED no merge de um PR da solução, mas QUEM decide se concluiu é o humano, num popup (`AskUserQuestion`), e a oferta é registrada por SOLUÇÃO (1×):** ao mergear, se a solução (identidade = `mission.md`/repo) ainda está em estado ofertável (`pending`/`deferred`), o agente abre o popup com a tabela **vai / NÃO-vai** + 4 opções — **✅ gerar+contribuir** (→ `publish_learnings`, estado `done`) · **📄 só local** (gera, não publica, `done`) · **⏳ ainda não** (`deferred` — re-pergunta no próximo merge) · **🚫 não p/ esta solução** (`declined`, terminal). O popup É a disclosure + consentimento por-solução (LGPD), além do opt-in global do 1º uso.

## Alternativas consideradas

1. **Oferecer a cada merge SEM saída** (sem `declined`/`done`). Aí sim vira nag eterno. **Rejeitada** — a oferta SURGE a cada merge enquanto não-resolvida (atende o "a cada merge" do dono), mas `declined`/`done` a ENCERRAM. "1×" = **1 publicação ao concluir**, não 1 pergunta.
2. **Adivinhar qual merge é o "final".** Frágil; o framework não deve inferir conclusão. **Rejeitada.**
3. **Só comando explícito (`/concluir`).** Limpo, mas o dono quer surfaçar no merge. **Mantido como atalho opcional.**
4. **Popup no merge + humano confirma + estado por-solução (ESCOLHIDA).** "PR+merge" (gatilho do dono) + "1× ao concluir" (humano decide) + "fácil/legal" (um popup) coexistem; `deferred`/`declined` matam o nag.

## Consequências

**Positivas:** cada solução deixa 1 relatório de aprendizado ao concluir, sem adivinhação (humano confirma no popup). **Sobre nag (honesto):** a oferta SURGE a cada merge enquanto `pending`/`deferred` (= o "a cada merge" do dono); quem ENCERRA é `done` (publicou) ou `declined` (nunca mais) — `deferred` ADIA (re-oferta), não silencia. Sem teto de re-ofertas por design (o dono pediu "a cada merge"); o `declined` é o corta-nag. LGPD por-solução (disclosure + escolha no momento); reusa todo o ADR-062/063/064 (a oferta é só a camada de QUANDO/COMO). **Negativas/limite:** merge feito FORA do agente não tem hook nativo → o popup surge **quando o agente faz o merge** OU **no próximo session-start** (via DOUTRINA — gate anunciado ADR-047, não mecanismo de runtime: o agente lê a SKILL e oferta se `should_offer`); pode atrasar a oferta, mas o estado persiste (não perde por silêncio); a identidade da solução depende de `mission.md`/repo — sem isso, cai no repo atual; o popup é ato do AGENTE (não hook) — é a doutrina (gate anunciado, ADR-047), não mecanismo de runtime. **SUPLANTA×EMENDA:** muda o gatilho/UX → novo ADR.

## Implementação (ponteiro)

- `execution_report.py`: `solution_id(root)` (de `mission.md`/origin/repo, slug seguro); `get_offer_state(sid)`/`set_offer_state(sid, state)` (marker `.claude/.report-offers/<sid>`); `should_offer(sid)` (True se `pending`/`deferred`); CLI `--offer-state` (lê + diz se deve ofertar) e `--set-offer <deferred|declined|done>` (seta; sid auto-detectado do repo). Reset (reverter `declined`) = deletar o marker em `.claude/.report-offers/`.
- **Doutrina** (`docops/SKILL.md` + `start-session`): ao mergear um PR da solução (ou no boot se mergeada e ofertável), se `should_offer`, o agente apresenta o popup `AskUserQuestion` (tabela vai/não-vai + 4 opções) e age: gerar+contribuir→`publish_learnings`+`done`; local→gera+`done`; ainda-não→`deferred`; não→`declined`.
- `.gitignore`: `.claude/.report-offers/`. **DONE quando:** ao concluir uma solução (merge + humano confirma no popup) sai 1 relatório; merges intermediários não nagueiam (`deferred`). Status→Aceito após verificação.
