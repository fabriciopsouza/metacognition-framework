# Execution-report — bloco 2b "runbooks R-01/R-02, nome vira placeholder" (ADR-062 · privado)

- **Sessão:** 21/09/2026 · **Repo de trabalho:** `linkedin-diagnostico` (privado, GitHub)
- **Pedido:** *"O nome podemos corrigir ao final, deixe o que está como placeholder, documente
  esta parte de busca e configuração inicial de forma clara / runbook, como fizemos no projeto CAPA."*
- **Rota:** squad (docops/developer de documentação); file-first no `capa-sharepoint/docs/runbooks/`
  para copiar o formato; `publica_runbooks.py` **reaproveitado sem alteração funcional** (régua §0)
- **Modelo:** autor **Fable 5.1** · QA adversarial **Sonnet isolado, crítico NOVO** (o anterior
  acumulou 210k tokens e travou uma vez), 2 rodadas
- **Arquivos:** 3 runbooks + 1 script + 3 cópias em `saida/` + 6 editados · **4 commits** · 1 PR
- **Rodadas de retrabalho:** 2 (r1 REPROVADO, 10 achados; r2 APROVADO-COM-RESSALVAS, 2)

---

## Placar gate × achado

| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| **`git grep` de segredos não pegava 3 dos 8 serviços do próprio cofre** (Cloudflare, `ghp_`, `re_`) | **QA r1** (testou o regex contra padrões reais) | Nenhum — eu escrevi o regex de cabeça e não o testei |
| **A 1ª correção do regex acusava `process.env.X_SERVICE_ROLE_KEY`** — uso correto; o gate "= 0" nunca fecharia e viraria ruído ignorado | **QA r2** (simulou um app limpo conforme a spec) | Nenhum — validei só positivos + 2 negativos triviais; faltou o negativo que importa: **código certo** |
| **RDAP do registro.br devolveu 403 COM o header** (`Nicbr-Permission-Denied`) — o A-01 de ontem ("faltava o header") estava incompleto: é bloqueio por IP/limite | **QA r1** (reproduziu ao vivo) → confirmado por mim 2× | Nenhum. Segundo dia seguido em que uma resposta de erro dessa API vira afirmação sobre o mundo |
| Faltava para onde reportar (o CAPA diz "Teams, Fabricio Souza — TI - Sistemas") | **QA r1** (comparou com o irmão) | Nenhum |
| "MP aceita PF", "Cloudflare cria MX/SPF", Resend/Brevo free, caminhos de tela sem `[INFERIDO]` | **QA r1** | Nenhum |
| "Passo 5b" na versão 1 — a convenção `3b` do CAPA existe para **não renumerar passo já executado**; aqui nada fora executado | **QA r1** | Nenhum — apliquei a forma sem a razão |
| Spam × caixa no e-mail de LGPD tratados igual | **QA r1** | Nenhum |
| Tempo do cabeçalho ≠ soma dos passos; nome literal onde devia ser `<nome>` | **QA r1** | Nenhum |
| Regex batia nos nomes das entradas do cofre no próprio runbook | **Autor** (varredura própria) | — (esperado; virou nota "rode no repo do app") |
| Frase truncada em `fontes.md` introduzida na correção | **QA r2** | Nenhum |

**Leitura:** 9 de 10 do crítico. Os dois achados do regex são o mesmo erro em duas direções —
primeiro **falso-negativo** (não pegava), depois **falso-positivo** (pegava o certo). Um gate de
segurança só existe se foi testado **contra o código correto** além do vazamento.

## Melhorias

1. **Todo gate por regex nasce com um oráculo de dois lados**: N formas de vazamento (têm de
   acusar) **e** N usos legítimos (não podem acusar), incluindo `process.env.X`, `${{ secrets }}`
   e nome de campo. O padrão de valor (prefixo+corpo, ou `= "literal"`) é reutilizável — candidato
   a nota no `developer`/`action-safety`, sem criar arquivo.
2. **Erro de API não é fato — segunda ocorrência em 2 dias.** Ontem: 403 sem header → "domínio
   inexistente". Hoje: "com header funciona" → 403 com header. A regra é a mesma do report
   anterior; a diferença é que agora está escrita no runbook como caminho oficial (site) + atalho
   (RDAP) com `403 = INCONCLUSIVO`. Reforça o candidato a linha no `anti-hallucination`.
3. **Copiar formato exige copiar a razão.** "5b" no CAPA existe por causa de execução prévia; eu
   copiei a forma. Ao clonar convenção, citar no próprio arquivo *por que* ela existe (o README
   dos runbooks agora diz).
4. **Crítico novo quando o anterior passa de ~200k tokens** — o de ontem travou; o de hoje, com
   contexto limpo, testou coisas que o outro não testaria (simulou um app).

## Boas práticas confirmadas

- File-first no projeto irmão antes de escrever: formato do CAPA reproduzido fielmente (o crítico
  comparou README-a-README).
- Reaproveitar `publica_runbooks.py` sem alteração funcional — só nota de procedência.
- Runbook nasce com `[INFERIDO]` nos caminhos de tela e "o critério é o resultado, não o botão".
- Cada parada = commit → PR → merge (regra do dono).

## Gaps declarados

- Textos legais seguem INFERIDOS (Planalto, normas.leg.br, CONAR bloqueiam fetch).
- Caminhos de tela do Lovable, Supabase, Mercado Pago, Cloudflare Email Routing, Instagram — não
  conferidos nesta data; o runbook mede por resultado.
- MP aceita PF para receber? `[INFERIDO]`. MEI serve? `[DESCONHECIDO — contador]`.
- INPI, `@handle`, registro.br, Meta Ad Library: só o dono (R-01).

## Próximo passo

Dono executa R-02 Parte A e R-01 para o candidato atual; Bloco 3 (dev no builder contra os 10 CA
da spec) começa com a Parte A pronta. Ledger: `linkedin-diagnostico-perfilcampeao`.
